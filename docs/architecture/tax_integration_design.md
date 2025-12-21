# Tax Integration into ScenarioResult Design

**Status:** Design Complete  
**Date:** 2025-12-20  
**Architect:** System Architect  
**Related Enhancement:** Phase 2 Enhancement - Real Estate Taxes Integration

---

## Overview

Design for integrating purchase tax (מס רכישה) and capital gains tax (מס שבח) calculations into the ScenarioResult's `total_profit` calculation. This ensures accurate profit calculations that account for all tax implications of real estate investment.

**Dependencies:**
- `tax_config.py` module (already implemented)
- `ScenarioInputs` model (needs enhancement)
- `ScenarioResult` calculation logic (needs modification)

---

## Requirements

### Functional Requirements

1. **Purchase Tax Integration**
   - Calculate purchase tax when property is bought
   - Include purchase tax in total acquisition cost
   - Deduct purchase tax from profit calculation
   - Support first house vs additional property logic

2. **Capital Gains Tax Integration**
   - Calculate capital gains tax when property is sold
   - Account for purchase tax paid (deductible from capital gains)
   - Account for improvement costs (if applicable)
   - Deduct capital gains tax from profit calculation

3. **Model Enhancements**
   - Add `is_first_house: bool` field to `ScenarioInputs`
   - Add `improvement_costs: float` field to `ScenarioInputs` (optional)
   - Add tax metrics to `ScenarioResult` or create new `TaxMetrics` dataclass

4. **Backward Compatibility**
   - Default `is_first_house=True` for existing code
   - Default `improvement_costs=0.0` if not provided
   - Maintain existing API where possible

---

## Architecture

### Current Flow

```
ScenarioInputs → Calculator → ScenarioResult
                                    ↓
                            total_profit = net_gain_property + net_portfolio_profit
```

### Enhanced Flow

```
ScenarioInputs (with is_first_house) 
    ↓
Calculator
    ↓
Tax Calculations (using tax_config.py)
    ↓
ScenarioResult (with tax-adjusted total_profit)
```

### Component Changes

#### 1. ScenarioInputs Model Enhancement

**Add Fields:**
```python
@dataclass
class ScenarioInputs:
    # ... existing fields ...
    
    # Tax-related fields
    is_first_house: bool = True  # True for first house, False for additional property
    improvement_costs: float = 0.0  # Costs of improvements (deductible from capital gains)
```

**Validation:**
- `improvement_costs >= 0`
- No validation needed for `is_first_house` (boolean)

#### 2. New TaxMetrics Dataclass

**Purpose:** Store all tax-related calculations for transparency and debugging.

```python
@dataclass
class TaxMetrics:
    """Tax-related calculations for the investment scenario.
    
    Attributes:
        purchase_tax: Purchase tax paid when buying property.
        purchase_tax_rate: Effective purchase tax rate.
        capital_gains: Capital gain from property sale.
        capital_gains_tax: Capital gains tax paid when selling.
        total_taxes: Total taxes paid (purchase + capital gains).
        net_profit_after_taxes: Net profit after all taxes.
    """
    purchase_tax: float
    purchase_tax_rate: float
    capital_gains: float
    capital_gains_tax: float
    total_taxes: float
    net_profit_after_taxes: float
```

#### 3. Calculator Integration

**New Method:**
```python
def calculate_taxes(
    self,
    appreciation_metrics: AppreciationMetrics,
    early_repayment_metrics: EarlyRepaymentMetrics
) -> TaxMetrics:
    """Calculate all tax-related metrics.
    
    Args:
        appreciation_metrics: Calculated appreciation metrics.
        early_repayment_metrics: Calculated early repayment metrics.
    
    Returns:
        TaxMetrics with all tax calculations.
    """
```

**Modified Method:**
```python
def calculate(self) -> ScenarioResult:
    # ... existing calculations ...
    
    # NEW: Calculate taxes
    tax_metrics = self.calculate_taxes(appreciation_metrics, early_repayment_metrics)
    
    # MODIFIED: Adjust total_profit to account for taxes
    total_profit = (
        early_repayment_metrics.net_gain_property +
        portfolio_metrics.net_portfolio_profit -
        tax_metrics.total_taxes  # Subtract total taxes
    )
    
    # ... rest of calculation ...
```

#### 4. ScenarioResult Enhancement

**Add Field:**
```python
@dataclass
class ScenarioResult:
    # ... existing fields ...
    tax_metrics: TaxMetrics  # NEW: Tax calculations
```

---

## Algorithm Design

### Purchase Tax Calculation

**When:** At property purchase (beginning of investment)

**Formula:**
```
purchase_tax = calculate_purchase_tax(
    property_value=inputs.property_price,
    is_first_house=inputs.is_first_house
)
```

**Impact:**
- Reduces available cash for investment
- Deductible from capital gains tax calculation
- Included in total acquisition cost

### Capital Gains Tax Calculation

**When:** At property sale (end of investment period)

**Formula:**
```
capital_gains = sale_value - purchase_price - purchase_tax - improvement_costs
capital_gains_tax = calculate_capital_gains_tax(
    sale_price=sale_value,
    purchase_price=inputs.property_price,
    purchase_tax_paid=purchase_tax,
    improvement_costs=inputs.improvement_costs
)
```

**Where:**
- `sale_value` = `appreciation_metrics.sale_value`
- `purchase_price` = `inputs.property_price`
- `purchase_tax` = calculated purchase tax
- `improvement_costs` = `inputs.improvement_costs`

### Total Profit Adjustment

**Current Formula:**
```
total_profit = net_gain_property + net_portfolio_profit
```

**New Formula:**
```
total_profit = net_gain_property + net_portfolio_profit - total_taxes
```

**Where:**
- `total_taxes = purchase_tax + capital_gains_tax`
- Note: Purchase tax is already accounted for in `net_gain_property` indirectly,
  but we need to explicitly subtract it for accuracy

### Detailed Profit Calculation

**Property Profit After Taxes:**
```
property_profit_before_tax = proceeds_minus_debt - down_payment
property_profit_after_tax = property_profit_before_tax - purchase_tax - capital_gains_tax
```

**Total Profit:**
```
total_profit = property_profit_after_tax + net_portfolio_profit
```

---

## Edge Cases

1. **Zero Purchase Tax (First House Below Threshold)**
   - Purchase tax = 0
   - No impact on profit
   - Capital gains calculation still works

2. **Negative Capital Gains (Loss)**
   - Capital gains tax = 0 (no tax on losses)
   - Total taxes = purchase_tax only

3. **No Improvements**
   - improvement_costs = 0 (default)
   - Capital gains = sale_value - purchase_price - purchase_tax

4. **Full Cash Purchase (No Mortgage)**
   - Purchase tax still applies
   - Capital gains tax still applies
   - No change to tax calculation logic

5. **Property Value Exactly at Bracket Boundary**
   - Tax calculation handles boundaries correctly
   - No special handling needed

---

## Dependencies

- **Existing Module:**
  - `tax_config.py` - Already implemented tax calculation functions

- **Standard Library:**
  - No new dependencies

---

## Implementation Steps

### Step 1: Enhance ScenarioInputs Model
- [x] Add `is_first_house: bool = True` field
- [x] Add `improvement_costs: float = 0.0` field
- [x] Add validation for `improvement_costs >= 0`
- [x] Update docstring

### Step 2: Create TaxMetrics Dataclass
- [x] Create new `TaxMetrics` dataclass in `models.py`
- [x] Add all required fields with type hints
- [x] Add comprehensive docstring

### Step 3: Implement calculate_taxes() Method
- [x] Add method to `ScenarioCalculator` class
- [x] Import tax calculation functions from `tax_config`
- [x] Calculate purchase tax
- [x] Calculate capital gains
- [x] Calculate capital gains tax
- [x] Calculate total taxes
- [x] Return `TaxMetrics` object

### Step 4: Modify calculate() Method
- [x] Call `calculate_taxes()` in calculation flow
- [x] Adjust `total_profit` calculation to subtract taxes
- [x] Include `tax_metrics` in `ScenarioResult`

### Step 5: Update ScenarioResult Model
- [x] Add `tax_metrics: TaxMetrics` field
- [x] Update docstring

### Step 6: Update Exporter (if needed)
- [ ] Add tax fields to CSV export
- [ ] Update variable descriptions

---

## Testing Considerations

**Test Cases Needed:**

1. **First House Scenarios:**
   - Property below tax threshold (0% tax)
   - Property in middle bracket (3.5% or 5% tax)
   - Property in luxury bracket (7.5% or 10% tax)

2. **Additional Property Scenarios:**
   - Property at various price points (all 8% except luxury)
   - Luxury property (10% tax)

3. **Capital Gains Scenarios:**
   - Positive capital gains (tax applies)
   - Negative capital gains (no tax)
   - Zero capital gains (no tax)

4. **Improvement Costs:**
   - With improvement costs
   - Without improvement costs (default)

5. **Integration Tests:**
   - Full scenario with taxes
   - Compare profit before/after tax integration
   - Verify tax metrics are calculated correctly

**Test Data Examples:**
- First house: 1.5M, 2M, 3M ILS
- Additional house: 1.5M, 2M, 3M ILS
- Various appreciation scenarios
- With/without improvements

---

## Backward Compatibility

**Breaking Changes:**
- None - all new fields have defaults

**Migration:**
- Existing code continues to work (defaults: `is_first_house=True`, `improvement_costs=0.0`)
- New code can explicitly set tax-related fields

**API Changes:**
- `ScenarioResult` gains new `tax_metrics` field
- `total_profit` calculation changes (but result should be more accurate)

---

## Documentation Updates

1. **Model Docstrings:**
   - Update `ScenarioInputs` docstring
   - Add `TaxMetrics` docstring
   - Update `ScenarioResult` docstring

2. **Calculator Docstrings:**
   - Document `calculate_taxes()` method
   - Update `calculate()` method docstring

3. **User Documentation:**
   - Explain tax implications
   - Provide examples with/without taxes

---

## Design Approval

**Status:** ✅ Design Complete  
**Implementation Status:** ✅ COMPLETE (2025-12-20)

**Completed Steps:**
1. ✅ SE reviewed design
2. ✅ SE implemented according to this design
3. ⏸️ Tester to write comprehensive unit tests (pending)
4. ⏸️ Integration testing (pending)

---

**Designer:** System Architect  
**Date:** 2025-12-20  
**Version:** 1.0

