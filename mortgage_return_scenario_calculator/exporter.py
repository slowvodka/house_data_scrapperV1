"""Scenario result exporter to CSV.

This module provides functionality to export scenario results to CSV format
with variable name, value, and description columns.
"""

import csv
from pathlib import Path
from typing import Union, List, Tuple

from mortgage_return_scenario_calculator.models import (
    ScenarioResult,
    ScenarioInputs,
    InvestmentAssumptions,
    InvestmentRestrictions,
    LoanMetrics,
    CashFlowMetrics,
    AppreciationMetrics,
    EarlyRepaymentMetrics,
    PortfolioMetrics,
)


# Variable descriptions for all fields
VARIABLE_DESCRIPTIONS = {
    # Inputs
    "property_price": "Purchase price of the property",
    "down_payment": "Equity/down payment amount",
    "available_cash": "Total cash available for investment",
    "monthly_income": "Monthly net income (for mortgage validation)",
    "monthly_available": "Monthly amount available for investment",
    "mortgage_term_years": "Duration of mortgage in years",
    "years_until_sale": "Number of years until property will be sold",
    "urban_renewal_value": "Added value from urban renewal project",
    
    # Assumptions
    "rental_yield": "Annual rental yield as percentage of property value",
    "mortgage_rate": "Annual mortgage interest rate",
    "appreciation_rate": "Annual property appreciation rate",
    "rent_increase_rate": "Annual rent increase rate",
    "portfolio_return_rate": "Annual return for alternative portfolio investment",
    "risk_free_rate": "Risk-free rate for discounting",
    "early_repayment_rate": "Interest rate at early mortgage repayment",
    "capital_gains_tax_rate": "Capital gains tax rate",
    
    # Restrictions
    "max_mortgage_to_income_ratio": "Maximum mortgage payment as fraction of income",
    "min_down_payment_percentage": "Minimum down payment as fraction of price",
    "max_loan_to_value": "Maximum loan-to-value ratio",
    "max_mortgage_percentage": "Maximum mortgage as percentage of property value",
    "max_urban_renewal_value": "Maximum urban renewal value cap",
    "require_positive_cash_flow": "Whether positive monthly cash flow is required",
    
    # Loan Metrics
    "loan_amount": "Total mortgage/loan amount",
    "leverage_ratio": "Loan as fraction of property price",
    "equity_ratio": "Down payment as fraction of property price",
    "leverage_multiplier": "Leverage effect multiplier (1/equity_ratio)",
    "monthly_payment": "Monthly mortgage payment",
    "total_payments": "Total mortgage payments over loan term",
    "total_interest": "Total interest paid over loan term",
    "avg_monthly_interest": "Average monthly interest payment",
    "mortgage_to_income_ratio": "Monthly payment as percentage of monthly income",
    
    # Cash Flow Metrics
    "monthly_rent": "Monthly rental income",
    "rental_yield_actual": "Actual annual rental yield",
    "monthly_net_cash_flow": "Monthly cash flow (rent - mortgage payment)",
    "monthly_interest_flow": "Monthly cash flow from interest perspective",
    "avg_principal_payment": "Average monthly principal payment",
    "leveraged_rental_yield": "Rental yield multiplied by leverage",
    "net_leveraged_yield": "Leveraged yield minus mortgage rate",
    
    # Appreciation Metrics
    "property_appreciation": "Property value increase over holding period",
    "urban_renewal_appreciation": "Urban renewal value increase over holding period",
    "total_appreciation": "Total appreciation (property + urban renewal)",
    "sale_value": "Expected sale value at end of period",
    "total_return_rate": "Total return as percentage",
    "annualized_return": "Annualized return rate",
    "leveraged_return": "Annualized return multiplied by leverage",
    "net_annual_return": "Net annual return after financing costs",
    
    # Early Repayment Metrics
    "remaining_mortgage": "Remaining mortgage balance at sale",
    "early_repayment_penalty": "Penalty for early mortgage repayment",
    "total_debt_to_bank": "Total debt to bank at sale",
    "proceeds_minus_debt": "Sale proceeds minus bank debt",
    "net_gain_property": "Net gain from property investment",
    
    # Portfolio Metrics
    "cash_in_portfolio": "Cash invested in alternative portfolio",
    "portfolio_initial_growth": "Growth of initial portfolio investment",
    "monthly_deposits": "Monthly deposits to portfolio",
    "accumulated_deposits": "Value accumulated from monthly deposits",
    "total_portfolio_value": "Total portfolio value at sale time",
    "portfolio_after_tax": "Portfolio value after capital gains tax",
    "net_portfolio_profit": "Net profit from portfolio investment",
    
    # Final Summary
    "total_value_at_sale": "Total combined value at time of sale",
    "total_profit": "Total profit from investment",
    "annual_return": "Overall annualized return rate",
    "is_valid": "Whether scenario passes all restrictions",
}


def format_value(value: float, is_percentage: bool = False, is_currency: bool = False) -> str:
    """Format a value for display.
    
    Args:
        value: The value to format.
        is_percentage: Whether to format as percentage.
        is_currency: Whether to format as currency.
    
    Returns:
        Formatted string.
    """
    if isinstance(value, bool):
        return str(value)
    
    if is_percentage:
        return f"{value * 100:.2f}%"
    elif is_currency:
        return f"{value:,.0f}"
    else:
        return f"{value:,.2f}" if isinstance(value, float) else str(value)


class ScenarioExporter:
    """Exports scenario results to CSV format."""
    
    def __init__(self, result: ScenarioResult):
        """Initialize the exporter.
        
        Args:
            result: The scenario result to export.
        """
        self.result = result
    
    def _get_rows(self) -> List[Tuple[str, str, str]]:
        """Get all rows for export.
        
        Returns:
            List of (var_name, value, description) tuples.
        """
        rows = []
        
        # Section header helper
        def add_section(title: str):
            rows.append(("", "", ""))
            rows.append((f"=== {title} ===", "", ""))
        
        # User Inputs
        add_section("USER INPUTS")
        inputs = self.result.inputs
        rows.extend([
            ("property_price", format_value(inputs.property_price, is_currency=True), 
             VARIABLE_DESCRIPTIONS["property_price"]),
            ("down_payment", format_value(inputs.down_payment, is_currency=True), 
             VARIABLE_DESCRIPTIONS["down_payment"]),
            ("available_cash", format_value(inputs.available_cash, is_currency=True), 
             VARIABLE_DESCRIPTIONS["available_cash"]),
            ("monthly_income", format_value(inputs.monthly_income, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_income"]),
            ("monthly_available", format_value(inputs.monthly_available, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_available"]),
            ("mortgage_term_years", str(inputs.mortgage_term_years), 
             VARIABLE_DESCRIPTIONS["mortgage_term_years"]),
            ("years_until_sale", str(inputs.years_until_sale), 
             VARIABLE_DESCRIPTIONS["years_until_sale"]),
            ("urban_renewal_value", format_value(inputs.urban_renewal_value, is_currency=True), 
             VARIABLE_DESCRIPTIONS["urban_renewal_value"]),
        ])
        
        # Assumptions
        add_section("ASSUMPTIONS")
        assumptions = self.result.assumptions
        rows.extend([
            ("rental_yield", format_value(assumptions.rental_yield, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["rental_yield"]),
            ("mortgage_rate", format_value(assumptions.mortgage_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["mortgage_rate"]),
            ("appreciation_rate", format_value(assumptions.appreciation_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["appreciation_rate"]),
            ("rent_increase_rate", format_value(assumptions.rent_increase_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["rent_increase_rate"]),
            ("portfolio_return_rate", format_value(assumptions.portfolio_return_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["portfolio_return_rate"]),
            ("risk_free_rate", format_value(assumptions.risk_free_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["risk_free_rate"]),
            ("early_repayment_rate", format_value(assumptions.early_repayment_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["early_repayment_rate"]),
            ("capital_gains_tax_rate", format_value(assumptions.capital_gains_tax_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["capital_gains_tax_rate"]),
        ])
        
        # Loan Metrics
        add_section("LOAN METRICS")
        loan = self.result.loan_metrics
        rows.extend([
            ("loan_amount", format_value(loan.loan_amount, is_currency=True), 
             VARIABLE_DESCRIPTIONS["loan_amount"]),
            ("leverage_ratio", format_value(loan.leverage_ratio, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["leverage_ratio"]),
            ("equity_ratio", format_value(loan.equity_ratio, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["equity_ratio"]),
            ("leverage_multiplier", f"{loan.leverage_multiplier:.2f}x", 
             VARIABLE_DESCRIPTIONS["leverage_multiplier"]),
            ("monthly_payment", format_value(loan.monthly_payment, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_payment"]),
            ("total_payments", format_value(loan.total_payments, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_payments"]),
            ("total_interest", format_value(loan.total_interest, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_interest"]),
            ("avg_monthly_interest", format_value(loan.avg_monthly_interest, is_currency=True), 
             VARIABLE_DESCRIPTIONS["avg_monthly_interest"]),
            ("mortgage_to_income_ratio", format_value(loan.mortgage_to_income_ratio, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["mortgage_to_income_ratio"]),
        ])
        
        # Cash Flow Metrics
        add_section("CASH FLOW METRICS")
        cf = self.result.cash_flow_metrics
        rows.extend([
            ("monthly_rent", format_value(cf.monthly_rent, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_rent"]),
            ("rental_yield_actual", format_value(cf.rental_yield, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["rental_yield_actual"]),
            ("monthly_net_cash_flow", format_value(cf.monthly_net_cash_flow, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_net_cash_flow"]),
            ("monthly_interest_flow", format_value(cf.monthly_interest_flow, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_interest_flow"]),
            ("avg_principal_payment", format_value(cf.avg_principal_payment, is_currency=True), 
             VARIABLE_DESCRIPTIONS["avg_principal_payment"]),
            ("leveraged_rental_yield", format_value(cf.leveraged_rental_yield, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["leveraged_rental_yield"]),
            ("net_leveraged_yield", format_value(cf.net_leveraged_yield, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["net_leveraged_yield"]),
        ])
        
        # Appreciation Metrics
        add_section("APPRECIATION METRICS")
        app = self.result.appreciation_metrics
        rows.extend([
            ("property_appreciation", format_value(app.property_appreciation, is_currency=True), 
             VARIABLE_DESCRIPTIONS["property_appreciation"]),
            ("urban_renewal_appreciation", format_value(app.urban_renewal_appreciation, is_currency=True), 
             VARIABLE_DESCRIPTIONS["urban_renewal_appreciation"]),
            ("total_appreciation", format_value(app.total_appreciation, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_appreciation"]),
            ("sale_value", format_value(app.sale_value, is_currency=True), 
             VARIABLE_DESCRIPTIONS["sale_value"]),
            ("total_return_rate", format_value(app.total_return_rate, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["total_return_rate"]),
            ("annualized_return", format_value(app.annualized_return, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["annualized_return"]),
            ("leveraged_return", format_value(app.leveraged_return, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["leveraged_return"]),
            ("net_annual_return", format_value(app.net_annual_return, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["net_annual_return"]),
        ])
        
        # Early Repayment Metrics
        add_section("EARLY REPAYMENT METRICS")
        er = self.result.early_repayment_metrics
        rows.extend([
            ("remaining_mortgage", format_value(er.remaining_mortgage, is_currency=True), 
             VARIABLE_DESCRIPTIONS["remaining_mortgage"]),
            ("early_repayment_penalty", format_value(er.early_repayment_penalty, is_currency=True), 
             VARIABLE_DESCRIPTIONS["early_repayment_penalty"]),
            ("total_debt_to_bank", format_value(er.total_debt_to_bank, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_debt_to_bank"]),
            ("proceeds_minus_debt", format_value(er.proceeds_minus_debt, is_currency=True), 
             VARIABLE_DESCRIPTIONS["proceeds_minus_debt"]),
            ("net_gain_property", format_value(er.net_gain_property, is_currency=True), 
             VARIABLE_DESCRIPTIONS["net_gain_property"]),
        ])
        
        # Portfolio Metrics
        add_section("PORTFOLIO METRICS")
        pm = self.result.portfolio_metrics
        rows.extend([
            ("cash_in_portfolio", format_value(pm.cash_in_portfolio, is_currency=True), 
             VARIABLE_DESCRIPTIONS["cash_in_portfolio"]),
            ("portfolio_initial_growth", format_value(pm.portfolio_initial_growth, is_currency=True), 
             VARIABLE_DESCRIPTIONS["portfolio_initial_growth"]),
            ("monthly_deposits", format_value(pm.monthly_deposits, is_currency=True), 
             VARIABLE_DESCRIPTIONS["monthly_deposits"]),
            ("accumulated_deposits", format_value(pm.accumulated_deposits, is_currency=True), 
             VARIABLE_DESCRIPTIONS["accumulated_deposits"]),
            ("total_portfolio_value", format_value(pm.total_portfolio_value, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_portfolio_value"]),
            ("portfolio_after_tax", format_value(pm.portfolio_after_tax, is_currency=True), 
             VARIABLE_DESCRIPTIONS["portfolio_after_tax"]),
            ("net_portfolio_profit", format_value(pm.net_portfolio_profit, is_currency=True), 
             VARIABLE_DESCRIPTIONS["net_portfolio_profit"]),
        ])
        
        # Final Summary
        add_section("FINAL SUMMARY")
        rows.extend([
            ("total_value_at_sale", format_value(self.result.total_value_at_sale, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_value_at_sale"]),
            ("total_profit", format_value(self.result.total_profit, is_currency=True), 
             VARIABLE_DESCRIPTIONS["total_profit"]),
            ("annual_return", format_value(self.result.annual_return, is_percentage=True), 
             VARIABLE_DESCRIPTIONS["annual_return"]),
            ("is_valid", str(self.result.is_valid), 
             VARIABLE_DESCRIPTIONS["is_valid"]),
        ])
        
        # Validation errors if any
        if self.result.validation_errors:
            add_section("VALIDATION ERRORS")
            for i, error in enumerate(self.result.validation_errors, 1):
                rows.append((f"error_{i}", error, "Validation error message"))
        
        return rows
    
    def to_csv(self, filepath: Union[str, Path]) -> Path:
        """Export scenario to CSV file.
        
        Args:
            filepath: Path to save the CSV file.
        
        Returns:
            Path to the saved file.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        rows = self._get_rows()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Variable Name", "Value", "Description"])
            writer.writerows(rows)
        
        return filepath
    
    def to_string(self) -> str:
        """Export scenario to CSV string.
        
        Returns:
            CSV formatted string.
        """
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Variable Name", "Value", "Description"])
        writer.writerows(self._get_rows())
        return output.getvalue()


def export_scenario_to_csv(result: ScenarioResult, filepath: Union[str, Path]) -> Path:
    """Convenience function to export scenario to CSV.
    
    Args:
        result: The scenario result to export.
        filepath: Path to save the CSV file.
    
    Returns:
        Path to the saved file.
    """
    exporter = ScenarioExporter(result)
    return exporter.to_csv(filepath)

