# Phase 2: Scenario Calculator - Design Document (v2)

## Overview

The Scenario Calculator models a single real estate investment scenario, comparing:
1. **Real Estate Investment** - Buy property with mortgage
2. **Alternative Investment** - Invest the same money in a portfolio

It calculates financial metrics including cash flow, ROI, leverage effects, and compares outcomes.

---

## User Inputs Identified (from Excel Yellow Cells)

| Row | Hebrew Label | English Name | Variable Name | Example Value | Description |
|-----|-------------|--------------|---------------|---------------|-------------|
| 2 | משך המשכנתא (שנים) | Mortgage term | `mortgage_term_years` | 20 | Duration of mortgage in years |
| 3 | שנים עד המכירה | Years until sale | `years_until_sale` | 15 | When property will be sold |
| 4 | מחיר הדירה | Property price | `property_price` | 2,650,000 | Purchase price |
| 5 | כסף פנוי להשקעה | Available cash | `available_cash` | 2,650,000 | Total cash available for investment |
| 6 | כמות ההון העצמי | Down payment | `down_payment` | varies | Equity/down payment amount |
| 7 | סכום חודשי שפנוי | Monthly available | `monthly_available` | 10,000 | Monthly amount available for investment |
| 12 | ריבית משכנתא | Mortgage interest rate | `mortgage_rate` | 0.048 | Annual interest rate (4.8%) |
| 18 | מחיר השכירות | Monthly rent | `monthly_rent` | 6,300 | Expected monthly rental income |
| 25 | שיעור עליית ערך | Appreciation rate | `appreciation_rate` | 0.04 | Annual property appreciation (4%) |
| 27 | עליית ערך מפינוי בינוי | Urban renewal value | `urban_renewal_value` | ≤400,000 | Added value from urban renewal |
| 39 | ריבית פירעון מוקדם | Early repayment rate | `early_repayment_rate` | 0.035 | Interest rate at early repayment |
| 48 | תשואת תיק השקעות | Portfolio return | `portfolio_return_rate` | 0.07 | Annual return for alternative investment |
| 58 | עליית מחירי שכירות | Rent increase rate | `rent_increase_rate` | 0.03 | Annual rent increase (3%) |
| 63 | ריבית חסרת סיכון | Risk-free rate | `risk_free_rate` | 0.03 | Risk-free rate for discounting |

---

## Calculation Groups

### Group 1: Loan Metrics (Rows 8-17)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 8 | גודל המשכנתא | Loan amount | `loan_amount` | `property_price - down_payment` |
| 9 | שיעור המינוף | Leverage ratio | `leverage_ratio` | `loan_amount / property_price` |
| 10 | שיעור ההון העצמי | Equity ratio | `equity_ratio` | `1 - leverage_ratio` |
| 11 | מכפיל המינוף | Leverage multiplier | `leverage_multiplier` | `1 / equity_ratio` |
| 13 | סך תשלומי המשכנתא | Total mortgage payments | `total_mortgage_payments` | `monthly_payment * 12 * mortgage_term` |
| 14 | החזר חודשי | Monthly payment | `monthly_payment` | `PMT(rate/12, months, loan)` |
| 15 | הכנסות נדרשות | Required income | `required_income` | `monthly_payment / 0.3` |
| 16 | סך החזרי הריבית | Total interest | `total_interest` | `total_payments - loan_amount` |
| 17 | ריבית חודשית ממוצעת | Avg monthly interest | `avg_monthly_interest` | `total_interest / 12 / mortgage_term` |

### Group 2: Cash Flow (Rows 18-24)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 18 | מחיר השכירות | Monthly rent | `monthly_rent` | INPUT |
| 19 | תשואת השכירות | Rental yield | `rental_yield` | `monthly_rent * 12 / property_price` |
| 20 | תזרים ריבית חודשי | Monthly interest flow | `monthly_interest_flow` | `monthly_rent - avg_monthly_interest` |
| 21 | החזר קרן ממוצע | Avg principal payment | `avg_principal_payment` | `-loan_amount / 12 / mortgage_term` |
| 22 | תזרים חודשי נטו | Monthly net cash flow | `monthly_net_cash_flow` | `monthly_rent - monthly_payment` |
| 23 | תשואת שכירות ממונפת | Leveraged rental yield | `leveraged_rental_yield` | `rental_yield * leverage_multiplier` |
| 24 | תשואה נטו ממונפת | Net leveraged yield | `net_leveraged_yield` | `IF(loan>0, leveraged_yield - rate, leveraged_yield)` |

### Group 3: Property Appreciation (Rows 25-35)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 25 | שיעור עליית ערך | Appreciation rate | `appreciation_rate` | INPUT |
| 26 | עליית ערך הנכס | Property appreciation | `property_appreciation` | `((1+rate)^years - 1) * price` |
| 27 | ערך פינוי בינוי | Urban renewal value | `urban_renewal_value` | INPUT (max 400,000) |
| 28 | עליית ערך פינוי בינוי | Urban renewal appreciation | `urban_renewal_appreciation` | `((1+rate)^years - 1) * urban_renewal` |
| 29 | עליית ערך כוללת | Total appreciation | `total_appreciation` | `urban_renewal + property_appreciation + urban_renewal_appreciation` |
| 30 | שווי במכירה | Sale value | `sale_value` | `property_price + total_appreciation` |
| 31 | שיעור תשואה כולל | Total return rate | `total_return_rate` | `(sale_value / property_price) - 1` |
| 32 | תשואה שנתית | Annualized return | `annualized_return` | `((1 + total_return)^(1/years)) - 1` |
| 33 | תשואה ממונפת | Leveraged return | `leveraged_return` | `annualized_return * leverage_multiplier` |
| 34 | + תשואת שכירות | + rental yield | `with_rental_yield` | `leveraged_return + leveraged_rental_yield` |
| 35 | תשואה שנתית נטו | Net annual return | `net_annual_return` | `with_rental_yield - mortgage_rate` |

### Group 4: Early Repayment (Rows 37-44)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 38 | שארית משכנתא | Remaining mortgage | `remaining_mortgage` | `IF(years<term, ((term-years)/term)*total_payments, 0)` |
| 40 | עמלת פירעון מוקדם | Early repayment penalty | `early_repayment_penalty` | `PV(old_rate) - PV(new_rate)` |
| 41 | סך חוב לבנק | Total debt to bank | `total_debt_to_bank` | `remaining_mortgage + penalty` |
| 43 | תקבול פחות חוב | Proceeds minus debt | `proceeds_minus_debt` | `sale_value - total_debt` |
| 44 | רווח נטו | Net gain from property | `net_gain_property` | `proceeds_minus_debt - down_payment` |

### Group 5: Alternative Investment Portfolio (Rows 46-54)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 47 | כסף בתיק השקעות | Cash in portfolio | `cash_in_portfolio` | `available_cash - down_payment` |
| 48 | תשואת תיק | Portfolio return | `portfolio_return_rate` | INPUT |
| 49 | שווי תיק ללא הפקדות | Portfolio value (initial) | `portfolio_initial_growth` | `initial * (1+rate)^years` |
| 50 | הפקדות חודשיות | Monthly deposits | `monthly_deposits` | `monthly_available + monthly_cash_flow` |
| 51 | צבירה מהפקדות | Accumulated deposits | `accumulated_deposits` | `FV(rate/12, months, -deposits)` |
| 52 | שווי תיק כולל | Total portfolio value | `total_portfolio_value` | `initial_growth + accumulated_deposits` |
| 53 | אחרי מס רווח הון | After capital gains tax | `portfolio_after_tax` | Complex formula (25% tax on gains) |
| 54 | רווח נטו מתיק | Net portfolio profit | `net_portfolio_profit` | `after_tax - initial - all_deposits` |

### Group 6: Post-Mortgage Rental (Rows 56-61)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 57 | שכירות אחרי פינוי בינוי | Rent after renewal | `rent_after_renewal` | `(price + urban_renewal) * yield / 12` |
| 58 | עליית שכירות | Rent increase rate | `rent_increase_rate` | INPUT |
| 59 | שכירות בתום משכנתא | Rent at mortgage end | `rent_at_mortgage_end` | `current_rent * (1+rate)^years` |
| 60 | תקבולי שכירות | Rental receipts | `rental_receipts` | `FV(rate, months_after_mortgage, -rent)` |
| 61 | אחרי מס | After tax | `rental_after_tax` | Complex formula (25% tax) |

### Group 7: Final Summary (Rows 63-66)

| Row | Hebrew | English | Variable | Formula |
|-----|--------|---------|----------|---------|
| 63 | ריבית חסרת סיכון | Risk-free rate | `risk_free_rate` | INPUT |
| 64 | שווי כולל | Total value at sale | `total_value_at_sale` | `rental_after_tax + portfolio_after_tax + proceeds_minus_debt` |
| 65 | רווח כולל | Total profit | `total_profit` | `rental_profit + portfolio_profit + property_profit` |
| 66 | תשואה שנתית | Annual return | `annual_return` | `(total_value / initial_investment)^(1/years) - 1` |

---

## Improved Class Structure

### 1. `ScenarioInputs` (Dataclass)
**All user inputs in one place**

```python
@dataclass
class ScenarioInputs:
    """All user inputs for the investment scenario."""
    
    # Property Details
    property_price: float  # מחיר הדירה - Purchase price
    monthly_rent: float  # מחיר השכירות - Expected monthly rental income
    urban_renewal_value: float = 0.0  # עליית ערך מפינוי בינוי - Added value (max 400,000)
    
    # Investment Capital
    available_cash: float  # כסף פנוי להשקעה - Total cash available
    down_payment: float  # כמות ההון העצמי - Equity/down payment
    monthly_available: float  # סכום חודשי שפנוי - Monthly investment capacity
    
    # Time Parameters
    mortgage_term_years: int  # משך המשכנתא - Mortgage duration in years
    years_until_sale: int  # שנים עד המכירה - When property will be sold
    
    # Interest Rates
    mortgage_rate: float  # ריבית משכנתא - Annual mortgage interest (e.g., 0.048)
    early_repayment_rate: float = 0.035  # ריבית פירעון מוקדם - Rate at early repayment
    
    # Growth Rates
    appreciation_rate: float  # שיעור עליית ערך - Annual property appreciation (e.g., 0.04)
    rent_increase_rate: float = 0.03  # עליית מחירי שכירות - Annual rent increase
    
    # Alternative Investment
    portfolio_return_rate: float = 0.07  # תשואת תיק השקעות - Portfolio annual return
    
    # Other
    risk_free_rate: float = 0.03  # ריבית חסרת סיכון - For discounting
    capital_gains_tax_rate: float = 0.25  # מס רווח הון - Capital gains tax (25%)
    
    def __post_init__(self):
        """Validate and cap values."""
        self.urban_renewal_value = min(self.urban_renewal_value, 400_000)
```

### 2. `InvestmentRestrictions` (Dataclass)
**Validation rules and constraints**

```python
@dataclass
class InvestmentRestrictions:
    """Investment validation rules and constraints."""
    
    max_mortgage_to_income_ratio: float = 0.3  # Maximum 30% of income
    min_down_payment_percentage: float = 0.0  # Minimum down payment %
    max_loan_to_value: float = 0.75  # Maximum LTV (75%)
    max_urban_renewal_value: float = 400_000  # Maximum urban renewal cap
    require_positive_cash_flow: bool = False  # Must have positive cash flow
```

### 3. `LoanMetrics` (Dataclass)
**Calculated loan-related values**

```python
@dataclass
class LoanMetrics:
    """Calculated loan metrics."""
    
    loan_amount: float  # גודל המשכנתא
    leverage_ratio: float  # שיעור המינוף
    equity_ratio: float  # שיעור ההון העצמי
    leverage_multiplier: float  # מכפיל המינוף
    monthly_payment: float  # החזר חודשי
    total_payments: float  # סך תשלומי המשכנתא
    total_interest: float  # סך החזרי הריבית
    avg_monthly_interest: float  # ריבית חודשית ממוצעת
    required_income: float  # הכנסות נדרשות (30% rule)
```

### 4. `CashFlowMetrics` (Dataclass)
**Calculated cash flow values**

```python
@dataclass
class CashFlowMetrics:
    """Calculated cash flow metrics."""
    
    rental_yield: float  # תשואת השכירות - Annual yield
    monthly_net_cash_flow: float  # תזרים חודשי נטו
    monthly_interest_flow: float  # תזרים ריבית חודשי
    avg_principal_payment: float  # החזר קרן ממוצע
    leveraged_rental_yield: float  # תשואת שכירות ממונפת
    net_leveraged_yield: float  # תשואה נטו ממונפת
```

### 5. `AppreciationMetrics` (Dataclass)
**Calculated appreciation values**

```python
@dataclass
class AppreciationMetrics:
    """Calculated appreciation metrics."""
    
    property_appreciation: float  # עליית ערך הנכס
    urban_renewal_appreciation: float  # עליית ערך פינוי בינוי
    total_appreciation: float  # עליית ערך כוללת
    sale_value: float  # שווי במכירה
    total_return_rate: float  # שיעור תשואה כולל
    annualized_return: float  # תשואה שנתית
    leveraged_return: float  # תשואה ממונפת
    net_annual_return: float  # תשואה שנתית נטו
```

### 6. `EarlyRepaymentMetrics` (Dataclass)
**Early repayment calculations**

```python
@dataclass
class EarlyRepaymentMetrics:
    """Early mortgage repayment metrics."""
    
    remaining_mortgage: float  # שארית משכנתא
    early_repayment_penalty: float  # עמלת פירעון מוקדם
    total_debt_to_bank: float  # סך חוב לבנק
    proceeds_minus_debt: float  # תקבול פחות חוב
    net_gain_property: float  # רווח נטו מהנכס
```

### 7. `PortfolioMetrics` (Dataclass)
**Alternative investment portfolio calculations**

```python
@dataclass
class PortfolioMetrics:
    """Alternative investment portfolio metrics."""
    
    cash_in_portfolio: float  # כסף בתיק השקעות
    portfolio_initial_growth: float  # צמיחת סכום ראשוני
    monthly_deposits: float  # הפקדות חודשיות
    accumulated_deposits: float  # צבירה מהפקדות
    total_portfolio_value: float  # שווי תיק כולל
    portfolio_after_tax: float  # אחרי מס רווח הון
    net_portfolio_profit: float  # רווח נטו מתיק
```

### 8. `ScenarioResult` (Dataclass)
**Complete scenario calculation result**

```python
@dataclass
class ScenarioResult:
    """Complete results from scenario calculation."""
    
    inputs: ScenarioInputs
    loan_metrics: LoanMetrics
    cash_flow_metrics: CashFlowMetrics
    appreciation_metrics: AppreciationMetrics
    early_repayment_metrics: EarlyRepaymentMetrics
    portfolio_metrics: PortfolioMetrics
    
    # Final summary
    total_value_at_sale: float  # שווי כולל ביום המכירה
    total_profit: float  # רווח כולל
    annual_return: float  # תשואה שנתית
    
    # Validation
    is_valid: bool
    validation_errors: List[str]
```

### 9. `ScenarioCalculator` (Main Class)
**Main calculator orchestrating all calculations**

```python
class ScenarioCalculator:
    """Main calculator for investment scenario analysis."""
    
    def __init__(
        self,
        inputs: ScenarioInputs,
        restrictions: Optional[InvestmentRestrictions] = None
    ):
        self.inputs = inputs
        self.restrictions = restrictions or InvestmentRestrictions()
    
    def calculate_loan_metrics(self) -> LoanMetrics:
        """Calculate all loan-related metrics."""
        ...
    
    def calculate_cash_flow(self) -> CashFlowMetrics:
        """Calculate cash flow metrics."""
        ...
    
    def calculate_appreciation(self) -> AppreciationMetrics:
        """Calculate appreciation and return metrics."""
        ...
    
    def calculate_early_repayment(self) -> EarlyRepaymentMetrics:
        """Calculate early repayment scenarios."""
        ...
    
    def calculate_portfolio(self) -> PortfolioMetrics:
        """Calculate alternative investment portfolio."""
        ...
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate inputs against restrictions."""
        ...
    
    def calculate(self) -> ScenarioResult:
        """Run all calculations and return complete result."""
        ...
```

---

## Key Financial Formulas

### PMT (Mortgage Payment)
```python
def calculate_pmt(rate: float, nper: int, pv: float) -> float:
    """Calculate monthly payment (Excel PMT function)."""
    if rate == 0:
        return pv / nper
    monthly_rate = rate / 12
    return pv * (monthly_rate * (1 + monthly_rate)**nper) / ((1 + monthly_rate)**nper - 1)
```

### FV (Future Value)
```python
def calculate_fv(rate: float, nper: int, pmt: float, pv: float = 0) -> float:
    """Calculate future value (Excel FV function)."""
    if rate == 0:
        return -(pv + pmt * nper)
    return -(pv * (1 + rate)**nper + pmt * ((1 + rate)**nper - 1) / rate)
```

### PV (Present Value)
```python
def calculate_pv(rate: float, nper: int, pmt: float) -> float:
    """Calculate present value (Excel PV function)."""
    if rate == 0:
        return -pmt * nper
    return -pmt * (1 - (1 + rate)**(-nper)) / rate
```

### Compound Growth
```python
def calculate_compound_growth(principal: float, rate: float, years: float) -> float:
    """Calculate compound growth: principal * ((1 + rate)^years - 1)."""
    return principal * (((1 + rate) ** years) - 1)
```

---

## Logic Issues / Improvements Identified

1. **Urban Renewal Value (Row 27):**
   - Currently references Regression sheet (hard dependency)
   - Should be a configurable input with cap at 400,000
   - Consider making it optional

2. **Tax Calculations:**
   - Capital gains tax (25%) is applied inconsistently
   - Should have clear rules for when tax applies
   - Consider adding tax deduction options

3. **Required Income (Row 15):**
   - Uses fixed 30% rule
   - Should be configurable restriction
   - Should account for other debts

4. **Missing Operating Expenses:**
   - Property taxes
   - Insurance
   - Maintenance (1-2% of property value annually)
   - Property management fees
   - Vacancy rate (5-10%)
   - **Recommendation:** Add optional operating expenses input

5. **Portfolio vs Real Estate Comparison:**
   - Excel compares both strategies well
   - Should output clear comparison metrics
   - Consider adding: which strategy is better?

6. **Early Repayment Penalty:**
   - Complex PV-based calculation
   - Should document assumptions clearly
   - May vary by bank/country

7. **Inflation Not Modeled:**
   - Returns are nominal, not real
   - Consider adding inflation-adjusted returns

---

## File Structure

```
analyzer/
├── __init__.py
├── models.py          # All dataclasses (ScenarioInputs, Metrics, etc.)
├── calculator.py      # ScenarioCalculator class
├── financial.py       # Financial functions (PMT, FV, PV, etc.)
├── validators.py      # Validation logic
└── formatters.py      # Output formatting (optional)

tests/
└── test_analyzer/
    ├── __init__.py
    ├── test_models.py
    ├── test_calculator.py
    ├── test_financial.py
    └── test_validators.py
```

---

## Next Steps

1. [ ] Create `analyzer/models.py` with all dataclasses
2. [ ] Create `analyzer/financial.py` with PMT, FV, PV functions
3. [ ] Create `analyzer/calculator.py` with ScenarioCalculator
4. [ ] Create `analyzer/validators.py` with validation logic
5. [ ] Write unit tests for each module
6. [ ] Test with Excel values to verify accuracy
