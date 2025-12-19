# 🧪 Scratchpad

> Think here BEFORE coding. Clear after feature complete.

---

## Phase 2: Scenario Calculator Design (v2 - Improved)

### Full Analysis Complete
- ✅ Analyzed all 66+ rows in Scenario Calculator sheet
- ✅ Separated User Inputs from Assumptions
- ✅ Documented all 35+ formulas
- ✅ Organized into 7 calculation groups

### Input Structure (Clarified)

**User Inputs (Property-Specific - Required):**
- `property_price` - Purchase price
- `down_payment` - Equity amount
- `available_cash` - Total cash available
- `monthly_available` - Monthly investment capacity
- `mortgage_term_years` - Loan duration
- `years_until_sale` - When to sell
- `urban_renewal_value` - Optional (max 400k)

**Assumptions (Market Defaults - Customizable):**
- `rental_yield` = 2.8% (monthly_rent = price * yield / 12)
- `mortgage_rate` = 4.8%
- `appreciation_rate` = 4%
- `rent_increase_rate` = 3%
- `portfolio_return_rate` = 7%
- `risk_free_rate` = 3%
- `early_repayment_rate` = 3.5%
- `capital_gains_tax_rate` = 25%

### Class Structure (10 Classes)
1. **InvestmentAssumptions** - Market defaults with sensible values
2. **ScenarioInputs** - Property-specific inputs (required)
3. **InvestmentRestrictions** - Validation rules
4. **LoanMetrics** - Calculated loan values
5. **CashFlowMetrics** - Calculated cash flow
6. **AppreciationMetrics** - Returns and appreciation
7. **EarlyRepaymentMetrics** - Early repayment scenarios
8. **PortfolioMetrics** - Alternative investment
9. **ScenarioResult** - Complete results
10. **ScenarioCalculator** - Main engine

**Full design document:** `SCENARIO_CALCULATOR_DESIGN.md`

---
