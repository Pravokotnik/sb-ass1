# Fingerprint recognition with NBIS (IBB Labs, Assignment 1)
#
# 1. Plot bozorth3 scores for genuine and impostor pairs on one graph.
# 2. Plot the similarity matrix of all the comparisons.
# 3. Plot the nfiq quality values of the fingerprints.
# 4. Find the best threshold: the one with the highest accuracy over all thresholds.
# 5. Classify every pair once with that threshold and report accuracy.
# 6. Same, but first group fingerprints by type (pcasys) and only match within a group.
#
# scores.txt was made beforehand (see proces.txt):
#   for f in out/*.xyt; do bozorth3 -A outfmt=spg -p "$f" out/*.xyt; done > scores.txt
# Each line: "score probe gallery", e.g. "60 out/101_1.xyt out/101_2.xyt"
#
# quality.txt was made beforehand:
#   for f in DB1_B_png/*.png; do echo "$(basename "${f%.png}") $(nfiq "$f")"; done > quality.txt
# Each line: "name quality", e.g. "101_1 2" (1 is best, 5 is worst)
#
# pcasys.out was made beforehand (pcasys needs images of at least 512 x 480, ours are 388 x 374,
# so each one is padded with white to 600 x 600; upscaling made pcasys crash):
#   mkdir wsq; for f in DB1_B_png/*.png; do n=$(basename "${f%.png}");
#     magick "$f" -gravity center -background white -extent 600x600 -depth 8 -type Grayscale \
#       -compress none -colorspace Gray -strip "gray:wsq/$n.gray";
#     cwsq 0.75 wsq "wsq/$n.gray" -raw_in 600,600,8,500; rm "wsq/$n.gray"; done
#   for f in wsq/*.wsq; do echo "../Desktop/MAG/SB/ASS1/$f A"; done > pcasys_list.txt
#   pcasys pcasys.prs
# Each line: "101_1.wsq: is A; nn: hyp R, conf 1.00; conup n; hyp R, conf 1.00; wrong"
#
# Run: .venv/bin/python script.py

import os

import numpy as np
import matplotlib.pyplot as plt

SCORES_FILE = "scores.txt"
QUALITY_FILE = "quality.txt"
PCASYS_FILE = "pcasys.out"
PLOT_DIR = "plots"


def name_of(path):
    # "out/101_3.xyt" -> "101_3"
    return os.path.splitext(os.path.basename(path))[0]


def subject_of(name):
    # "101_3" -> "101": the number before "_" is the finger, the one after is the impression
    return name.split("_")[0]


def read_scores():
    genuine, impostor = [], []
    with open(SCORES_FILE) as handle:
        for line in handle:
            score, probe, gallery = line.split()
            probe, gallery = name_of(probe), name_of(gallery)

            # Each pair only once: keep A vs. B, skip B vs. A and A vs. A
            if probe >= gallery:
                continue

            if subject_of(probe) == subject_of(gallery):
                genuine.append(int(score))
            else:
                impostor.append(int(score))
    return np.array(genuine), np.array(impostor)


def read_matrix():
    # All comparisons (80 x 80), including A vs. A and both A vs. B and B vs. A
    rows = []
    with open(SCORES_FILE) as handle:
        for line in handle:
            score, probe, gallery = line.split()
            rows.append((name_of(probe), name_of(gallery), int(score)))

    names = sorted(set(probe for probe, _, _ in rows))
    index = {name: i for i, name in enumerate(names)}
    matrix = np.zeros((len(names), len(names)), dtype=int)
    for probe, gallery, score in rows:
        matrix[index[probe], index[gallery]] = score
    return names, matrix


def read_quality():
    names, quality = [], []
    with open(QUALITY_FILE) as handle:
        for line in handle:
            name, value = line.split()
            names.append(name)
            quality.append(int(value))
    return names, np.array(quality)


def read_pairs():
    # Same pairs as read_scores (each only once), but keeping the names: (name1, name2, score)
    pairs = []
    with open(SCORES_FILE) as handle:
        for line in handle:
            score, probe, gallery = line.split()
            probe, gallery = name_of(probe), name_of(gallery)
            if probe < gallery:
                pairs.append((probe, gallery, int(score)))
    return pairs


def read_types():
    # Fingerprint type = the letter after the first "hyp" in each line of pcasys.out
    types = {}
    with open(PCASYS_FILE) as handle:
        for line in handle:
            if "hyp" not in line:
                continue  # skip the summary table at the end
            name = line.split(".wsq")[0]
            types[name] = line.split("hyp ")[1][0]
    return types


def plot_genuine_impostor(genuine, impostor):
    os.makedirs(PLOT_DIR, exist_ok=True)
    bins = np.arange(0, max(genuine.max(), impostor.max()) + 5, 5)
    plt.figure(figsize=(7, 4))
    # density=True so both groups are comparable, even though there are ~10x more impostor pairs
    plt.hist(impostor, bins=bins, alpha=0.6, density=True, label=f"Impostors (n={len(impostor)})")
    plt.hist(genuine, bins=bins, alpha=0.6, density=True, label=f"Genuines (n={len(genuine)})")
    plt.xlabel("bozorth3 score")
    plt.ylabel("Density")
    plt.title("bozorth3 scores of genuine and impostor pairs")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "genuine_impostor.png"), dpi=200)
    plt.close()


def plot_similarity_matrix(names, matrix):
    os.makedirs(PLOT_DIR, exist_ok=True)
    # Self-comparisons (diagonal) mostly score much higher (up to 499) than other pairs (max 289),
    # so the colour scale stops at the highest non-diagonal score; otherwise everything else would look dark
    off_diagonal = matrix[~np.eye(len(names), dtype=bool)]
    plt.figure(figsize=(7, 6))
    plt.imshow(matrix, cmap="viridis", vmin=0, vmax=off_diagonal.max())
    plt.colorbar(label="bozorth3 score")
    # One tick per finger (at its first impression) to keep the axes readable
    ticks = [i for i, name in enumerate(names) if name.endswith("_1")]
    plt.xticks(ticks, [subject_of(names[i]) for i in ticks], rotation=90)
    plt.yticks(ticks, [subject_of(names[i]) for i in ticks])
    plt.xlabel("Gallery fingerprint")
    plt.ylabel("Probe fingerprint")
    plt.title("Similarity matrix (all vs. all)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "similarity_matrix.png"), dpi=200)
    plt.close()


def plot_quality(names, quality):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.bar(range(len(names)), quality)
    plt.xticks(range(len(names)), names, rotation=90, fontsize=6)
    plt.yticks([1, 2, 3, 4, 5])
    plt.ylim(0, 5.5)
    plt.xlabel("Fingerprint")
    plt.ylabel("NFIQ quality (1 = best, 5 = worst)")
    plt.title("Fingerprint quality")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "quality.png"), dpi=200)
    plt.close()


def accuracy_per_threshold(genuine, impostor):
    # A pair is predicted "same finger" when score >= threshold.
    # Accuracy = (genuine pairs accepted + impostor pairs rejected) / all pairs
    thresholds = np.arange(0, max(genuine.max(), impostor.max()) + 2)
    accuracy = np.array([(np.sum(genuine >= t) + np.sum(impostor < t)) / (len(genuine) + len(impostor))
                         for t in thresholds])
    return thresholds, accuracy


def plot_accuracy(thresholds, accuracy, best_threshold):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(7, 4))
    plt.plot(thresholds, accuracy)
    plt.axvline(best_threshold, color="black", linestyle="--",
                label=f"Best threshold = {best_threshold} (accuracy {accuracy.max():.2%})")
    plt.xlim(0, 100)  # accuracy only keeps slowly dropping after this
    plt.xlabel("Threshold")
    plt.ylabel("Accuracy")
    plt.title("Classification accuracy across thresholds")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "accuracy.png"), dpi=200)
    plt.close()


if __name__ == "__main__":
    genuine, impostor = read_scores()
    print(f"{len(genuine)} genuine pairs, {len(impostor)} impostor pairs")
    plot_genuine_impostor(genuine, impostor)

    names, matrix = read_matrix()
    print(f"Similarity matrix: {matrix.shape[0]} x {matrix.shape[1]}")
    plot_similarity_matrix(names, matrix)


    names, quality = read_quality()
    print("Quality counts:", {q: int(np.sum(quality == q)) for q in range(1, 6)})
    plot_quality(names, quality)


    # Try every threshold and keep the one with the highest accuracy
    thresholds, accuracy = accuracy_per_threshold(genuine, impostor)
    threshold = thresholds[np.argmax(accuracy)]
    print(f"Best threshold = {threshold} (accuracy {accuracy.max():.2%})")
    plot_accuracy(thresholds, accuracy, threshold)


    # Classification: each pair only once (from read_scores), predicted "same finger" when score >= threshold.
    # Correct = genuine pair predicted same + impostor pair predicted different
    true_accepts = np.sum(genuine >= threshold)
    true_rejects = np.sum(impostor < threshold)
    total = len(genuine) + len(impostor)
    accuracy = (true_accepts + true_rejects) / total
    print(f"Classification at threshold {threshold}: {true_accepts}/{len(genuine)} genuine and "
          f"{true_rejects}/{len(impostor)} impostor pairs correct")
    print(f"Accuracy = {true_accepts + true_rejects}/{total} = {accuracy:.2%}")



    # Classification within type groups: a pair is only matched with bozorth3 if pcasys gave both
    # fingerprints the same type; pairs of different types are predicted "different finger" directly
    types = read_types()
    print("Types:", {t: list(types.values()).count(t) for t in sorted(set(types.values()))})
    correct = matched = 0
    pairs = read_pairs()
    for a, b, score in pairs:
        same_finger = subject_of(a) == subject_of(b)
        if types[a] == types[b]:
            matched += 1
            predicted_same = score >= threshold
        else:
            predicted_same = False
        correct += predicted_same == same_finger
    print(f"Matched within type groups: {matched}/{len(pairs)} pairs")
    print(f"Accuracy with types = {correct}/{len(pairs)} = {correct / len(pairs):.2%}")
