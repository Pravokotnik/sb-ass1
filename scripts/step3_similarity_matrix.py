import csv
import os

import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the ASS1 folder
SCORES_FILE = os.path.join(ROOT, "results", "scores.csv")
PLOT_DIR = os.path.join(ROOT, "plots")


def load_matrix():
    # returns the image names (sorted) and the 80 x 80 score matrix

    # read every comparison into a dictionary: (probe, gallery) -> score
    scores = {}
    names = []
    with open(SCORES_FILE) as f:
        for row in csv.DictReader(f):
            probe = row["probe"]
            gallery = row["gallery"]
            scores[(probe, gallery)] = int(row["score"])

            if probe not in names:
                names.append(probe)

    names.sort()

    # fill the matrix: row i = probe image i, column j = gallery image j
    n = len(names)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i, j] = scores[(names[i], names[j])]

    return names, matrix


def plot_similarity_matrix(names, matrix):
    os.makedirs(PLOT_DIR, exist_ok=True)

    plt.rcParams["font.size"] = 8
    plt.figure(figsize=(3.5, 2.4))  # one report column wide
    plt.imshow(matrix, cmap="RdPu")
    plt.colorbar(label="bozorth3 score")

    # Each finger is a block of 8 images; label where each block starts.
    subjects = []
    for name in names:
        subjects.append(name.split("_")[0])

    plt.xticks(range(0, len(names), 8), subjects[::8], rotation=90)
    plt.yticks(range(0, len(names), 8), subjects[::8])

    plt.xlabel("Gallery fingerprint")
    plt.ylabel("Probe fingerprint")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "similarity_matrix.png"), dpi=300)
    print("Saved plots/similarity_matrix.png")


if __name__ == "__main__":
    names, matrix = load_matrix()
    print(f"Matrix size: {matrix.shape}")
    plot_similarity_matrix(names, matrix)
