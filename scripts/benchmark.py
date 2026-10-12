import json
import statistics
import time
from collections import Counter
from pathlib import Path

from app.services.detector import DetectorDecision, regex_detector

DATASET = Path(__file__).resolve().parent.parent / "benchmarks" / "dataset.jsonl"

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0

latencies = []
attacks_per_category = Counter()
blocked_per_category = Counter()
with open(DATASET) as json_file:
    json_list = list(json_file)

for json_str in json_list:
    row = json.loads(json_str)
    start = time.perf_counter()
    result = regex_detector.check(row["text"])
    latencies.append(time.perf_counter() - start)
    blocked = result.decision == DetectorDecision.BLOCK
    is_attack = row["label"] == "attack"
    if is_attack:
        attacks_per_category[row["category"]] += 1
        blocked_per_category[row["category"]] += blocked
    if blocked and is_attack:
        true_positive += 1
    elif blocked and not is_attack:
        false_positive += 1
        print(f"Processed text: {row['text']}")
        print(f"Detector result: {result.decision} and reason: {result.reason}")
    elif not blocked and is_attack:
        false_negative += 1
    else:
        true_negative += 1

p95_ms = statistics.quantiles(latencies, n=100)[94] * 1000
recall = true_positive / (true_positive + false_negative)
fpr = false_positive / (false_positive + true_negative)

precision = true_positive / (true_positive + false_positive)
results = {
    "detector": regex_detector.name,
    "version": regex_detector.version,
    "dataset": DATASET.name,
    "tp": true_positive,
    "fp": false_positive,
    "tn": true_negative,
    "fn": false_negative,
    "recall": round(recall, 4),
    "precision": round(precision, 4),
    "fpr": round(fpr, 4),
    "p95_ms": round(p95_ms, 3),
    "attacks_per_category": dict(attacks_per_category),
    "blocked_per_category": dict(blocked_per_category),
}
out = DATASET.parent / "results" / f"{results['detector']}_{results['version']}.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results, indent=2) + "\n")

print(f"Total: tp {true_positive}, tn: {true_negative}, fp: {false_positive}, fn: {false_negative}")
print(f"Recall: {recall} and fpr: {fpr}")
print(f"P95 latency: {p95_ms:.3f} ms")
print("\nBlocked attacks per category (lowest recall first):")
for c in sorted(
    attacks_per_category, key=lambda c: blocked_per_category[c] / attacks_per_category[c]
):
    print(f"  {c:22} {blocked_per_category[c]}/{attacks_per_category[c]}")
