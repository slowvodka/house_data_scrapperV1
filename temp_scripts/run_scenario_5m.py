"""Run scenario calculator for 5M apartment with 4M loan.

This is a temporary script for running a specific scenario.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mortgage_return_scenario_calculator.calculator import ScenarioCalculator
from mortgage_return_scenario_calculator.models import (
    ScenarioInputs,
    InvestmentAssumptions,
)
from mortgage_return_scenario_calculator.exporter import ScenarioExporter

# Scenario inputs
# Property: 5M ILS
# Loan: 4M ILS (so down payment = 1M ILS)
# Income: 100K monthly

property_price = 5_000_000
loan_amount = 4_000_000
down_payment = property_price - loan_amount  # 1M ILS
monthly_income = 100_000  # 100K monthly
available_cash = 1_500_000  # Assume 1.5M available cash
monthly_available = 30_000  # Assume 30K available for mortgage payments
mortgage_term_years = 25  # 25 year mortgage
years_until_sale = 15  # Hold for 15 years

inputs = ScenarioInputs(
    property_price=property_price,
    down_payment=down_payment,
    available_cash=available_cash,
    monthly_income=monthly_income,
    monthly_available=monthly_available,
    mortgage_term_years=mortgage_term_years,
    years_until_sale=years_until_sale,
    is_first_house=True,  # First house
    improvement_costs=0.0,  # No improvements
)

# Create calculator with default assumptions
calculator = ScenarioCalculator(inputs)

# Calculate
result = calculator.calculate()

# Print summary
print("=" * 80)
print("SCENARIO CALCULATION RESULTS")
print("=" * 80)
print(f"\nProperty Price: {property_price:,.0f} ILS")
print(f"Down Payment: {down_payment:,.0f} ILS")
print(f"Loan Amount: {loan_amount:,.0f} ILS")
print(f"Monthly Income: {monthly_income:,.0f} ILS")
print(f"\n{'=' * 80}\n")

print("LOAN METRICS:")
print(f"  Monthly Payment: {result.loan_metrics.monthly_payment:,.0f} ILS")
print(f"  Total Payments: {result.loan_metrics.total_payments:,.0f} ILS")
print(f"  Total Interest: {result.loan_metrics.total_interest:,.0f} ILS")
print(f"  Mortgage-to-Income Ratio: {result.loan_metrics.mortgage_to_income_ratio:.1%}")
print(f"  Leverage Ratio: {result.loan_metrics.leverage_ratio:.1%}")

print("\nCASH FLOW METRICS:")
print(f"  Monthly Rent: {result.cash_flow_metrics.monthly_rent:,.0f} ILS")
print(f"  Rental Yield: {result.cash_flow_metrics.rental_yield:.2%}")
print(f"  Monthly Net Cash Flow: {result.cash_flow_metrics.monthly_net_cash_flow:,.0f} ILS")

print("\nAPPRECIATION METRICS:")
print(f"  Property Appreciation: {result.appreciation_metrics.property_appreciation:,.0f} ILS")
print(f"  Sale Value: {result.appreciation_metrics.sale_value:,.0f} ILS")
print(f"  Total Return Rate: {result.appreciation_metrics.total_return_rate:.2%}")
print(f"  Annualized Return: {result.appreciation_metrics.annualized_return:.2%}")

print("\nEARLY REPAYMENT METRICS:")
print(f"  Remaining Mortgage: {result.early_repayment_metrics.remaining_mortgage:,.0f} ILS")
print(f"  Early Repayment Penalty: {result.early_repayment_metrics.early_repayment_penalty:,.0f} ILS")
print(f"  Total Debt to Bank: {result.early_repayment_metrics.total_debt_to_bank:,.0f} ILS")
print(f"  Proceeds Minus Debt: {result.early_repayment_metrics.proceeds_minus_debt:,.0f} ILS")
print(f"  Net Gain Property: {result.early_repayment_metrics.net_gain_property:,.0f} ILS")

print("\nPORTFOLIO METRICS:")
print(f"  Cash in Portfolio: {result.portfolio_metrics.cash_in_portfolio:,.0f} ILS")
print(f"  Total Portfolio Value: {result.portfolio_metrics.total_portfolio_value:,.0f} ILS")
print(f"  Portfolio After Tax: {result.portfolio_metrics.portfolio_after_tax:,.0f} ILS")
print(f"  Net Portfolio Profit: {result.portfolio_metrics.net_portfolio_profit:,.0f} ILS")

print("\nTAX METRICS:")
print(f"  Purchase Tax (מס רכישה): {result.tax_metrics.purchase_tax:,.0f} ILS ({result.tax_metrics.purchase_tax_rate:.2%})")
print(f"  Capital Gains: {result.tax_metrics.capital_gains:,.0f} ILS")
print(f"  Capital Gains Tax (מס שבח): {result.tax_metrics.capital_gains_tax:,.0f} ILS")
print(f"  Total Taxes: {result.tax_metrics.total_taxes:,.0f} ILS")
print(f"  Net Profit After Taxes: {result.tax_metrics.net_profit_after_taxes:,.0f} ILS")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"  Total Value at Sale: {result.total_value_at_sale:,.0f} ILS")
print(f"  Total Profit (AFTER TAXES): {result.total_profit:,.0f} ILS")
print(f"  Annual Return: {result.annual_return:.2%}")
print(f"  Scenario Valid: {result.is_valid}")

if result.validation_errors:
    print(f"\nValidation Errors: {result.validation_errors}")

print("\n" + "=" * 80)

