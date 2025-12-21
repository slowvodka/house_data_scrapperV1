"""Data models for the Scenario Calculator.

This module contains all dataclasses used in the investment scenario calculations.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class InvestmentAssumptions:
    """Market assumptions with default values.
    
    These are market/economic parameters that have sensible defaults
    but can be customized by the user.
    
    Attributes:
        rental_yield: Annual rental yield as decimal (default 2.8% = 0.028).
            Monthly rent is calculated as: property_price * rental_yield / 12
        mortgage_rate: Annual mortgage interest rate as decimal (default 4.8% = 0.048).
        appreciation_rate: Annual property appreciation rate as decimal (default 4% = 0.04).
        rent_increase_rate: Annual rent increase rate as decimal (default 3% = 0.03).
        portfolio_return_rate: Annual return for alternative investment (default 7% = 0.07).
        risk_free_rate: Risk-free rate for discounting (default 3% = 0.03).
        early_repayment_rate: Interest rate at early mortgage repayment (default 3.5% = 0.035).
        capital_gains_tax_rate: Capital gains tax rate as decimal (default 25% = 0.25).
    """
    
    # Rental assumptions
    rental_yield: float = 0.028  # 2.8% annual rental yield
    rent_increase_rate: float = 0.03  # 3% annual rent increase
    
    # Mortgage assumptions
    mortgage_rate: float = 0.048  # 4.8% annual interest rate
    early_repayment_rate: float = 0.035  # 3.5% rate at early repayment
    
    # Growth assumptions
    appreciation_rate: float = 0.04  # 4% annual property appreciation
    
    # Alternative investment assumptions
    portfolio_return_rate: float = 0.07  # 7% annual portfolio return
    
    # Other assumptions
    risk_free_rate: float = 0.03  # 3% risk-free rate
    capital_gains_tax_rate: float = 0.25  # 25% capital gains tax


@dataclass
class ScenarioInputs:
    """Property-specific inputs that must be provided by the user.
    
    These are the inputs specific to the property being analyzed.
    All monetary values should be in the same currency (e.g., ILS).
    
    Attributes:
        property_price: Purchase price of the property.
        down_payment: Equity/down payment amount.
        available_cash: Total cash available for investment.
        monthly_income: Monthly net income (for mortgage-to-income validation).
        monthly_available: Monthly amount available for investment/mortgage payments.
        mortgage_term_years: Duration of mortgage in years.
        years_until_sale: Number of years until property will be sold.
        urban_renewal_value: Optional added value from urban renewal (max 400,000).
        is_first_house: True if this is the buyer's first house (דירה יחידה),
            False if it's an additional property (דירה נוספת). Default True.
        improvement_costs: Costs of improvements made to property (deductible
            from capital gains tax). Default 0.0.
    """
    
    # Property details
    property_price: float
    
    # Investment capital
    down_payment: float
    available_cash: float
    
    # Income
    monthly_income: float  # Net monthly income for validation
    monthly_available: float  # Amount available for investment after expenses
    
    # Time parameters
    mortgage_term_years: int
    years_until_sale: int
    
    # Optional
    urban_renewal_value: float = 0.0
    
    # Tax-related fields
    is_first_house: bool = True  # True for first house (דירה יחידה), False for additional property
    improvement_costs: float = 0.0  # Costs of improvements (deductible from capital gains)
    
    def __post_init__(self) -> None:
        """Validate and cap values after initialization."""
        # Cap urban renewal value at 400,000
        self.urban_renewal_value = min(self.urban_renewal_value, 400_000)
        
        # Validate positive values
        if self.property_price <= 0:
            raise ValueError("property_price must be positive")
        if self.down_payment < 0:
            raise ValueError("down_payment cannot be negative")
        if self.available_cash < 0:
            raise ValueError("available_cash cannot be negative")
        if self.mortgage_term_years <= 0:
            raise ValueError("mortgage_term_years must be positive")
        if self.years_until_sale <= 0:
            raise ValueError("years_until_sale must be positive")
        if self.monthly_income <= 0:
            raise ValueError("monthly_income must be positive")
        if self.improvement_costs < 0:
            raise ValueError("improvement_costs cannot be negative")
    
    def calculate_monthly_rent(self, rental_yield: float) -> float:
        """Calculate monthly rent from property price and rental yield.
        
        Args:
            rental_yield: Annual rental yield as decimal (e.g., 0.028 for 2.8%).
        
        Returns:
            Monthly rental income.
        """
        return self.property_price * rental_yield / 12
    
    def calculate_mortgage_amount(self) -> float:
        """Calculate the mortgage amount (property price minus down payment).
        
        Returns:
            Mortgage amount.
        """
        return self.property_price - self.down_payment


@dataclass
class InvestmentRestrictions:
    """Investment validation rules and constraints.
    
    These define the boundaries for what is considered a valid investment scenario.
    
    Attributes:
        max_mortgage_to_income_ratio: Maximum mortgage payment as fraction of income (default 30%).
        min_down_payment_percentage: Minimum down payment as fraction of price (default 0%).
        max_loan_to_value: Maximum loan-to-value ratio (default 75%).
        max_mortgage_percentage: Maximum mortgage as percentage of property value (default 75%).
        max_urban_renewal_value: Maximum urban renewal value cap (default 400,000).
        require_positive_cash_flow: Whether positive monthly cash flow is required.
    """
    
    max_mortgage_to_income_ratio: float = 0.3  # 30% max
    min_down_payment_percentage: float = 0.0  # 0% minimum
    max_loan_to_value: float = 0.75  # 75% max LTV
    max_mortgage_percentage: float = 0.75  # 75% max mortgage of property value
    max_urban_renewal_value: float = 400_000
    require_positive_cash_flow: bool = False


@dataclass
class LoanMetrics:
    """Calculated loan-related metrics.
    
    Attributes:
        loan_amount: Total loan amount (property_price - down_payment).
        leverage_ratio: Loan as fraction of property price (loan / price).
        equity_ratio: Down payment as fraction of property price (1 - leverage_ratio).
        leverage_multiplier: Leverage effect multiplier (1 / equity_ratio).
        monthly_payment: Monthly mortgage payment.
        total_payments: Total mortgage payments over loan term.
        total_interest: Total interest paid over loan term.
        avg_monthly_interest: Average monthly interest payment.
        mortgage_to_income_ratio: Monthly payment as fraction of monthly income.
    """
    
    loan_amount: float
    leverage_ratio: float
    equity_ratio: float
    leverage_multiplier: float
    monthly_payment: float
    total_payments: float
    total_interest: float
    avg_monthly_interest: float
    mortgage_to_income_ratio: float


@dataclass
class CashFlowMetrics:
    """Calculated cash flow metrics.
    
    Attributes:
        monthly_rent: Monthly rental income.
        rental_yield: Annual rental yield (rent * 12 / price).
        monthly_net_cash_flow: Monthly cash flow (rent - mortgage payment).
        monthly_interest_flow: Monthly cash flow from interest perspective (rent - avg interest).
        avg_principal_payment: Average monthly principal payment.
        leveraged_rental_yield: Rental yield multiplied by leverage.
        net_leveraged_yield: Leveraged yield minus mortgage rate (if loan > 0).
    """
    
    monthly_rent: float
    rental_yield: float
    monthly_net_cash_flow: float
    monthly_interest_flow: float
    avg_principal_payment: float
    leveraged_rental_yield: float
    net_leveraged_yield: float


@dataclass
class AppreciationMetrics:
    """Calculated appreciation and return metrics.
    
    Attributes:
        property_appreciation: Property value increase over holding period.
        urban_renewal_appreciation: Urban renewal value increase over holding period.
        total_appreciation: Total appreciation (property + urban renewal).
        sale_value: Expected sale value (price + appreciation).
        total_return_rate: Total return as fraction ((sale / price) - 1).
        annualized_return: Annualized return rate.
        leveraged_return: Annualized return multiplied by leverage.
        net_annual_return: Net annual return after financing costs.
    """
    
    property_appreciation: float
    urban_renewal_appreciation: float
    total_appreciation: float
    sale_value: float
    total_return_rate: float
    annualized_return: float
    leveraged_return: float
    net_annual_return: float


@dataclass
class EarlyRepaymentMetrics:
    """Early mortgage repayment metrics.
    
    Attributes:
        remaining_mortgage: Remaining mortgage balance at sale.
        early_repayment_penalty: Penalty for early mortgage repayment.
        total_debt_to_bank: Total debt to bank at sale (remaining + penalty).
        proceeds_minus_debt: Sale proceeds minus bank debt.
        net_gain_property: Net gain from property (proceeds - debt - down payment).
    """
    
    remaining_mortgage: float
    early_repayment_penalty: float
    total_debt_to_bank: float
    proceeds_minus_debt: float
    net_gain_property: float


@dataclass
class TaxMetrics:
    """Tax-related calculations for the investment scenario.
    
    Attributes:
        purchase_tax: Purchase tax (מס רכישה) paid when buying property.
        purchase_tax_rate: Effective purchase tax rate.
        capital_gains: Capital gain from property sale.
        capital_gains_tax: Capital gains tax (מס שבח) paid when selling.
        total_taxes: Total taxes paid (purchase + capital gains).
        net_profit_after_taxes: Net profit after all taxes.
    """
    purchase_tax: float
    purchase_tax_rate: float
    capital_gains: float
    capital_gains_tax: float
    total_taxes: float
    net_profit_after_taxes: float


@dataclass
class PortfolioMetrics:
    """Alternative investment portfolio metrics.
    
    Calculates what would happen if the same money was invested
    in a portfolio instead of real estate.
    
    Attributes:
        cash_in_portfolio: Initial cash invested in portfolio (available - down payment).
        portfolio_initial_growth: Growth of initial investment.
        monthly_deposits: Monthly deposits to portfolio.
        accumulated_deposits: Value accumulated from monthly deposits.
        total_portfolio_value: Total portfolio value at sale time.
        portfolio_after_tax: Portfolio value after capital gains tax.
        net_portfolio_profit: Net profit from portfolio investment.
    """
    
    cash_in_portfolio: float
    portfolio_initial_growth: float
    monthly_deposits: float
    accumulated_deposits: float
    total_portfolio_value: float
    portfolio_after_tax: float
    net_portfolio_profit: float


@dataclass
class ScenarioResult:
    """Complete results from scenario calculation.
    
    Contains all calculated metrics and final summary values.
    
    Attributes:
        inputs: Original scenario inputs.
        assumptions: Investment assumptions used.
        loan_metrics: Calculated loan metrics.
        cash_flow_metrics: Calculated cash flow metrics.
        appreciation_metrics: Calculated appreciation metrics.
        early_repayment_metrics: Early repayment metrics.
        portfolio_metrics: Alternative investment metrics.
        tax_metrics: Tax-related calculations (purchase tax and capital gains tax).
        total_value_at_sale: Total value at time of sale.
        total_profit: Total profit from investment (after taxes).
        annual_return: Annualized return rate.
        is_valid: Whether the scenario passes all restrictions.
        validation_errors: List of validation error messages.
    """
    
    inputs: ScenarioInputs
    assumptions: InvestmentAssumptions
    loan_metrics: LoanMetrics
    cash_flow_metrics: CashFlowMetrics
    appreciation_metrics: AppreciationMetrics
    early_repayment_metrics: EarlyRepaymentMetrics
    portfolio_metrics: PortfolioMetrics
    tax_metrics: TaxMetrics
    
    # Final summary
    total_value_at_sale: float
    total_profit: float
    annual_return: float
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)

