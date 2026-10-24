import csv
import os

import matplotlib.pyplot as plt
import numpy as np

SCORES_FILE = "scores.csv"
PLOT_DIR = "plots"

GENUINE_COLOR = "#ee0dae"   # blue
IMPOSTOR_COLOR = "#8d32ee"  # orange

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


def plot_genuine_impostor(genuine, impostor):
    os.makedirs(PLOT_DIR, exist_ok=True)
    bins = range(0, max(genuine.max(), impostor.max()) + 2, 1)

    plt.hist(impostor, bins=bins, alpha=0.7, color=IMPOSTOR_COLOR, label="Impostor")
    plt.hist(genuine, bins=bins, alpha=0.7, color=GENUINE_COLOR, label="Genuine")

    plt.xlabel("bozorth3 score")
    plt.ylabel("Number of pairs")
    plt.title("Genuine vs. impostor bozorth3 scores")
    plt.legend()
    plt.savefig(os.path.join(PLOT_DIR, "genuine_impostor.png"), dpi=200)
    print("Saved plots/genuine_impostor.png")


if __name__ == "__main__":
    genuine, impostor = load_unique_pairs()
    print(f"Genuine pairs:  {len(genuine):5d}  mean={genuine.mean():6.1f}  "
          f"min={genuine.min()}  max={genuine.max()}")
    print(f"Impostor pairs: {len(impostor):5d}  mean={impostor.mean():6.1f}  "
          f"min={impostor.min()}  max={impostor.max()}")
    plot_genuine_impostor(genuine, impostor)
