# 🧪 Scratchpad

> Think here BEFORE coding. Clear after feature complete.

---

## Phase 2: Scenario Calculator Design (v2 - Improved)

### Full Analysis Complete
- ✅ Analyzed all 66+ rows in Scenario Calculator sheet
- ✅ Identified 14 user inputs (yellow cells)
- ✅ Translated all Hebrew labels to English
- ✅ Documented all 35+ formulas
- ✅ Organized into 7 calculation groups
- ✅ Identified logic issues

### Calculation Groups
1. **Loan Metrics** - loan amount, leverage, monthly payment, interest
2. **Cash Flow** - rental yield, net cash flow, leveraged yield
3. **Property Appreciation** - value growth, sale value, returns
4. **Early Repayment** - remaining mortgage, penalties, net gain
5. **Portfolio Comparison** - alternative investment calculations
6. **Post-Mortgage Rental** - rental income after mortgage ends
7. **Final Summary** - total value, profit, annual return

### Class Structure (Improved)
1. **ScenarioInputs** - All 14 user inputs
2. **InvestmentRestrictions** - Validation rules
3. **LoanMetrics** - Calculated loan values
4. **CashFlowMetrics** - Calculated cash flow
5. **AppreciationMetrics** - Returns and appreciation
6. **EarlyRepaymentMetrics** - Early repayment scenarios
7. **PortfolioMetrics** - Alternative investment
8. **ScenarioResult** - Complete results
9. **ScenarioCalculator** - Main engine

### Key Findings
- Excel compares real estate vs portfolio investment
- Uses PMT, FV, PV financial functions
- Accounts for leverage, taxes (25% capital gains)
- Missing: operating expenses, vacancy rate, inflation

**Full design document:** `SCENARIO_CALCULATOR_DESIGN.md`

---
