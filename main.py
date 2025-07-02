# main.py

import os
import shutil
import csv
from datetime import datetime

from ocr_module import extract_text_from_file
from llm_module import classify_text_with_llm
from jd_utils import get_jd_folder, jd_code_dict
from jd_gui import select_files_to_analyze, show_progress_window

def move_file_to_folder(file_path, target_folder):
    if not target_folder or target_folder == ".":
        print(f"❌ ERROR: Target folder invalid for {file_path}. Aborting move!")
        return
    os.makedirs(target_folder, exist_ok=True)
    destination_path = os.path.join(target_folder, os.path.basename(file_path))

    print(f"Moving FROM: {file_path}")
    print(f"Moving TO:   {destination_path}")

    if os.path.abspath(file_path) == os.path.abspath(destination_path):
        print("⚠️ Source and destination are the same! Skipping move to prevent file loss.")
        return

    if os.path.exists(destination_path):
        print("⚠️ File with the same name already exists in destination. Renaming to avoid overwrite.")
        base, ext = os.path.splitext(destination_path)
        counter = 1
        new_destination = f"{base}_{counter}{ext}"
        while os.path.exists(new_destination):
            counter += 1
            new_destination = f"{base}_{counter}{ext}"
        destination_path = new_destination
        print(f"Moving to new name: {destination_path}")

    try:
        shutil.move(file_path, destination_path)
        print(f"✅ Moved {file_path} to {destination_path}")
    except Exception as e:
        print(f"❌ Error moving file: {e}")


def user_review_and_correction(file_path, content, llm_code, jd_code_dict):
    print(f"\n[USER REVIEW] File: {os.path.basename(file_path)}")
    print(f"LLM suggested code: {llm_code} ({jd_code_dict.get(llm_code, 'Unknown')})")
    print("If correct, press Enter. Otherwise, enter the correct code from the list below:")
    for code, desc in jd_code_dict.items():
        print(f"{code}: {desc}")
    user_input = input("JD Code (or Enter to accept): ").strip()
    if user_input and user_input in jd_code_dict:
        corrected_code = user_input
    else:
        corrected_code = llm_code
    return corrected_code

def log_correction(filename, text_snippet, llm_code, user_code):
    with open("correction_log.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), filename, text_snippet, llm_code, user_code])

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

            # ---- USER CORRECTION STEP ----
            corrected_code = user_review_and_correction(file_path, text[:250], jd_code, jd_code_dict)
            if corrected_code != jd_code:
                log_correction(file_path, text[:250], jd_code, corrected_code)
            jd_code = corrected_code
            # --------------------------------

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
    import sys
    while True:
        main()
        # After processing (including any GUI windows closing)
        answer = input("All files processed. Would you like to process another file? (y/n): ").strip().lower()
        if answer not in ["y", "yes"]:
            print("Exiting program.")
            sys.exit(0)
