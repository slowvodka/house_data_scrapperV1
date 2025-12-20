# 🎯 Project Mission

## Goal

Build a comprehensive real estate investment analysis system that:
1. Scrapes apartment listings from yad2.co.il
2. Calculates investment scenarios and ROI projections
3. Projects long-term investment performance

## High-Level Objectives

**Input:** List of cities (English or Hebrew)  
**Output:** 
- Phase 1: Parquet files with structured listing data
- Phase 2-3: Investment analysis reports with scenario comparisons
**Method:** API requests (primary), Playwright browser automation (fallback)

## Target Site

- **Site:** yad2.co.il (Hebrew, RTL)
- **Primary Method:** API requests to `gw.yad2.co.il/recommendations/items/realestate`
- **Fallback:** Playwright browser automation (if API is blocked)
- **Data Format:** Output ONLY Parquet files (no JSON)
- **Encoding:** Handle Hebrew text properly (UTF-8)
- **Rate Limiting:** Be respectful to the target server (add delays between requests)

## Success Criteria

- ✅ Phase 1: Complete scraping engine with 100+ tests passing
- 🎯 Phase 2: Investment scenario calculator with financial metrics
- ⏸️ Phase 3: Timeline projection for long-term analysis
- 🔜 Future: Price prediction model and investment scoring system

