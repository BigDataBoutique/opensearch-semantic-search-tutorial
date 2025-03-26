import json
import os

import cohere
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

load_dotenv()

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

INDEX_NAME = "recipes"

co = cohere.ClientV2(api_key=os.getenv("CO_API_KEY"))
client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
    verify_certs=False,
    use_ssl=True
)

def print_results(results):
    hits = results["hits"]["hits"]

    print("-----------------------")
    for hit in hits:
        # print recipe name
        print(hit["_source"]["Name"])
    print("-----------------------")


results = client.search({
    "size": 5,
    "query": {
        "match": {
            "RecipeCategory": "Chicken"
        }
    }

})

print_results(results)

question = "I want to eat a some chicken asian dish with noodles and peanuts "
question_embedding = co.embed(texts=[question], model="embed-english-v3.0",
                              input_type="search_query", embedding_types=["float"]).embeddings.float_[0]

results = client.search({
    "size": 5,
    "query": {
        "knn": {
            "embedding": {
                "vector": question_embedding,
                "k": 5
            }
        }
    }
})

question = "I want to eat a low sugar dessert "
question_embedding = co.embed(texts=[question], model="embed-english-v3.0",
                              input_type="search_query", embedding_types=["float"]).embeddings.float_[0]

results = client.search({
  "size": 5,
  "query": {
    "bool": {
      "must": [
        {
          "knn": {
            "embedding": {
              "vector": question_embedding,
              "k": 5
            }
          }
        }
      ],
      "filter": [
        { "term": { "RecipeCategory": "Dessert" } },
      ]
    }
  }
})

print_results(results)