# 📘 Project Core Documentation

## Project Goals

**Project Name:** Yad2 Real Estate Scraper

**Objective:** Build a robust, test-driven web scraping engine to extract comprehensive real estate data from the "For Sale" section of yad2.co.il (Israeli classifieds site).

### Core Requirements

| Requirement | Description |
|-------------|-------------|
| **Input** | Configurable list of Israeli cities (e.g., "תל אביב", "חיפה") |
| **Process** | Navigate search results, handle pagination, extract listing details |
| **Data Points** | Price, Rooms, Floor, Sq. Meters, Neighborhood, Asset Type, Description |
| **Output** | Flattened tabular data saved as `.parquet` file |

### Success Criteria
- [ ] Scrape all listings for a given list of cities
- [ ] Handle pagination seamlessly
- [ ] Extract all required fields per listing
- [ ] Output clean, analytics-ready Parquet file
- [ ] 80%+ test coverage

---

## Architecture & Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Yad2 Scraper Engine                      │
├─────────────────────────────────────────────────────────────┤
│  Config Layer     │  cities.yaml / config.py                │
├───────────────────┼─────────────────────────────────────────┤
│  Scraper Layer    │  Playwright (browser automation)        │
├───────────────────┼─────────────────────────────────────────┤
│  Parser Layer     │  Data extraction & normalization        │
├───────────────────┼─────────────────────────────────────────┤
│  Data Layer       │  pandas DataFrame → Parquet output      │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.11+ |
| Browser Automation | Playwright | Latest |
| Data Processing | pandas | 2.x |
| Parquet I/O | pyarrow | Latest |
| Testing | pytest | Latest |
| Test Coverage | pytest-cov | Latest |

---

## High-Level Roadmap

| Phase | Milestone | Status |
|-------|-----------|--------|
| 1 | Project Setup & Configuration Module | ✅ Complete |
| 2 | Exporter Module (Parquet output) | 🔄 In Progress |
| 3 | Search Results Scraper (single page) | 🔲 Pending |
| 4 | Pagination Handler | 🔲 Pending |
| 5 | Listing Detail Extractor | 🔲 Pending |
| 6 | Data Flattening & Parquet Export | 🔲 Pending |
| 7 | Multi-City Orchestration | 🔲 Pending |
| 8 | Error Handling & Retry Logic | 🔲 Pending |
| 9 | Final Integration & Polish | 🔲 Pending |

---

## Completed Features

| Feature | Date Completed | Notes |
|---------|----------------|-------|
| Configuration Module | 2025-12-12 | ScraperConfig with validation, 17 tests passing |

