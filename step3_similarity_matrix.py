import csv
import os

import matplotlib.pyplot as plt
import numpy as np

SCORES_FILE = "scores.csv"
PLOT_DIR = "plots"


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

    plt.imshow(matrix, cmap="RdPu")
    plt.colorbar(label="bozorth3 score")

    # Each finger is a block of 8 images; label where each block starts.
    subjects = []
    for name in names:
        subjects.append(name.split("_")[0])

    plt.xticks(range(0, len(names), 8), subjects[::8])
    plt.yticks(range(0, len(names), 8), subjects[::8])

    plt.xlabel("Gallery fingerprint")
    plt.ylabel("Probe fingerprint")
    plt.title("Similarity matrix (bozorth3 scores)")
    plt.savefig(os.path.join(PLOT_DIR, "similarity_matrix.png"), dpi=200)
    print("Saved plots/similarity_matrix.png")


if __name__ == "__main__":
    names, matrix = load_matrix()
    print(f"Matrix size: {matrix.shape}")
    plot_similarity_matrix(names, matrix)
