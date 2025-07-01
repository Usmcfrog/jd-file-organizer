import os
import json

# Load the Johnny.Decimal structure from the known file
with open("jd_structure.json", "r", encoding="utf-8") as f:
    jd_structure = json.load(f)

def get_jd_folder(file_path):
    """
    Given a file path, attempt to classify it based on keywords using the Johnny.Decimal structure.
    Returns the best-matching folder path or None.
    """
    file_name = os.path.basename(file_path).lower()

    best_match = None
    highest_score = 0

    for path in jd_structure:
        parts = path.lower().split("/")
        score = sum(1 for part in parts if part in file_name)

        if score > highest_score:
            highest_score = score
            best_match = path

    return best_match

def get_all_jd_folders():
    """
    Returns a list of all JD folder paths from the structure.
    """
    return jd_structure
