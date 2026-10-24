import glob
import os
import subprocess

from step2_genuine_impostor import load_unique_pairs, subject_of
from step5_threshold import find_best_threshold
from step6_classification import load_pairs

PNG_DIR = "DB1_B_png"
WSQ_DIR = "wsq"
LIST_FILE = "pcasys_list.txt"
PRS_FILE = "pcasys.prs"
PCASYS_OUT = "pcasys.out"

# pcasys does not read paths as given: it puts its own folders in front of them.
#   - the image list path is read relative to the NBIS install folder
#   - the image paths inside the list are read relative to the folder NBIS was built in
# (found by running pcasys with absolute paths and reading the error messages)
NBIS_INSTALL_DIR = os.path.expanduser("~/nbis/nbis")
NBIS_BUILD_DIR = os.path.expanduser("~/Downloads")

# pcasys needs images of at least 512 x 480; ours are 388 x 374, so we pad them
# with white to 600 x 600 (upscaling them instead made pcasys crash)
WSQ_SIZE = 600


def convert_to_wsq():
    # PNG -> raw grayscale (padded to 600 x 600) -> WSQ, like png2wsq_example.sh
    os.makedirs(WSQ_DIR, exist_ok=True)
    for png in sorted(glob.glob(os.path.join(PNG_DIR, "*.png"))):
        name = os.path.splitext(os.path.basename(png))[0]
        gray = os.path.join(WSQ_DIR, name + ".gray")

        subprocess.run(["magick", png,
                        "-gravity", "center", "-background", "white",
                        "-extent", f"{WSQ_SIZE}x{WSQ_SIZE}",
                        "-depth", "8", "-type", "Grayscale", "-colorspace", "Gray",
                        "-strip", "gray:" + gray], check=True)
        subprocess.run(["cwsq", "0.75", "wsq", gray,
                        "-raw_in", f"{WSQ_SIZE},{WSQ_SIZE},8,500"],
                       check=True, capture_output=True)
        os.remove(gray)
    print(f"Converted images to WSQ in {WSQ_DIR}/")


def write_pcasys_files():
    # list file: one "path_to_image.wsq A" per line (the letter does not matter)
    with open(LIST_FILE, "w") as f:
        for wsq in sorted(glob.glob(os.path.join(WSQ_DIR, "*.wsq"))):
            path = os.path.relpath(os.path.abspath(wsq), NBIS_BUILD_DIR)
            f.write(f"{path} A\n")

    list_path = os.path.relpath(os.path.abspath(LIST_FILE), NBIS_INSTALL_DIR)
    with open(PRS_FILE, "w") as f:
        f.write("network_type 2\n")
        f.write("verbose n\n")
        f.write(f"outfile {os.path.abspath(PCASYS_OUT)}\n")
        f.write(f"demo_images_list {list_path}\n")
    print(f"Wrote {LIST_FILE} and {PRS_FILE}")


def run_pcasys():
    # pcasys refuses to overwrite its output file, so delete the old one first
    if os.path.exists(PCASYS_OUT):
        os.remove(PCASYS_OUT)
    subprocess.run(["pcasys", PRS_FILE], check=True, capture_output=True)
    print(f"Ran pcasys, output in {PCASYS_OUT}")


def read_types():
    # each line looks like:
    #   101_1.wsq: is A; nn: hyp R, conf 1.00; conup n; hyp R, conf 1.00; wrong
    # the type we want is the letter after the first "hyp" (here R)
    types = {}
    with open(PCASYS_OUT) as f:
        for line in f:
            if "hyp" not in line:  # skip the summary table at the end
                continue
            name = line.split(".wsq")[0]
            types[name] = line.split("hyp ")[1][0]
    return types


def classify_with_types(pairs, types, threshold):
    correct = 0
    matched = 0
    for a, b, score in pairs:
        actually_same = subject_of(a) == subject_of(b)

        if types[a] == types[b]:
            matched += 1
            predicted_same = score >= threshold
        else:
            predicted_same = False  # different type -> not even compared

        if predicted_same == actually_same:
            correct += 1

    accuracy = correct / len(pairs)
    print(f"Pairs matched with bozorth3 (same type): {matched} / {len(pairs)}")
    print(f"Accuracy: {correct} / {len(pairs)} = {accuracy:.2%}")
    return accuracy


if __name__ == "__main__":
    convert_to_wsq()
    write_pcasys_files()
    run_pcasys()

    types = read_types()
    print("\nType of every finger (8 impressions each):")
    for subject in sorted(set(subject_of(name) for name in types)):
        subject_types = [types[name] for name in sorted(types) if subject_of(name) == subject]
        print(f"  {subject}: {' '.join(subject_types)}")

    # threshold from step 5 (tuned on all pairs, without types)
    genuine, impostor = load_unique_pairs()
    _, _, threshold, _ = find_best_threshold(genuine, impostor)
    print(f"\nThreshold from step 5: {threshold}")
    classify_with_types(load_pairs(), types, threshold)
