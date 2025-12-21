"""Purchase Tax (מס רכישה) Configuration for Israel.

This module contains the tax brackets and rates for calculating purchase tax
based on property value and whether it's a first house or additional property.

Reference: https://www.kolzchut.org.il/he/חישוב_מס_רכישה

IMPORTANT: Tax rates are updated annually. Update this file each year with
the latest rates from the Israel Tax Authority (רשות המסים).

Last Updated: 2025
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TaxBracket:
    """Represents a single tax bracket.
    
    Attributes:
        min_value: Minimum property value for this bracket (inclusive).
        max_value: Maximum property value for this bracket (exclusive).
            Use None for the highest bracket (no upper limit).
        rate: Tax rate as decimal (e.g., 0.05 for 5%).
    """
    min_value: float
    max_value: float | None  # None means no upper limit
    rate: float
    
    def applies_to(self, value: float) -> bool:
        """Check if this bracket applies to the given value.
        
        Args:
            value: Property value to check.
            
        Returns:
            True if value falls within this bracket.
        """
        if value < self.min_value:
            return False
        if self.max_value is None:
            return True
        return value < self.max_value


# First House (דירה יחידה) Tax Brackets
# IMPORTANT: Rates are updated annually by the Israel Tax Authority (רשות המסים)
# Verify current rates at: https://www.gov.il/he/departments/taxes/purchase_tax
# Or use the official simulator: https://www.gov.il/he/departments/taxes/purchase_tax_simulator
# 
# These brackets are based on typical Israeli tax structure and should be
# updated with the official rates for the current tax year.
FIRST_HOUSE_BRACKETS: List[TaxBracket] = [
    # Up to 1,805,000 ILS: 0% (exempt)
    TaxBracket(min_value=0, max_value=1_805_000, rate=0.0),
    
    # 1,805,000 - 2,085,000 ILS: 3.5%
    TaxBracket(min_value=1_805_000, max_value=2_085_000, rate=0.035),
    
    # 2,085,000 - 5,000,000 ILS: 5%
    TaxBracket(min_value=2_085_000, max_value=5_000_000, rate=0.05),
    
    # 5,000,000 - 17,000,000 ILS: 7.5%
    TaxBracket(min_value=5_000_000, max_value=17_000_000, rate=0.075),
    
    # Above 17,000,000 ILS: 10%
    TaxBracket(min_value=17_000_000, max_value=None, rate=0.10),
]

# Additional House (דירה נוספת) Tax Brackets
# IMPORTANT: Rates are updated annually by the Israel Tax Authority (רשות המסים)
# Verify current rates at: https://www.gov.il/he/departments/taxes/purchase_tax
#
# Additional properties typically have a flat rate up to a certain threshold,
# then a higher rate for luxury properties.
ADDITIONAL_HOUSE_BRACKETS: List[TaxBracket] = [
    # Up to 1,805,000 ILS: 8%
    TaxBracket(min_value=0, max_value=1_805_000, rate=0.08),
    
    # 1,805,000 - 2,085,000 ILS: 8%
    TaxBracket(min_value=1_805_000, max_value=2_085_000, rate=0.08),
    
    # 2,085,000 - 5,000,000 ILS: 8%
    TaxBracket(min_value=2_085_000, max_value=5_000_000, rate=0.08),
    
    # 5,000,000 - 17,000,000 ILS: 8%
    TaxBracket(min_value=5_000_000, max_value=17_000_000, rate=0.08),
    
    # Above 17,000,000 ILS: 10%
    TaxBracket(min_value=17_000_000, max_value=None, rate=0.10),
]


def calculate_purchase_tax(
    property_value: float,
    is_first_house: bool = True
) -> float:
    """Calculate purchase tax (מס רכישה) based on property value.
    
    Purchase tax is calculated using progressive brackets. Each bracket
    applies only to the portion of the value that falls within that bracket.
    
    Reference: https://www.kolzchut.org.il/he/חישוב_מס_רכישה
    
    Args:
        property_value: Total property value (transaction value including VAT
            if purchasing from a contractor).
        is_first_house: True if this is the buyer's first house (דירה יחידה),
            False if it's an additional property (דירה נוספת).
    
    Returns:
        Total purchase tax amount in ILS.
    
    Example:
        >>> # First house worth 2,000,000 ILS
        >>> tax = calculate_purchase_tax(2_000_000, is_first_house=True)
        >>> # Tax: 0% on first 1,805,000 + 3.5% on next 195,000 = 6,825 ILS
        
        >>> # Additional house worth 2,000,000 ILS
        >>> tax = calculate_purchase_tax(2_000_000, is_first_house=False)
        >>> # Tax: 8% on entire amount = 160,000 ILS
    """
    if property_value <= 0:
        return 0.0
    
    brackets = FIRST_HOUSE_BRACKETS if is_first_house else ADDITIONAL_HOUSE_BRACKETS
    
    total_tax = 0.0
    
    for bracket in brackets:
        # Skip brackets below the property value
        if property_value <= bracket.min_value:
            break
        
        # Calculate the upper limit of this bracket
        bracket_max = bracket.max_value if bracket.max_value is not None else float('inf')
        
        # Calculate how much of the property value falls in this bracket
        bracket_start = bracket.min_value
        bracket_end = min(property_value, bracket_max)
        
        # Amount taxed in this bracket
        amount_in_bracket = bracket_end - bracket_start
        
        if amount_in_bracket > 0:
            tax_for_bracket = amount_in_bracket * bracket.rate
            total_tax += tax_for_bracket
    
    return total_tax


def calculate_purchase_tax_rate(
    property_value: float,
    is_first_house: bool = True
) -> float:
    """Calculate the effective purchase tax rate as a percentage.
    
    Args:
        property_value: Total property value.
        is_first_house: True if first house, False if additional property.
    
    Returns:
        Effective tax rate as decimal (e.g., 0.05 for 5%).
    """
    if property_value <= 0:
        return 0.0
    
    tax_amount = calculate_purchase_tax(property_value, is_first_house)
    return tax_amount / property_value


# Capital Gains Tax (מס שבח) on Sale
# This is typically a flat rate, but can vary based on holding period
# and other factors. Update annually.
CAPITAL_GAINS_TAX_RATE: float = 0.25  # 25% - verify current rate


def calculate_capital_gains_tax(
    sale_price: float,
    purchase_price: float,
    purchase_tax_paid: float = 0.0,
    improvement_costs: float = 0.0
) -> float:
    """Calculate capital gains tax (מס שבח) on property sale.
    
    Capital gains = Sale Price - Purchase Price - Purchase Tax - Improvements
    
    Args:
        sale_price: Price at which property is sold.
        purchase_price: Original purchase price.
        purchase_tax_paid: Purchase tax paid when buying (can be deducted).
        improvement_costs: Costs of improvements made to property.
    
    Returns:
        Capital gains tax amount in ILS.
    """
    capital_gain = sale_price - purchase_price - purchase_tax_paid - improvement_costs
    
    if capital_gain <= 0:
        return 0.0
    
    return capital_gain * CAPITAL_GAINS_TAX_RATE

