import json

with open("evaluation/results.json") as f:
    results = json.load(f)

faithfulness = 0
relevance = 0
persona = 0
refusal = 0

for result in results:

    scores = result["scores"]

    faithfulness += scores["faithfulness"]
    relevance += scores["relevance"]
    persona += scores["persona"]
    refusal += scores["refusal"]

count = len(results)

print("=" * 40)
print("Digital Twin Evaluation")
print("=" * 40)

print(f"Questions      : {count}")
print(f"Faithfulness   : {faithfulness / count:.2f}")
print(f"Relevance      : {relevance / count:.2f}")
print(f"Persona        : {persona / count:.2f}")
print(f"Refusal        : {refusal / count:.2f}")