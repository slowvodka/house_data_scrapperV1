"""Tests for the main ScenarioCalculator.

Run only calculator tests with: pytest -m calculator
"""
import pytest

from mortgage_return_scenario_calculator import (
    ScenarioCalculator,
    ScenarioInputs,
    InvestmentAssumptions,
    InvestmentRestrictions,
)


pytestmark = pytest.mark.calculator


class TestScenarioCalculatorInit:
    """Tests for ScenarioCalculator initialization."""
    
    def test_basic_initialization(self):
        """Test basic calculator initialization."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        
        calculator = ScenarioCalculator(inputs)
        
        assert calculator.inputs == inputs
        assert isinstance(calculator.assumptions, InvestmentAssumptions)
        assert isinstance(calculator.restrictions, InvestmentRestrictions)
    
    def test_custom_assumptions(self):
        """Test calculator with custom assumptions."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions(
            rental_yield=0.03,
            mortgage_rate=0.05,
        )
        
        calculator = ScenarioCalculator(inputs, assumptions)
        
        assert calculator.assumptions.rental_yield == 0.03
        assert calculator.assumptions.mortgage_rate == 0.05
    
    def test_monthly_rent_calculation_on_init(self):
        """Test monthly rent is calculated on initialization."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions(rental_yield=0.03)  # 3%
        
        calculator = ScenarioCalculator(inputs, assumptions)
        
        expected_rent = 2_000_000 * 0.03 / 12  # 5,000
        assert abs(calculator.monthly_rent - expected_rent) < 0.01


class TestLoanMetricsCalculation:
    """Tests for loan metrics calculation."""
    
    def test_basic_loan_metrics(self):
        """Test basic loan metrics calculation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        calculator = ScenarioCalculator(inputs)
        metrics = calculator.calculate_loan_metrics()
        
        assert metrics.loan_amount == 1_000_000
        assert metrics.leverage_ratio == 0.5
        assert metrics.equity_ratio == 0.5
        assert metrics.leverage_multiplier == 2.0
        assert metrics.monthly_payment > 0
        assert metrics.total_payments > metrics.loan_amount  # Interest
        assert metrics.total_interest > 0
    
    def test_full_cash_purchase(self):
        """Test loan metrics for full cash purchase (no loan)."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=2_000_000,  # Full cash
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        calculator = ScenarioCalculator(inputs)
        metrics = calculator.calculate_loan_metrics()
        
        assert metrics.loan_amount == 0
        assert metrics.leverage_ratio == 0
        assert metrics.equity_ratio == 1.0
        assert metrics.leverage_multiplier == 1.0
        assert metrics.monthly_payment == 0
        assert metrics.total_interest == 0
    
    def test_high_leverage_loan(self):
        """Test loan metrics with high leverage (low down payment)."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=500_000,  # 25% down
            available_cash=2_000_000,
            monthly_income=50_000,
            monthly_available=10_000,
            mortgage_term_years=20,
            years_until_sale=15,
        )
        calculator = ScenarioCalculator(inputs)
        metrics = calculator.calculate_loan_metrics()
        
        assert metrics.loan_amount == 1_500_000
        assert metrics.leverage_ratio == 0.75
        assert metrics.equity_ratio == 0.25
        assert metrics.leverage_multiplier == 4.0


class TestCashFlowCalculation:
    """Tests for cash flow calculation."""
    
    def test_negative_cash_flow(self):
        """Test scenario with negative monthly cash flow."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions(
            rental_yield=0.025,  # 2.5% - low rent
            mortgage_rate=0.048,
        )
        calculator = ScenarioCalculator(inputs, assumptions)
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        
        # With 2.5% yield on 2M = 4,167/month rent
        # But mortgage payment is higher, so negative cash flow
        assert cash_flow.monthly_net_cash_flow < 0
    
    def test_positive_cash_flow(self):
        """Test scenario with positive monthly cash flow."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_800_000,  # 90% down = low mortgage payment
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions(
            rental_yield=0.05,  # 5% - high rent
            mortgage_rate=0.048,
        )
        calculator = ScenarioCalculator(inputs, assumptions)
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        
        # High rent + low mortgage = positive cash flow
        assert cash_flow.monthly_net_cash_flow > 0


class TestAppreciationCalculation:
    """Tests for appreciation calculation."""
    
    def test_property_appreciation(self):
        """Test property appreciation calculation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions(appreciation_rate=0.04)
        calculator = ScenarioCalculator(inputs, assumptions)
        
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        appreciation = calculator.calculate_appreciation(loan_metrics, cash_flow)
        
        # Property should appreciate at 4% annually over 10 years
        expected_appreciation = 2_000_000 * ((1.04 ** 10) - 1)
        assert abs(appreciation.property_appreciation - expected_appreciation) < 1
    
    def test_urban_renewal_appreciation(self):
        """Test urban renewal value appreciation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
            urban_renewal_value=400_000,
        )
        assumptions = InvestmentAssumptions(appreciation_rate=0.04)
        calculator = ScenarioCalculator(inputs, assumptions)
        
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        appreciation = calculator.calculate_appreciation(loan_metrics, cash_flow)
        
        # Urban renewal should also appreciate
        assert appreciation.urban_renewal_appreciation > 0
        # Total should include base urban renewal + appreciation
        assert appreciation.total_appreciation > appreciation.property_appreciation


class TestEarlyRepaymentCalculation:
    """Tests for early repayment calculation."""
    
    def test_no_early_repayment(self):
        """Test when sale is after mortgage term (no early repayment)."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,  # Equal to mortgage term
        )
        calculator = ScenarioCalculator(inputs)
        
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        appreciation = calculator.calculate_appreciation(loan_metrics, cash_flow)
        early_repay = calculator.calculate_early_repayment(loan_metrics, appreciation)
        
        assert early_repay.remaining_mortgage == 0
        assert early_repay.early_repayment_penalty == 0
        assert early_repay.total_debt_to_bank == 0
    
    def test_with_early_repayment(self):
        """Test when sale is before mortgage term ends."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=20,
            years_until_sale=10,  # Early sale
        )
        calculator = ScenarioCalculator(inputs)
        
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        appreciation = calculator.calculate_appreciation(loan_metrics, cash_flow)
        early_repay = calculator.calculate_early_repayment(loan_metrics, appreciation)
        
        assert early_repay.remaining_mortgage > 0
        assert early_repay.total_debt_to_bank > 0


class TestPortfolioCalculation:
    """Tests for portfolio calculation."""
    
    def test_basic_portfolio(self):
        """Test basic portfolio calculation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        calculator = ScenarioCalculator(inputs)
        
        loan_metrics = calculator.calculate_loan_metrics()
        cash_flow = calculator.calculate_cash_flow(loan_metrics)
        portfolio = calculator.calculate_portfolio(cash_flow)
        
        # Cash in portfolio = available - down payment
        assert portfolio.cash_in_portfolio == 1_000_000
        # Should grow over time
        assert portfolio.portfolio_initial_growth > portfolio.cash_in_portfolio
        assert portfolio.total_portfolio_value > 0


class TestValidation:
    """Tests for scenario validation."""
    
    def test_valid_scenario(self):
        """Test validation passes for valid scenario."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,  # 50% down
            available_cash=2_000_000,
            monthly_income=50_000,  # High income = valid
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        calculator = ScenarioCalculator(inputs)
        
        is_valid, errors = calculator.validate()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_exceeds_max_ltv(self):
        """Test validation fails when LTV exceeds maximum."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=200_000,  # Only 10% down = 90% LTV
            available_cash=2_000_000,
            monthly_income=100_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        restrictions = InvestmentRestrictions(max_loan_to_value=0.75)
        calculator = ScenarioCalculator(inputs, restrictions=restrictions)
        
        is_valid, errors = calculator.validate()
        
        assert is_valid is False
        assert any("Loan-to-value" in e for e in errors)
    
    def test_requires_positive_cash_flow(self):
        """Test validation fails when positive cash flow required but negative."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=50_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions(rental_yield=0.02)  # Low rent
        restrictions = InvestmentRestrictions(require_positive_cash_flow=True)
        calculator = ScenarioCalculator(inputs, assumptions, restrictions)
        
        is_valid, errors = calculator.validate()
        
        assert is_valid is False
        assert any("Negative cash flow" in e for e in errors)


class TestFullCalculation:
    """Tests for complete scenario calculation."""
    
    def test_full_calculation_returns_result(self):
        """Test full calculation returns ScenarioResult."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=50_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        calculator = ScenarioCalculator(inputs)
        
        result = calculator.calculate()
        
        assert result.inputs == inputs
        assert result.loan_metrics is not None
        assert result.cash_flow_metrics is not None
        assert result.appreciation_metrics is not None
        assert result.early_repayment_metrics is not None
        assert result.portfolio_metrics is not None
        assert result.total_value_at_sale > 0
        assert result.total_profit != 0  # Could be positive or negative
    
    def test_specific_scenario(self):
        """Test specific scenario matching user requirements."""
        # 2M house, 1M mortgage, 10 years
        # monthly_income=36_000 ensures payment is under 30% (payment ~10,509)
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=36_000,  # High enough to pass 30% rule
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
            urban_renewal_value=400_000,
        )
        assumptions = InvestmentAssumptions(
            rental_yield=0.025,  # 2.5%
            mortgage_rate=0.048,  # 4.8%
            appreciation_rate=0.04,  # 4%
        )
        calculator = ScenarioCalculator(inputs, assumptions)
        result = calculator.calculate()
        
        # Verify loan metrics
        assert result.loan_metrics.loan_amount == 1_000_000
        assert result.loan_metrics.leverage_ratio == 0.5
        
        # Verify monthly rent calculation
        expected_rent = 2_000_000 * 0.025 / 12  # ~4,167
        assert abs(result.cash_flow_metrics.monthly_rent - expected_rent) < 1
        
        # Verify cash flow is negative (low rent vs mortgage payment)
        assert result.cash_flow_metrics.monthly_net_cash_flow < 0
        
        # Verify appreciation
        assert result.appreciation_metrics.property_appreciation > 0
        assert result.appreciation_metrics.urban_renewal_appreciation > 0
        
        # Verify result is valid
        assert result.is_valid is True
        
        # Verify total profit is positive (appreciation should offset negative cash flow)
        assert result.total_profit > 0
    
    def test_full_cash_scenario(self):
        """Test scenario with full cash purchase (no mortgage)."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=2_000_000,  # Full cash
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        calculator = ScenarioCalculator(inputs)
        result = calculator.calculate()
        
        # No loan
        assert result.loan_metrics.loan_amount == 0
        assert result.loan_metrics.monthly_payment == 0
        
        # Positive cash flow (just rent, no mortgage)
        assert result.cash_flow_metrics.monthly_net_cash_flow > 0
        
        # No portfolio investment (all cash in property)
        assert result.portfolio_metrics.cash_in_portfolio == 0

