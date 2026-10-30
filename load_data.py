# load_data.py - Reads JSON files from data/ and loads them into PostgreSQL
import os, json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode=os.getenv("DB_SSLMODE", "prefer"),
    connect_timeout=30, keepalives=1, keepalives_idle=30)
cur = conn.cursor()

def read(name):
    with open(f"data/{name}", encoding="utf-8") as f:
        return json.load(f)

# ---------- 1. Categories + Competitions ----------
comp_data = read("competitions.json")
categories, competitions = {}, {}

for c in comp_data.get("competitions", []):
    cat = c.get("category", {})
    if cat.get("id"):
        categories[cat["id"]] = cat.get("name")
    competitions[c.get("id")] = (
        c.get("id"), c.get("name"), c.get("parent_id"),
        c.get("type"), c.get("gender"), c.get("level"), cat.get("id"))

execute_values(cur,
    "INSERT INTO categories (category_id, category_name) VALUES %s "
    "ON CONFLICT (category_id) DO NOTHING",
    list(categories.items()), page_size=1000)

execute_values(cur,
    "INSERT INTO competitions (competition_id, competition_name, parent_id, type, gender, level, category_id) "
    "VALUES %s ON CONFLICT (competition_id) DO NOTHING",
    list(competitions.values()), page_size=1000)

# ---------- 2. Complexes + Venues ----------
cx_data = read("complexes.json")
complexes, venues = {}, {}

for cx in cx_data.get("complexes", []):
    complexes[cx.get("id")] = (cx.get("id"), cx.get("name"))
    for v in cx.get("venues", []):
        venues[v.get("id")] = (
            v.get("id"), v.get("name"), v.get("city_name"), v.get("country_name"),
            v.get("country_code"), v.get("timezone"), cx.get("id"))

execute_values(cur,
    "INSERT INTO complexes (complex_id, complex_name) VALUES %s "
    "ON CONFLICT (complex_id) DO NOTHING",
    list(complexes.values()), page_size=1000)

execute_values(cur,
    "INSERT INTO venues (venue_id, venue_name, city_name, country_name, country_code, timezone, complex_id) "
    "VALUES %s ON CONFLICT (venue_id) DO NOTHING",
    list(venues.values()), page_size=1000)

# ---------- 3. Competitors + Rankings ----------
rk_data = read("doubles_rankings.json")
competitors, rankings = {}, []

for block in rk_data.get("rankings", []):
    for r in block.get("competitor_rankings", []):
        p = r.get("competitor", {})
        competitors[p.get("id")] = (
            p.get("id"), p.get("name"), p.get("country"),
            p.get("country_code"), p.get("abbreviation"))
        rankings.append((
            r.get("rank"), r.get("movement"), r.get("points"),
            r.get("competitions_played"), p.get("id")))

execute_values(cur,
    "INSERT INTO competitors (competitor_id, name, country, country_code, abbreviation) "
    "VALUES %s ON CONFLICT (competitor_id) DO NOTHING",
    list(competitors.values()), page_size=1000)

cur.execute("TRUNCATE competitor_rankings RESTART IDENTITY")
execute_values(cur,
    "INSERT INTO competitor_rankings (rank, movement, points, competitions_played, competitor_id) "
    "VALUES %s",
    rankings, page_size=1000)

conn.commit()

# ---------- Summary ----------
for t in ["categories", "competitions", "complexes", "venues", "competitors", "competitor_rankings"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t:22} {cur.fetchone()[0]} rows")

cur.close()
conn.close()
print("Load complete!")