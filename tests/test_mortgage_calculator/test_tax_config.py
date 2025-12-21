"""Tests for tax configuration module.

Run only calculator tests with: pytest -m calculator
"""
import pytest

from mortgage_return_scenario_calculator.tax_config import (
    TaxBracket,
    FIRST_HOUSE_BRACKETS,
    ADDITIONAL_HOUSE_BRACKETS,
    CAPITAL_GAINS_TAX_RATE,
    calculate_purchase_tax,
    calculate_purchase_tax_rate,
    calculate_capital_gains_tax,
)


pytestmark = pytest.mark.calculator


class TestTaxBracket:
    """Tests for TaxBracket dataclass."""
    
    def test_bracket_creation(self):
        """Test TaxBracket can be created with valid values."""
        bracket = TaxBracket(min_value=0, max_value=100_000, rate=0.05)
        
        assert bracket.min_value == 0
        assert bracket.max_value == 100_000
        assert bracket.rate == 0.05
    
    def test_bracket_with_no_max(self):
        """Test TaxBracket with None max_value (no upper limit)."""
        bracket = TaxBracket(min_value=1_000_000, max_value=None, rate=0.10)
        
        assert bracket.min_value == 1_000_000
        assert bracket.max_value is None
        assert bracket.rate == 0.10
    
    def test_applies_to_value_in_bracket(self):
        """Test applies_to returns True for value within bracket."""
        bracket = TaxBracket(min_value=100_000, max_value=200_000, rate=0.05)
        
        assert bracket.applies_to(150_000) is True
        assert bracket.applies_to(100_000) is True  # Inclusive min
        assert bracket.applies_to(199_999) is True
    
    def test_applies_to_value_below_bracket(self):
        """Test applies_to returns False for value below bracket."""
        bracket = TaxBracket(min_value=100_000, max_value=200_000, rate=0.05)
        
        assert bracket.applies_to(50_000) is False
        assert bracket.applies_to(99_999) is False
    
    def test_applies_to_value_above_bracket(self):
        """Test applies_to returns False for value above bracket."""
        bracket = TaxBracket(min_value=100_000, max_value=200_000, rate=0.05)
        
        assert bracket.applies_to(200_000) is False  # Exclusive max
        assert bracket.applies_to(250_000) is False
    
    def test_applies_to_unlimited_bracket(self):
        """Test applies_to for bracket with no upper limit."""
        bracket = TaxBracket(min_value=1_000_000, max_value=None, rate=0.10)
        
        assert bracket.applies_to(1_000_000) is True
        assert bracket.applies_to(10_000_000) is True
        assert bracket.applies_to(100_000_000) is True
        assert bracket.applies_to(999_999) is False


class TestPurchaseTaxFirstHouse:
    """Tests for purchase tax calculation - First House."""
    
    def test_zero_property_value(self):
        """Test purchase tax for zero property value."""
        tax = calculate_purchase_tax(0, is_first_house=True)
        assert tax == 0.0
    
    def test_negative_property_value(self):
        """Test purchase tax for negative property value."""
        tax = calculate_purchase_tax(-100_000, is_first_house=True)
        assert tax == 0.0
    
    def test_first_house_below_threshold(self):
        """Test first house below tax threshold (0% tax)."""
        # Property value: 1,500,000 ILS (below 1,805,000 threshold)
        tax = calculate_purchase_tax(1_500_000, is_first_house=True)
        assert tax == 0.0
    
    def test_first_house_at_threshold(self):
        """Test first house exactly at threshold boundary."""
        # Property value: 1,805,000 ILS (at threshold, still 0%)
        tax = calculate_purchase_tax(1_805_000, is_first_house=True)
        assert tax == 0.0
    
    def test_first_house_in_second_bracket(self):
        """Test first house in 3.5% bracket."""
        # Property value: 2,000,000 ILS
        # Tax: 0% on first 1,805,000 + 3.5% on next 195,000 = 6,825 ILS
        tax = calculate_purchase_tax(2_000_000, is_first_house=True)
        expected = (2_000_000 - 1_805_000) * 0.035
        assert abs(tax - expected) < 0.01
        assert abs(tax - 6_825) < 0.01
    
    def test_first_house_in_third_bracket(self):
        """Test first house in 5% bracket."""
        # Property value: 3,000,000 ILS
        # Tax: 0% on first 1,805,000 + 3.5% on 280,000 + 5% on 915,000
        tax = calculate_purchase_tax(3_000_000, is_first_house=True)
        expected = (
            0 +  # First bracket: 0%
            (2_085_000 - 1_805_000) * 0.035 +  # Second bracket: 3.5%
            (3_000_000 - 2_085_000) * 0.05  # Third bracket: 5%
        )
        assert abs(tax - expected) < 0.01
    
    def test_first_house_in_fourth_bracket(self):
        """Test first house in 7.5% bracket."""
        # Property value: 6,000,000 ILS
        tax = calculate_purchase_tax(6_000_000, is_first_house=True)
        expected = (
            0 +  # First bracket: 0%
            (2_085_000 - 1_805_000) * 0.035 +  # Second bracket: 3.5%
            (5_000_000 - 2_085_000) * 0.05 +  # Third bracket: 5%
            (6_000_000 - 5_000_000) * 0.075  # Fourth bracket: 7.5%
        )
        assert abs(tax - expected) < 0.01
    
    def test_first_house_in_luxury_bracket(self):
        """Test first house in 10% luxury bracket."""
        # Property value: 20,000,000 ILS
        tax = calculate_purchase_tax(20_000_000, is_first_house=True)
        expected = (
            0 +  # First bracket: 0%
            (2_085_000 - 1_805_000) * 0.035 +  # Second bracket: 3.5%
            (5_000_000 - 2_085_000) * 0.05 +  # Third bracket: 5%
            (17_000_000 - 5_000_000) * 0.075 +  # Fourth bracket: 7.5%
            (20_000_000 - 17_000_000) * 0.10  # Fifth bracket: 10%
        )
        assert abs(tax - expected) < 0.01
    
    def test_first_house_at_bracket_boundaries(self):
        """Test first house at various bracket boundaries."""
        # At 2,085,000 boundary (between 3.5% and 5% brackets)
        tax_1 = calculate_purchase_tax(2_085_000, is_first_house=True)
        tax_2 = calculate_purchase_tax(2_085_001, is_first_house=True)
        # Should be different (one in 3.5% bracket, one in 5% bracket)
        assert tax_2 > tax_1
        
        # At 5,000,000 boundary (between 5% and 7.5% brackets)
        tax_3 = calculate_purchase_tax(5_000_000, is_first_house=True)
        tax_4 = calculate_purchase_tax(5_000_001, is_first_house=True)
        assert tax_4 > tax_3


class TestPurchaseTaxAdditionalProperty:
    """Tests for purchase tax calculation - Additional Property."""
    
    def test_additional_property_below_threshold(self):
        """Test additional property below threshold (8% tax applies)."""
        # Property value: 1,500,000 ILS
        tax = calculate_purchase_tax(1_500_000, is_first_house=False)
        expected = 1_500_000 * 0.08
        assert abs(tax - expected) < 0.01
        assert abs(tax - 120_000) < 0.01
    
    def test_additional_property_mid_range(self):
        """Test additional property in mid-range (8% flat rate)."""
        # Property value: 3,000,000 ILS
        tax = calculate_purchase_tax(3_000_000, is_first_house=False)
        expected = 3_000_000 * 0.08
        assert abs(tax - expected) < 0.01
        assert abs(tax - 240_000) < 0.01
    
    def test_additional_property_luxury(self):
        """Test additional property in luxury bracket (10% tax)."""
        # Property value: 20,000,000 ILS
        tax = calculate_purchase_tax(20_000_000, is_first_house=False)
        expected = (
            17_000_000 * 0.08 +  # First 17M at 8%
            (20_000_000 - 17_000_000) * 0.10  # Above 17M at 10%
        )
        assert abs(tax - expected) < 0.01
    
    def test_additional_property_at_luxury_threshold(self):
        """Test additional property exactly at luxury threshold."""
        # Property value: 17,000,000 ILS (at threshold)
        tax = calculate_purchase_tax(17_000_000, is_first_house=False)
        expected = 17_000_000 * 0.08
        assert abs(tax - expected) < 0.01


class TestPurchaseTaxRate:
    """Tests for purchase tax rate calculation."""
    
    def test_tax_rate_zero_value(self):
        """Test tax rate for zero property value."""
        rate = calculate_purchase_tax_rate(0, is_first_house=True)
        assert rate == 0.0
    
    def test_tax_rate_first_house_below_threshold(self):
        """Test tax rate for first house below threshold."""
        rate = calculate_purchase_tax_rate(1_500_000, is_first_house=True)
        assert rate == 0.0
    
    def test_tax_rate_first_house_above_threshold(self):
        """Test tax rate for first house above threshold."""
        # Property: 2,000,000 ILS, Tax: 6,825 ILS
        rate = calculate_purchase_tax_rate(2_000_000, is_first_house=True)
        expected_rate = 6_825 / 2_000_000
        assert abs(rate - expected_rate) < 0.0001
    
    def test_tax_rate_additional_property(self):
        """Test tax rate for additional property (should be 8%)."""
        rate = calculate_purchase_tax_rate(2_000_000, is_first_house=False)
        expected_rate = 0.08  # 8% flat rate
        assert abs(rate - expected_rate) < 0.0001
    
    def test_tax_rate_additional_property_luxury(self):
        """Test tax rate for additional property in luxury bracket."""
        # Property: 20,000,000 ILS
        # Tax: 17M * 8% + 3M * 10% = 1,360,000 + 300,000 = 1,660,000
        # Rate: 1,660,000 / 20,000,000 = 0.083 (8.3%)
        rate = calculate_purchase_tax_rate(20_000_000, is_first_house=False)
        expected_tax = 17_000_000 * 0.08 + 3_000_000 * 0.10
        expected_rate = expected_tax / 20_000_000
        assert abs(rate - expected_rate) < 0.0001


class TestCapitalGainsTax:
    """Tests for capital gains tax calculation."""
    
    def test_positive_capital_gains(self):
        """Test capital gains tax with positive gain."""
        # Sale: 3,000,000, Purchase: 2,000,000
        # Gain: 1,000,000, Tax: 250,000 (25%)
        tax = calculate_capital_gains_tax(
            sale_price=3_000_000,
            purchase_price=2_000_000
        )
        expected = (3_000_000 - 2_000_000) * CAPITAL_GAINS_TAX_RATE
        assert abs(tax - expected) < 0.01
        assert abs(tax - 250_000) < 0.01
    
    def test_capital_gains_with_purchase_tax(self):
        """Test capital gains tax with purchase tax deduction."""
        # Sale: 3,000,000, Purchase: 2,000,000, Purchase Tax: 100,000
        # Gain: 3,000,000 - 2,000,000 - 100,000 = 900,000
        # Tax: 900,000 * 25% = 225,000
        tax = calculate_capital_gains_tax(
            sale_price=3_000_000,
            purchase_price=2_000_000,
            purchase_tax_paid=100_000
        )
        expected = (3_000_000 - 2_000_000 - 100_000) * CAPITAL_GAINS_TAX_RATE
        assert abs(tax - expected) < 0.01
        assert abs(tax - 225_000) < 0.01
    
    def test_capital_gains_with_improvements(self):
        """Test capital gains tax with improvement costs deduction."""
        # Sale: 3,000,000, Purchase: 2,000,000, Improvements: 200,000
        # Gain: 3,000,000 - 2,000,000 - 200,000 = 800,000
        # Tax: 800,000 * 25% = 200,000
        tax = calculate_capital_gains_tax(
            sale_price=3_000_000,
            purchase_price=2_000_000,
            improvement_costs=200_000
        )
        expected = (3_000_000 - 2_000_000 - 200_000) * CAPITAL_GAINS_TAX_RATE
        assert abs(tax - expected) < 0.01
        assert abs(tax - 200_000) < 0.01
    
    def test_capital_gains_with_all_deductions(self):
        """Test capital gains tax with both purchase tax and improvements."""
        # Sale: 3,000,000, Purchase: 2,000,000, Purchase Tax: 100,000, Improvements: 200,000
        # Gain: 3,000,000 - 2,000,000 - 100,000 - 200,000 = 700,000
        # Tax: 700,000 * 25% = 175,000
        tax = calculate_capital_gains_tax(
            sale_price=3_000_000,
            purchase_price=2_000_000,
            purchase_tax_paid=100_000,
            improvement_costs=200_000
        )
        expected = (3_000_000 - 2_000_000 - 100_000 - 200_000) * CAPITAL_GAINS_TAX_RATE
        assert abs(tax - expected) < 0.01
        assert abs(tax - 175_000) < 0.01
    
    def test_zero_capital_gains(self):
        """Test capital gains tax with zero gain (no tax)."""
        # Sale equals purchase price
        tax = calculate_capital_gains_tax(
            sale_price=2_000_000,
            purchase_price=2_000_000
        )
        assert tax == 0.0
    
    def test_negative_capital_gains(self):
        """Test capital gains tax with loss (no tax on losses)."""
        # Sale less than purchase price
        tax = calculate_capital_gains_tax(
            sale_price=1_500_000,
            purchase_price=2_000_000
        )
        assert tax == 0.0
    
    def test_negative_capital_gains_with_deductions(self):
        """Test capital gains tax with loss after deductions (no tax)."""
        # Sale: 2,000,000, Purchase: 2,500,000, Purchase Tax: 200,000
        # Gain: 2,000,000 - 2,500,000 - 200,000 = -700,000 (loss)
        tax = calculate_capital_gains_tax(
            sale_price=2_000_000,
            purchase_price=2_500_000,
            purchase_tax_paid=200_000
        )
        assert tax == 0.0
    
    def test_capital_gains_break_even_with_deductions(self):
        """Test capital gains tax when deductions equal gain (no tax)."""
        # Sale: 2,000,000, Purchase: 1,500,000, Purchase Tax: 100,000, Improvements: 400,000
        # Gain: 2,000,000 - 1,500,000 - 100,000 - 400,000 = 0
        tax = calculate_capital_gains_tax(
            sale_price=2_000_000,
            purchase_price=1_500_000,
            purchase_tax_paid=100_000,
            improvement_costs=400_000
        )
        assert tax == 0.0


class TestTaxIntegrationScenarios:
    """Integration tests combining purchase tax and capital gains tax."""
    
    def test_full_scenario_first_house(self):
        """Test full tax scenario for first house."""
        property_value = 2_000_000
        sale_value = 3_000_000
        
        # Purchase tax
        purchase_tax = calculate_purchase_tax(property_value, is_first_house=True)
        assert purchase_tax > 0
        
        # Capital gains tax
        capital_gains_tax = calculate_capital_gains_tax(
            sale_price=sale_value,
            purchase_price=property_value,
            purchase_tax_paid=purchase_tax
        )
        assert capital_gains_tax > 0
        
        # Total taxes
        total_taxes = purchase_tax + capital_gains_tax
        assert total_taxes > purchase_tax
        assert total_taxes > capital_gains_tax
    
    def test_full_scenario_additional_property(self):
        """Test full tax scenario for additional property."""
        property_value = 2_000_000
        sale_value = 3_000_000
        
        # Purchase tax (higher for additional property)
        purchase_tax = calculate_purchase_tax(property_value, is_first_house=False)
        assert purchase_tax > 0
        
        # Capital gains tax
        capital_gains_tax = calculate_capital_gains_tax(
            sale_price=sale_value,
            purchase_price=property_value,
            purchase_tax_paid=purchase_tax
        )
        assert capital_gains_tax > 0
        
        # Additional property should have higher purchase tax
        first_house_tax = calculate_purchase_tax(property_value, is_first_house=True)
        assert purchase_tax > first_house_tax


class TestTaxBracketsConstants:
    """Tests for tax bracket constants."""
    
    def test_first_house_brackets_defined(self):
        """Test FIRST_HOUSE_BRACKETS is properly defined."""
        assert len(FIRST_HOUSE_BRACKETS) > 0
        assert all(isinstance(b, TaxBracket) for b in FIRST_HOUSE_BRACKETS)
        
        # Check first bracket starts at 0
        assert FIRST_HOUSE_BRACKETS[0].min_value == 0
    
    def test_additional_house_brackets_defined(self):
        """Test ADDITIONAL_HOUSE_BRACKETS is properly defined."""
        assert len(ADDITIONAL_HOUSE_BRACKETS) > 0
        assert all(isinstance(b, TaxBracket) for b in ADDITIONAL_HOUSE_BRACKETS)
        
        # Check first bracket starts at 0
        assert ADDITIONAL_HOUSE_BRACKETS[0].min_value == 0
    
    def test_capital_gains_tax_rate_defined(self):
        """Test CAPITAL_GAINS_TAX_RATE is properly defined."""
        assert CAPITAL_GAINS_TAX_RATE > 0
        assert CAPITAL_GAINS_TAX_RATE <= 1.0  # Should be a rate, not percentage
        assert CAPITAL_GAINS_TAX_RATE == 0.25  # 25%

