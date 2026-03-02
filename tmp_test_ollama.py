import sys
import os
import json
import urllib.request
sys.path.append("/Users/yakarteek/Code/Accion/Summit/ECL")
from ecl_llm import OllamaClient, AdaptiveLLMExpert

text = """TOWER SITE INSPECTION REPORT
Tower ID: T-789 | Location: 40.6892° N, 74.0445° W | Type: Monopole | Height: 150ft"""

client = OllamaClient(model="llama3:8b")
expert = AdaptiveLLMExpert(client)
prompt = expert.get_extraction_prompt(text)
system = expert.get_system_prompt()

payload = {
    "model": "llama3:8b",
    "prompt": prompt,
    "system": system,
    "stream": False,
    "format": "json",
    "options": {
        "temperature": 0.1,
    }
}

try:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
        print("\n--- RAW RESPONSE ---")
        print(result.get("response", ""))
except Exception as e:
    print(f"HTTP REQUEST FAILED: {e}")
