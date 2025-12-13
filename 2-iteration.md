# 🔄 Current Iteration

## Goal

**Investigate zoom parameter** to discover how to get more listings.

---

## Next Session Tasks

### 1. Browser DevTools Investigation
```
1. Open: https://www.yad2.co.il/realestate/forsale?zoom=1
2. DevTools → Network tab → filter XHR/Fetch
3. Interact with map (zoom in/out, pan)
4. Capture any API calls that return listing data
5. Note: endpoint, parameters, response structure
```

### 2. If Endpoint Found
- [ ] Test with requests library
- [ ] Add to `api_client.py`
- [ ] Write tests (TDD)
- [ ] Run scrape, compare to current 574

### 3. If No Endpoint
- [ ] Check WebSocket tab
- [ ] Use Playwright to intercept traffic
- [ ] Examine Mapbox vector tiles

---

## Done This Session

- [x] Fixed 7 broken tests (94 now passing)
- [x] Tested `type` param → only `home` valid
- [x] Tested `categoryId` param → only `2` valid
- [x] Tested 15+ endpoint variations → all 404
- [x] Restructured documentation files
