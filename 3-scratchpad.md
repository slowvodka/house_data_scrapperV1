# 🧪 Scratchpad

> Think here BEFORE coding. Clear after feature complete.

---

## File Structure Analysis: date/city vs city/date

### Current State
- Files saved directly in `data/output/`
- Naming: `{city}_{timestamp}.parquet` or `{city}_neighborhoods_{timestamp}.parquet`
- Examples: `tel_aviv_20251214_092543.parquet`, `תל_אביב_יפו_neighborhoods_20251217_234305.parquet`

### Option 1: date/city
```
data/output/
  ├── 20251214/
  │   ├── tel_aviv_20251214_092543.parquet
  │   ├── ירושלים_20251214_093011.parquet
  │   └── חיפה_20251214_093953.parquet
  ├── 20251215/
  │   └── tel_aviv_20251215_120000.parquet
  └── 20251216/
      └── tel_aviv_20251216_202620.parquet
```

**Pros:**
- Easy to find all cities scraped on a specific date
- Good for time-series analysis across cities
- Easy to archive/delete old dates (just delete folder)
- Natural for daily/weekly scraping workflows

**Cons:**
- Harder to track a specific city over time
- Need to traverse multiple date folders to get city history
- Less intuitive for city-focused analysis

### Option 2: city/date
```
data/output/
  ├── tel_aviv/
  │   ├── 20251214_092543.parquet
  │   ├── 20251215_120000.parquet
  │   └── 20251216_202620.parquet
  ├── ירושלים/
  │   └── 20251214_093011.parquet
  └── חיפה/
      └── 20251214_093953.parquet
```

**Pros:**
- Easy to find all historical data for a specific city
- Better for city-specific analysis
- Natural grouping by entity (city)
- Easier to compare city data over time
- Common pattern in data engineering (organize by entity, then time)

**Cons:**
- Harder to see what was scraped on a specific date
- More folders if many cities (but manageable)

### Recommendation: **city/date** ✅

**Reasoning:**
1. **Primary use case**: Scraper is designed to scrape specific cities
2. **Analysis pattern**: Users likely want to analyze a specific city over time
3. **Data management**: Easier to manage per-city data (backup, archive, delete)
4. **Industry standard**: Common pattern in data engineering (organize by entity, then time)
5. **Scalability**: As more cities are added, city/date scales better

### Implementation Complete ✅

1. ✅ Updated `ParquetExporter.export()` with structured mode
2. ✅ Added `generate_output_path()` method
3. ✅ Updated `scrape_city_by_neighborhoods.py` to use new structure
4. ✅ Updated `scrape_tel_aviv.py` to use new structure
5. ✅ Updated `ScraperConfig.output_path` documentation
6. ✅ Added tests for structured output (5 new tests)
7. ✅ All 16 exporter tests passing

**Result:** Files now saved as `{city_name}/{YYYYMMDD}_{city_name}.parquet`
- Same-day scrapes overwrite (one file per city per day)
- Easy to sort and get most recent file

---

## CLI Design Analysis

### Requirements
1. **Command Structure:**
   - `yad2-scraper scrape <city1> [city2] ...` - Scrape one or more cities
   - `yad2-scraper list-cities` - List available cities
   - `yad2-scraper --help` - Show help

2. **Features:**
   - Accept multiple cities as arguments
   - Use existing `scrape_city_by_neighborhoods()` function
   - Support `--output` flag for custom output directory
   - Support `--verbose` flag for detailed output
   - Handle errors gracefully (invalid city, missing mappings)

3. **Implementation Plan:**
   - Create `src/cli.py` with argparse
   - Extract scraping logic from `scrape_city_by_neighborhoods.py` to reusable function
   - Add `list_cities()` command to show available cities from mappings
   - Use `__main__.py` pattern for `python -m src.cli` execution
   - Write tests for CLI argument parsing and command execution

4. **Edge Cases:**
   - Invalid city name → show error with available cities
   - Missing neighborhood mappings → clear error message
   - Network errors → retry logic (already in api_client)
   - Empty results → still create file (empty parquet)

5. **User Experience:**
   - Progress indicators (already in scrape function)
   - Clear error messages
   - Summary at end
   - Exit codes: 0 = success, 1 = error

### Implementation Complete ✅

1. ✅ Created `src/cli.py` with argparse structure
2. ✅ Implemented `scrape_city()` function (extracted from scrape_city_by_neighborhoods.py)
3. ✅ Implemented `scrape_command()` for multiple cities
4. ✅ Implemented `list_cities_command()` to show available cities
5. ✅ Added `--verbose` and `--output` flags
6. ✅ Created `src/__main__.py` for module execution
7. ✅ Wrote 12 unit tests (all passing)
8. ✅ Tested end-to-end

**Usage Examples:**
- `python -m src.cli scrape "תל אביב יפו"`
- `python -m src.cli scrape "תל אביב יפו" "רמת גן" "גבעתיים"`
- `python -m src.cli scrape "תל אביב יפו" --verbose`
- `python -m src.cli list-cities`

---
