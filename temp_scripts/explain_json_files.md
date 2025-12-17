# JSON Files Explanation

## Current Files

### 1. `city_to_neighborhoods.json` ✅ **PRIMARY - USED**
**Purpose:** Maps city names to their neighborhood IDs
**Structure:** `{"תל אביב יפו": [195, 196, 197, ...], "אשדוד": [4, 5, 6, ...]}`
**Used by:** `scrape_city_by_neighborhoods.py` (primary method)
**Status:** ✅ Essential - used actively

### 2. `neighborhood_details.json` ✅ **SUPPLEMENTARY - USED**
**Purpose:** Full metadata for each neighborhood (name, city, listing counts, etc.)
**Structure:** `{"195": {"name": "...", "city": "...", "total_listings": 114, ...}, ...}`
**Used by:** `scrape_city_by_neighborhoods.py` (loads details when using city_to_neighborhoods.json)
**Status:** ✅ Useful - provides neighborhood names and stats

### 3. `tel_aviv_neighborhoods.json` ⚠️ **LEGACY/FALLBACK - RARELY USED**
**Purpose:** Tel Aviv-specific neighborhood data (subset of neighborhood_details.json)
**Structure:** Same as neighborhood_details.json but only Tel Aviv neighborhoods
**Used by:** `scrape_city_by_neighborhoods.py` (fallback method 3)
**Status:** ⚠️ Redundant - Tel Aviv data already in city_to_neighborhoods.json + neighborhood_details.json

### 4. `neighborhood_to_city.json` ❌ **NOT USED**
**Purpose:** Reverse mapping: neighborhood ID -> city name
**Structure:** `{"195": "תל אביב יפו", "196": "תל אביב יפו", ...}`
**Used by:** Nothing! Only mentioned in docs
**Status:** ❌ Unused - can be derived from neighborhood_details.json

## Problems

1. **Redundancy:** `tel_aviv_neighborhoods.json` duplicates data already in other files
2. **Unused file:** `neighborhood_to_city.json` is not used anywhere
3. **Poor organization:** All files in root directory
4. **Hardcoded paths:** Scraper has hardcoded file paths

## Proposed Solution

### Consolidate to 2 files:
1. **`city_to_neighborhoods.json`** - Keep as primary mapping
2. **`neighborhood_details.json`** - Keep for metadata

### Delete:
- `tel_aviv_neighborhoods.json` (redundant)
- `neighborhood_to_city.json` (unused)

### Move to `data/mappings/`:
- Better organization
- Separates data from code
- Clear purpose

