# 🔄 Current Iteration Tracker

## Current Session Goal

**Phase 2: API Client Module** 🔄 IN PROGRESS

Building an HTTP-based API client after discovering Yad2's internal API:
- Endpoint: `https://gw.yad2.co.il/recommendations/items/realestate`
- Returns structured JSON with all listing data
- No need for browser automation!

---

## API Discovery Notes

### Endpoint
```
https://gw.yad2.co.il/recommendations/items/realestate
```

### Query Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `type` | Listing type | `home` |
| `count` | Results per page | `20` |
| `categoryId` | Category (2 = real estate) | `2` |
| `subCategoriesIds` | Property type (1 = apartments) | `1` |
| `cityValues` | City ID | `9000` (Beer Sheva) |
| `roomValues` | Room filter (optional) | `4` |

### Response Structure
```json
{
  "data": [[
    {
      "token": "unique_id",
      "price": 1820000,
      "additionalDetails": {
        "roomsCount": 4,
        "squareMeter": 150,
        "balconiesCount": 1,
        "parkingSpacesCount": 1,
        "buildingTopFloor": 16,
        "entranceDate": "2025-06-16T00:00:00",
        "propertyCondition": {"text": "חדש (גרו בנכס)"},
        "property": {"text": "דירה"}
      },
      "inProperty": {
        "includeElevator": true,
        "includeSecurityRoom": false,
        "includeWarehouse": true,
        "includeParking": true
      },
      "address": {
        "city": {"text": "באר שבע"},
        "neighborhood": {"text": "שכונה ג'"},
        "street": {"text": "גולומב"},
        "house": {"floor": 2, "number": 17}
      },
      "metaData": {"description": "..."}
    }
  ]]
}
```

---

## Phase 2 Tasks: API Client

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Update config for API settings | ⬜ Pending | Add API base URL, city mappings |
| 2 | Write test: API client initialization | ⬜ Pending | |
| 3 | Implement API client basic structure | ⬜ Pending | |
| 4 | Write test: Build API URL with params | ⬜ Pending | |
| 5 | Implement URL builder | ⬜ Pending | |
| 6 | Write test: Make API request | ⬜ Pending | Mock responses |
| 7 | Implement request with retry logic | ⬜ Pending | |
| 8 | Write test: Handle errors | ⬜ Pending | |
| 9 | Implement error handling | ⬜ Pending | |

---

## Completed Phases

### Phase 1: Configuration Module ✅
- ScraperConfig dataclass (17 tests)

### Phase 5: Exporter Module ✅
- Listing dataclass with 20 fields
- ParquetExporter with explicit PyArrow schema (11 tests)

---

## Active Context

### Architecture Change
**Before:** Browser automation (Playwright) → HTML parsing
**After:** HTTP requests → JSON parsing

This simplifies the project significantly:
- Faster (no browser overhead)
- More reliable (structured JSON)
- Simpler code (no DOM parsing)

### Files To Create
- `src/api_client.py` - HTTP client for Yad2 API
- `tests/test_api_client.py` - API client tests

---

## Session History

| Session | Date | Goal | Outcome |
|---------|------|------|---------|
| 1 | 2025-12-12 | Project initialization | ✅ Complete |
| 2 | 2025-12-12 | Phase 1: Config Module | ✅ Complete (17 tests) |
| 3 | 2025-12-12 | Phase 2: Exporter Module | ✅ Complete (11 tests) |
| 4 | 2025-12-13 | API Discovery | ✅ Found internal API! |
| 5 | 2025-12-13 | Phase 2: API Client | 🔄 In Progress |
