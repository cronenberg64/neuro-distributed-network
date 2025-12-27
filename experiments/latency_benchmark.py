import asyncio
import httpx
import time
import csv
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

CORTEX_IP = os.getenv("CORTEX_IP")
if not CORTEX_IP:
    raise ValueError("CORTEX_IP environment variable not set. Please check your .env file.")

OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", 11434))
LOG_FILE = "experiments/latency_log.csv"

async def measure_ttft():
    """
    Measures the Time to First Token (TTFT) for a simple prompt sent to the Cortex node.
    Cognitive Role: Benchmarks the reaction speed of the System 2 node to determine
    latency overhead for real-time reasoning tasks.
    """
    url = f"http://{CORTEX_IP}:{OLLAMA_PORT}/api/generate"
    # Using llama3.1 as a default high-performance model likely to be on Cortex
    payload = {
        "model": "llama3.1:8b", 
        "prompt": "Hello, are you ready?",
        "stream": True
    }
    
    print(f"Benchmarking TTFT on {CORTEX_IP}...")
    
    start_time = time.time()
    first_token_time = None
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=10.0) as response:
                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code}")
                    return

                async for chunk in response.aiter_bytes():
                    if not first_token_time:
                        first_token_time = time.time()
                        break # We only need the first token for TTFT
                        
        if first_token_time:
            ttft = (first_token_time - start_time) * 1000 # ms
            print(f"TTFT: {ttft:.2f} ms")
            
            # Log to CSV
            file_exists = os.path.isfile(LOG_FILE)
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Timestamp", "Node", "TTFT_ms"])
                
                writer.writerow([datetime.now().isoformat(), "Cortex-01", f"{ttft:.2f}"])
                print(f"Logged to {LOG_FILE}")
        else:
            print("No data received.")

    except Exception as e:
        print(f"Benchmark failed: {e}")

if __name__ == "__main__":
    asyncio.run(measure_ttft())
