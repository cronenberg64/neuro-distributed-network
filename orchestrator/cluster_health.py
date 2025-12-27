import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CORTEX_IP = os.getenv("CORTEX_IP")
if not CORTEX_IP:
    raise ValueError("CORTEX_IP environment variable not set. Please check your .env file.")

OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", 11434))

async def check_cortex_health():
    """
    Pings the Cortex-01 node and checks if the Ollama service is responsive.
    Cognitive Role: Acts as a heartbeat monitor for the System 2 reasoning node,
    ensuring high-VRAM resources are available before routing complex tasks.
    """
    url = f"http://{CORTEX_IP}:{OLLAMA_PORT}/api/tags"
    print(f"Checking Cortex health at {url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                print("Cortex-01 is ONLINE and Ollama is responsive.")
                return True
            else:
                print(f"Cortex-01 is reachable but returned status {response.status_code}.")
                return False
    except httpx.ConnectTimeout:
        print("Cortex-01 Connection TIMEOUT.")
        return False
    except httpx.ConnectError:
        print("Cortex-01 Connection REFUSED (Check VPN or Service).")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_cortex_health())
