from generation import generate_answer


# Confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.55
LOW_CONFIDENCE_THRESHOLD = 0.35


HANDOFF_MESSAGE = (
    "I couldn't find a reliable answer in the HR policy knowledge base. "
    "Please contact HR at hr-support@company.com."
)


def classify_confidence(score):
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    elif score >= LOW_CONFIDENCE_THRESHOLD:
        return "medium"
    else:
        return "low"


def build_response(top_result, question):

    confidence_level = classify_confidence(top_result["score"])

    # Low confidence → do NOT call the LLM
    if confidence_level == "low":
        return {
            "confidence_level": confidence_level,
            "score": top_result["score"],
            "handoff": True,
            "answer_text": HANDOFF_MESSAGE,
            "policy_id": None,
            "source_reference": None,
            "related_form": None
        }

    # Medium or high confidence → use the local LLM
    answer_text = generate_answer(
        question,
        top_result["policy_text"]
    )

    # Add warning for medium confidence
    if confidence_level == "medium":
        answer_text += (
            "\n\n(Note: I'm not fully certain this is the exact policy "
            "you're asking about. Please confirm with HR if this doesn't "
            "match your situation.)"
        )

    return {
        "confidence_level": confidence_level,
        "score": top_result["score"],
        "handoff": False,
        "answer_text": answer_text,
        "policy_id": top_result["policy_id"],
        "source_reference": top_result["source_reference"],
        "related_form": top_result["related_form"]
    }