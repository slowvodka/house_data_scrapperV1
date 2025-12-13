# 🧪 Scratchpad

> Think here BEFORE coding. Clear after feature complete.

---

## Zoom Mystery Analysis

### Facts
- Website URL `?zoom=1` shows thousands of map markers
- Our API (`/recommendations/items/realestate`) returns ~60 per property type
- API rejects: `zoom`, `page`, `offset`, `lat`, `lon`, `bounds`
- Tested 15+ endpoint guesses → all 404

### Hypotheses

**H1: Different endpoint**
- Map uses `/feed/`, `/search/`, or `/map/` instead of `/recommendations/`
- Result: Not found via guessing

**H2: Mapbox vector tiles**
- Map is Mapbox-based
- Listing data might be embedded in `.pbf` vector tiles
- Would explain why we can't find a JSON endpoint

**H3: WebSocket**
- Real-time map data via WebSocket connection
- Need to check WS tab in DevTools

**H4: Client-side aggregation**
- Browser might make many small requests
- JavaScript aggregates into map display

### Next Step
Watch DevTools Network tab while interacting with the map.
Observe ALL traffic types (XHR, WS, Fetch, Other).

---
