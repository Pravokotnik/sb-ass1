import csv

from step2_genuine_impostor import SCORES_FILE, load_unique_pairs, subject_of
from step5_threshold import find_best_threshold


def load_pairs():
    # returns a list of (image_a, image_b, score), each pair only once
    pairs = []
    with open(SCORES_FILE) as f:
        for row in csv.DictReader(f):
            a = row["probe"]
            b = row["gallery"]
            if a >= b:  # skip self-comparisons and the repeated B vs. A
                continue
            pairs.append((a, b, int(row["score"])))
    return pairs


def classify(pairs, threshold):
    correct_accept = 0  # same finger,      predicted same
    false_reject = 0    # same finger,      predicted different
    false_accept = 0    # different finger, predicted same
    correct_reject = 0  # different finger, predicted different

    for a, b, score in pairs:
        predicted_same = score >= threshold
        actually_same = subject_of(a) == subject_of(b)

        if actually_same and predicted_same:
            correct_accept += 1
        elif actually_same and not predicted_same:
            false_reject += 1
        elif not actually_same and predicted_same:
            false_accept += 1
        else:
            correct_reject += 1

    correct = correct_accept + correct_reject
    accuracy = correct / len(pairs)

    print(f"Compared pairs:   {len(pairs)}")
    print(f"Correct accepts:  {correct_accept}")
    print(f"Correct rejects:  {correct_reject}")
    print(f"False rejects:    {false_reject}")
    print(f"False accepts:    {false_accept}")
    print(f"Accuracy:         {correct} / {len(pairs)} = {accuracy:.2%}")
    return accuracy


if __name__ == "__main__":
    genuine, impostor = load_unique_pairs()
    _, _, threshold, _ = find_best_threshold(genuine, impostor)
    print(f"Threshold: {threshold}\n")

    classify(load_pairs(), threshold)
