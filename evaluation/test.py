import json

from rule_based import evaluate_rules
from judge import judge

with open("evaluation/predictions.json", "r") as f:
    predictions = json.load(f)

results = []

for sample in predictions:

    print(f"Judging: {sample['question']}")

    answer = sample["answer"]

    rule_scores = evaluate_rules(
        sample["question"],
        answer
    )

    llm_scores = judge(
        sample["question"],
        answer
    )

    results.append({
        "id": sample["id"],
        "question": sample["question"],
        "answer": sample["answer"],
        "rule_scores": rule_scores,
        "llm_scores": llm_scores
    })

with open("evaluation/results.json", "w") as f:
    json.dump(results, f, indent=4)

print("Evaluation Finished")