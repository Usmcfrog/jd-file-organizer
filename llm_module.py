import os
import re
import json
import csv
from llama_cpp import Llama
from jd_utils import collect_jd_codes, jd_code_dict

# Load config and model path from preferences
with open("jd_structure.json", "r", encoding="utf-8") as f:
    jd_json = json.load(f)
with open("preferences.json", "r", encoding="utf-8") as f:
    prefs = json.load(f)
model_path = prefs["llm_model_path"]

structure = jd_json.get("content", jd_json)
jd_paths = collect_jd_codes(structure)

valid_ids = {path.split()[0].strip() for path in jd_paths if " " in path}

jd_code_dict = {}
for path in jd_paths:
    code, _, desc = path.partition(" ")
    jd_code_dict[code] = desc

# Only load model ONCE
llm = Llama(
    model_path=model_path,
    n_ctx=2048,  # Or increase to match your model/context length if memory allows
    n_threads=4,
    n_gpu_layers=0
)

def get_recent_corrections(n=5):
    corrections = []
    try:
        with open("correction_log.csv", newline='', encoding="utf-8") as f:
            reader = list(csv.reader(f))
            # Only get most recent n corrections
            for row in reader[-n:]:
                _, _, snippet, llm_code, user_code = row
                if llm_code != user_code:
                    corrections.append((snippet, user_code))
    except FileNotFoundError:
        pass
    return corrections

def classify_text_with_llm(text, max_chars=1000, max_codes=25):
    # Truncate content and codes for prompt size
    truncated_text = text[:max_chars]
    short_text = truncated_text
    code_items = list(jd_code_dict.items())[:max_codes]
    choices = "\n".join([f"{code}: {desc}" for code, desc in code_items])

    corrections = get_recent_corrections()
    example_block = ""
    for snippet, code in corrections:
        example_block += f"Content: {snippet}\nJD Code: {code}\n"

    prompt = (
        "Classify the following document content into the best JD code from the list. "
        "ONLY output the code, nothing else. For example: 11.17\n"
        f"{example_block}"
        "If unsure, choose the closest match.\n"
        "Here are some examples:\n"
        "JD Codes:\n"
        "11.11: Birth & Identity Documents (birth certificates, ID cards, passports)\n"
        "11.17: Academic & Qualifications (school transcripts, diplomas, degrees)\n"
        "Content: Jane Doe, Bachelor of Science, Official Transcript from Texas A&M\n"
        "JD Code: 11.17\n"
        "Content: John Smith, birth certificate, issued Dallas, TX\n"
        "JD Code: 11.11\n\n"
        "JD Codes:\n"
        f"{choices}\n\n"
        "Content:\n"
        f"{short_text}\n\n"
        "JD Code:"
    )


    print(f"[DEBUG] Prompt sent to LLM:\n{prompt}")

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        stop=["JD Code:"]
    )
    raw_output = response["choices"][0]["message"]["content"].strip()
    print(f"[DEBUG] LLM returned: '{raw_output}'")

    # Find a JD code in the output, regardless of position
    match = re.search(r"\b\d{2}\.\d{2}\b", raw_output)
    if match and match.group() in valid_ids:
        jd_code = match.group()
    else:
        jd_code = None

    # Fallback to Inbox if the code is missing or invalid
    if not jd_code or jd_code not in jd_code_dict:
        jd_code = "11.01"

    return jd_code
