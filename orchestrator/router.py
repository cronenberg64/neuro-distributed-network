import asyncio
import httpx
import os
import csv
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import Tuple, Optional

# Load environment variables
load_dotenv()

# Configuration
CORTEX_IP = os.getenv("CORTEX_IP")
CEREBELLUM_IP = os.getenv("CEREBELLUM_IP")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", 11434))

if not CORTEX_IP or not CEREBELLUM_IP:
    raise ValueError("Missing CORTEX_IP or CEREBELLUM_IP in .env")

# Models
MODEL_CORTEX = "llama3.1:8b"
MODEL_CEREBELLUM = "llama3.2:3b"

# Logging
LOG_FILE = "experiments/routing_stats.csv"

async def _send_request(ip: str, model: str, prompt: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Helper to send a prompt to a node and return response + TTFT.
    """
    # Ensure no double slash issues
    base_url = f"http://{ip}:{OLLAMA_PORT}"
    url = f"{base_url.rstrip('/')}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    start_time = time.time()
    first_token_time = None
    full_response = []
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=30.0) as response:
                if response.status_code != 200:
                    print(f"Error from {ip}: Status {response.status_code}")
                    return None, None

                async for chunk in response.aiter_bytes():
                    if not first_token_time:
                        first_token_time = time.time()
                    pass 
                
    except Exception as e:
        print(f"Request failed to {ip}: {e}")
        return None, None
        
    return "Placeholder", 0.0 

async def query_node_stream(ip: str, model: str, prompt: str) -> Tuple[str, float]:
    """
    Queries a node, measures TTFT, and returns the full response text.
    """
    # Ensure no double slash issues
    base_url = f"http://{ip}:{OLLAMA_PORT}"
    url = f"{base_url.rstrip('/')}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    start_time = time.time()
    first_token_time = None
    full_text = ""
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                if response.status_code != 200:
                    return f"Error: {response.status_code}", 0.0

                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if not first_token_time:
                                first_token_time = time.time()
                            
                            if "response" in data:
                                full_text += data["response"]
                            
                            if data.get("done", False):
                                break
                        except:
                            continue
                            
        ttft = (first_token_time - start_time) * 1000 if first_token_time else 0.0
        return full_text.strip(), ttft

    except Exception as e:
        return f"Exception: {e}", 0.0

async def route_query(query: str):
    """
    Orchestrates the classification and routing of a user query.
    Cognitive Role: The 'Thalamus' that relays sensory input (queries) to the appropriate processing center.
    """
    print(f"\nProcessing Query: '{query}'")
    
    # 1. Classification (System 1 - Cerebellum)
    classification_prompt = (
        f"Classify the following query as either 'SIMPLE' or 'COMPLEX'. "
        f"SIMPLE: Factual questions, math, definitions, greetings. "
        f"COMPLEX: Reasoning, coding, creative writing, analysis, multi-step problems. "
        f"Respond with ONLY one word: SIMPLE or COMPLEX.\n\nQuery: {query}"
    )
    
    print(f"   ↳ Asking Cerebellum ({CEREBELLUM_IP})...")
    classification, class_ttft = await query_node_stream(CEREBELLUM_IP, MODEL_CEREBELLUM, classification_prompt)
    
    # Clean up classification
    classification = classification.upper().replace(".", "").strip()
    if "SIMPLE" in classification:
        decision = "SIMPLE"
    elif "COMPLEX" in classification:
        decision = "COMPLEX"
    else:
        decision = "COMPLEX" # Fallback to safe mode
        print(f"Ambiguous classification '{classification}', defaulting to COMPLEX.")

    print(f"   Classified as: {decision} (TTFT: {class_ttft:.2f}ms)")

    # 2. Execution
    target_node = "Cerebellum" if decision == "SIMPLE" else "Cortex"
    target_ip = CEREBELLUM_IP if decision == "SIMPLE" else CORTEX_IP
    target_model = MODEL_CEREBELLUM if decision == "SIMPLE" else MODEL_CORTEX
    
    print(f"   Routing to {target_node} ({target_ip})...")
    response_text, exec_ttft = await query_node_stream(target_ip, target_model, query)
    
    print(f"   Response received (TTFT: {exec_ttft:.2f}ms)")
    print(f"   Output: {response_text[:100]}...")

    # 3. Logging
    log_entry = [
        datetime.now().isoformat(),
        query,
        decision,
        target_node,
        f"{class_ttft:.2f}",
        f"{exec_ttft:.2f}"
    ]
    
    file_exists = os.path.isfile(LOG_FILE)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Query", "Classification", "Target_Node", "Class_TTFT_ms", "Exec_TTFT_ms"])
        writer.writerow(log_entry)
        print(f"Logged to {LOG_FILE}")

if __name__ == "__main__":
    # Test Loop
    test_queries = [
        "What is 2 + 2?",
        "Explain the impact of the printing press on the Reformation."
    ]
    
    for q in test_queries:
        asyncio.run(route_query(q))
