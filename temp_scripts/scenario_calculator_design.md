# Scenario Calculator Design Plan

## User Inputs Identified (Yellow Cells - Column B)

Based on Excel analysis, here are the user inputs:

1. **B2: 20** - Loan term in years (Scenario A)
2. **B3: 15** - Alternative loan term (years)
3. **B4: 2,650,000** - Property price
4. **B5: 2,650,000** - Total investment amount
5. **B6: 1,350,000** - Down payment amount
6. **B7: 10,000** - Additional costs (purchase costs, etc.)
7. **B12: 0.048** - Interest rate (4.8%)
8. **B18: 6,300** - Monthly rental income
9. **B25: 0.04** - Annual appreciation rate (4%)
10. **B27: Formula** - Additional costs (references Regression sheet, max 400,000)
11. **B39: 0.035** - Alternative interest rate (3.5%)
12. **B48: 0.07** - Another rate (7%)
13. **B57: Formula** - Monthly payment calculation
14. **B58: 0.03** - Some rate (3%)
15. **B63: 0.03** - Another rate (3%)

## Row Labels Translation (Hebrew → English)

Based on formulas and context:

1. **Row 2:** Loan term (years) - Scenario A
2. **Row 3:** Alternative loan term (years)
3. **Row 4:** Property price
4. **Row 5:** Total investment amount (if not using loan)
5. **Row 6:** Down payment amount
6. **Row 7:** Additional purchase costs
7. **Row 8:** Loan amount (calculated: Property price - Down payment)
8. **Row 9:** Down payment percentage (calculated: Down payment / Property price)
9. **Row 10:** Loan percentage (calculated: 1 - Down payment %)
10. **Row 11:** Leverage multiplier (calculated: 1 / Loan percentage)
11. **Row 12:** Interest rate (annual, as decimal)
12. **Row 13:** Total interest paid over loan term
13. **Row 14:** Monthly mortgage payment (PMT function)
14. **Row 15:** Required monthly income (mortgage / 0.3 = 30% rule)
15. **Row 16:** Total interest paid
16. **Row 17:** Average annual interest
17. **Row 18:** Monthly rental income
18. **Row 19:** Annual rental yield (rental * 12 / property price)
19. **Row 20:** Net rental income after mortgage
20. **Row 21:** Monthly principal paydown
21. **Row 22:** Cash flow (rental - mortgage payment)
22. **Row 23:** Leveraged yield
23. **Row 24:** Net leveraged yield (after interest)
24. **Row 25:** Annual appreciation rate
25. **Row 26:** Property appreciation over term
26. **Row 27:** Additional costs (renovation, etc.)
27. **Row 28:** Additional costs appreciation
28. **Row 29:** Total additional value
29. **Row 30:** Total property value at end
30. **Row 31:** Total return
31. **Row 32:** Annualized return
32. **Row 33:** Leveraged annualized return

## Key Formulas Analysis

### Mortgage Calculations:
- **Monthly Payment:** `PMT(rate/12, 12*years, loan_amount)`
- **Loan Amount:** `Property Price - Down Payment`
- **Down Payment %:** `Down Payment / Property Price`
- **Leverage:** `1 / (1 - Down Payment %)`

### Cash Flow:
- **Monthly Cash Flow:** `Monthly Rent - Monthly Mortgage Payment`
- **Annual Cash Flow:** `Monthly Cash Flow * 12`

### Returns:
- **Property Appreciation:** `Property Price * ((1 + appreciation_rate)^years - 1)`
- **Total Return:** `(Final Value / Initial Investment) - 1`
- **Annualized Return:** `((1 + total_return)^(1/years)) - 1`
- **Leveraged Return:** `Annualized Return * Leverage Multiplier`

## Logic Flow

```
1. User Inputs:
   - Property Price
   - Down Payment
   - Loan Term
   - Interest Rate
   - Monthly Rental Income
   - Annual Appreciation Rate
   - Additional Costs

2. Calculate Loan:
   - Loan Amount = Price - Down Payment
   - Down Payment % = Down Payment / Price
   - Leverage = 1 / (1 - Down Payment %)

3. Calculate Mortgage:
   - Monthly Payment = PMT(rate/12, months, loan_amount)
   - Total Interest = Sum of interest over loan term

4. Calculate Cash Flow:
   - Monthly Cash Flow = Rent - Mortgage Payment
   - Annual Cash Flow = Monthly Cash Flow * 12

5. Calculate Returns:
   - Property Appreciation = Price * ((1 + rate)^years - 1)
   - Additional Costs Appreciation = Costs * ((1 + rate)^years - 1)
   - Total Value = Price + Appreciation + Additional Value
   - Total Return = (Total Value / Initial Investment) - 1
   - Annualized Return = ((1 + total_return)^(1/years)) - 1
   - Leveraged Return = Annualized Return * Leverage

## Potential Logic Flaws / Issues

1. **Row 15 (Required Income):** Uses 0.3 (30% rule) - should this be configurable?
2. **Row 27 (Additional Costs):** References Regression sheet - hard dependency
3. **Cash Flow Calculation:** Doesn't account for:
   - Property taxes
   - Insurance
   - Maintenance costs
   - Vacancy rate
   - Property management fees
4. **Appreciation:** Assumes constant appreciation rate - no volatility modeling
5. **Interest Rate:** Fixed rate assumed - no variable rate option
6. **Tax Considerations:** No tax deductions or capital gains tax
7. **Inflation:** Not accounted for in returns

