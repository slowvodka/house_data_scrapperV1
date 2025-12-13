# 📘 Project Core Documentation

## Project Goals

**Project Name:** Yad2 Real Estate Scraper

**Objective:** Build a robust, test-driven scraping engine to extract comprehensive real estate data from the "For Sale" section of yad2.co.il (Israeli classifieds site).

### Core Requirements

| Requirement | Description |
|-------------|-------------|
| **Input** | Configurable list of Israeli cities (e.g., "תל אביב", "חיפה") |
| **Process** | Fetch listings via API, handle pagination, extract all details |
| **Data Points** | Price, Rooms, Floor, Sq. Meters, Address, Neighborhood, Asset Type, Description, Parking, Elevator, Balconies, Mamad, Condition, etc. |
| **Output** | Flattened tabular data saved as `.parquet` file |

### Success Criteria
- [ ] Scrape all listings for a given list of cities
- [ ] Handle pagination seamlessly
- [ ] Extract all 20 required fields per listing
- [ ] Output clean, analytics-ready Parquet file
- [ ] 80%+ test coverage

---

## Architecture & Tech Stack

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    Yad2 Scraper Engine                      │
├─────────────────────────────────────────────────────────────┤
│  Config Layer     │  ScraperConfig (cities, delays, etc.)   │
├───────────────────┼─────────────────────────────────────────┤
│  API Layer        │  Yad2ApiClient (HTTP requests)          │
├───────────────────┼─────────────────────────────────────────┤
│  Parser Layer     │  ListingParser (JSON → Listing)         │
├───────────────────┼─────────────────────────────────────────┤
│  Data Layer       │  ParquetExporter (Listing → .parquet)   │
├───────────────────┼─────────────────────────────────────────┤
│  Orchestration    │  Scraper (coordinates all layers)       │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack
| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.11+ |
| HTTP Client | requests | Latest |
| Data Processing | pandas | 2.x |
| Parquet I/O | pyarrow | Latest |
| Testing | pytest | Latest |
| Test Mocking | responses | Latest |
| Browser (fallback) | Playwright | Latest |

---

## High-Level Roadmap

| Phase | Milestone | Status |
|-------|-----------|--------|
| 1 | Configuration Module (config.py) | ✅ Complete |
| 2 | Data Models (models.py) | ✅ Complete |
| 3 | Exporter Module (exporter.py) | ✅ Complete |
| 4 | API Client Module (api_client.py) | ✅ Complete |
| 5 | Parser Module (parser.py) | ✅ Complete |
| 6 | Scraper Module (scraper.py) | ⬜ Next |
| 7 | Integration & CLI | ⬜ Pending |
| 8 | Browser Fallback (optional) | ⬜ Pending |

---

## Completed Features

| Feature | Date Completed | Tests | Notes |
|---------|----------------|-------|-------|
| Configuration Module | 2025-12-12 | 17 | ScraperConfig with validation, city ID mapping |
| Data Models | 2025-12-12 | - | Listing dataclass with 20 fields |
| Exporter Module | 2025-12-12 | 11 | ParquetExporter with explicit PyArrow schema |
| API Client Module | 2025-12-13 | 15 | Yad2ApiClient with retry logic, browser-like headers |
| Parser Module | 2025-12-13 | 28 | ListingParser for JSON→Listing conversion |

**Total Tests: 71 passing**

---

## API Discovery (Key Finding)

Instead of browser automation, we discovered Yad2's internal API:

```
https://gw.yad2.co.il/recommendations/items/realestate
```

**Benefits:**
- ⚡ Much faster (no browser overhead)
- 📊 Structured JSON response (no HTML parsing)
- 🎯 All fields available directly

**Query Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `type` | Listing type | `home` |
| `count` | Results per page | `40` |
| `categoryId` | Category (2 = real estate) | `2` |
| `cityValues` | City ID | `9000` (Beer Sheva) |

---

## Git Tags (Milestones)

| Tag | Description |
|-----|-------------|
| `v0.3.0` | Core modules complete (config, models, exporter, api_client, parser) |
