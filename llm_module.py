import os
import re
from llama_cpp import Llama
import json

# Load and cache JD structure for validation
with open("jd_structure.json", "r", encoding="utf-8") as f:
    jd_paths = json.load(f)

# Extract just the IDs from JD paths (e.g., "12.01.03")
valid_ids = {path.split()[0].strip() for path in jd_paths if " " in path}

# Load the LLM model
llm = Llama(
    model_path="models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0
)

def classify_text_with_llm(text, max_chars=6000):
    from llama_cpp import Llama
    llm = Llama(
        model_path="models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
        n_ctx=2048
    )

    # Truncate text to avoid token overflow
    truncated_text = text[:max_chars]

    prompt = (
        "You are a document classifier. Based on the following content, "
        "classify it into one of the JD codes from the structure. Only return the JD code.\n\n"
        f"{truncated_text}\n\nJD Code:"
    )

    response = llm.create_chat_completion(
        messages=[
            {"role": "user", "content": prompt}
        ],
        stop=["\n", " "]
    )
    return response['choices'][0]['message']['content'].strip()


    raw_output = response["choices"][0]["message"]["content"].strip()
    match = re.match(r"\d{2}\.\d{2}", raw_output)

    if match and match.group() in valid_ids:
        return match.group()
    else:
        return None
