# Phase 2: Scenario Calculator - Design Document

## Overview

The Scenario Calculator models a single real estate investment scenario, calculating financial metrics including cash flow, ROI, NPV, and IRR based on user inputs and assumptions.

## Class Structure Design

### 1. `InvestmentAssumptions` (Dataclass)
**Purpose:** Holds all assumptions and parameters for the investment scenario

```python
@dataclass
class InvestmentAssumptions:
    """Investment scenario assumptions and parameters."""
    
    # Loan Parameters
    loan_term_years: float  # Loan duration in years
    interest_rate_annual: float  # Annual interest rate (as decimal, e.g., 0.048 for 4.8%)
    
    # Property Parameters  
    property_price: float  # Purchase price of property
    down_payment_amount: float  # Down payment amount
    additional_purchase_costs: float  # Closing costs, fees, etc.
    additional_investment_costs: float  # Renovation, improvements (max 400,000)
    
    # Income Parameters
    monthly_rental_income: float  # Expected monthly rental income
    
    # Appreciation Parameters
    annual_appreciation_rate: float  # Expected annual property appreciation (as decimal, e.g., 0.04 for 4%)
    
    # Restrictions/Constraints
    max_mortgage_to_income_ratio: float = 0.3  # Max mortgage payment as % of income (30% rule)
    max_additional_costs: float = 400000.0  # Maximum additional costs cap
```

**Variable Descriptions:**
- `loan_term_years`: Duration of the mortgage loan in years
- `interest_rate_annual`: Annual interest rate expressed as decimal (0.048 = 4.8%)
- `property_price`: Total purchase price of the property
- `down_payment_amount`: Initial cash down payment
- `additional_purchase_costs`: One-time costs at purchase (legal fees, taxes, etc.)
- `additional_investment_costs`: Renovation/improvement costs (capped at max_additional_costs)
- `monthly_rental_income`: Expected monthly rental income
- `annual_appreciation_rate`: Expected annual property value appreciation rate
- `max_mortgage_to_income_ratio`: Maximum mortgage payment as percentage of income (default 30%)
- `max_additional_costs`: Maximum cap for additional investment costs

---

### 2. `UserFeatures` (Dataclass)
**Purpose:** Holds user-specific financial features and constraints

```python
@dataclass
class UserFeatures:
    """User financial features and constraints."""
    
    monthly_income: Optional[float] = None  # User's monthly income (for affordability check)
    max_down_payment: Optional[float] = None  # Maximum down payment user can afford
    max_monthly_payment: Optional[float] = None  # Maximum monthly payment user can afford
    
    # Risk Preferences
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    
    # Restrictions
    min_cash_flow: float = 0.0  # Minimum acceptable monthly cash flow
    min_roi_threshold: float = 0.0  # Minimum acceptable ROI
```

**Variable Descriptions:**
- `monthly_income`: User's monthly income (used for affordability calculations)
- `max_down_payment`: Maximum down payment the user can afford
- `max_monthly_payment`: Maximum monthly mortgage payment user can afford
- `risk_tolerance`: User's risk preference level
- `min_cash_flow`: Minimum acceptable monthly cash flow threshold
- `min_roi_threshold`: Minimum acceptable return on investment threshold

---

### 3. `InvestmentRestrictions` (Dataclass)
**Purpose:** Holds validation rules and restrictions

```python
@dataclass
class InvestmentRestrictions:
    """Investment validation rules and restrictions."""
    
    max_mortgage_to_income_ratio: float = 0.3  # 30% rule
    min_down_payment_percentage: float = 0.0  # Minimum down payment as % of price
    max_loan_to_value_ratio: float = 1.0  # Maximum LTV ratio
    require_positive_cash_flow: bool = False  # Require positive cash flow
    max_additional_costs: float = 400000.0  # Maximum additional costs
```

**Variable Descriptions:**
- `max_mortgage_to_income_ratio`: Maximum mortgage payment as percentage of income (default 30%)
- `min_down_payment_percentage`: Minimum down payment required as percentage of property price
- `max_loan_to_value_ratio`: Maximum loan-to-value ratio allowed
- `require_positive_cash_flow`: Whether positive cash flow is required
- `max_additional_costs`: Maximum allowed additional investment costs

---

### 4. `ScenarioCalculator` (Main Class)
**Purpose:** Main calculator class that performs all calculations

```python
class ScenarioCalculator:
    """Calculates investment scenario metrics."""
    
    def __init__(
        self,
        assumptions: InvestmentAssumptions,
        user_features: Optional[UserFeatures] = None,
        restrictions: Optional[InvestmentRestrictions] = None
    ):
        self.assumptions = assumptions
        self.user_features = user_features or UserFeatures()
        self.restrictions = restrictions or InvestmentRestrictions()
        
        # Calculated values (cached)
        self._loan_amount: Optional[float] = None
        self._down_payment_percentage: Optional[float] = None
        self._leverage_multiplier: Optional[float] = None
        self._monthly_mortgage_payment: Optional[float] = None
        self._total_interest_paid: Optional[float] = None
        self._monthly_cash_flow: Optional[float] = None
        self._annual_cash_flow: Optional[float] = None
        self._property_appreciation: Optional[float] = None
        self._total_return: Optional[float] = None
        self._annualized_return: Optional[float] = None
        self._leveraged_return: Optional[float] = None
    
    # Calculation Methods
    def calculate_loan_metrics(self) -> Dict[str, float]:
        """Calculate loan-related metrics."""
        pass
    
    def calculate_cash_flow(self) -> Dict[str, float]:
        """Calculate cash flow metrics."""
        pass
    
    def calculate_returns(self) -> Dict[str, float]:
        """Calculate return metrics."""
        pass
    
    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all metrics."""
        pass
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate assumptions against restrictions."""
        pass
```

---

## Calculation Methods

### Loan Calculations

```python
def calculate_loan_amount(self) -> float:
    """Loan amount = Property price - Down payment."""
    return self.assumptions.property_price - self.assumptions.down_payment_amount

def calculate_down_payment_percentage(self) -> float:
    """Down payment as percentage of property price."""
    return self.assumptions.down_payment_amount / self.assumptions.property_price

def calculate_leverage_multiplier(self) -> float:
    """Leverage multiplier = 1 / (1 - down_payment_percentage)."""
    dp_pct = self.calculate_down_payment_percentage()
    return 1.0 / (1.0 - dp_pct) if dp_pct < 1.0 else 1.0

def calculate_monthly_mortgage_payment(self) -> float:
    """Monthly mortgage payment using PMT formula."""
    # PMT(rate/12, 12*years, loan_amount)
    monthly_rate = self.assumptions.interest_rate_annual / 12
    num_payments = self.assumptions.loan_term_years * 12
    loan_amount = self.calculate_loan_amount()
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    return loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
           ((1 + monthly_rate)**num_payments - 1)
```

### Cash Flow Calculations

```python
def calculate_monthly_cash_flow(self) -> float:
    """Monthly cash flow = Rental income - Mortgage payment."""
    return self.assumptions.monthly_rental_income - self.calculate_monthly_mortgage_payment()

def calculate_annual_cash_flow(self) -> float:
    """Annual cash flow = Monthly cash flow * 12."""
    return self.calculate_monthly_cash_flow() * 12

def calculate_rental_yield(self) -> float:
    """Annual rental yield = (Monthly rent * 12) / Property price."""
    return (self.assumptions.monthly_rental_income * 12) / self.assumptions.property_price
```

### Return Calculations

```python
def calculate_property_appreciation(self) -> float:
    """Property appreciation over loan term."""
    rate = self.assumptions.annual_appreciation_rate
    years = self.assumptions.loan_term_years
    return self.assumptions.property_price * (((1 + rate) ** years) - 1)

def calculate_additional_costs_appreciation(self) -> float:
    """Additional costs appreciation over loan term."""
    rate = self.assumptions.annual_appreciation_rate
    years = self.assumptions.loan_term_years
    costs = min(self.assumptions.additional_investment_costs, 
                self.restrictions.max_additional_costs)
    return costs * (((1 + rate) ** years) - 1)

def calculate_total_property_value(self) -> float:
    """Total property value at end of term."""
    return (self.assumptions.property_price + 
            self.calculate_property_appreciation() + 
            self.calculate_additional_costs_appreciation())

def calculate_total_return(self) -> float:
    """Total return = (Final value / Initial investment) - 1."""
    initial_investment = (self.assumptions.down_payment_amount + 
                         self.assumptions.additional_purchase_costs +
                         min(self.assumptions.additional_investment_costs,
                             self.restrictions.max_additional_costs))
    final_value = self.calculate_total_property_value()
    return (final_value / initial_investment) - 1 if initial_investment > 0 else 0

def calculate_annualized_return(self) -> float:
    """Annualized return = ((1 + total_return)^(1/years)) - 1."""
    total_return = self.calculate_total_return()
    years = self.assumptions.loan_term_years
    return ((1 + total_return) ** (1 / years)) - 1

def calculate_leveraged_return(self) -> float:
    """Leveraged return = Annualized return * Leverage multiplier."""
    return self.calculate_annualized_return() * self.calculate_leverage_multiplier()
```

---

## Validation Logic

```python
def validate(self) -> Tuple[bool, List[str]]:
    """Validate assumptions against restrictions and user features."""
    errors = []
    
    # Check down payment percentage
    dp_pct = self.calculate_down_payment_percentage()
    if dp_pct < self.restrictions.min_down_payment_percentage:
        errors.append(f"Down payment {dp_pct:.1%} below minimum {self.restrictions.min_down_payment_percentage:.1%}")
    
    # Check loan-to-value ratio
    ltv = 1 - dp_pct
    if ltv > self.restrictions.max_loan_to_value_ratio:
        errors.append(f"Loan-to-value {ltv:.1%} exceeds maximum {self.restrictions.max_loan_to_value_ratio:.1%}")
    
    # Check mortgage-to-income ratio (if user income provided)
    if self.user_features.monthly_income:
        mortgage_payment = self.calculate_monthly_mortgage_payment()
        ratio = mortgage_payment / self.user_features.monthly_income
        if ratio > self.restrictions.max_mortgage_to_income_ratio:
            errors.append(f"Mortgage-to-income {ratio:.1%} exceeds maximum {self.restrictions.max_mortgage_to_income_ratio:.1%}")
    
    # Check positive cash flow requirement
    if self.restrictions.require_positive_cash_flow:
        cash_flow = self.calculate_monthly_cash_flow()
        if cash_flow < 0:
            errors.append(f"Negative cash flow: {cash_flow:.2f}")
    
    # Check minimum cash flow
    cash_flow = self.calculate_monthly_cash_flow()
    if cash_flow < self.user_features.min_cash_flow:
        errors.append(f"Cash flow {cash_flow:.2f} below minimum {self.user_features.min_cash_flow:.2f}")
    
    return len(errors) == 0, errors
```

---

## Identified Logic Issues / Improvements Needed

1. **Missing Operating Expenses:**
   - Property taxes
   - Insurance
   - Maintenance (1-2% of property value annually)
   - Property management fees (if applicable)
   - Vacancy rate (typically 5-10%)

2. **Tax Considerations:**
   - Mortgage interest deduction
   - Property tax deduction
   - Depreciation
   - Capital gains tax on sale

3. **Additional Costs Formula:**
   - Currently references Regression sheet (hard dependency)
   - Should be configurable or calculated independently

4. **Required Income Calculation:**
   - Uses fixed 0.3 (30% rule) - should be configurable
   - Should account for other debts

5. **Cash Flow Simplification:**
   - Only considers rent - mortgage
   - Should subtract operating expenses

6. **Appreciation Assumption:**
   - Assumes constant rate
   - No volatility or market risk consideration

7. **Interest Rate:**
   - Fixed rate only
   - No variable rate option

---

## Next Steps

1. Implement `InvestmentAssumptions` dataclass
2. Implement `UserFeatures` dataclass  
3. Implement `InvestmentRestrictions` dataclass
4. Implement `ScenarioCalculator` class with calculation methods
5. Add validation logic
6. Write unit tests
7. Consider enhancements (operating expenses, taxes, etc.)

