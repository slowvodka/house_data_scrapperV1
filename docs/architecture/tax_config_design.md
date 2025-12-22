# Tax Configuration Module Design

**Status:** Design Complete  
**Date:** 2025-12-20  
**Architect:** System Architect  
**Related Enhancement:** Phase 2 Enhancement - Real Estate Taxes

---

## Overview

Design for a tax configuration module that calculates Israeli purchase tax (מס רכישה) and capital gains tax (מס שבח) based on property value and whether it's a first house or additional property.

**Reference:** [kolzchut.org.il - Purchase Tax Calculation](https://www.kolzchut.org.il/he/חישוב_מס_רכישה)

---

## Requirements

### Functional Requirements

1. **Purchase Tax Calculation**
   - Calculate purchase tax based on progressive brackets
   - Support different rates for first house vs additional properties
   - Handle property values across all tax brackets
   - Return both tax amount and effective tax rate

2. **Capital Gains Tax Calculation**
   - Calculate capital gains tax on property sale
   - Account for purchase tax paid (deductible)
   - Account for improvement costs (deductible)

3. **Tax Bracket Management**
   - Define tax brackets as data structures
   - Support annual updates to tax rates
   - Clear documentation of current tax year

### Non-Functional Requirements

- **Maintainability:** Easy to update tax brackets annually
- **Accuracy:** Correct progressive tax calculation
- **Documentation:** Clear references to official sources
- **Type Safety:** Use type hints throughout

---

## Architecture

### Module Structure

```
mortgage_return_scenario_calculator/
├── tax_config.py          # Tax calculation module
    ├── TaxBracket         # Dataclass for tax bracket
    ├── FIRST_HOUSE_BRACKETS    # Tax brackets for first house
    ├── ADDITIONAL_HOUSE_BRACKETS  # Tax brackets for additional properties
    ├── calculate_purchase_tax()   # Main calculation function
    ├── calculate_purchase_tax_rate()  # Effective rate calculator
    └── calculate_capital_gains_tax()   # Capital gains calculator
```

### Component Design

#### 1. TaxBracket Dataclass

**Purpose:** Represent a single tax bracket with min, max, and rate.

**Attributes:**
- `min_value: float` - Minimum property value (inclusive)
- `max_value: float | None` - Maximum property value (exclusive, None = no limit)
- `rate: float` - Tax rate as decimal (e.g., 0.05 for 5%)

**Methods:**
- `applies_to(value: float) -> bool` - Check if value falls in bracket

#### 2. Tax Brackets Configuration

**First House Brackets (דירה יחידה):**
- Progressive brackets with increasing rates
- Lower rates for lower property values
- Exemption threshold (0% up to certain amount)

**Additional House Brackets (דירה נוספת):**
- Higher flat rate for most property values
- Same luxury property threshold as first house

#### 3. Calculation Functions

**`calculate_purchase_tax(property_value, is_first_house) -> float`**
- Input: Property value, first house flag
- Process: Apply progressive brackets
- Output: Total tax amount

**`calculate_purchase_tax_rate(property_value, is_first_house) -> float`**
- Input: Property value, first house flag
- Process: Calculate tax, divide by value
- Output: Effective tax rate as decimal

**`calculate_capital_gains_tax(sale_price, purchase_price, ...) -> float`**
- Input: Sale price, purchase price, purchase tax paid, improvements
- Process: Calculate gain, apply tax rate
- Output: Capital gains tax amount

---

## Data Models

### TaxBracket

```python
@dataclass
class TaxBracket:
    min_value: float
    max_value: float | None
    rate: float
    
    def applies_to(self, value: float) -> bool:
        """Check if value falls within bracket."""
```

### Tax Brackets Lists

```python
FIRST_HOUSE_BRACKETS: List[TaxBracket]
ADDITIONAL_HOUSE_BRACKETS: List[TaxBracket]
CAPITAL_GAINS_TAX_RATE: float
```

---

## Algorithm Design

### Purchase Tax Calculation (Progressive Brackets)

**Pseudo-code:**
```
function calculate_purchase_tax(property_value, is_first_house):
    if property_value <= 0:
        return 0.0
    
    brackets = FIRST_HOUSE_BRACKETS if is_first_house else ADDITIONAL_HOUSE_BRACKETS
    total_tax = 0.0
    
    for each bracket in brackets:
        if property_value <= bracket.min_value:
            break  # Skip brackets below property value
        
        bracket_max = bracket.max_value or infinity
        bracket_start = bracket.min_value
        bracket_end = min(property_value, bracket_max)
        
        amount_in_bracket = bracket_end - bracket_start
        tax_for_bracket = amount_in_bracket * bracket.rate
        total_tax += tax_for_bracket
    
    return total_tax
```

**Example Calculation:**
- Property value: 2,000,000 ILS (first house)
- Bracket 1: 0 to 1,805,000 at 0% = 0 ILS
- Bracket 2: 1,805,000 to 2,085,000 at 3.5% = (2,000,000 - 1,805,000) * 0.035 = 6,825 ILS
- Total: 6,825 ILS

### Capital Gains Tax Calculation

**Pseudo-code:**
```
function calculate_capital_gains_tax(sale_price, purchase_price, purchase_tax_paid, improvements):
    capital_gain = sale_price - purchase_price - purchase_tax_paid - improvements
    
    if capital_gain <= 0:
        return 0.0
    
    return capital_gain * CAPITAL_GAINS_TAX_RATE
```

---

## Edge Cases

1. **Zero or Negative Property Value**
   - Return 0 tax
   - Return 0 rate

2. **Property Value Exactly at Bracket Boundary**
   - Use inclusive min, exclusive max
   - Handle boundary correctly in calculation

3. **Property Value Above Highest Bracket**
   - Use bracket with max_value = None
   - Apply rate to remaining amount

4. **Negative Capital Gain**
   - Return 0 tax (no tax on losses)

5. **Missing Purchase Tax/Improvements**
   - Default to 0 if not provided

---

## Dependencies

- **Standard Library:**
  - `dataclasses` - For TaxBracket dataclass
  - `typing` - For type hints (List, Optional)

- **No External Dependencies** - Pure Python implementation

---

## Implementation Steps

### Step 1: Create TaxBracket Dataclass
- [x] Define TaxBracket with min_value, max_value, rate
- [x] Add applies_to() method
- [x] Add type hints

### Step 2: Define Tax Brackets
- [x] Create FIRST_HOUSE_BRACKETS list
- [x] Create ADDITIONAL_HOUSE_BRACKETS list
- [x] Add comments with tax year and source references
- [x] Set CAPITAL_GAINS_TAX_RATE constant

### Step 3: Implement Purchase Tax Calculation
- [x] Implement calculate_purchase_tax() function
- [x] Handle progressive bracket logic correctly
- [x] Handle edge cases (zero, negative, boundaries)
- [x] Add comprehensive docstring with examples

### Step 4: Implement Tax Rate Calculation
- [x] Implement calculate_purchase_tax_rate() function
- [x] Calculate effective rate from tax amount
- [x] Handle division by zero

### Step 5: Implement Capital Gains Tax Calculation
- [x] Implement calculate_capital_gains_tax() function
- [x] Account for purchase tax and improvements
- [x] Handle negative gains

### Step 6: Add Example Usage
- [x] Add __main__ block with test cases
- [x] Display example calculations
- [x] Include warnings about annual updates

---

## Integration Points

### Future Integration with Calculator

1. **ScenarioInputs Model**
   - Add `is_first_house: bool` field
   - Add `purchase_tax_paid: float` field (calculated)

2. **Financial Calculations**
   - Integrate purchase tax into initial investment calculation
   - Include purchase tax in total acquisition cost
   - Use capital gains tax in sale calculations

3. **Config Generator**
   - Add tax calculation to config generation
   - Include tax fields in CSV export

---

## Testing Considerations

**Test Cases Needed:**
1. First house at various price points (below threshold, mid-range, luxury)
2. Additional house at various price points
3. Property value exactly at bracket boundaries
4. Property value above highest bracket
5. Zero/negative property values
6. Capital gains with and without improvements
7. Negative capital gains (losses)

**Test Data:**
- First house: 1.5M, 2M, 3M, 6M, 20M ILS
- Additional house: 1.5M, 2M, 3M, 6M, 20M ILS
- Capital gains: Various scenarios

---

## Documentation Requirements

1. **Module Docstring**
   - Purpose and reference to official sources
   - Warning about annual updates

2. **Function Docstrings**
   - Clear parameter descriptions
   - Return value descriptions
   - Example calculations

3. **Inline Comments**
   - Explain bracket logic
   - Reference official tax authority sources

---

## Maintenance Notes

**Annual Updates Required:**
- Tax brackets may change each year
- Update FIRST_HOUSE_BRACKETS
- Update ADDITIONAL_HOUSE_BRACKETS
- Update CAPITAL_GAINS_TAX_RATE if changed
- Update "Last Updated" date in docstring

**Sources for Updates:**
- Israel Tax Authority website
- Official tax simulator
- kolzchut.org.il updates

---

## Design Approval

**Status:** ✅ Design Complete

**Next Steps:**
1. SE to review design
2. SE to implement according to this design
3. Tester to write unit tests
4. Integration with existing calculator models

---

**Designer:** System Architect  
**Date:** 2025-12-20  
**Version:** 1.0


