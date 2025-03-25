import json
import os

from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

load_dotenv()

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

BATCH_SIZE = 50
INDEX_NAME = "recipes"
INPUT_FILE = "embeddings.jsonl"

client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
    verify_certs=False,
    use_ssl=True
)

print(client.info())

def load_data_in_batches(file_path, batch_size):
    batch = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            batch.append({
                "_index": INDEX_NAME,
                "_source": doc
            })
            
            if len(batch) >= batch_size:
                yield batch
                batch = []

    if batch:
        yield batch

# Bulk insert into Elasticsearch in batches
for batch in load_data_in_batches(INPUT_FILE, BATCH_SIZE):
    try:
        helpers.bulk(client, batch)
        print(f"Inserted {len(batch)} documents into '{INDEX_NAME}' index.")
    except Exception as e:
        print(e)
        print(f"Error inserting documents: {e}")