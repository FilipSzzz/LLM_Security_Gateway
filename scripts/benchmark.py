import json
import statistics
import time
from pathlib import Path

from app.services.detector import DetectorDecision, regex_detector

DATASET = Path(__file__).resolve().parent.parent / "benchmarks" / "dataset.jsonl"

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0

latencies = []
with open(DATASET) as json_file:
    json_list = list(json_file)

for json_str in json_list:
    row = json.loads(json_str)
    start = time.perf_counter()
    result = regex_detector.check(row["text"])
    latencies.append(time.perf_counter() - start)
    blocked = result.decision == DetectorDecision.BLOCK
    is_attack = row["label"] == "attack"
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

print(f"Total: tp {true_positive}, tn: {true_negative}, fp: {false_positive}, fn: {false_negative}")
print(f"Recall: {recall} and fpr: {fpr}")
print(f"P95 latency: {p95_ms:.3f} ms")
