"""Tests for data models.

Run only calculator tests with: pytest -m calculator
"""
import pytest

from mortgage_return_scenario_calculator.models import (
    InvestmentAssumptions,
    ScenarioInputs,
    InvestmentRestrictions,
    LoanMetrics,
    CashFlowMetrics,
    AppreciationMetrics,
    EarlyRepaymentMetrics,
    PortfolioMetrics,
    TaxMetrics,
    ScenarioResult,
)


pytestmark = pytest.mark.calculator


class TestInvestmentAssumptions:
    """Tests for InvestmentAssumptions dataclass."""
    
    def test_default_values(self):
        """Test default assumption values."""
        assumptions = InvestmentAssumptions()
        
        assert assumptions.rental_yield == 0.028  # 2.8%
        assert assumptions.mortgage_rate == 0.048  # 4.8%
        assert assumptions.appreciation_rate == 0.04  # 4%
        assert assumptions.rent_increase_rate == 0.03  # 3%
        assert assumptions.portfolio_return_rate == 0.07  # 7%
        assert assumptions.risk_free_rate == 0.03  # 3%
        assert assumptions.early_repayment_rate == 0.035  # 3.5%
        assert assumptions.capital_gains_tax_rate == 0.25  # 25%
    
    def test_custom_values(self):
        """Test custom assumption values."""
        assumptions = InvestmentAssumptions(
            rental_yield=0.03,
            mortgage_rate=0.05,
            appreciation_rate=0.05,
        )
        
        assert assumptions.rental_yield == 0.03
        assert assumptions.mortgage_rate == 0.05
        assert assumptions.appreciation_rate == 0.05
        # Other values should remain default
        assert assumptions.portfolio_return_rate == 0.07


class TestScenarioInputs:
    """Tests for ScenarioInputs dataclass."""
    
    def test_basic_creation(self):
        """Test basic scenario inputs creation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        
        assert inputs.property_price == 2_000_000
        assert inputs.down_payment == 1_000_000
        assert inputs.monthly_income == 30_000
        assert inputs.mortgage_term_years == 10
        assert inputs.urban_renewal_value == 0.0  # Default
        assert inputs.is_first_house is True  # Default should be True
        assert inputs.improvement_costs == 0.0  # Default should be 0.0
    
    def test_urban_renewal_cap(self):
        """Test urban renewal value is capped at 400,000."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
            urban_renewal_value=500_000,  # Should be capped
        )
        
        assert inputs.urban_renewal_value == 400_000
    
    def test_calculate_monthly_rent(self):
        """Test monthly rent calculation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        
        monthly_rent = inputs.calculate_monthly_rent(0.03)  # 3% yield
        expected = 2_000_000 * 0.03 / 12  # 5,000
        assert abs(monthly_rent - expected) < 0.01
    
    def test_calculate_mortgage_amount(self):
        """Test mortgage amount calculation."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=500_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        
        mortgage = inputs.calculate_mortgage_amount()
        assert mortgage == 1_500_000
    
    def test_validation_negative_property_price(self):
        """Test validation rejects negative property price."""
        with pytest.raises(ValueError, match="property_price must be positive"):
            ScenarioInputs(
                property_price=-100,
                down_payment=1_000_000,
                available_cash=2_000_000,
                monthly_income=30_000,
                monthly_available=10_000,
                mortgage_term_years=10,
                years_until_sale=10,
            )
    
    def test_validation_zero_property_price(self):
        """Test validation rejects zero property price."""
        with pytest.raises(ValueError, match="property_price must be positive"):
            ScenarioInputs(
                property_price=0,
                down_payment=1_000_000,
                available_cash=2_000_000,
                monthly_income=30_000,
                monthly_available=10_000,
                mortgage_term_years=10,
                years_until_sale=10,
            )
    
    def test_validation_negative_down_payment(self):
        """Test validation rejects negative down payment."""
        with pytest.raises(ValueError, match="down_payment cannot be negative"):
            ScenarioInputs(
                property_price=2_000_000,
                down_payment=-100,
                available_cash=2_000_000,
                monthly_income=30_000,
                monthly_available=10_000,
                mortgage_term_years=10,
                years_until_sale=10,
            )
    
    def test_validation_zero_mortgage_term(self):
        """Test validation rejects zero mortgage term."""
        with pytest.raises(ValueError, match="mortgage_term_years must be positive"):
            ScenarioInputs(
                property_price=2_000_000,
                down_payment=1_000_000,
                available_cash=2_000_000,
                monthly_income=30_000,
                monthly_available=10_000,
                mortgage_term_years=0,
                years_until_sale=10,
            )


class TestInvestmentRestrictions:
    """Tests for InvestmentRestrictions dataclass."""
    
    def test_default_values(self):
        """Test default restriction values."""
        restrictions = InvestmentRestrictions()
        
        assert restrictions.max_mortgage_to_income_ratio == 0.3  # 30%
        assert restrictions.min_down_payment_percentage == 0.0  # 0%
        assert restrictions.max_loan_to_value == 0.75  # 75%
        assert restrictions.max_mortgage_percentage == 0.75  # 75%
        assert restrictions.max_urban_renewal_value == 400_000
        assert restrictions.require_positive_cash_flow is False
    
    def test_custom_restrictions(self):
        """Test custom restriction values."""
        restrictions = InvestmentRestrictions(
            max_mortgage_to_income_ratio=0.25,
            require_positive_cash_flow=True,
        )
        
        assert restrictions.max_mortgage_to_income_ratio == 0.25
        assert restrictions.require_positive_cash_flow is True


class TestLoanMetrics:
    """Tests for LoanMetrics dataclass."""
    
    def test_creation(self):
        """Test loan metrics creation."""
        metrics = LoanMetrics(
            loan_amount=1_000_000,
            leverage_ratio=0.5,
            equity_ratio=0.5,
            leverage_multiplier=2.0,
            monthly_payment=10_000,
            total_payments=1_200_000,
            total_interest=200_000,
            avg_monthly_interest=1_667,
            mortgage_to_income_ratio=0.30,
        )
        
        assert metrics.loan_amount == 1_000_000
        assert metrics.leverage_ratio == 0.5
        assert metrics.monthly_payment == 10_000
        assert metrics.mortgage_to_income_ratio == 0.30


class TestCashFlowMetrics:
    """Tests for CashFlowMetrics dataclass."""
    
    def test_creation(self):
        """Test cash flow metrics creation."""
        metrics = CashFlowMetrics(
            monthly_rent=5_000,
            rental_yield=0.025,
            monthly_net_cash_flow=-5_000,
            monthly_interest_flow=3_333,
            avg_principal_payment=-8_333,
            leveraged_rental_yield=0.05,
            net_leveraged_yield=0.002,
        )
        
        assert metrics.monthly_rent == 5_000
        assert metrics.monthly_net_cash_flow == -5_000


class TestAppreciationMetrics:
    """Tests for AppreciationMetrics dataclass."""
    
    def test_creation(self):
        """Test appreciation metrics creation."""
        metrics = AppreciationMetrics(
            property_appreciation=800_000,
            urban_renewal_appreciation=160_000,
            total_appreciation=1_360_000,
            sale_value=3_360_000,
            total_return_rate=0.68,
            annualized_return=0.04,
            leveraged_return=0.08,
            net_annual_return=0.10,
        )
        
        assert metrics.property_appreciation == 800_000
        assert metrics.total_return_rate == 0.68


class TestEarlyRepaymentMetrics:
    """Tests for EarlyRepaymentMetrics dataclass."""
    
    def test_creation(self):
        """Test early repayment metrics creation."""
        metrics = EarlyRepaymentMetrics(
            remaining_mortgage=500_000,
            early_repayment_penalty=10_000,
            total_debt_to_bank=510_000,
            proceeds_minus_debt=2_850_000,
            net_gain_property=1_850_000,
        )
        
        assert metrics.remaining_mortgage == 500_000
        assert metrics.total_debt_to_bank == 510_000


class TestPortfolioMetrics:
    """Tests for PortfolioMetrics dataclass."""
    
    def test_creation(self):
        """Test portfolio metrics creation."""
        metrics = PortfolioMetrics(
            cash_in_portfolio=1_000_000,
            portfolio_initial_growth=1_967_151,
            monthly_deposits=3_658,
            accumulated_deposits=633_076,
            total_portfolio_value=2_600_227,
            portfolio_after_tax=2_309_898,
            net_portfolio_profit=870_986,
        )
        
        assert metrics.cash_in_portfolio == 1_000_000
        assert metrics.total_portfolio_value == 2_600_227


class TestScenarioResult:
    """Tests for ScenarioResult dataclass."""
    
    def test_default_validation(self):
        """Test default validation state."""
        # Create minimal mocks
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
        )
        assumptions = InvestmentAssumptions()
        loan = LoanMetrics(0, 0, 1, 1, 0, 0, 0, 0, 0)
        cash_flow = CashFlowMetrics(0, 0, 0, 0, 0, 0, 0)
        appreciation = AppreciationMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        early_repay = EarlyRepaymentMetrics(0, 0, 0, 0, 0)
        portfolio = PortfolioMetrics(0, 0, 0, 0, 0, 0, 0)
        
        result = ScenarioResult(
            inputs=inputs,
            assumptions=assumptions,
            loan_metrics=loan,
            cash_flow_metrics=cash_flow,
            appreciation_metrics=appreciation,
            early_repayment_metrics=early_repay,
            portfolio_metrics=portfolio,
            tax_metrics=TaxMetrics(0, 0, 0, 0, 0, 0),
            total_value_at_sale=0,
            total_profit=0,
            annual_return=0,
        )
        
        assert result.is_valid is True
        assert result.validation_errors == []


class TestTaxMetrics:
    """Tests for TaxMetrics dataclass."""
    
    def test_tax_metrics_creation(self):
        """Test TaxMetrics can be created with valid values."""
        tax_metrics = TaxMetrics(
            purchase_tax=100_000,
            purchase_tax_rate=0.05,
            capital_gains=500_000,
            capital_gains_tax=125_000,
            total_taxes=225_000,
            net_profit_after_taxes=275_000,
        )
        
        assert tax_metrics.purchase_tax == 100_000
        assert tax_metrics.purchase_tax_rate == 0.05
        assert tax_metrics.capital_gains == 500_000
        assert tax_metrics.capital_gains_tax == 125_000
        assert tax_metrics.total_taxes == 225_000
        assert tax_metrics.net_profit_after_taxes == 275_000
    
    def test_tax_metrics_total_taxes_calculation(self):
        """Test that total_taxes equals purchase_tax + capital_gains_tax."""
        tax_metrics = TaxMetrics(
            purchase_tax=50_000,
            purchase_tax_rate=0.025,
            capital_gains=200_000,
            capital_gains_tax=50_000,
            total_taxes=100_000,
            net_profit_after_taxes=150_000,
        )
        
        assert tax_metrics.total_taxes == tax_metrics.purchase_tax + tax_metrics.capital_gains_tax


class TestScenarioInputsTaxFields:
    """Tests for tax-related fields in ScenarioInputs."""
    
    def test_is_first_house_field(self):
        """Test is_first_house field can be set."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
            is_first_house=False,
        )
        
        assert inputs.is_first_house is False
    
    def test_improvement_costs_field(self):
        """Test improvement_costs field can be set."""
        inputs = ScenarioInputs(
            property_price=2_000_000,
            down_payment=1_000_000,
            available_cash=2_000_000,
            monthly_income=30_000,
            monthly_available=10_000,
            mortgage_term_years=10,
            years_until_sale=10,
            improvement_costs=200_000,
        )
        
        assert inputs.improvement_costs == 200_000
    
    def test_improvement_costs_validation(self):
        """Test improvement_costs cannot be negative."""
        with pytest.raises(ValueError, match="improvement_costs cannot be negative"):
            ScenarioInputs(
                property_price=2_000_000,
                down_payment=1_000_000,
                available_cash=2_000_000,
                monthly_income=30_000,
                monthly_available=10_000,
                mortgage_term_years=10,
                years_until_sale=10,
                improvement_costs=-100_000,
            )

