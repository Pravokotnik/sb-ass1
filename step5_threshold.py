import os
import matplotlib.pyplot as plt

from step2_genuine_impostor import load_unique_pairs

PLOT_DIR = "plots"


def accuracy_at(threshold, genuine, impostor):
    # genuine pair is correct if accepted, impostor pair is correct if rejected
    correct = 0
    for score in genuine:
        if score >= threshold:
            correct += 1
    for score in impostor:
        if score < threshold:
            correct += 1
    return correct / (len(genuine) + len(impostor))


def find_best_threshold(genuine, impostor):
    # try every threshold, remember the best one
    thresholds = list(range(0, max(genuine.max(), impostor.max()) + 2, 1))
    accuracies = []

    best_threshold = 0
    best_accuracy = 0
    for threshold in thresholds:
        accuracy = accuracy_at(threshold, genuine, impostor)
        accuracies.append(accuracy)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold

    return thresholds, accuracies, best_threshold, best_accuracy


def plot_accuracy(thresholds, accuracies, best_threshold, best_accuracy):
    os.makedirs(PLOT_DIR, exist_ok=True)

    plt.plot(thresholds, accuracies, color="#b339c5")
    plt.axvline(best_threshold, color="grey", linestyle="--",
                label=f"best threshold = {best_threshold} ({best_accuracy:.2%})")
    plt.xlabel("Threshold (bozorth3 score)")
    plt.ylabel("Accuracy")
    plt.title("Accuracy for every threshold")
    plt.legend()
    plt.savefig(os.path.join(PLOT_DIR, "accuracy.png"), dpi=200)
    print("Saved plots/accuracy.png")


if __name__ == "__main__":
    # find best bozorth3 score threshold for genuine vs impostor pairs
    genuine, impostor = load_unique_pairs()
    thresholds, accuracies, best_threshold, best_accuracy = find_best_threshold(genuine, impostor)

    print(f"Best threshold: {best_threshold}")
    print(f"Accuracy:       {best_accuracy:.2%}")
    print(f"Genuine pairs accepted:  {(genuine >= best_threshold).sum()} / {len(genuine)}")
    print(f"Impostor pairs rejected: {(impostor < best_threshold).sum()} / {len(impostor)}")

    plot_accuracy(thresholds, accuracies, best_threshold, best_accuracy)
