# 🔄 Current Iteration Tracker

## Current Session Goal

**Phase 6: Scraper Module** 🔄 IN PROGRESS (paused for investigation)

---

## ⚠️ Current State: Tests Need Update

During API debugging, we made breaking changes:
- Removed `page` parameter (API doesn't support pagination)
- Added `property_type` parameter to fetch all property types
- Changed scraper logic to loop through property types

**Tests written but likely broken** - need to run and fix before Phase 6 is complete.

---

## 🔬 Next Steps (Priority Order)

### 1. Run Tests & Fix Breakages
```bash
python -m pytest tests/ -v
```

### 2. Investigate Untested API Parameters

| Parameter | Current Value | To Test | Notes |
|-----------|---------------|---------|-------|
| `type` | `"home"` | Other values? | May unlock different listing types |
| `categoryId` | `2` | `1`, `3`, etc.? | `2` = for sale, others = rentals? |
| `zoom` | Not used | **INVESTIGATE** | Works on website URL but rejected by API |

### 3. The Zoom Mystery 🔍

**Observation:** `https://www.yad2.co.il/realestate/forsale?zoom=1` shows thousands of map points, but API rejects `zoom` parameter.

**To investigate:**
- Use browser dev tools to capture API calls when changing zoom
- Look for map-specific endpoints
- Consider Playwright to intercept XHR requests

---

## Session Work Done (Not Committed)

| Task | Status | Notes |
|------|--------|-------|
| Debug API authentication | ✅ Done | Need cookies from main site |
| Discover `page` not allowed | ✅ Done | API doesn't paginate |
| Test `subCategoriesIds` | ✅ Done | Valid: 1, 2, 4, 5, 6, 7 |
| Fetch all property types | ✅ Done | 162 → 574 listings |
| Update tests | ❌ TODO | Tests likely broken |

---

## Completed Phases

| Phase | Module | Tests | Date | Status |
|-------|--------|-------|------|--------|
| 1 | Configuration | 17 | 2025-12-12 | ✅ |
| 2 | Data Models | - | 2025-12-12 | ✅ |
| 3 | Exporter | 11 | 2025-12-12 | ✅ |
| 4 | API Client | 15 | 2025-12-13 | ⚠️ Tests need update |
| 5 | Parser | 28 | 2025-12-13 | ✅ |
| 6 | Scraper | 12 | 2025-12-13 | ⚠️ Tests need update |

---

## Known Limitations

- API capped at ~60 items per property type per city
- No pagination support
- Zoom parameter mystery unresolved
