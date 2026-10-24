"""
Step 1 ("First steps") of Assignment 1 - Fingerprint Recognition with NBIS.

  1. Convert every TIFF in DB1_B/ to PNG          (magick img.tif img.png)
  2. Extract minutiae from every PNG              (mindtct img.png out/img)
  3. Compare every fingerprint with every other   (bozorth3 out/a.xyt out/b.xyt)

Output:
  DB1_B_png/<name>.png   converted images (also used later by nfiq / png2wsq)
  out/<name>.*           mindtct output files (.xyt is the one bozorth3 needs)
  scores.csv             all-vs-all bozorth3 scores: probe,gallery,score

Run:  python step1_prepare.py
"""

import csv
import glob
import os
import subprocess

TIFF_DIR = "DB1_B"
PNG_DIR = "DB1_B_png"
MINUTIAE_DIR = "out"
SCORES_FILE = "scores.csv"


def convert_tiff_to_png():
    """mindtct cannot read TIFF (it silently fails), so convert to PNG first."""
    os.makedirs(PNG_DIR, exist_ok=True)
    tiffs = sorted(glob.glob(os.path.join(TIFF_DIR, "*.tif")))
    for tif in tiffs:
        name = os.path.splitext(os.path.basename(tif))[0]
        png = os.path.join(PNG_DIR, name + ".png")
        subprocess.run(["magick", tif, png], check=True)
    print(f"Converted {len(tiffs)} TIFF images to PNG in {PNG_DIR}/")


def compute_minutiae():
    """Run mindtct on every PNG. It writes several files per image; .xyt holds
    one minutia per line: x  y  angle(theta)  quality."""
    os.makedirs(MINUTIAE_DIR, exist_ok=True)
    pngs = sorted(glob.glob(os.path.join(PNG_DIR, "*.png")))
    for png in pngs:
        name = os.path.splitext(os.path.basename(png))[0]
        subprocess.run(["mindtct", png, os.path.join(MINUTIAE_DIR, name)], check=True)

        xyt = os.path.join(MINUTIAE_DIR, name + ".xyt")
        if not os.path.isfile(xyt):
            raise RuntimeError(f"mindtct produced no {xyt}")
    print(f"Computed minutiae for {len(pngs)} images in {MINUTIAE_DIR}/")


def compute_bozorth_scores():
    """All vs. all comparisons. Instead of 80*80 separate bozorth3 calls we call
    it once per probe with the whole gallery (-p probe file1 file2 ...), which
    gives exactly the same scores as `bozorth3 a.xyt b.xyt`, just faster.
    -A outfmt=spg prints "score probe gallery" on each line."""
    xyts = sorted(glob.glob(os.path.join(MINUTIAE_DIR, "*.xyt")))
    rows = []
    for probe in xyts:
        result = subprocess.run(
            ["bozorth3", "-A", "outfmt=spg", "-p", probe] + xyts,
            check=True, capture_output=True, text=True,
        )
        for line in result.stdout.strip().splitlines():
            score, p, g = line.split()
            rows.append((name_of(p), name_of(g), int(score)))

    with open(SCORES_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["probe", "gallery", "score"])
        writer.writerows(rows)
    print(f"Saved {len(rows)} bozorth3 scores ({len(xyts)} x {len(xyts)}) to {SCORES_FILE}")


def name_of(path):
    return os.path.splitext(os.path.basename(path))[0]


if __name__ == "__main__":
    convert_tiff_to_png()
    compute_minutiae()
    compute_bozorth_scores()
