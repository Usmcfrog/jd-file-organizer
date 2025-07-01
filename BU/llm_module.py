from llama_cpp import Llama
from collections import Counter
import re

# Load your model once
llm = Llama(
    model_path="models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
    n_ctx=2048,
    verbose=False
)

def _classify_chunk(chunk):
    prompt = (
        "You are a document classifier using the Johnny.Decimal system. "
        "Given the text below, respond with a two-digit ID in NN.NN format only.\n\n"
        f"{chunk}\n\nID:"
    )
    res = llm(prompt=prompt, max_tokens=10, temperature=0.1)
    return res["choices"][0]["text"].strip()

def classify_text(text, chunk_size=1500):
    text = text.replace("\n", " ")
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    preds = []
    for chunk in chunks:
        id_ = _classify_chunk(chunk)
        if re.match(r"^\d{2}\.\d{2}$", id_):
            preds.append(id_)
    if not preds:
        raise ValueError("No valid JD ID returned from any chunk.")
    return Counter(preds).most_common(1)[0][0]
