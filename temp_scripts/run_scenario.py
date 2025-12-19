"""Run a test scenario matching the Excel calculations."""
import sys
sys.path.insert(0, '.')

from mortgage_return_scenario_calculator import (
    ScenarioCalculator,
    ScenarioInputs,
    InvestmentAssumptions,
    InvestmentRestrictions,
    ConfigGenerator,
    export_scenario_to_csv,
)

# Create the scenario:
# - Property price: 2,000,000
# - Available cash: 2,000,000
# - Down payment: 1,000,000 (taking 1M mortgage)
# - Mortgage term: 10 years
# - Years until sale: 10 years (same as mortgage term for simplicity)
# - Monthly available: 10,000
# - Mortgage rate: 4.8%
# - Rental yield: 2.5%
# - Appreciation rate: 4%
# - Urban renewal value: 400,000

inputs = ScenarioInputs(
    property_price=2_000_000,
    down_payment=1_000_000,  # Taking 1M mortgage
    available_cash=2_000_000,
    monthly_income=20_000,  # Net monthly income
    monthly_available=10_000,
    mortgage_term_years=30,
    years_until_sale=15,
    urban_renewal_value=400_000,
)

# Custom assumptions
assumptions = InvestmentAssumptions(
    rental_yield=0.025,  # 2.5%
    mortgage_rate=0.048,  # 4.8%
    appreciation_rate=0.04,  # 4%
    rent_increase_rate=0.03,  # 3% default
    portfolio_return_rate=0.07,  # 7% default
    risk_free_rate=0.03,  # 3% default
    early_repayment_rate=0.035,  # 3.5% default
    capital_gains_tax_rate=0.25,  # 25%
)

# Create calculator and run
calculator = ScenarioCalculator(inputs, assumptions)
result = calculator.calculate()

# Print all metrics as in Excel
print("=" * 80)
print("SCENARIO CALCULATOR RESULTS")
print("=" * 80)

print("\n" + "=" * 80)
print("USER INPUTS")
print("=" * 80)
print(f"Property Price:        {inputs.property_price:>15,.0f} ILS")
print(f"Down Payment:          {inputs.down_payment:>15,.0f} ILS")
print(f"Available Cash:        {inputs.available_cash:>15,.0f} ILS")
print(f"Monthly Income (Net):  {inputs.monthly_income:>15,.0f} ILS")
print(f"Monthly Available:     {inputs.monthly_available:>15,.0f} ILS")
print(f"Mortgage Term:         {inputs.mortgage_term_years:>15} years")
print(f"Years Until Sale:      {inputs.years_until_sale:>15} years")
print(f"Urban Renewal Value:   {inputs.urban_renewal_value:>15,.0f} ILS")

print("\n" + "=" * 80)
print("ASSUMPTIONS")
print("=" * 80)
print(f"Rental Yield:          {assumptions.rental_yield:>15.2%}")
print(f"Mortgage Rate:         {assumptions.mortgage_rate:>15.2%}")
print(f"Appreciation Rate:     {assumptions.appreciation_rate:>15.2%}")
print(f"Rent Increase Rate:    {assumptions.rent_increase_rate:>15.2%}")
print(f"Portfolio Return:      {assumptions.portfolio_return_rate:>15.2%}")
print(f"Capital Gains Tax:     {assumptions.capital_gains_tax_rate:>15.2%}")

print("\n" + "=" * 80)
print("LOAN METRICS (Group 1)")
print("=" * 80)
lm = result.loan_metrics
print(f"Mortgage Amount:       {lm.loan_amount:>15,.0f} ILS")
print(f"Leverage Ratio:        {lm.leverage_ratio:>15.2%}")
print(f"Equity Ratio:          {lm.equity_ratio:>15.2%}")
print(f"Leverage Multiplier:   {lm.leverage_multiplier:>15.2f}x")
print(f"Monthly Payment:       {lm.monthly_payment:>15,.0f} ILS")
print(f"Total Payments:        {lm.total_payments:>15,.0f} ILS")
print(f"Total Interest:        {lm.total_interest:>15,.0f} ILS")
print(f"Avg Monthly Interest:  {lm.avg_monthly_interest:>15,.0f} ILS")
print(f"Mortgage/Income Ratio: {lm.mortgage_to_income_ratio:>15.2%}")

print("\n" + "=" * 80)
print("CASH FLOW METRICS (Group 2)")
print("=" * 80)
cf = result.cash_flow_metrics
print(f"Monthly Rent:          {cf.monthly_rent:>15,.0f} ILS")
print(f"Rental Yield:          {cf.rental_yield:>15.2%}")
print(f"Monthly Net Cash Flow: {cf.monthly_net_cash_flow:>15,.0f} ILS")
print(f"Monthly Interest Flow: {cf.monthly_interest_flow:>15,.0f} ILS")
print(f"Avg Principal Payment: {cf.avg_principal_payment:>15,.0f} ILS")
print(f"Leveraged Rental Yield:{cf.leveraged_rental_yield:>15.2%}")
print(f"Net Leveraged Yield:   {cf.net_leveraged_yield:>15.2%}")

print("\n" + "=" * 80)
print("APPRECIATION METRICS (Group 3)")
print("=" * 80)
am = result.appreciation_metrics
print(f"Property Appreciation: {am.property_appreciation:>15,.0f} ILS")
print(f"Urban Renewal Apprec.: {am.urban_renewal_appreciation:>15,.0f} ILS")
print(f"Total Appreciation:    {am.total_appreciation:>15,.0f} ILS")
print(f"Sale Value:            {am.sale_value:>15,.0f} ILS")
print(f"Total Return Rate:     {am.total_return_rate:>15.2%}")
print(f"Annualized Return:     {am.annualized_return:>15.2%}")
print(f"Leveraged Return:      {am.leveraged_return:>15.2%}")
print(f"Net Annual Return:     {am.net_annual_return:>15.2%}")

print("\n" + "=" * 80)
print("EARLY REPAYMENT METRICS (Group 4)")
print("=" * 80)
er = result.early_repayment_metrics
print(f"Remaining Mortgage:    {er.remaining_mortgage:>15,.0f} ILS")
print(f"Early Repay Penalty:   {er.early_repayment_penalty:>15,.0f} ILS")
print(f"Total Debt to Bank:    {er.total_debt_to_bank:>15,.0f} ILS")
print(f"Proceeds Minus Debt:   {er.proceeds_minus_debt:>15,.0f} ILS")
print(f"Net Gain (Property):   {er.net_gain_property:>15,.0f} ILS")

print("\n" + "=" * 80)
print("PORTFOLIO METRICS (Group 5 - Alternative Investment)")
print("=" * 80)
pm = result.portfolio_metrics
print(f"Cash in Portfolio:     {pm.cash_in_portfolio:>15,.0f} ILS")
print(f"Initial Growth:        {pm.portfolio_initial_growth:>15,.0f} ILS")
print(f"Monthly Deposits:      {pm.monthly_deposits:>15,.0f} ILS")
print(f"Accumulated Deposits:  {pm.accumulated_deposits:>15,.0f} ILS")
print(f"Total Portfolio Value: {pm.total_portfolio_value:>15,.0f} ILS")
print(f"After Tax:             {pm.portfolio_after_tax:>15,.0f} ILS")
print(f"Net Portfolio Profit:  {pm.net_portfolio_profit:>15,.0f} ILS")

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Total Value at Sale:   {result.total_value_at_sale:>15,.0f} ILS")
print(f"Total Profit:          {result.total_profit:>15,.0f} ILS")
print(f"Annual Return:         {result.annual_return:>15.2%}")

print("\n" + "=" * 80)
print("VALIDATION")
print("=" * 80)
print(f"Is Valid:              {result.is_valid}")
if result.validation_errors:
    print("Errors:")
    for error in result.validation_errors:
        print(f"  - {error}")
else:
    print("No validation errors.")

print("\n" + "=" * 80)
print("COMPARISON: Real Estate vs Portfolio Only")
print("=" * 80)
# What if we invested everything in portfolio?
portfolio_only_initial = inputs.available_cash
portfolio_only_monthly = inputs.monthly_available
years = inputs.years_until_sale
from mortgage_return_scenario_calculator.financial import calculate_fv, calculate_compound_value

portfolio_only_growth = calculate_compound_value(portfolio_only_initial, assumptions.portfolio_return_rate, years)
portfolio_only_deposits = calculate_fv(assumptions.portfolio_return_rate/12, years*12, -portfolio_only_monthly)
portfolio_only_total = portfolio_only_growth + portfolio_only_deposits
total_contributions = portfolio_only_initial + (portfolio_only_monthly * years * 12)
portfolio_only_gains = portfolio_only_total - total_contributions
portfolio_only_tax = portfolio_only_gains * assumptions.capital_gains_tax_rate if portfolio_only_gains > 0 else 0
portfolio_only_after_tax = portfolio_only_total - portfolio_only_tax

print(f"Portfolio Only (no RE): {portfolio_only_after_tax:>15,.0f} ILS")
print(f"Real Estate + Portfolio:{result.total_value_at_sale:>15,.0f} ILS")
print(f"Difference:            {result.total_value_at_sale - portfolio_only_after_tax:>15,.0f} ILS")
print(f"Better Strategy:       {'Real Estate' if result.total_value_at_sale > portfolio_only_after_tax else 'Portfolio Only'}")

# Export to CSV
print("\n" + "=" * 80)
print("EXPORTING TO CSV")
print("=" * 80)
csv_path = export_scenario_to_csv(result, "data/output/scenario_result_new.csv")
print(f"Scenario exported to: {csv_path}")

