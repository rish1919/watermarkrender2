import json
import os

CODES_FILE = "codes.json"

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({"valid": [], "used": {}}, f)

def load_codes():
    with open(CODES_FILE) as f:
        return json.load(f)

def save_codes(data):
    with open(CODES_FILE, "w") as f:
        json.dump(data, f)

def claim_channel(code, channel_id):
    data = load_codes()
    if code in data["valid"]:
        data["valid"].remove(code)
        data["used"][channel_id] = code
        save_codes(data)
        return True
    return False

def is_channel_claimed(channel_id):
    return channel_id in load_codes()["used"]

def add_code(code):
    data = load_codes()
    if code not in data["valid"]:
        data["valid"].append(code)
        save_codes(data)
