import os
import shutil
from datetime import datetime

def move_file_to_jd_folder(file_path, jd_id, jd_root):
    if not jd_id or not jd_root:
        raise ValueError("JD ID or root folder missing.")

    folder_name = None
    for root, dirs, _ in os.walk(jd_root):
        for d in dirs:
            if d.startswith(jd_id):
                folder_name = os.path.join(root, d)
                break

    if not folder_name:
        raise FileNotFoundError(f"No folder found matching JD ID: {jd_id}")

    base_name = os.path.basename(file_path)
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    new_name = f"{date_prefix} - {base_name}"
    new_path = os.path.join(folder_name, new_name)

    shutil.move(file_path, new_path)
