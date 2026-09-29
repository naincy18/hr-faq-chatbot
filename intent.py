
# Rule-based intent detection for the HR chatbot


INTENT_TRIGGERS = {
    "leave_entitlement": [
        "annual leave",
        "how many leave",
        "how many leaves",
        "leave days",
        "vacation",
        "vacation leave",
        "leave entitlement",
        "paid leave",
        "days off",
        "how much leave",
        "leave balance",
        "leaves do i get",
        "leaves am i entitled",
        "how many days off",
    ],

    "leave_carry_forward": [
        "carry forward",
        "carry over",
        "carried over",
        "rollover",
        "roll over",
        "unused leave",
        "leave into next year",
        "leftover leave",
    ],

    "sick_leave": [
        "sick leave",
        "sick days",
        "medical leave",
        "medical certificate",
        "sick pay",
        "fall ill",
        "when i'm sick",
        "when i am sick",
        "doctor's note",
        "medical certificate needed",
    ],

    "wfh": [
        "work from home",
        "wfh",
        "remote work",
        "working remotely",
        "work remotely",
        "home office",
        "telecommute",
        "work from a different location",
    ],
}


def detect_intent(question):
    """
    Identify the topic of an HR question using trigger phrases.
    Return 'other' when no known intent matches.
    """

    question_lower = question.lower()

    scores = {}

    for intent, triggers in INTENT_TRIGGERS.items():
        match_count = sum(
            1 for phrase in triggers
            if phrase in question_lower
        )

        if match_count > 0:
            scores[intent] = match_count

    if not scores:
        return "other"

    return max(scores, key=scores.get)


# Standalone tests
if __name__ == "__main__":
    test_questions = [
    "How many annual leave days do I get?",
    "How many leaves do I get?",
    "What is my leave entitlement?",
    "How many sick days do I get?",
    "Do I need a medical certificate?",
    "Can I work from home?",
    "What's the WFH policy?",
    "Am I allowed to work remotely?",
    "Can unused leave be carried over?",
    "What is the capital of France?",
    "How is my salary paid?",
]

    for question in test_questions:
        intent = detect_intent(question)
        print(f"{intent:20s} <- {question}")