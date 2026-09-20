"""Statistics, and the acceptance rule that turns them into a verdict.

The rule is deliberately dull, because it has to be written down and committed
*before* a live call is made. Three shapes:

* **proportion** — a share out of n. The reported number is reproduced when it
  falls inside our 95% Wilson interval; partially reproduced when it is outside
  but within the tolerance the job fixed; otherwise not reproduced. The Wilson
  interval is used rather than the normal approximation because it behaves at
  the edges, where a near-perfect accuracy actually lives.
* **absolute** — a number with no n behind it (ECE, AUC, a mean). Judged against
  two fixed distances.
* **gate** — a claim admitting no tolerance at all, such as "no dangerous command
  got through". One escape is a failure.

An unmeasured criterion is "not run". It is never a pass.
"""

import math

REPRODUCED = "reproduced"
PARTIAL = "partially reproduced"
FAILED = "not reproduced"
NOT_RUN = "not run"

#: The order of severity, weakest verdict last.
RANK = {REPRODUCED: 0, PARTIAL: 1, FAILED: 2, NOT_RUN: 3}

Z95 = 1.959963984540054


def wilson(k, n, z=Z95):
    """The 95% Wilson score interval for k successes out of n."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    denominator = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def roc_auc(scores, labels):
    """Area under the ROC curve by rank, ties counted as half. None if one class."""
    positives = [s for s, y in zip(scores, labels) if y == 1]
    negatives = [s for s, y in zip(scores, labels) if y == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    for p in positives:
        for q in negatives:
            if p > q:
                wins += 1.0
            elif p == q:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def confusion(scores, labels, threshold=0.5):
    """The confusion matrix at a threshold, with the shares that follow from it."""
    tp = fp = tn = fn = 0
    for score, label in zip(scores, labels):
        predicted = 1 if score >= threshold else 0
        if predicted == 1 and label == 1:
            tp += 1
        elif predicted == 1:
            fp += 1
        elif label == 1:
            fn += 1
        else:
            tn += 1
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if precision + recall else 0.0)
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "n": total,
            "correct": tp + tn,
            "accuracy": (tp + tn) / total if total else 0.0,
            "precision": precision, "recall": recall, "f1": f1}


def ece(scores, labels, bins=10):
    """Expected calibration error over equal-width probability bins."""
    if not scores:
        return 0.0
    buckets = [[] for _ in range(bins)]
    for score, label in zip(scores, labels):
        index = min(bins - 1, max(0, int(score * bins)))
        buckets[index].append((score, label))
    total = len(scores)
    out = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        claimed = sum(s for s, _ in bucket) / len(bucket)
        actual = sum(y for _, y in bucket) / len(bucket)
        out += len(bucket) / total * abs(claimed - actual)
    return out


def _judgement(verdict, reported, observed, extra=None):
    out = {"verdict": verdict, "reported": reported, "observed": observed}
    out.update(extra or {})
    return out


def judge_proportion(reported, k, n, tolerance):
    """A reported share against our own sample."""
    if n <= 0:
        return _judgement(NOT_RUN, reported, None, {"n": 0, "ci95": None})
    observed = k / n
    low, high = wilson(k, n)
    if low <= reported <= high:
        verdict = REPRODUCED
    elif abs(observed - reported) <= tolerance:
        verdict = PARTIAL
    else:
        verdict = FAILED
    return _judgement(verdict, reported, observed,
                      {"n": n, "k": k, "ci95": [low, high],
                       "tolerance": tolerance})


def judge_absolute(reported, observed, tolerance, partial):
    """A number with no denominator behind it, judged by distance alone."""
    if observed is None:
        return _judgement(NOT_RUN, reported, None, {"tolerance": tolerance})
    distance = abs(observed - reported)
    if distance <= tolerance:
        verdict = REPRODUCED
    elif distance <= partial:
        verdict = PARTIAL
    else:
        verdict = FAILED
    return _judgement(verdict, reported, observed,
                      {"distance": distance, "tolerance": tolerance,
                       "partial_tolerance": partial})


def judge_gate(reported, observed):
    """A claim with no tolerance: it held exactly, or it did not hold."""
    if observed is None:
        return _judgement(NOT_RUN, reported, None)
    return _judgement(REPRODUCED if observed == reported else FAILED,
                      reported, observed)


def judge(criterion, measured):
    """Apply one job criterion to the measured numbers."""
    kind = criterion["kind"]
    metric = criterion["metric"]
    if kind == "proportion":
        counts = measured.get(metric)
        if counts is None:
            return _judgement(NOT_RUN, criterion["reported"], None, {"n": 0})
        if not isinstance(counts, dict):
            # A share measured without a denominator we can defend: there is no
            # interval to build, so it is judged by distance alone and the job's
            # tolerance does all the work.
            return judge_absolute(criterion["reported"], counts,
                                  criterion.get("tolerance", 0.0),
                                  criterion.get("tolerance", 0.0))
        return judge_proportion(criterion["reported"], counts["k"], counts["n"],
                                criterion.get("tolerance", 0.0))
    if kind == "absolute":
        return judge_absolute(criterion["reported"], measured.get(metric),
                              criterion.get("tolerance", 0.0),
                              criterion.get("partial_tolerance",
                                            criterion.get("tolerance", 0.0) * 5))
    return judge_gate(criterion["reported"], measured.get(metric))
