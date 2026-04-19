import json
import os
from datetime import datetime

MEMORY_FILE = "jarvis_memory.json"

def load_history() -> list:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history: list):
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def add_to_history(history: list, role: str, content: str) -> list:
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    save_history(history)
    return history

def clear_history():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    return []