import json
import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

DATASET_NAME="irkaal/foodcom-recipes-and-reviews"
FILE_NAME="./recipes.csv"
OUTPUT_FILE = "./recipes.jsonl"
MAX_LINES = 10000

if not os.path.exists(FILE_NAME):
    api.dataset_download_files(DATASET_NAME, path=".", unzip=True)
else: 
    print(f"Dataset {DATASET_NAME} already downloaded")

if not os.path.exists(OUTPUT_FILE):
    print(f"Converting {FILE_NAME} to {OUTPUT_FILE}...")
    df = pd.read_csv(FILE_NAME)
    
    line_count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as jsonl_file:
        for record in df.to_dict(orient="records"):
            line_count += 1
            jsonl_file.write(json.dumps(record) + "\n")
            if line_count >= MAX_LINES:
                break

    print(f"Conversion complete! JSONL file saved as {OUTPUT_FILE}")
else:
    print(f"File {OUTPUT_FILE} already exists")

print("Done!")