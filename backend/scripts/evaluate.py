import json
import requests
import time
import os

# Ensure we are reading the JSON from the exact same directory as the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, "ground_truth.json")

API_URL = "http://localhost:8000/api/search"

def calculate_mrr():
    print("Starting Search Engine Evaluation...")
    print("-" * 40)
    
    try:
        with open(DATASET_PATH, "r") as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"Could not find dataset at {DATASET_PATH}")
        return

    total_reciprocal_rank = 0.0
    queries_evaluated = len(dataset)

    for item in dataset:
        query = item["query"]
        expected_snippet = item["expected_url_snippet"]
        
        print(f"Query: '{query}'")
        
        # Bypass cache for accurate live evaluation if desired, but here we just hit the standard endpoint
        start_time = time.time()
        response = requests.get(f"{API_URL}?q={query}&limit=15")
        latency = (time.time() - start_time) * 1000
        
        if response.status_code != 200:
            print(f"  -> Error: API returned {response.status_code}")
            queries_evaluated -= 1
            continue
            
        results = response.json()
        
        # Find the rank of the expected document
        rank = 0
        for idx, doc in enumerate(results):
            if expected_snippet in doc["url"]:
                rank = idx + 1
                break
                
        if rank > 0:
            reciprocal_rank = 1.0 / rank
            print(f"  -> Found match at Rank {rank} (RR: {reciprocal_rank:.2f}) - {latency:.0f}ms")
        else:
            reciprocal_rank = 0.0
            print(f"  -> Match NOT found in top 15 (RR: 0.00) - {latency:.0f}ms")
            
        total_reciprocal_rank += reciprocal_rank

    # Calculate final MRR
    mrr = total_reciprocal_rank / queries_evaluated if queries_evaluated > 0 else 0.0
    
    print("-" * 40)
    print(f"Evaluation Complete!")
    print(f"Total Queries: {queries_evaluated}")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")
    
    if mrr >= 0.7:
        print("Status: EXCELLENT. The correct answers are consistently at the top.")
    elif mrr >= 0.4:
        print("Status: GOOD. The correct answers are usually in the top 3.")
    else:
        print("Status: NEEDS IMPROVEMENT. Consider tweaking BM25 or Hybrid weights.")

if __name__ == "__main__":
    calculate_mrr()