"""Main scenario calculator.

This module contains the ScenarioCalculator class that orchestrates
all investment calculations.
"""

from typing import List, Optional, Tuple

from mortgage_return_scenario_calculator.models import (
    InvestmentAssumptions,
    ScenarioInputs,
    InvestmentRestrictions,
    LoanMetrics,
    CashFlowMetrics,
    AppreciationMetrics,
    EarlyRepaymentMetrics,
    PortfolioMetrics,
    ScenarioResult,
)
from mortgage_return_scenario_calculator.financial import (
    calculate_pmt,
    calculate_fv,
    calculate_pv,
    calculate_compound_growth,
    calculate_compound_value,
    calculate_annualized_return,
)


class ScenarioCalculator:
    """Main calculator for investment scenario analysis.
    
    Orchestrates all calculations for comparing real estate investment
    with alternative portfolio investment.
    
    Attributes:
        inputs: Property-specific scenario inputs.
        assumptions: Market assumptions (uses defaults if not provided).
        restrictions: Investment restrictions for validation.
        monthly_rent: Calculated monthly rent based on rental yield.
    
    Example:
        >>> from mortgage_return_scenario_calculator import (
        ...     ScenarioCalculator, ScenarioInputs, ConfigGenerator
        ... )
        >>> 
        >>> inputs = ScenarioInputs(
        ...     property_price=2_650_000,
        ...     down_payment=1_350_000,
        ...     available_cash=2_650_000,
        ...     monthly_available=10_000,
        ...     mortgage_term_years=20,
        ...     years_until_sale=15,
        ... )
        >>> 
        >>> calculator = ScenarioCalculator(inputs)
        >>> result = calculator.calculate()
        >>> print(f"Annual Return: {result.annual_return:.2%}")
    """
    
    def __init__(
        self,
        inputs: ScenarioInputs,
        assumptions: Optional[InvestmentAssumptions] = None,
        restrictions: Optional[InvestmentRestrictions] = None,
    ):
        """Initialize the calculator.
        
        Args:
            inputs: Property-specific scenario inputs (required).
            assumptions: Market assumptions (uses defaults if not provided).
            restrictions: Investment restrictions (uses defaults if not provided).
        """
        self.inputs = inputs
        self.assumptions = assumptions or InvestmentAssumptions()
        self.restrictions = restrictions or InvestmentRestrictions()
        
        # Calculate derived values
        self.monthly_rent = inputs.calculate_monthly_rent(self.assumptions.rental_yield)
    
    def calculate_loan_metrics(self) -> LoanMetrics:
        """Calculate all loan-related metrics.
        
        Returns:
            LoanMetrics with all calculated values.
        """
        loan_amount = self.inputs.calculate_mortgage_amount()
        
        # Handle case where there's no loan (full cash purchase)
        if loan_amount <= 0:
            return LoanMetrics(
                loan_amount=0,
                leverage_ratio=0,
                equity_ratio=1.0,
                leverage_multiplier=1.0,
                monthly_payment=0,
                total_payments=0,
                total_interest=0,
                avg_monthly_interest=0,
                mortgage_to_income_ratio=0,
            )
        
        leverage_ratio = loan_amount / self.inputs.property_price
        equity_ratio = 1 - leverage_ratio
        leverage_multiplier = 1 / equity_ratio if equity_ratio > 0 else float('inf')
        
        # Calculate mortgage payment
        num_payments = self.inputs.mortgage_term_years * 12
        monthly_payment = calculate_pmt(
            self.assumptions.mortgage_rate,
            num_payments,
            loan_amount
        )
        
        total_payments = monthly_payment * num_payments
        total_interest = total_payments - loan_amount
        avg_monthly_interest = total_interest / num_payments if num_payments > 0 else 0
        
        # Calculate mortgage-to-income ratio using actual income
        mortgage_to_income_ratio = (
            monthly_payment / self.inputs.monthly_income 
            if self.inputs.monthly_income > 0 else 0
        )
        
        return LoanMetrics(
            loan_amount=loan_amount,
            leverage_ratio=leverage_ratio,
            equity_ratio=equity_ratio,
            leverage_multiplier=leverage_multiplier,
            monthly_payment=monthly_payment,
            total_payments=total_payments,
            total_interest=total_interest,
            avg_monthly_interest=avg_monthly_interest,
            mortgage_to_income_ratio=mortgage_to_income_ratio,
        )
    
    def calculate_cash_flow(self, loan_metrics: LoanMetrics) -> CashFlowMetrics:
        """Calculate cash flow metrics.
        
        Args:
            loan_metrics: Previously calculated loan metrics.
        
        Returns:
            CashFlowMetrics with all calculated values.
        """
        rental_yield = (self.monthly_rent * 12) / self.inputs.property_price
        monthly_net_cash_flow = self.monthly_rent - loan_metrics.monthly_payment
        monthly_interest_flow = self.monthly_rent - loan_metrics.avg_monthly_interest
        
        # Average principal payment (negative because it reduces debt)
        if loan_metrics.loan_amount > 0 and self.inputs.mortgage_term_years > 0:
            avg_principal_payment = -loan_metrics.loan_amount / (12 * self.inputs.mortgage_term_years)
        else:
            avg_principal_payment = 0
        
        leveraged_rental_yield = rental_yield * loan_metrics.leverage_multiplier
        
        # Net leveraged yield (subtract interest rate if there's a loan)
        if loan_metrics.loan_amount > 0:
            net_leveraged_yield = leveraged_rental_yield - self.assumptions.mortgage_rate
        else:
            net_leveraged_yield = leveraged_rental_yield
        
        return CashFlowMetrics(
            monthly_rent=self.monthly_rent,
            rental_yield=rental_yield,
            monthly_net_cash_flow=monthly_net_cash_flow,
            monthly_interest_flow=monthly_interest_flow,
            avg_principal_payment=avg_principal_payment,
            leveraged_rental_yield=leveraged_rental_yield,
            net_leveraged_yield=net_leveraged_yield,
        )
    
    def calculate_appreciation(self, loan_metrics: LoanMetrics, cash_flow_metrics: CashFlowMetrics) -> AppreciationMetrics:
        """Calculate appreciation and return metrics.
        
        Args:
            loan_metrics: Previously calculated loan metrics.
            cash_flow_metrics: Previously calculated cash flow metrics.
        
        Returns:
            AppreciationMetrics with all calculated values.
        """
        years = self.inputs.years_until_sale
        
        # Property appreciation
        property_appreciation = calculate_compound_growth(
            self.inputs.property_price,
            self.assumptions.appreciation_rate,
            years
        )
        
        # Urban renewal appreciation
        urban_renewal_appreciation = calculate_compound_growth(
            self.inputs.urban_renewal_value,
            self.assumptions.appreciation_rate,
            years
        )
        
        # Total appreciation includes urban renewal value plus both appreciations
        total_appreciation = (
            self.inputs.urban_renewal_value +
            property_appreciation +
            urban_renewal_appreciation
        )
        
        sale_value = self.inputs.property_price + total_appreciation
        
        # Total return rate
        total_return_rate = (sale_value / self.inputs.property_price) - 1
        
        # Annualized return
        annualized_return = calculate_annualized_return(total_return_rate, years)
        
        # Leveraged return
        leveraged_return = annualized_return * loan_metrics.leverage_multiplier
        
        # Net annual return (add rental yield, subtract financing cost)
        net_annual_return = (
            leveraged_return +
            cash_flow_metrics.leveraged_rental_yield -
            self.assumptions.mortgage_rate
        ) if loan_metrics.loan_amount > 0 else (
            leveraged_return + cash_flow_metrics.leveraged_rental_yield
        )
        
        return AppreciationMetrics(
            property_appreciation=property_appreciation,
            urban_renewal_appreciation=urban_renewal_appreciation,
            total_appreciation=total_appreciation,
            sale_value=sale_value,
            total_return_rate=total_return_rate,
            annualized_return=annualized_return,
            leveraged_return=leveraged_return,
            net_annual_return=net_annual_return,
        )
    
    def calculate_early_repayment(
        self,
        loan_metrics: LoanMetrics,
        appreciation_metrics: AppreciationMetrics
    ) -> EarlyRepaymentMetrics:
        """Calculate early mortgage repayment metrics.
        
        Args:
            loan_metrics: Previously calculated loan metrics.
            appreciation_metrics: Previously calculated appreciation metrics.
        
        Returns:
            EarlyRepaymentMetrics with all calculated values.
        """
        years_until_sale = self.inputs.years_until_sale
        mortgage_term = self.inputs.mortgage_term_years
        
        # If no loan or selling after mortgage is paid off
        if loan_metrics.loan_amount <= 0 or years_until_sale >= mortgage_term:
            return EarlyRepaymentMetrics(
                remaining_mortgage=0,
                early_repayment_penalty=0,
                total_debt_to_bank=0,
                proceeds_minus_debt=appreciation_metrics.sale_value,
                net_gain_property=appreciation_metrics.sale_value - self.inputs.down_payment,
            )
        
        # Remaining mortgage (simplified linear calculation)
        remaining_ratio = (mortgage_term - years_until_sale) / mortgage_term
        remaining_mortgage = remaining_ratio * loan_metrics.total_payments
        
        # Early repayment penalty calculation
        # PV at current rate minus PV at early repayment rate
        remaining_months = (mortgage_term - years_until_sale) * 12
        pv_current = calculate_pv(
            self.assumptions.mortgage_rate / 12,
            remaining_months,
            loan_metrics.monthly_payment
        )
        pv_new = calculate_pv(
            self.assumptions.early_repayment_rate / 12,
            remaining_months,
            loan_metrics.monthly_payment
        )
        early_repayment_penalty = max(0, pv_current - pv_new)
        
        total_debt_to_bank = remaining_mortgage + early_repayment_penalty
        proceeds_minus_debt = appreciation_metrics.sale_value - total_debt_to_bank
        net_gain_property = proceeds_minus_debt - self.inputs.down_payment
        
        return EarlyRepaymentMetrics(
            remaining_mortgage=remaining_mortgage,
            early_repayment_penalty=early_repayment_penalty,
            total_debt_to_bank=total_debt_to_bank,
            proceeds_minus_debt=proceeds_minus_debt,
            net_gain_property=net_gain_property,
        )
    
    def calculate_portfolio(self, cash_flow_metrics: CashFlowMetrics) -> PortfolioMetrics:
        """Calculate alternative investment portfolio metrics.
        
        Args:
            cash_flow_metrics: Previously calculated cash flow metrics.
        
        Returns:
            PortfolioMetrics with all calculated values.
        """
        years = self.inputs.years_until_sale
        months = years * 12
        monthly_rate = self.assumptions.portfolio_return_rate / 12
        
        # Cash invested in portfolio (what wasn't used for down payment)
        cash_in_portfolio = self.inputs.available_cash - self.inputs.down_payment
        
        # Growth of initial investment
        portfolio_initial_growth = calculate_compound_value(
            cash_in_portfolio,
            self.assumptions.portfolio_return_rate,
            years
        )
        
        # Monthly deposits (available + cash flow from property)
        monthly_deposits = self.inputs.monthly_available + cash_flow_metrics.monthly_net_cash_flow
        
        # Value accumulated from monthly deposits
        accumulated_deposits = calculate_fv(monthly_rate, months, -monthly_deposits)
        
        # Total portfolio value
        total_portfolio_value = portfolio_initial_growth + accumulated_deposits
        
        # After capital gains tax (25% on gains)
        deposit_gains = accumulated_deposits - (monthly_deposits * months)
        initial_gains = portfolio_initial_growth - cash_in_portfolio
        total_gains = deposit_gains + initial_gains
        tax = total_gains * self.assumptions.capital_gains_tax_rate if total_gains > 0 else 0
        portfolio_after_tax = total_portfolio_value - tax
        
        # Net profit
        total_contributions = cash_in_portfolio + (monthly_deposits * months)
        net_portfolio_profit = portfolio_after_tax - total_contributions
        
        return PortfolioMetrics(
            cash_in_portfolio=cash_in_portfolio,
            portfolio_initial_growth=portfolio_initial_growth,
            monthly_deposits=monthly_deposits,
            accumulated_deposits=accumulated_deposits,
            total_portfolio_value=total_portfolio_value,
            portfolio_after_tax=portfolio_after_tax,
            net_portfolio_profit=net_portfolio_profit,
        )
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate inputs against restrictions.
        
        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []
        
        # Calculate necessary metrics for validation
        loan_metrics = self.calculate_loan_metrics()
        cash_flow_metrics = self.calculate_cash_flow(loan_metrics)
        
        # Check down payment percentage
        down_payment_pct = self.inputs.down_payment / self.inputs.property_price
        if down_payment_pct < self.restrictions.min_down_payment_percentage:
            errors.append(
                f"Down payment {down_payment_pct:.1%} is below minimum "
                f"{self.restrictions.min_down_payment_percentage:.1%}"
            )
        
        # Check loan-to-value ratio
        if loan_metrics.leverage_ratio > self.restrictions.max_loan_to_value:
            errors.append(
                f"Loan-to-value {loan_metrics.leverage_ratio:.1%} exceeds maximum "
                f"{self.restrictions.max_loan_to_value:.1%}"
            )
        
        # Check mortgage percentage of property value
        mortgage_pct = loan_metrics.loan_amount / self.inputs.property_price
        if mortgage_pct > self.restrictions.max_mortgage_percentage:
            errors.append(
                f"Mortgage {mortgage_pct:.1%} of property value exceeds maximum "
                f"{self.restrictions.max_mortgage_percentage:.1%}"
            )
        
        # Check mortgage-to-income ratio
        if loan_metrics.mortgage_to_income_ratio > self.restrictions.max_mortgage_to_income_ratio:
            errors.append(
                f"Mortgage payment {loan_metrics.mortgage_to_income_ratio:.1%} of income "
                f"exceeds maximum {self.restrictions.max_mortgage_to_income_ratio:.1%} "
                f"(payment: {loan_metrics.monthly_payment:,.0f}, income: {self.inputs.monthly_income:,.0f})"
            )
        
        # Check positive cash flow requirement
        if self.restrictions.require_positive_cash_flow:
            if cash_flow_metrics.monthly_net_cash_flow < 0:
                errors.append(
                    f"Negative cash flow: {cash_flow_metrics.monthly_net_cash_flow:,.0f}/month"
                )
        
        # Check urban renewal cap
        if self.inputs.urban_renewal_value > self.restrictions.max_urban_renewal_value:
            errors.append(
                f"Urban renewal value {self.inputs.urban_renewal_value:,.0f} exceeds maximum "
                f"{self.restrictions.max_urban_renewal_value:,.0f}"
            )
        
        return len(errors) == 0, errors
    
    def calculate(self) -> ScenarioResult:
        """Run all calculations and return complete result.
        
        Returns:
            ScenarioResult with all calculated metrics.
        """
        # Calculate all metrics
        loan_metrics = self.calculate_loan_metrics()
        cash_flow_metrics = self.calculate_cash_flow(loan_metrics)
        appreciation_metrics = self.calculate_appreciation(loan_metrics, cash_flow_metrics)
        early_repayment_metrics = self.calculate_early_repayment(loan_metrics, appreciation_metrics)
        portfolio_metrics = self.calculate_portfolio(cash_flow_metrics)
        
        # Validate
        is_valid, validation_errors = self.validate()
        
        # Calculate final summary values
        # Total value = property proceeds + portfolio value (after tax)
        total_value_at_sale = (
            early_repayment_metrics.proceeds_minus_debt +
            portfolio_metrics.portfolio_after_tax
        )
        
        # Total profit
        total_profit = (
            early_repayment_metrics.net_gain_property +
            portfolio_metrics.net_portfolio_profit
        )
        
        # Annual return
        years = self.inputs.years_until_sale
        if self.inputs.available_cash > 0 and years > 0:
            annual_return = (total_value_at_sale / self.inputs.available_cash) ** (1 / years) - 1
        else:
            annual_return = 0
        
        return ScenarioResult(
            inputs=self.inputs,
            assumptions=self.assumptions,
            loan_metrics=loan_metrics,
            cash_flow_metrics=cash_flow_metrics,
            appreciation_metrics=appreciation_metrics,
            early_repayment_metrics=early_repayment_metrics,
            portfolio_metrics=portfolio_metrics,
            total_value_at_sale=total_value_at_sale,
            total_profit=total_profit,
            annual_return=annual_return,
            is_valid=is_valid,
            validation_errors=validation_errors,
        )

