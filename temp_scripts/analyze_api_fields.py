"""Analyze available fields in API response vs what we extract.

Queries a sample Tel Aviv listing and shows:
1. All available fields in the API response
2. Fields we currently extract
3. Fields we're missing
"""
import json
from scraper.api_client import Yad2ApiClient
from scraper.config import ScraperConfig
from scraper.parser import ListingParser

config = ScraperConfig()
client = Yad2ApiClient(config)
client.init_session()

parser = ListingParser()

print("=" * 70)
print("API Field Analysis: Available vs Extracted")
print("=" * 70)

# Query a sample Tel Aviv neighborhood
neighborhood_id = 307  # רמת אביב החדשה
url = f"https://gw.yad2.co.il/realestate-feed/forsale/map?city=5000&neighborhood={neighborhood_id}"

print(f"\nQuerying neighborhood ID {neighborhood_id}...")
response = client.session.get(url, timeout=5)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    client.close()
    exit(1)

data = response.json()
markers = data.get("data", {}).get("markers", [])

if not markers:
    print("No listings found")
    client.close()
    exit(1)

# Get first listing as sample
sample_listing = markers[0]

print(f"\nSample listing found. Analyzing fields...")
print("=" * 70)

# Parse with our parser
parsed_listing = parser.parse_listing(sample_listing, "תל אביב יפו")

# Get all available fields from raw JSON
def get_all_keys(obj, prefix="", max_depth=5):
    """Recursively get all keys from nested dict."""
    if max_depth == 0:
        return []
    
    keys = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, (dict, list)):
                keys.extend(get_all_keys(value, full_key, max_depth - 1))
    elif isinstance(obj, list) and len(obj) > 0:
        # Check first element
        keys.extend(get_all_keys(obj[0], prefix, max_depth - 1))
    return keys

all_fields = sorted(set(get_all_keys(sample_listing)))

# Fields we extract (from Listing dataclass)
extracted_fields = {
    "city": "address.city.text",
    "url": "constructed from token",
    "scraped_at": "added by parser",
    "price": "price",
    "rooms": "additionalDetails.roomsCount",
    "floor": "address.house.floor",
    "sqm": "additionalDetails.squareMeter",
    "address": "constructed from address.street + address.house.number",
    "neighborhood": "address.neighborhood.text",
    "asset_type": "additionalDetails.property.text",
    "description": "metaData.description",
    "total_floors": "additionalDetails.buildingTopFloor",
    "year_built": "additionalDetails.yearBuilt",
    "elevator": "inProperty.includeElevator",
    "parking": "additionalDetails.parkingSpacesCount",
    "balconies": "additionalDetails.balconiesCount",
    "mamad": "inProperty.includeSecurityRoom",
    "storage_unit": "inProperty.includeWarehouse",
    "condition": "additionalDetails.propertyCondition.text",
    "entrance_date": "additionalDetails.entranceDate",
}

print("\n" + "=" * 70)
print("FIELDS WE CURRENTLY EXTRACT:")
print("=" * 70)
for field, source in extracted_fields.items():
    value = getattr(parsed_listing, field, None)
    value_str = str(value)[:50] + "..." if value and len(str(value)) > 50 else value
    print(f"  {field:20} <- {source:40} = {value_str}")

print("\n" + "=" * 70)
print("ALL AVAILABLE FIELDS IN API RESPONSE:")
print("=" * 70)

# Group fields by top-level category
top_level_fields = {}
nested_fields = {}

for field in all_fields:
    if "." in field:
        top = field.split(".")[0]
        if top not in nested_fields:
            nested_fields[top] = []
        nested_fields[top].append(field)
    else:
        top_level_fields[field] = sample_listing.get(field)

print("\nTop-level fields:")
for field, value in sorted(top_level_fields.items()):
    value_str = str(value)[:60] + "..." if value and len(str(value)) > 60 else value
    print(f"  {field:30} = {value_str}")

print("\nNested fields by category:")
for category in sorted(nested_fields.keys()):
    print(f"\n  [{category}]")
    for field in sorted(nested_fields[category])[:15]:  # Limit to 15 per category
        # Get value
        parts = field.split(".")
        value = sample_listing
        try:
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and len(value) > 0:
                    value = value[0].get(part) if isinstance(value[0], dict) else None
                else:
                    value = None
                    break
        except:
            value = None
        
        value_str = str(value)[:50] + "..." if value and len(str(value)) > 50 else value
        print(f"    {field:50} = {value_str}")
    if len(nested_fields[category]) > 15:
        print(f"    ... ({len(nested_fields[category]) - 15} more fields)")

# Find fields we're not extracting
extracted_paths = set(extracted_fields.values())
missing_fields = [f for f in all_fields if f not in extracted_paths and not any(f.startswith(ep.split(".")[0]) for ep in extracted_paths if "." in ep)]

# Filter out some common non-data fields
exclude_patterns = ["metaData", "token", "id", "images", "thumbnail"]
missing_fields = [f for f in missing_fields if not any(pattern in f.lower() for pattern in exclude_patterns)]

print("\n" + "=" * 70)
print("POTENTIALLY USEFUL FIELDS WE'RE NOT EXTRACTING:")
print("=" * 70)

if missing_fields:
    for field in missing_fields[:30]:
        # Get value
        parts = field.split(".")
        value = sample_listing
        try:
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and len(value) > 0:
                    value = value[0].get(part) if isinstance(value[0], dict) else None
                else:
                    value = None
                    break
        except:
            value = None
        
        value_str = str(value)[:60] + "..." if value and len(str(value)) > 60 else value
        print(f"  {field:50} = {value_str}")
    
    if len(missing_fields) > 30:
        print(f"\n  ... ({len(missing_fields) - 30} more fields)")
else:
    print("  None found")

# Show full JSON structure for reference
print("\n" + "=" * 70)
print("FULL JSON STRUCTURE (first listing):")
print("=" * 70)
print(json.dumps(sample_listing, ensure_ascii=False, indent=2)[:2000])
print("... (truncated)")

client.close()

print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
print(f"Total fields available: {len(all_fields)}")
print(f"Fields we extract: {len(extracted_fields)}")
print(f"Potentially useful missing fields: {len(missing_fields)}")

