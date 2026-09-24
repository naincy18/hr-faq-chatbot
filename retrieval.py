import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class PolicyRetriever:
    def __init__(self, csv_path="data/hr_policies.csv"):
        # Load the knowledge base
        self.df = pd.read_csv(csv_path)

        # Load a small, free, local embedding model
        # This downloads once (~80MB) and is cached locally after that
        print("Loading embedding model... (first run may take a minute)")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Build the text we will embed for each policy:
        # combining title + policy_text gives richer context than text alone
        self.df["embedding_source"] = self.df["title"] + ". " + self.df["policy_text"]

        # Convert every policy into an embedding vector (done once, at startup)
        print("Embedding knowledge base...")
        self.policy_embeddings = self.model.encode(
            self.df["embedding_source"].tolist(),
            convert_to_numpy=True
        )
        print(f"Done. {len(self.df)} policies embedded.\n")

    def retrieve(self, query, top_k=1):
        """
        Given a user question, return the top_k most similar policies
        along with their similarity scores (0 to 1, higher = more similar).
        """
        # Embed the user's question the same way we embedded the policies
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Compare the question's vector to every policy vector
        similarities = cosine_similarity(query_embedding, self.policy_embeddings)[0]

        # Get the indices of the top_k highest scores, sorted descending
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "policy_id": self.df.iloc[idx]["policy_id"],
                "title": self.df.iloc[idx]["title"],
                "policy_text": self.df.iloc[idx]["policy_text"],
                "source_reference": self.df.iloc[idx]["source_reference"],
                "related_form": self.df.iloc[idx]["related_form"],
                "score": float(similarities[idx])
            })
        return results


# --- Standalone test ---
if __name__ == "__main__":
    retriever = PolicyRetriever()

    test_questions = [
        "How many annual leave days do I get?",
        "What happens if I'm late to work?",
        "Can I work from home?",
        "What is the capital of France?",  # should retrieve poorly - not HR related
    ]

    for question in test_questions:
        print(f"Question: {question}")
        results = retriever.retrieve(question, top_k=2)
        for r in results:
            print(f"  [{r['score']:.3f}] {r['policy_id']} — {r['title']}")
        print()