import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



from intent import detect_intent

# Map detected intents to HR policy categories
INTENT_TO_POLICY_IDS = {
    "leave_entitlement": ["HR-LEAVE-001"],
    "leave_carry_forward": ["HR-LEAVE-002"],
    "sick_leave": ["HR-SICK-001"],
    "wfh": ["HR-WFH-001"],
}

# Weights for the three scoring signals
WEIGHT_SEMANTIC = 0.6
WEIGHT_KEYWORD = 0.25
WEIGHT_INTENT = 0.15


def normalize_word(word):
    """Normalize common plural forms."""

    # Handle this irregular spelling explicitly
    if word == "leaves":
        return "leave"

    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"

    if len(word) > 4 and word.endswith("es"):
        return word[:-2]

    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]

    return word


def keyword_overlap_score(question, policy_text):
    """Measure keyword overlap between a question and a policy."""

    stopwords = {
        "a", "an", "the", "is", "are", "do", "does", "i", "my", "me",
        "to", "for", "of", "in", "on", "at", "and", "or", "what", "how",
        "many", "much", "can", "get", "have", "has", "with", "about",
    }

    def clean_words(text):
        words = (
            text.lower()
            .replace("?", "")
            .replace(",", "")
            .replace(".", "")
            .split()
        )

        return {
            normalize_word(word)
            for word in words
            if word not in stopwords and len(word) > 2
        }

    question_words = clean_words(question)
    policy_words = clean_words(policy_text)

    if not question_words:
        return 0.0

    overlap = question_words.intersection(policy_words)
    return len(overlap) / len(question_words)


def compute_combined_score(semantic_score, keyword_score, intent, policy_id):
    """Combine semantic, keyword, and intent scores."""

    intent_bonus = (
        1.0
        if policy_id in INTENT_TO_POLICY_IDS.get(intent, [])
        else 0.0
    )

    combined = (
        WEIGHT_SEMANTIC * semantic_score
        + WEIGHT_KEYWORD * keyword_score
        + WEIGHT_INTENT * intent_bonus
    )

    return combined, intent_bonus

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
        """Rank policies using semantic, keyword, and intent scores."""

        # 1. Calculate semantic similarity
        query_embedding = self.model.encode(
            [query], convert_to_numpy=True
        )
        semantic_scores = cosine_similarity(
            query_embedding, self.policy_embeddings
        )[0]

        # 2. Detect the question's intent once
        detected_intent = detect_intent(query)

        # 3. Calculate the combined score for each policy
        scored_results = []

        for idx in range(len(self.df)):
            row = self.df.iloc[idx]

            semantic_score = float(semantic_scores[idx])

            keyword_score = keyword_overlap_score(
                query, row["embedding_source"]
            )

            combined, intent_bonus = compute_combined_score(
                semantic_score,
                keyword_score,
                detected_intent,
                row["policy_id"],
            )

            scored_results.append({
                "policy_id": row["policy_id"],
                "title": row["title"],
                "policy_text": row["policy_text"],
                "source_reference": row["source_reference"],
                "related_form": row["related_form"],
                "score": combined,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "intent_bonus": intent_bonus,
                "detected_intent": detected_intent,
            })

        # 4. Sort by combined score, highest first
        scored_results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return scored_results[:top_k]    




# --- Standalone test ---

if __name__ == "__main__":
    retriever = PolicyRetriever()

    test_questions = [
        "How many annual leave days do I get?",
        "How many leaves do I get?",
        "How much vacation leave do I have?",
        "Do I need a medical certificate?",
        "Am I allowed to work remotely on Fridays?",
        "What is the capital of France?",
        "Can unused leave be carried over?",
    ]

    for question in test_questions:
        print(f"Question: {question}")

        results = retriever.retrieve(question, top_k=1)
        top_result = results[0]

        print(
            f"  {top_result['policy_id']} | "
            f"combined={top_result['score']:.3f} "
            f"(semantic={top_result['semantic_score']:.3f}, "
            f"keyword={top_result['keyword_score']:.3f}, "
            f"intent_bonus={top_result['intent_bonus']:.1f}, "
            f"intent='{top_result['detected_intent']}')"
        )
        print()