import csv
import glob
import os
import subprocess

import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the ASS1 folder
PNG_DIR = os.path.join(ROOT, "DB1_B_png")
QUALITY_FILE = os.path.join(ROOT, "results", "quality.csv")
PLOT_DIR = os.path.join(ROOT, "plots")


def compute_quality():
    # runs nfiq on every image; nfiq prints a single number (1-5)
    qualities = {}
    for png in sorted(glob.glob(os.path.join(PNG_DIR, "*.png"))):
        name = os.path.splitext(os.path.basename(png))[0]
        result = subprocess.run(["nfiq", png], check=True, capture_output=True, text=True)
        qualities[name] = int(result.stdout.strip())

    os.makedirs(os.path.dirname(QUALITY_FILE), exist_ok=True)
    with open(QUALITY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "quality"])
        for name in qualities:
            writer.writerow([name, qualities[name]])
    print(f"Saved {len(qualities)} quality values to results/quality.csv")

    return qualities


def plot_quality(qualities):
    os.makedirs(PLOT_DIR, exist_ok=True)

    # count how many images have each quality level
    levels = [1, 2, 3, 4, 5]
    counts = []
    for level in levels:
        count = 0
        for name in qualities:
            if qualities[name] == level:
                count += 1
        counts.append(count)
        print(f"Quality {level}: {count} images")

    plt.rcParams["font.size"] = 8
    plt.figure(figsize=(3.5, 1.8))  # one report column wide
    plt.bar(levels, counts, color="#760176")
    plt.xlabel("nfiq quality (1 = best, 5 = worst)")
    plt.ylabel("Number of images")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "quality.png"), dpi=300)
    print("Saved plots/quality.png")


if __name__ == "__main__":
    qualities = compute_quality()
    plot_quality(qualities)
