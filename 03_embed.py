import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

import cohere

INPUT_FILE = "chunks.jsonl"
OUTPUT_FILE = "embeddings.jsonl"

# Define batch size (Cohere API allows up to 96 docs per request)
BATCH_SIZE = 96  

co = cohere.ClientV2(api_key=os.getenv("CO_API_KEY"))
total_docs = 0

def read_jsonl(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def write_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as f: 
        for item in data:
            f.write(json.dumps(item) + "\n")

def batch_process():
    buffer = []
    # Clear file before writing
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f: 
        pass 

    for chunk in read_jsonl(INPUT_FILE):
        buffer.append(chunk)

        if len(buffer) >= BATCH_SIZE:
            process_batch(buffer)
            buffer.clear()

    if buffer:
        process_batch(buffer)

def process_batch(batch):
    """Handles embedding requests and writes results to file."""
    global total_docs
    try:
        texts = [doc["Text"] for doc in batch]
        response = co.embed(
            texts=texts, 
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        )

        for doc, embedding in zip(batch, response.embeddings.float_):
            if embedding:
                doc["embedding"] = embedding

        write_jsonl(OUTPUT_FILE, batch)
        total_docs += len(batch)
        print(f"Processed {total_docs} documents...")

    except Exception as e:
        print(e)
        print(f"Error processing batch: {e}")
        time.sleep(5)  # Wait before retrying

# Run batch processing
batch_process()

print(f"Embeddings saved to {OUTPUT_FILE}")
