import json
import sys
from pathlib import Path
from judge import judge
sys.path.append(str(Path(__file__).resolve().parent.parent))

from inference import ask_digital_twin


with open("evaluation/dataset.json") as f:
    dataset = json.load(f)

predictions = []

for sample in dataset:

    print(f"Running: {sample['question']}")

    answer = ask_digital_twin(sample["question"])

    scores = judge(
        sample["question"],
        answer
    )

    predictions.append({
        "id": sample["id"],
        "question": sample["question"],
        "answer": answer,
        "scores": scores
    })

with open("evaluation/results.json", "w") as f:
    json.dump(predictions, f, indent=4)

print("Finished")