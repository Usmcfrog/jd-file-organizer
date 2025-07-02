import os
import json

# Load the tree-structured JD hierarchy
with open("preferences.json", "r", encoding="utf-8") as f:
    prefs = json.load(f)
root = prefs["destination_folder"]

with open("jd_structure.json", "r", encoding="utf-8") as f:
    jd_json = json.load(f)

def collect_jd_codes(structure):
    """Recursively collect all JD codes and their descriptions from the structure."""
    codes = []
    if isinstance(structure, dict):
        name = structure.get("name", "")
        # JD code format is always 'NN.NN ...'
        if len(name) >= 5 and name[2] == "." and name[:2].isdigit() and name[3:5].isdigit():
            codes.append(name)
        for child in structure.get("children", []):
            codes.extend(collect_jd_codes(child))
    elif isinstance(structure, list):
        for item in structure:
            codes.extend(collect_jd_codes(item))
    return codes

def find_jd_folder_path(structure, jd_code, path_so_far=None):
    """
    Recursively search for a JD code in the tree structure.
    Returns the path as a list of folder names, or None if not found.
    """
    if path_so_far is None:
        path_so_far = []

    # If current node is a dict with 'name' key
    if isinstance(structure, dict):
        name = structure.get("name", "")
        # Check if this folder matches the JD code (start of string)
        if name.startswith(jd_code):
            return path_so_far + [name]
        # Otherwise, search children recursively
        for child in structure.get("children", []):
            result = find_jd_folder_path(child, jd_code, path_so_far + [name])
            if result:
                return result

    # If current node is a list (e.g., top-level 'content')
    elif isinstance(structure, list):
        for item in structure:
            result = find_jd_folder_path(item, jd_code, path_so_far)
            if result:
                return result

    return None

def get_jd_folder(jd_code):
    """
    Find the folder path for a JD code (e.g., "11.22").
    Returns the full absolute path as an OS-specific string, or None.
    """
    structure = jd_json.get("content", jd_json)
    folder_path = find_jd_folder_path(structure, jd_code)
    if folder_path:
        # Use the root directory from preferences.json!
        return os.path.abspath(os.path.join(root, *folder_path))
    return None

def build_jd_code_dict(structure):
    """Recursively build a code: description dictionary."""
    d = {}
    if isinstance(structure, dict):
        name = structure.get("name", "")
        # Split "11.22 Academic & Qualifications" → code, desc
        if len(name) >= 5 and name[2] == "." and name[:2].isdigit() and name[3:5].isdigit():
            code, _, desc = name.partition(" ")
            d[code] = desc.strip()
        for child in structure.get("children", []):
            d.update(build_jd_code_dict(child))
    elif isinstance(structure, list):
        for item in structure:
            d.update(build_jd_code_dict(item))
    return d

structure = jd_json.get("content", jd_json)
jd_code_dict = build_jd_code_dict(structure)
