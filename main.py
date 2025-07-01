# main.py

import os
import shutil
import threading
from ocr_module import extract_text_from_file
from llm_module import classify_text_with_llm
from jd_utils import get_jd_folder
from jd_gui import select_files_to_analyze, show_progress_window

def move_file_to_folder(file_path, target_folder):
    os.makedirs(target_folder, exist_ok=True)
    shutil.copy2(file_path, os.path.join(target_folder, os.path.basename(file_path)))
    print(f"✅ Moved {file_path} to {target_folder}")

def process_files(selected_files, update_progress, finish_progress, log_hook=None, cancel_flag=None):
    total = len(selected_files)

    for index, file_path in enumerate(selected_files):
        if cancel_flag and cancel_flag():
            update_progress(index, "⛔ Operation cancelled by user.")
            break

        status = f"📄 Processing file {index + 1} of {total}: {os.path.basename(file_path)}"
        update_progress(index, status)
        if log_hook:
            log_hook(status)

        try:
            update_progress(index, f"🔍 Extracting text from: {os.path.basename(file_path)}")
            if log_hook:
                log_hook(f"Extracting text from: {file_path}")
            text = extract_text_from_file(file_path)

            if not text.strip():
                warning = f"⚠️ No text extracted from {os.path.basename(file_path)}"
                update_progress(index, warning)
                if log_hook:
                    log_hook(warning)
                continue

            update_progress(index, f"🧠 Classifying: {os.path.basename(file_path)}")
            if log_hook:
                log_hook(f"Classifying text from: {file_path}")
            jd_code = classify_text_with_llm(text)

            update_progress(index, f"📁 Resolving JD folder for code: {jd_code}")
            if log_hook:
                log_hook(f"Resolved JD Code: {jd_code}")
            jd_folder = get_jd_folder(jd_code)

            if jd_folder:
                move_file_to_folder(file_path, jd_folder)
                msg = f"✅ Moved to: {jd_folder}"
                update_progress(index, msg)
                if log_hook:
                    log_hook(msg)
            else:
                error = f"❌ Could not resolve JD folder for: {jd_code}"
                update_progress(index, error)
                if log_hook:
                    log_hook(error)

        except Exception as e:
            err_msg = f"❌ Error processing {file_path}: {str(e)}"
            update_progress(index, err_msg)
            if log_hook:
                log_hook(err_msg)

    finish_progress()

def main():
    selected_files = select_files_to_analyze()

    if not selected_files:
        print("❌ No files selected. Exiting.")
        return

    show_progress_window(
        files=selected_files,
        process_function=process_files
    )

if __name__ == "__main__":
    main()
