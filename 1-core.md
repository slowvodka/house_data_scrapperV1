# 📘 Project Core Documentation

## Project Goals

**Project Name:** Yad2 Real Estate Scraper

**Objective:** Build a robust, test-driven scraping engine to extract comprehensive real estate data from yad2.co.il.

### Current Status: 🔄 Phase 6 In Progress

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

## API Discovery

### Endpoint
```
https://gw.yad2.co.il/recommendations/items/realestate
```

### Parameters Tested

| Parameter | Values Tested | Status |
|-----------|---------------|--------|
| `subCategoriesIds` | 1,2,4,5,6,7 | ✅ All valid property types |
| `type` | `"home"` only | ❓ Untested: other values? |
| `categoryId` | `2` only | ❓ Untested: 1, 3, etc.? |
| `zoom` | Rejected by API | ❓ **Mystery:** affects website map |

### Rejected Parameters
- `page` - "not allowed"
- `offset` - "not allowed"
- `zoom` - "not allowed"

---

## Module Status

| Module | Tests Written | Tests Passing | Status |
|--------|---------------|---------------|--------|
| Config | 17 | ✅ Yes | Complete |
| Models | - | - | Complete |
| Exporter | 11 | ✅ Yes | Complete |
| API Client | 15 | ⚠️ Need check | Modified during debugging |
| Parser | 28 | ✅ Yes | Complete |
| Scraper | 12 | ⚠️ Need check | Modified during debugging |

---

## Current Results

| City | Listings |
|------|----------|
| Tel Aviv | 214 |
| Ramat Gan | 197 |
| Givatayim | 163 |
| **Total** | **574** |

**Limitation:** API capped at ~60 per property type per city.

---

## Git Tags

| Tag | Description |
|-----|-------------|
| `v0.3.0` | Core modules complete (before API debugging) |

---

## Next Session Priority

1. Run all tests, fix any broken ones
2. Test `type` and `categoryId` parameters
3. Investigate zoom mystery (may need Playwright)
