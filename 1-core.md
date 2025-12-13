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

## Completed Phases

| Phase | Module | File | Tests | Description |
|-------|--------|------|-------|-------------|
| 1 | Config | `config.py` | 17 | ScraperConfig dataclass, CITY_ID_MAP (20 cities), validation |
| 2 | Models | `models.py` | - | Listing dataclass with 20 fields |
| 3 | Exporter | `exporter.py` | 11 | ParquetExporter with PyArrow schema |
| 4 | API Client | `api_client.py` | 15 | Yad2ApiClient with retry, cookies, headers |
| 5 | Parser | `parser.py` | 28 | ListingParser: JSON → Listing objects |
| 6 | Scraper | `scraper.py` | 12 | Yad2Scraper: orchestrates all components |

**Total: 94 tests passing**

---

## Module Details

### config.py
- `ScraperConfig` dataclass with API URL, delays, timeouts
- `CITY_ID_MAP`: 20 Hebrew city names → Yad2 IDs
- `get_city_id()`, `get_random_delay()` methods

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
- `fetch_listings(city_id, property_type)`: calls API
- `PROPERTY_TYPES = [1, 2, 4, 5, 6, 7]` (6 types)

### parser.py
- `ListingParser.parse_listing()`: single JSON → Listing
- `ListingParser.parse_response()`: full API response → List[Listing]
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
| Cities scraped | 3 (Tel Aviv, Ramat Gan, Givatayim) |
| Listings collected | 574 |
| Tests passing | 94 |

---

## Open Problem: Zoom Mystery

**Observation:** Website `?zoom=1` shows thousands of map points.  
**Problem:** Our API returns only ~60 per property type.  
**Status:** Under investigation - need to capture browser's actual API calls.
