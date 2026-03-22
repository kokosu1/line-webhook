import json
import os

NAMES_FILE = "staff_names.json"

def get_names():
    if not os.path.exists(NAMES_FILE):
        return []
    with open(NAMES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def add_name(name: str):
    names = get_names()
    if name not in names:
        names.append(name)
        _save(names)

def remove_name(name: str):
    names = get_names()
    if name in names:
        names.remove(name)
        _save(names)

def _save(names):
    with open(NAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)
