# Unused/Redundant Code Analysis Report

## Summary
Scanned codebase for redundant functionality and unused code.

---

## 🔴 Issues Found

### 1. Redundant Imports

#### `src/scraper.py:99`
- **Issue:** Redundant import `from src.api_client import Yad2ApiClient`
- **Reason:** Already imported at top of file (line 13)
- **Fix:** Remove line 99

#### `scrape_city_by_neighborhoods.py:33`
- **Issue:** Unused import `import os`
- **Reason:** Never used in the file
- **Fix:** Remove line 33

---

### 2. Unused Methods

#### `src/api_client.py:fetch_listings_for_city()`
- **Location:** Lines 164-181
- **Issue:** Convenience method that wraps `fetch_listings()` with city name lookup
- **Usage:** Not used anywhere in codebase (only defined)
- **Decision:** 
  - ✅ **KEEP** - Useful for CLI/future use, provides cleaner API
  - Could be used in CLI: `client.fetch_listings_for_city("תל אביב")`

#### `src/api_client.py:__enter__()` and `__exit__()`
- **Location:** Lines 237-243
- **Issue:** Context manager methods not used anywhere
- **Usage:** No `with Yad2ApiClient(...)` statements found
- **Decision:**
  - ⚠️ **CONSIDER REMOVING** - Not used, adds complexity
  - OR keep for future use if we want context manager pattern

---

### 3. Unused Constants

#### `src/api_client.py:ISRAEL_BBOX`
- **Location:** Line 23
- **Issue:** Constant defined but only referenced in docstring and test
- **Usage:** Only in `fetch_map_listings()` docstring and `test_israel_bbox_constant_exists()`
- **Decision:**
  - ✅ **KEEP** - Useful constant for documentation and future use
  - Provides clear reference for full country coverage

---

### 4. Module Usage Analysis

#### `src/scraper.py`
- **Issue:** Module not used by actual scraper scripts
- **Usage:** 
  - ✅ Used by tests (`test_scraper.py`)
  - ❌ NOT used by `scrape_city_by_neighborhoods.py`
  - ❌ NOT used by `scrape_tel_aviv.py`
- **Decision:**
  - ✅ **KEEP** - Part of core architecture
  - Will be used by CLI (planned for next session)
  - Provides clean API: `scraper.scrape_city("תל אביב")`

---

## ✅ Code That's Actually Used

### Core Modules (All Used)
- `src/config.py` - ✅ Used everywhere
- `src/models.py` - ✅ Used by parser, exporter
- `src/parser.py` - ✅ Used by all scrapers
- `src/exporter.py` - ✅ Used by all scrapers
- `src/api_client.py` - ✅ Used by all scrapers

### Methods Used
- `Yad2ApiClient.init_session()` - ✅ Used
- `Yad2ApiClient.fetch_listings()` - ✅ Used by scraper.py
- `Yad2ApiClient.fetch_map_listings()` - ✅ Used by scrape_tel_aviv.py
- `Yad2ApiClient.build_url()` - ✅ Used internally
- `Yad2ApiClient.build_map_url()` - ✅ Used internally
- `Yad2ApiClient.close()` - ✅ Used

---

## 📋 Action Items

### Immediate Fixes (Low Risk)
1. ✅ Remove redundant import in `src/scraper.py:99`
2. ✅ Remove unused import in `scrape_city_by_neighborhoods.py:33`

### Consider Removing (Medium Risk)
3. ⚠️ Remove context manager methods (`__enter__`, `__exit__`) if not planning to use
4. ⚠️ Remove `fetch_listings_for_city()` if not needed for CLI

### Keep (Future Use)
5. ✅ Keep `scraper.py` - Needed for CLI
6. ✅ Keep `ISRAEL_BBOX` - Useful constant
7. ✅ Keep `fetch_listings_for_city()` - Useful for CLI

---

## Notes

- The codebase is generally clean with minimal redundancy
- Most "unused" code is actually reserved for future CLI/API use
- The two redundant imports are the only real issues to fix immediately

