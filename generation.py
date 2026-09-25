import ollama

MODEL_NAME = "llama3.2:1b"

SYSTEM_PROMPT = """You are an HR policy assistant.

IMPORTANT:
The POLICY TEXT below is the ONLY source of information you may use.

Your job is to answer the QUESTION using the information in the POLICY TEXT.

If the POLICY TEXT contains an answer, ALWAYS give the answer.
Do not refuse when the policy contains relevant information.

Rules:
1. Use only facts explicitly present in the POLICY TEXT.
2. Do not add outside knowledge.
3. Do not invent numbers, dates, or rules.
4. Keep the answer to 1-3 sentences.
5. Answer directly and naturally.
6. If the POLICY TEXT truly contains no information that can answer the QUESTION, respond exactly:
"I couldn't find a reliable answer in the HR policy knowledge base. Please contact HR."
"""


def generate_answer(question, policy_text):
    """
    Uses a local LLM to rephrase the retrieved policy_text
    into a natural answer — using only the policy text.
    """

    user_prompt = f"""POLICY TEXT:
{policy_text}

QUESTION:
{question}

Answer the QUESTION using only the POLICY TEXT above."""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0.2},
    )

    return response["message"]["content"].strip()


# --- Standalone test ---
if __name__ == "__main__":

    test_policy = (
        "All full-time employees are eligible for 24 annual leave days per "
        "calendar year. Leave is accrued monthly at a rate of 2 days per "
        "month and must be approved by the employee's direct manager at "
        "least 3 working days in advance."
    )

    test_question = "How many annual leave days do I get?"

    print("Generating answer...")

    answer = generate_answer(test_question, test_policy)

    print("\nGenerated answer:\n", answer)