"""Check if JSON files have redundant data."""
import json

# Load files
with open("city_to_neighborhoods.json", "r", encoding="utf-8") as f:
    city_map = json.load(f)

with open("tel_aviv_neighborhoods.json", "r", encoding="utf-8") as f:
    tel_aviv_data = json.load(f)

# Check if Tel Aviv is in city_map
tel_aviv_key = "תל אביב יפו"
has_tel_aviv = tel_aviv_key in city_map

if has_tel_aviv:
    city_nids = set(city_map[tel_aviv_key])
    tel_aviv_nids = set(int(k) for k in tel_aviv_data.keys())
    
    print(f"city_to_neighborhoods.json has Tel Aviv: {has_tel_aviv}")
    print(f"Tel Aviv neighborhoods in city_to_neighborhoods: {len(city_nids)}")
    print(f"Tel Aviv neighborhoods in tel_aviv_neighborhoods.json: {len(tel_aviv_nids)}")
    print(f"Overlap: {city_nids == tel_aviv_nids}")
    print(f"Missing in city_map: {tel_aviv_nids - city_nids}")
    print(f"Extra in city_map: {city_nids - tel_aviv_nids}")
else:
    print("Tel Aviv not found in city_to_neighborhoods.json")

