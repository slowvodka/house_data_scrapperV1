# 🧪 Scratchpad

> **Purpose:** Raw thinking space. Write here BEFORE coding.  
> **Rule:** Clear after each feature is complete.

---

## What Belongs Here

✅ **DO write:**
- Algorithm drafts / pseudo-code
- Edge cases to handle
- Data structure designs
- "What could go wrong?" analysis
- Decision reasoning (why X over Y?)
- Quick calculations or estimates

❌ **DON'T write:**
- Final plans (that's `2-iteration.md`)
- Project status (that's `1-core.md`)
- Polished documentation

---

## Current Thinking Space

### Problem: How to get MORE listings?

**Current state:** 574 listings from 3 cities (~190 per city)
**Limitation:** API returns ~60 per property type, 6 property types = ~360 max per city... but we're getting less

### Ideas to explore:

**1. Test other API parameters**
- `type` - currently "home", what else? "commercial"? "land"?
- `categoryId` - currently 2 (for sale), what about 1? 3?
- Could unlock completely different data sets

**2. The Zoom Mystery 🔍**
- Website URL: `?zoom=1` shows thousands of points on map
- But API rejects `zoom` parameter
- **Hypothesis:** The map uses a DIFFERENT endpoint than recommendations API
- **Action:** Use browser DevTools to capture what API the map calls

**3. Find the map/feed endpoint**
- The recommendations API is meant for "similar listings" sidebar
- There must be a main feed/search endpoint somewhere
- Look for endpoints like `/feed/`, `/search/`, `/items/`

**4. Playwright intercept**
- If we can't find the endpoint manually, use Playwright
- Navigate to the page, intercept XHR requests
- Capture the actual API calls the website makes

### Priority order:
1. ~~First: Fix broken tests (technical debt)~~ DONE
2. ~~Quick win: Test type/categoryId (5 min experiment)~~ DONE - no new data
3. Investigation: Browser DevTools to find map endpoint
4. Fallback: Playwright intercept if manual search fails

### API Parameter Test Results:
- `categoryId`: ONLY `2` allowed (API returns "categoryId must be [2]")
- `type`: ONLY `home` or `item` (`item` requires itemId for specific listing)
- `lat`, `lon`, `bounds`: NOT ALLOWED
- `count=1000`: Still returns only ~55 results (server-side cap)

### Endpoint Search Results:
Tested 15+ endpoint variations, all returned 404:
- /feed-search/realestate/forsale
- /map/realestate/forsale
- /markers/realestate/forsale
- /listings/realestate
- etc.

### Conclusion:
The recommendations API is the only accessible endpoint, and it's hard-capped at ~60 results per request.
The map data source remains a mystery - likely one of:
1. WebSocket connection (not visible in simple HTTP requests)
2. Mapbox vector tiles with embedded data
3. Browser-only endpoint protected by captcha/JS challenge

### Next Steps:
Use Playwright to intercept XHR/WebSocket requests while navigating the map

---
