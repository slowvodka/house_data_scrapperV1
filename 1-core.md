# 📘 House Data Scraper & Investment Analysis - Project Core

## Project Objective

**Goal:** Build a comprehensive real estate investment analysis system that:
1. Scrapes apartment listings from yad2.co.il
2. Calculates investment scenarios and ROI projections
3. Projects long-term investment performance

**Phase 1 (Complete):** Scraping engine - Extract comprehensive real estate data  
**Phase 4 (Next):** Scenario Calculator - Model investment scenarios with ROI, cash flow, NPV, IRR  
**Phase 5 (Next):** Timeline Projection - Project cash flows and returns over time  
**Phase 2-3 (Future):** Price prediction model and investment scoring system

**Input:** List of cities (English or Hebrew)  
**Output:** 
- Phase 1: Parquet files with structured listing data
- Phase 4-5: Investment analysis reports with scenario comparisons
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

### Phase 1: Scraping Engine ✅ COMPLETE

| Module | File | Tests | Status |
|--------|------|-------|--------|
| Config | `scraper/config.py` | 28 | ✅ Done |
| Models | `scraper/models.py` | - | ✅ Done |
| Exporter | `scraper/exporter.py` | 11 | ✅ Done |
| API Client | `scraper/api_client.py` | 21 | ✅ Done |
| Parser | `scraper/parser.py` | 28 | ✅ Done |
| Scraper | `scraper/scraper.py` | 12 | ✅ Done |
| CLI | `scraper/cli.py` | 12 | ✅ Done |

**Total: 112 tests passing** (100 + 12 CLI tests)

### Phase 2: Price Prediction Model 🔜 FUTURE
- Train regression model on historical data
- Predict property prices based on features
- Compare predicted vs actual prices

### Phase 3: Investment Scoring System 🔜 FUTURE
- Calculate multiple ranking metrics
- Combine into composite score
- Rank properties by investment potential

### Phase 4: Scenario Calculator 🎯 NEXT
- Model different investment scenarios (A, B, C)
- Calculate ROI, cash flow, NPV, IRR
- Compare financing options

### Phase 5: Timeline Projection 🎯 NEXT
- Project cash flows over time
- Calculate cumulative returns
- Visualize investment performance

---

## Module Details

### config.py
- `ScraperConfig` dataclass with API URL, delays, timeouts
- `CITY_DATA`: 20 cities with IDs + bounding boxes
- `get_city_id()`, `get_city_bbox()`, `get_random_delay()` methods

### models.py
- `Listing` dataclass with 25 fields:
  - Required: city, url, scraped_at
  - Property: price, rooms, floor, sqm, sqm_build, address, area, neighborhood, latitude, longitude, asset_type, description, images
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
- `ParquetExporter.generate_output_path()`: Generates structured path: `{city_name}/{YYYYMMDD}_{city_name}.parquet`
- `LISTING_SCHEMA`: explicit PyArrow schema for type safety
- **Output Structure:** Files saved as `{base_output_path}/{city_name}/{YYYYMMDD}_{city_name}.parquet`
  - Same-day scrapes overwrite the file (one file per city per day)
  - Easy to sort and get most recent file

### scraper.py
- `Yad2Scraper.create(config)`: factory method (handles cookie init)
- `scrape_city()`: loops all property types, dedupes by URL
- `scrape_all_cities()`: loops all config.cities
- `run()`: full pipeline → Parquet file

### cli.py
- `scrape_city()`: Scrape single city by neighborhoods
- `scrape_command()`: Execute scrape command for one or more cities
- `list_cities_command()`: List all available cities from mappings
- `parse_args()`: Parse command-line arguments with argparse
- `main()`: CLI entry point
- **Usage:** `python -m scraper.cli scrape "tel aviv"` or `python -m scraper.cli list-cities`
- **Features:** Multiple cities, --verbose flag, --output flag, error handling

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
| Best result (neighborhood-based) | 5,359 Tel Aviv listings |
| Best result (grid-based) | 11,580 listings (Gush Dan, 25×25 grid) |
| Tel Aviv neighborhoods discovered | 65 |
| Cities mapped with neighborhoods | 98 |
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
- Use fine grid (25×25) to avoid cap
- Deduplicate by URL/token

**Gush Dan Coverage:** ✅ Solved
- Expanded Tel Aviv bbox to `(31.95, 34.70, 32.25, 34.92)` to cover full metropolitan area
- Includes: Tel Aviv, Ramat Gan, Givatayim, Holon, Bat Yam, Bnei Brak
- Result: 11,580 listings (exceeded 10K target)

---

## Neighborhood-Based Scraping (Final Approach)

**Endpoint:** `https://gw.yad2.co.il/realestate-feed/forsale/map`

**Parameters:**
| Param | Example | Notes |
|-------|---------|-------|
| `city` | `5000` | City ID (Tel Aviv = 5000) |
| `neighborhood` | `307` | Neighborhood ID |

**Strategy:** Neighborhood-based scraping
- Query each neighborhood individually using its ID
- API caps at 200 listings per request (no neighborhoods exceed this)
- 100% city-specific results (no filtering needed)
- More efficient than grid approach (65 requests vs 625)

**Results:**
- **5,359 Tel Aviv listings** collected
- **65 neighborhoods** discovered and mapped
- **98 cities** mapped with neighborhoods in `city_to_neighborhoods.json`

**Files:**
- `scrape_city_by_neighborhoods.py` - Final neighborhood scraper script
- `data/mappings/city_to_neighborhoods.json` - Complete city-to-neighborhood mapping
- `data/mappings/neighborhood_details.json` - Detailed neighborhood metadata

---

## Field Analysis

**API Response Structure:**
- Total fields available: ~33 fields
- Fields we extract: 25 fields

**Currently Extracted Fields:**

| Category | Field | Source Path |
|----------|-------|-------------|
| **Core** | city | `address.city.text` |
| | url | Constructed from `token` |
| | scraped_at | Added by parser |
| | price | `price` |
| | rooms | `additionalDetails.roomsCount` |
| | floor | `address.house.floor` |
| | sqm | `additionalDetails.squareMeter` |
| | sqm_build | `metaData.squareMeterBuild` |
| | address | `address.street.text` + `address.house.number` |
| | area | `address.area.text` |
| | neighborhood | `address.neighborhood.text` |
| | latitude | `address.coords.lat` |
| | longitude | `address.coords.lon` |
| | asset_type | `additionalDetails.property.text` |
| | description | `metaData.description` |
| | images | `metaData.images` (list of URLs) |
| **Building** | total_floors | `additionalDetails.buildingTopFloor` |
| | year_built | `additionalDetails.yearBuilt` |
| | elevator | `inProperty.includeElevator` |
| **Features** | parking | `additionalDetails.parkingSpacesCount` |
| | balconies | `additionalDetails.balconiesCount` |
| | mamad | `inProperty.includeSecurityRoom` |
| | storage_unit | `inProperty.includeWarehouse` |
| | condition | `additionalDetails.propertyCondition.text` |
| **Availability** | entrance_date | `additionalDetails.entranceDate` |

**Available but Not Extracted:**
- `adType` - Type of ad (private/broker)
- `priority` - Listing priority
- `metaData.coverImage` - Cover image URL (we extract full `images` array instead)
- `orderId` - Order ID
- `categoryId`, `subcategoryId` - Category IDs
