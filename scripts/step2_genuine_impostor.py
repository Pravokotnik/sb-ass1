import csv
import os

import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the ASS1 folder
SCORES_FILE = os.path.join(ROOT, "results", "scores.csv")
PLOT_DIR = os.path.join(ROOT, "plots")

GENUINE_COLOR = "#ee0dae"   # blue
IMPOSTOR_COLOR = "#760176"  # orange

def subject_of(name):
    # so that '104_3' -> '104' (ignore finger number)
    return name.split("_")[0]


def load_unique_pairs():
    # returns genuine and impostor scores as numpy arrays
    genuine, impostor = [], []
    with open(SCORES_FILE) as f:
        for row in csv.DictReader(f):
            a, b, score = row["probe"], row["gallery"], int(row["score"])
            if a >= b:  # skip self-comparisons and the repeated B vs. A
                continue
            if subject_of(a) == subject_of(b):
                genuine.append(score)
            else:
                impostor.append(score)
    return np.array(genuine), np.array(impostor)


def plot_genuine_impostor(genuine, impostor, threshold):
    os.makedirs(PLOT_DIR, exist_ok=True)
    bins = range(0, max(genuine.max(), impostor.max()) + 2, 1)
    plt.rcParams["font.size"] = 8
    plt.figure(figsize=(3.5, 2.3))  # one report column wide

    plt.hist(impostor, bins=bins, alpha=0.7, color=IMPOSTOR_COLOR, label="Impostor")
    plt.hist(genuine, bins=bins, alpha=0.7, color=GENUINE_COLOR, label="Genuine")

    plt.axvline(threshold, color="grey", linestyle="--",
                label=f"threshold = {threshold}")

    plt.yscale("log")
    plt.xlabel("bozorth3 score")
    plt.ylabel("Number of pairs (log scale)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "genuine_impostor.png"), dpi=300)
    print("Saved plots/genuine_impostor.png")


if __name__ == "__main__":
    genuine, impostor = load_unique_pairs()
    print(f"Genuine pairs:  {len(genuine):5d}  mean={genuine.mean():6.1f}  "
          f"min={genuine.min()}  max={genuine.max()}")
    print(f"Impostor pairs: {len(impostor):5d}  mean={impostor.mean():6.1f}  "
          f"min={impostor.min()}  max={impostor.max()}")
    from step5_threshold import find_best_threshold
    best_threshold = find_best_threshold(genuine, impostor)[2]
    plot_genuine_impostor(genuine, impostor, best_threshold)
