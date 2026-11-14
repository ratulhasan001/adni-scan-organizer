# ADNI Scan Organizer

A Python utility from the data-preparation pipeline of my undergraduate thesis on forecasting hippocampal atrophy in Alzheimer's disease from ADNI MRI data. ADNI downloads arrive as deeply nested folders per subject (one folder per image, named by its Image Data ID). This script uses the image-collection metadata file to map each Image Data ID to its visit, keeps one NIfTI scan per subject per visit, renames it after the visit and flattens each subject folder, so that every subject ends up as a simple set of `<Visit>.nii` / `<Visit>.nii.gz` files.

> **Warning:** the script works in place and is destructive. It deletes duplicate scans and removes every sub-folder inside each processed subject folder. Run it on a copy of your download.

## Features

- Reads the metadata from CSV or Excel (`.xls` / `.xlsx`) and builds an `Image Data ID -> Visit` mapping
- Searches each subject folder recursively for folders whose name is a known Image Data ID and collects the `.nii` / `.nii.gz` files inside them
- If a subject has several scans for the same visit, keeps the newest one, defined as the highest numeric image ID (`I123456` -> `123456`), and deletes the others
- Moves the kept scan to `<subject>/<Visit>.nii` or `<subject>/<Visit>.nii.gz`
- Deletes all remaining sub-folders of the subject (including empty folders and any other files they contain)
- Subjects with no matching NIfTI files are left unchanged
- Prints a log line for each kept scan, each finished subject and any file that could not be moved or deleted

## Tech stack

- Python 3
- pandas (metadata loading), openpyxl (`.xlsx` support)
- Standard library: `os`, `shutil`

## Inputs

**1. Metadata file** (`META_FILE`): the image-collection CSV/Excel exported with the ADNI download. Only two columns are used (column names are matched after trimming whitespace):

| Column | Use |
| --- | --- |
| `Image Data ID` | Image ID, which must match the name of the folder that contains the scan (e.g. `I123456`) |
| `Visit` | Visit label; becomes the output file name |

**2. Root directory** (`ROOT_DIR`): a folder containing one sub-folder per subject. The Image-ID folder can be at any depth inside the subject folder:

```
ROOT_DIR/
├── <subject_id>/
│   └── <any>/<nested>/<folders>/
│       ├── I123456/
│       │   └── scan.nii.gz
│       └── I234567/
│           └── scan.nii
└── <subject_id>/
    └── ...
```

Only files ending in `.nii` or `.nii.gz` are considered; other formats (such as DICOM) are ignored when choosing scans, but are deleted along with the sub-folders of any subject that has at least one matching NIfTI scan.

## Output

Each processed subject folder is flattened to one file per visit, named after the `Visit` value from the metadata:

```
ROOT_DIR/
└── <subject_id>/
    ├── <Visit A>.nii.gz
    └── <Visit B>.nii
```

## Configuration

The paths are constants at the top of `organize_adni_scans.py`; edit them before running:

| Constant | Meaning |
| --- | --- |
| `META_FILE` | Path to the metadata CSV or Excel file |
| `ROOT_DIR` | Path to the root directory containing the subject folders |

## Getting started

```bash
git clone https://github.com/ratulhasan001/adni-scan-organizer.git
cd adni-scan-organizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set `META_FILE` and `ROOT_DIR` in `organize_adni_scans.py`, back up the data, then run:

```bash
python organize_adni_scans.py
```

If `ROOT_DIR` does not exist, the script prints a message and exits without changes.

Notes:

- Reading legacy `.xls` files with pandas also requires `xlrd` (`pip install xlrd`); `.xlsx` and `.csv` work with `requirements.txt` as is.
- ADNI data are not included and are subject to the [ADNI data use agreement](https://adni.loni.usc.edu/).

## Limitations

- "Newest scan" is approximated by the largest image ID, not by acquisition date.
- If one Image-ID folder contains several NIfTI files, only one of them is kept for that visit.
- There is no dry-run mode and no command-line arguments; paths are set by editing the script.

---

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)
