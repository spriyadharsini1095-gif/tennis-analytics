import os, json, time, requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)
KEY = os.getenv("SPORTRADAR_API_KEY")
BASE = "https://api.sportradar.com/tennis/trial/v3/en/"

endpoints = {
    "competitions.json": "competitions.json",
    "complexes.json": "complexes.json",
    "doubles_rankings.json": "double_competitors_rankings.json",
}

os.makedirs("data", exist_ok=True)

for filename, path in endpoints.items():
    try:
        r = requests.get(BASE + path, params={"api_key": KEY}, timeout=30)
        print(filename, "->", r.status_code)
        if r.status_code == 200:
            with open(f"data/{filename}", "w", encoding="utf-8") as f:
                json.dump(r.json(), f, indent=2)
        else:
            print("  Error:", r.text[:200])
    except requests.RequestException as e:
        print("  Request failed:", e)
    time.sleep(2)   # trial key allows ~1 request/second