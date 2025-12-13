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

### NEXT SESSION: Zoom Parameter Investigation

**Hypothesis:** The `zoom` URL parameter controls how many results the API returns.

**Plan for next session:**
1. Open browser DevTools on `https://www.yad2.co.il/realestate/forsale?zoom=1`
2. Watch Network tab while changing zoom levels
3. Capture the exact API call made when zoom changes
4. Look for differences in request parameters or endpoint
5. Implement in our scraper if successful

**What to look for:**
- Different API endpoint when map zooms?
- Additional parameters sent with zoom?
- WebSocket messages?
- Changes in response size/count?

---
