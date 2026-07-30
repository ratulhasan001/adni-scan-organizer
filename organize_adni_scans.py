import os
import shutil
import pandas as pd

META_FILE = "input_your_metadata_csv_file_here"  # Replace with the actual path to the metadata file (CSV or Excel)
ROOT_DIR = 'input_your_directory_here'  # Replace with the actual path to the root directory containing subject folders


def build_id_to_visit(meta_path):
    if meta_path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(meta_path)
    else:
        df = pd.read_csv(meta_path)

    df.columns = [c.strip() for c in df.columns]

    id_to_visit = {}
    for _, row in df.iterrows():
        img_id = str(row["Image Data ID"]).strip()
        if img_id:
            id_to_visit[img_id] = str(row["Visit"]).strip()
    return id_to_visit


def img_id_num(folder_name):
    # 'I12345' -> 12345, used to figure out which scan is newest
    if folder_name.startswith('I') and folder_name[1:].isdigit():
        return int(folder_name[1:])
    return 0


def flatten_subject(subject_path, id_to_visit):
    candidates = {}

    for dirpath, _, _ in os.walk(subject_path, topdown=False):
        folder_name = os.path.basename(dirpath)
        if folder_name not in id_to_visit:
            continue

        visit = id_to_visit[folder_name]
        for file_root, _, files in os.walk(dirpath):
            for fname in files:
                if not fname.lower().endswith((".nii", ".nii.gz")):
                    continue
                candidates.setdefault(visit, []).append({
                    'id': folder_name,
                    'num': img_id_num(folder_name),
                    'path': os.path.join(file_root, fname),
                    'fname': fname,
                })

    if not candidates:
        return False

    for visit, files in candidates.items():
        # newest scan = highest image ID number, keep that one
        files.sort(key=lambda f: f['num'], reverse=True)
        winner, losers = files[0], files[1:]

        ext = ".nii.gz" if winner['fname'].lower().endswith(".nii.gz") else ".nii"
        dest = os.path.join(subject_path, f"{visit}{ext}")

        if winner['path'] != dest:
            try:
                shutil.move(winner['path'], dest)
                print(f"  kept {visit} (from {winner['id']}) -> {os.path.basename(dest)}")
            except Exception as e:
                print(f"  couldn't move winner for {visit}: {e}")

        for loser in losers:
            try:
                os.remove(loser['path'])
            except Exception as e:
                print(f"  couldn't delete {loser['id']}: {e}")

    # whatever subfolders are left over (empty or otherwise) can go
    for item in os.listdir(subject_path):
        item_path = os.path.join(subject_path, item)
        if os.path.isdir(item_path):
            try:
                shutil.rmtree(item_path)
            except Exception as e:
                print(f"  couldn't remove folder {item}: {e}")

    return True


def run(root_dir, id_to_visit):
    print(f"scanning {root_dir}")
    subjects = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]

    for subject_id in subjects:
        subject_path = os.path.join(root_dir, subject_id)
        if flatten_subject(subject_path, id_to_visit):
            print(f"done with {subject_id}")


if __name__ == "__main__":
    if not os.path.exists(ROOT_DIR):
        print("root dir doesn't exist, check the path")
    else:
        mapping = build_id_to_visit(META_FILE)
        run(ROOT_DIR, mapping)
        print("\nall done")
