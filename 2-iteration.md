# 🔄 Current Iteration Tracker

## Current Session Goal

**Improve scraping results** - Get more than 574 listings

---

## 📋 Session Plan

### Step 1: Fix Technical Debt (Tests) ✅ DONE
- [x] Run `pytest tests/ -v`
- [x] Fix any broken tests in `test_api_client.py`
- [x] Fix any broken tests in `test_scraper.py`

**Result:** 94 tests passing

### Step 2: Quick Parameter Experiments ✅ DONE
- [x] Test `type` parameter: only `home` and `item` valid (`item` needs itemId)
- [x] Test `categoryId` parameter: only `2` valid (API enforces)
- [x] Document findings

**Result:** No additional data from these params - API is locked down

### Step 3: Investigate Zoom Parameter 🔄 NEXT SESSION
- [x] Tested 15+ endpoint variations - all 404
- [x] Tested geo params (lat, lon, bounds) - "not allowed" on recommendations API
- [ ] **NEXT:** Use Playwright to capture how zoom affects API responses
- [ ] **NEXT:** Watch Network tab when changing zoom on yad2 map

**Key Insight:**
The `zoom` parameter on the website URL likely controls result count.
Need to capture what API call the browser makes when zoom changes.

### Step 4: Implement New Endpoint (if found)
- [ ] Add new endpoint to `api_client.py`
- [ ] Update tests
- [ ] Run full scrape and compare results

---

## Known Context

**Current endpoint:** `https://gw.yad2.co.il/recommendations/items/realestate`

**Parameters tested:**
| Parameter | Values | Result |
|-----------|--------|--------|
| `subCategoriesIds` | 1,2,4,5,6,7 | ✅ All work |
| `page`, `offset`, `zoom` | - | ❌ Rejected |
| `type` | "home" | ❓ Untested others |
| `categoryId` | 2 | ❓ Untested others |

---

## Completed Phases

| Phase | Module | Status |
|-------|--------|--------|
| 1 | Config | ✅ |
| 2 | Models | ✅ |
| 3 | Exporter | ✅ |
| 4 | API Client | ⚠️ Tests need fix |
| 5 | Parser | ✅ |
| 6 | Scraper | ⚠️ Tests need fix |

---
