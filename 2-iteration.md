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

### Step 2: Quick Parameter Experiments
- [ ] Test `type` parameter: try values other than `"home"`
- [ ] Test `categoryId` parameter: try `1`, `3`, etc.
- [ ] Document findings

### Step 3: Investigate Map Endpoint (The Zoom Mystery)
- [ ] Open browser DevTools on yad2.co.il
- [ ] Change zoom level, observe Network tab
- [ ] Identify which endpoint serves the map data
- [ ] Document the endpoint and parameters

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
