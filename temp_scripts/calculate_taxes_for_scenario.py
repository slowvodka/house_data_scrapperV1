"""Calculate taxes for the 5M apartment scenario.

This shows what taxes SHOULD be calculated when tax integration is complete.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mortgage_return_scenario_calculator.tax_config import (
    calculate_purchase_tax,
    calculate_purchase_tax_rate,
    calculate_capital_gains_tax,
)

# Scenario parameters
property_price = 5_000_000
loan_amount = 4_000_000
down_payment = 1_000_000
sale_value = 9_004_718  # From the calculator output
years_until_sale = 15

# Assume first house (user can change this)
is_first_house = True
improvement_costs = 0  # No improvements assumed

print("=" * 80)
print("REAL ESTATE TAX CALCULATIONS")
print("=" * 80)

# Purchase Tax (מס רכישה)
print("\n1. PURCHASE TAX (מס רכישה) - Paid when buying:")
print(f"   Property Value: {property_price:,.0f} ILS")
print(f"   First House: {is_first_house}")

purchase_tax = calculate_purchase_tax(property_price, is_first_house)
purchase_tax_rate = calculate_purchase_tax_rate(property_price, is_first_house)

print(f"   Purchase Tax: {purchase_tax:,.0f} ILS ({purchase_tax_rate:.2%})")
print(f"   Total Acquisition Cost: {property_price + purchase_tax:,.0f} ILS")

# Capital Gains Tax (מס שבח)
print("\n2. CAPITAL GAINS TAX (מס שבח) - Paid when selling:")
print(f"   Sale Value: {sale_value:,.0f} ILS")
print(f"   Purchase Price: {property_price:,.0f} ILS")
print(f"   Purchase Tax Paid: {purchase_tax:,.0f} ILS (deductible)")
print(f"   Improvement Costs: {improvement_costs:,.0f} ILS (deductible)")

capital_gains = sale_value - property_price - purchase_tax - improvement_costs
capital_gains_tax = calculate_capital_gains_tax(
    sale_value,
    property_price,
    purchase_tax_paid=purchase_tax,
    improvement_costs=improvement_costs
)

print(f"   Capital Gain: {capital_gains:,.0f} ILS")
print(f"   Capital Gains Tax: {capital_gains_tax:,.0f} ILS")
print(f"   Net Proceeds After Tax: {sale_value - capital_gains_tax:,.0f} ILS")

# Total Taxes
total_taxes = purchase_tax + capital_gains_tax
print("\n" + "=" * 80)
print("TOTAL TAXES:")
print(f"   Purchase Tax: {purchase_tax:,.0f} ILS")
print(f"   Capital Gains Tax: {capital_gains_tax:,.0f} ILS")
print(f"   Total Taxes: {total_taxes:,.0f} ILS")
print("=" * 80)

# Impact on Profit
print("\nIMPACT ON PROFIT:")
print(f"   Current Total Profit (without taxes): 7,702,823 ILS")
print(f"   Total Taxes: {total_taxes:,.0f} ILS")
print(f"   Adjusted Total Profit: {7_702_823 - total_taxes:,.0f} ILS")
print(f"   Tax Impact: -{total_taxes:,.0f} ILS ({total_taxes/7_702_823:.1%} of profit)")

# Comparison: First House vs Additional Property
print("\n" + "=" * 80)
print("COMPARISON: First House vs Additional Property")
print("=" * 80)

for is_first in [True, False]:
    house_type = "First House" if is_first else "Additional Property"
    purchase_tax_comp = calculate_purchase_tax(property_price, is_first)
    capital_gains_comp = calculate_capital_gains_tax(
        sale_value, property_price, purchase_tax_comp, improvement_costs
    )
    total_taxes_comp = purchase_tax_comp + capital_gains_comp
    
    print(f"\n{house_type}:")
    print(f"  Purchase Tax: {purchase_tax_comp:,.0f} ILS")
    print(f"  Capital Gains Tax: {capital_gains_comp:,.0f} ILS")
    print(f"  Total Taxes: {total_taxes_comp:,.0f} ILS")
    print(f"  Adjusted Profit: {7_702_823 - total_taxes_comp:,.0f} ILS")

print("\n" + "=" * 80)
print("NOTE: Tax integration is now complete!")
print("Taxes are automatically calculated in ScenarioResult.total_profit")
print("=" * 80)

