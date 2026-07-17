import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from context import resume, summary


GROUND_TRUTH = (resume + "\n" + summary).lower()


def evaluate_rules(question: str, answer: str):

    score = {
        "empty_response": False,
        "should_refuse": False,
        "refused_correctly": False,
        "mentioned_chatgpt": False,
        "grounded": True,
    }

    answer_lower = answer.lower()
    question_lower = question.lower()

    # -------------------------
    # Rule 1 : Empty response
    # -------------------------

    if len(answer.strip()) == 0:
        score["empty_response"] = True

    # -------------------------
    # Rule 2 : Out of scope
    # -------------------------

    out_of_scope_keywords = [
        "capital",
        "france",
        "weather",
        "movie",
        "football",
        "recipe",
        "bitcoin",
    ]

    should_refuse = any(
        word in question_lower
        for word in out_of_scope_keywords
    )

    score["should_refuse"] = should_refuse

    refusal_phrase = (
        "i am designed to answer questions about parth"
    )

    if should_refuse and refusal_phrase in answer_lower:
        score["refused_correctly"] = True

    # -------------------------
    # Rule 3 : Broke persona
    # -------------------------

    if "chatgpt" in answer_lower:
        score["mentioned_chatgpt"] = True

    return score