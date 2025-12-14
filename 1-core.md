# 📘 Yad2 Scraper - Project Core

## Project Objective

**Goal:** Build a robust, test-driven scraping engine to extract comprehensive real estate data from yad2.co.il (Israeli classifieds site).

**Input:** List of cities in Hebrew (e.g., "תל אביב", "רמת גן")  
**Output:** Parquet files with structured listing data  
**Method:** API requests (primary), Playwright browser automation (fallback)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Yad2 Scraper Engine                      │
├─────────────────────────────────────────────────────────────┤
│  Config Layer     │  ScraperConfig (cities, delays)         │
├───────────────────┼─────────────────────────────────────────┤
│  API Layer        │  Yad2ApiClient (HTTP + session cookies) │
├───────────────────┼─────────────────────────────────────────┤
│  Parser Layer     │  ListingParser (JSON → Listing)         │
├───────────────────┼─────────────────────────────────────────┤
│  Data Layer       │  ParquetExporter (Listing → .parquet)   │
├───────────────────┼─────────────────────────────────────────┤
│  Orchestration    │  Yad2Scraper (coordinates all layers)   │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase Status

| Phase | Module | File | Tests | Status |
|-------|--------|------|-------|--------|
| 1 | Config | `config.py` | 28 | ✅ Done |
| 2 | Models | `models.py` | - | ✅ Done |
| 3 | Exporter | `exporter.py` | 11 | ✅ Done |
| 4 | API Client | `api_client.py` | 21 | ✅ Done |
| 5 | Parser | `parser.py` | 28 | ✅ Done |
| 6 | Scraper | `scraper.py` | 12 | 🔄 In Progress |
| 7 | CLI | `main.py` | - | ⏳ Pending |

**Total: 100 tests passing**

---

## Module Details

### config.py
- `ScraperConfig` dataclass with API URL, delays, timeouts
- `CITY_DATA`: 20 cities with IDs + bounding boxes
- `get_city_id()`, `get_city_bbox()`, `get_random_delay()` methods

### models.py
- `Listing` dataclass with 20 fields:
  - Required: city, url, scraped_at
  - Property: price, rooms, floor, sqm, address, neighborhood, asset_type, description
  - Building: total_floors, year_built, elevator
  - Features: parking, balconies, mamad, storage_unit, condition
  - Availability: entrance_date

### api_client.py
- `Yad2ApiClient` with requests.Session
- `init_session()`: visits main site for cookies (required!)
- `fetch_listings(city_id, property_type)`: recommendations API
- `fetch_map_listings(bbox, zoom)`: map API (grid-based scraping)
- `PROPERTY_TYPES = [1, 2, 4, 5, 6, 7]` (6 types)

### parser.py
- `ListingParser.parse_listing()`: single JSON → Listing
- `ListingParser.parse_response()`: recommendations API → List[Listing]
- `ListingParser.parse_map_response()`: map API → List[Listing]
- Handles nested JSON, missing fields, Hebrew text

### exporter.py
- `ParquetExporter.export()`: List[Listing] → .parquet file
- `LISTING_SCHEMA`: explicit PyArrow schema for type safety

### scraper.py
- `Yad2Scraper.create(config)`: factory method (handles cookie init)
- `scrape_city()`: loops all property types, dedupes by URL
- `scrape_all_cities()`: loops all config.cities
- `run()`: full pipeline → Parquet file

---

## API Reference

### Endpoint
```
https://gw.yad2.co.il/recommendations/items/realestate
```

### Parameters
| Param | Value | Notes |
|-------|-------|-------|
| `type` | `home` | Only valid value |
| `categoryId` | `2` | API enforces this |
| `subCategoriesIds` | `1,2,4,5,6,7` | Property type IDs |
| `cityValues` | city ID | From CITY_ID_MAP |
| `count` | `500` | Max requested |

### Property Type IDs
| ID | Type |
|----|------|
| 1 | Apartment |
| 2 | Garden Apartment |
| 4 | Penthouse |
| 5 | Duplex |
| 6 | Roof Apartment |
| 7 | House/Cottage |

### Authentication
Must call `init_session()` first to get cookies from main site, otherwise API returns 401.

### Rejected Parameters
`page`, `offset`, `zoom`, `lat`, `lon`, `bounds` - all rejected by API

---

## Current Metrics

| Metric | Value |
|--------|-------|
| Best result so far | 4,225 listings (Tel Aviv, 20×20 grid) |
| Tests passing | 100 |

---

## Map API (Discovered)

**Endpoint:** `https://gw.yad2.co.il/realestate-feed/forsale/map`

**Parameters:**
| Param | Example | Notes |
|-------|---------|-------|
| `bBox` | `32.03,34.74,32.15,34.85` | lat_min,lon_min,lat_max,lon_max |
| `zoom` | `16` | Higher = smaller area |

**Strategy:** Grid-based scraping
- API caps at 200 per request
- Use fine grid (20×20) to avoid cap
- Deduplicate by URL/token

**Current Challenge:** Website shows ~10K for "Tel Aviv" but that includes Gush Dan (metro area). Need to expand bbox to cover full metropolitan area.
