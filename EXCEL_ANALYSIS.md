# Excel File Analysis: "דירה להשקעה עדכון V3.2 8.24.xlsx"

## Overview
This Excel file is an **Investment Apartment Analysis Tool** that processes real estate listings from Yad2, predicts prices using regression models, calculates investment metrics, and ranks properties for investment potential.

---

## Sheet-by-Sheet Analysis

### 1. **Data Table** (Main Data Sheet)
**Purpose:** Primary data table containing apartment listings with calculated investment metrics

**Dimensions:** 56 rows × 28 columns

**Key Columns:**
- **Input Data:**
  - `ID` - Unique identifier
  - `לינק` (Link) - Yad2 listing URL
  - `עיר` (City) - City name
  - `שכונה` (Neighborhood) - Neighborhood name
  - `רחוב` (Street) - Street address
  - `מצב הדירה` (Apartment Condition) - Condition status
  - `גודל דירה (מר)` (Apartment Size in sqm)
  - `מספר חדרים` (Number of Rooms)
  - `קומה` (Floor)
  - `מעלית` (Elevator) - Yes/No
  - `חניה` (Parking) - Number of parking spots
  - `מחיר` (Price) - Listing price

- **Calculated Metrics:**
  - `מחיר למטר` (Price per sqm) - `=Price / (Apartment Size + Balcony/2)`
  - `שכירות צפויה` (Expected Rent) - Calculated rental income
  - `תשואת שכירות` (Rental Yield) - `=(Expected Rent * 12) / Price`
  - `שכירות 3% תשואה` (Rent at 3% Yield) - `=3%/12 * Price`
  - `predicted price` - **ML model prediction** (from Regression sheet)
  - `Predicted-Actual` - Difference between predicted and actual price
  - `Price rank` - Ranking based on price (0-100, lower is better)
  - `price/size rank` - Ranking based on price per sqm
  - `yield rank` - Ranking based on rental yield
  - `Prediced- actual rank` - Ranking based on prediction accuracy
  - `Score` - **Final composite score** combining all ranks

**Key Formulas:**
- Condition encoding: Maps condition text to numeric (0-4)
- Price per sqm: `Price / (Size + Balcony/2)`
- Yield: `(Expected Rent * 12) / Price`
- Ranks: Normalized 0-100 scale (inverse for price, direct for yield)
- Score: Weighted combination of ranks

**Purpose:** This is the **core data processing sheet** that takes raw listing data and calculates all investment metrics, then ranks properties.

---

### 2. **Data Table copy only new**
**Purpose:** Subset of new listings (18 out of 56 total)

**Dimensions:** 18 rows × 28 columns

**Same structure as "Data Table"** but contains only recently added listings. Used for tracking new additions separately.

---

### 3. **Regression**
**Purpose:** Statistical regression model output for price prediction

**Dimensions:** 88 rows × 9 columns

**Content:** Standard Excel regression output including:
- Multiple R (correlation coefficient)
- R-squared (model fit)
- Adjusted R-squared
- Standard Error
- ANOVA table
- Coefficients for each feature
- P-values and significance tests
- Confidence intervals

**Purpose:** This sheet contains the **trained regression model** that predicts apartment prices based on features (size, rooms, condition, location, etc.). The model coefficients are used in "Data Table" to calculate `predicted price`.

**Key Insight:** The model uses features like:
- Apartment size
- Number of rooms
- Condition rating
- Location (city/neighborhood)
- Other property features

---

### 4. **מערכת מידע נדלן - זבוטינסקי רשי** (Real Estate Information System - Zevotinsky List)
**Purpose:** Reference data or historical price information

**Dimensions:** 51 rows × 12 columns

**Content:** Appears to contain reference data, possibly:
- Historical prices
- Market benchmarks
- Property IDs
- Date information

**Purpose:** Supporting reference data, possibly used for validation or comparison.

---

### 5. **Scenarios Calculator**
**Purpose:** Investment scenario analysis calculator

**Dimensions:** 90 rows × 8 columns

**Structure:** 
- Columns A, B, C represent **3 different investment scenarios**
- Contains calculations for:
  - Down payment percentage
  - Loan terms
  - Monthly payments
  - Cash flow
  - ROI calculations
  - Net present value (NPV)
  - Internal rate of return (IRR)

**Purpose:** Allows users to model **different investment scenarios** (conservative, moderate, aggressive) and calculate:
- Total investment required
- Monthly cash flow
- Return on investment
- Break-even analysis
- Profit projections

**Key Insight:** This is a **financial modeling tool** that takes a property from "Data Table" and calculates investment returns under different financing scenarios.

---

### 6. **ציר זמן** (Timeline)
**Purpose:** Time-based cash flow and investment analysis

**Dimensions:** 367 rows × 25 columns

**Structure:**
- Row-based timeline (likely monthly or yearly periods)
- Multiple scenario columns
- Cash flow projections over time
- Cumulative calculations

**Purpose:** Projects **investment performance over time**, showing:
- Monthly/yearly cash flows
- Cumulative returns
- Property value appreciation
- Loan paydown
- Net equity growth

**Key Insight:** This creates a **financial projection timeline** showing how the investment performs over months/years, including all cash flows, expenses, and returns.

---

## Main Functions Identified

### 1. **Data Ingestion & Processing**
- Takes raw apartment listing data (from Yad2)
- Processes and normalizes property features
- Calculates derived metrics (price per sqm, yield, etc.)

### 2. **Price Prediction (ML Model)**
- Uses regression model to predict property prices
- Compares predicted vs actual prices
- Identifies undervalued properties

### 3. **Investment Scoring System**
- Calculates multiple ranking metrics:
  - Price ranking (lower price = better)
  - Price/size ranking (value per sqm)
  - Yield ranking (rental return)
  - Prediction accuracy ranking
- Combines ranks into composite **Score**

### 4. **Scenario Analysis**
- Models 3 different investment scenarios
- Calculates ROI, cash flow, NPV, IRR
- Allows comparison of different financing strategies

### 5. **Timeline Projection**
- Projects investment performance over time
- Shows cash flows, returns, equity growth
- Helps visualize long-term investment outcomes

---

## Data Flow

```
Yad2 Listings (Scraped Data)
    ↓
Data Table (Process & Calculate Metrics)
    ↓
Regression Model (Predict Prices)
    ↓
Data Table (Add Predictions & Calculate Ranks)
    ↓
Scenarios Calculator (Model Investment Scenarios)
    ↓
Timeline (Project Long-term Performance)
```

---

## Next Phase Planning

Based on this Excel file, the next phases should implement:

### Phase 1: **Data Processing Engine** ✅ COMPLETE
- Ingest scraped apartment data
- Calculate derived metrics (price per sqm, yield, etc.)
- Normalize and clean data
- **Status:** Already implemented in scraper module

### Phase 2: **Scenario Calculator** 🎯 NEXT
- Model different investment scenarios
- Calculate ROI, cash flow, NPV, IRR
- Compare financing options

### Phase 3: **Timeline Projection** 🎯 NEXT
- Project cash flows over time
- Calculate cumulative returns
- Visualize investment performance

### Future: **Price Prediction & Scoring** 🔜 DEFERRED
- Price prediction model (regression)
- Investment scoring system (ranking metrics)

---

## Technical Notes

- **Formulas:** Heavy use of Excel formulas (672+ in Data Table alone)
- **Array Formulas:** Used in Timeline sheet for complex calculations
- **Conditional Logic:** IF statements for encoding categorical data
- **Ranking:** Uses MIN/MAX normalization for 0-100 scale
- **Regression:** Standard linear regression (likely using Excel's Data Analysis ToolPak)

---

## Questions for Clarification

1. Should we replicate the exact Excel formulas or improve/optimize them?
2. What regression algorithm should we use? (Linear, Polynomial, Random Forest?)
3. How should we weight the different ranking components in the final Score?
4. Should scenario calculations be configurable (user inputs)?
5. What time horizon should the timeline projection cover?

