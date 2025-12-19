"""Configuration generator for investment assumptions and restrictions.

This module provides utilities to generate default configurations and
customize them for different scenarios (conservative, moderate, aggressive).
"""

from dataclasses import asdict
from typing import Dict, Any, Optional

from mortgage_return_scenario_calculator.models import (
    InvestmentAssumptions,
    InvestmentRestrictions,
)


class ConfigGenerator:
    """Generator for investment assumptions and restrictions.
    
    Provides factory methods for creating default and preset configurations,
    as well as utilities for customization and export.
    
    Example:
        >>> generator = ConfigGenerator()
        >>> assumptions = generator.create_assumptions()  # Default assumptions
        >>> restrictions = generator.create_restrictions()  # Default restrictions
        >>> 
        >>> # Create conservative assumptions
        >>> conservative = generator.create_conservative_assumptions()
    """
    
    # Preset profiles
    CONSERVATIVE_PROFILE = {
        "rental_yield": 0.025,  # 2.5% - lower rental expectations
        "rent_increase_rate": 0.02,  # 2% - lower rent growth
        "mortgage_rate": 0.055,  # 5.5% - higher mortgage rate assumption
        "early_repayment_rate": 0.04,  # 4% - higher early repayment rate
        "appreciation_rate": 0.025,  # 2.5% - lower property appreciation
        "portfolio_return_rate": 0.05,  # 5% - lower portfolio return
        "risk_free_rate": 0.025,  # 2.5%
        "capital_gains_tax_rate": 0.25,  # 25%
    }
    
    MODERATE_PROFILE = {
        "rental_yield": 0.028,  # 2.8% - standard rental yield
        "rent_increase_rate": 0.03,  # 3% - standard rent growth
        "mortgage_rate": 0.048,  # 4.8% - current market rate
        "early_repayment_rate": 0.035,  # 3.5%
        "appreciation_rate": 0.04,  # 4% - standard appreciation
        "portfolio_return_rate": 0.07,  # 7% - standard portfolio return
        "risk_free_rate": 0.03,  # 3%
        "capital_gains_tax_rate": 0.25,  # 25%
    }
    
    AGGRESSIVE_PROFILE = {
        "rental_yield": 0.032,  # 3.2% - optimistic rental yield
        "rent_increase_rate": 0.04,  # 4% - higher rent growth
        "mortgage_rate": 0.042,  # 4.2% - optimistic rate assumption
        "early_repayment_rate": 0.03,  # 3%
        "appreciation_rate": 0.06,  # 6% - optimistic appreciation
        "portfolio_return_rate": 0.10,  # 10% - optimistic portfolio return
        "risk_free_rate": 0.03,  # 3%
        "capital_gains_tax_rate": 0.25,  # 25%
    }
    
    @staticmethod
    def create_assumptions(
        rental_yield: Optional[float] = None,
        rent_increase_rate: Optional[float] = None,
        mortgage_rate: Optional[float] = None,
        early_repayment_rate: Optional[float] = None,
        appreciation_rate: Optional[float] = None,
        portfolio_return_rate: Optional[float] = None,
        risk_free_rate: Optional[float] = None,
        capital_gains_tax_rate: Optional[float] = None,
    ) -> InvestmentAssumptions:
        """Create investment assumptions with optional overrides.
        
        Creates InvestmentAssumptions with default values, allowing
        specific fields to be overridden.
        
        Args:
            rental_yield: Annual rental yield (default 2.8%).
            rent_increase_rate: Annual rent increase (default 3%).
            mortgage_rate: Annual mortgage rate (default 4.8%).
            early_repayment_rate: Early repayment rate (default 3.5%).
            appreciation_rate: Property appreciation (default 4%).
            portfolio_return_rate: Portfolio return (default 7%).
            risk_free_rate: Risk-free rate (default 3%).
            capital_gains_tax_rate: Capital gains tax (default 25%).
        
        Returns:
            InvestmentAssumptions instance.
        
        Example:
            >>> assumptions = ConfigGenerator.create_assumptions(
            ...     mortgage_rate=0.05,  # Override mortgage rate to 5%
            ...     appreciation_rate=0.035  # Override appreciation to 3.5%
            ... )
        """
        defaults = InvestmentAssumptions()
        
        return InvestmentAssumptions(
            rental_yield=rental_yield if rental_yield is not None else defaults.rental_yield,
            rent_increase_rate=rent_increase_rate if rent_increase_rate is not None else defaults.rent_increase_rate,
            mortgage_rate=mortgage_rate if mortgage_rate is not None else defaults.mortgage_rate,
            early_repayment_rate=early_repayment_rate if early_repayment_rate is not None else defaults.early_repayment_rate,
            appreciation_rate=appreciation_rate if appreciation_rate is not None else defaults.appreciation_rate,
            portfolio_return_rate=portfolio_return_rate if portfolio_return_rate is not None else defaults.portfolio_return_rate,
            risk_free_rate=risk_free_rate if risk_free_rate is not None else defaults.risk_free_rate,
            capital_gains_tax_rate=capital_gains_tax_rate if capital_gains_tax_rate is not None else defaults.capital_gains_tax_rate,
        )
    
    @classmethod
    def create_conservative_assumptions(cls) -> InvestmentAssumptions:
        """Create conservative investment assumptions.
        
        Conservative assumptions use lower expected returns and higher costs,
        suitable for risk-averse investors.
        
        Returns:
            InvestmentAssumptions with conservative values.
        """
        return InvestmentAssumptions(**cls.CONSERVATIVE_PROFILE)
    
    @classmethod
    def create_moderate_assumptions(cls) -> InvestmentAssumptions:
        """Create moderate investment assumptions.
        
        Moderate assumptions use market-standard values,
        suitable for balanced investors.
        
        Returns:
            InvestmentAssumptions with moderate (default) values.
        """
        return InvestmentAssumptions(**cls.MODERATE_PROFILE)
    
    @classmethod
    def create_aggressive_assumptions(cls) -> InvestmentAssumptions:
        """Create aggressive investment assumptions.
        
        Aggressive assumptions use higher expected returns and lower costs,
        suitable for risk-tolerant investors.
        
        Returns:
            InvestmentAssumptions with aggressive values.
        """
        return InvestmentAssumptions(**cls.AGGRESSIVE_PROFILE)
    
    @staticmethod
    def create_restrictions(
        max_mortgage_to_income_ratio: Optional[float] = None,
        min_down_payment_percentage: Optional[float] = None,
        max_loan_to_value: Optional[float] = None,
        max_urban_renewal_value: Optional[float] = None,
        require_positive_cash_flow: Optional[bool] = None,
    ) -> InvestmentRestrictions:
        """Create investment restrictions with optional overrides.
        
        Creates InvestmentRestrictions with default values, allowing
        specific fields to be overridden.
        
        Args:
            max_mortgage_to_income_ratio: Max mortgage/income ratio (default 30%).
            min_down_payment_percentage: Min down payment % (default 0%).
            max_loan_to_value: Max LTV ratio (default 75%).
            max_urban_renewal_value: Max urban renewal cap (default 400,000).
            require_positive_cash_flow: Require positive cash flow (default False).
        
        Returns:
            InvestmentRestrictions instance.
        """
        defaults = InvestmentRestrictions()
        
        return InvestmentRestrictions(
            max_mortgage_to_income_ratio=(
                max_mortgage_to_income_ratio 
                if max_mortgage_to_income_ratio is not None 
                else defaults.max_mortgage_to_income_ratio
            ),
            min_down_payment_percentage=(
                min_down_payment_percentage 
                if min_down_payment_percentage is not None 
                else defaults.min_down_payment_percentage
            ),
            max_loan_to_value=(
                max_loan_to_value 
                if max_loan_to_value is not None 
                else defaults.max_loan_to_value
            ),
            max_urban_renewal_value=(
                max_urban_renewal_value 
                if max_urban_renewal_value is not None 
                else defaults.max_urban_renewal_value
            ),
            require_positive_cash_flow=(
                require_positive_cash_flow 
                if require_positive_cash_flow is not None 
                else defaults.require_positive_cash_flow
            ),
        )
    
    @staticmethod
    def create_strict_restrictions() -> InvestmentRestrictions:
        """Create strict investment restrictions.
        
        Strict restrictions enforce conservative lending standards,
        suitable for banks or conservative investors.
        
        Returns:
            InvestmentRestrictions with strict values.
        """
        return InvestmentRestrictions(
            max_mortgage_to_income_ratio=0.25,  # 25% max
            min_down_payment_percentage=0.25,  # 25% minimum down payment
            max_loan_to_value=0.70,  # 70% max LTV
            max_urban_renewal_value=300_000,
            require_positive_cash_flow=True,
        )
    
    @staticmethod
    def create_lenient_restrictions() -> InvestmentRestrictions:
        """Create lenient investment restrictions.
        
        Lenient restrictions allow more leverage and flexibility,
        suitable for aggressive investors.
        
        Returns:
            InvestmentRestrictions with lenient values.
        """
        return InvestmentRestrictions(
            max_mortgage_to_income_ratio=0.40,  # 40% max
            min_down_payment_percentage=0.10,  # 10% minimum down payment
            max_loan_to_value=0.90,  # 90% max LTV
            max_urban_renewal_value=500_000,
            require_positive_cash_flow=False,
        )
    
    @staticmethod
    def assumptions_to_dict(assumptions: InvestmentAssumptions) -> Dict[str, Any]:
        """Convert assumptions to dictionary.
        
        Args:
            assumptions: InvestmentAssumptions instance.
        
        Returns:
            Dictionary representation of assumptions.
        """
        return asdict(assumptions)
    
    @staticmethod
    def restrictions_to_dict(restrictions: InvestmentRestrictions) -> Dict[str, Any]:
        """Convert restrictions to dictionary.
        
        Args:
            restrictions: InvestmentRestrictions instance.
        
        Returns:
            Dictionary representation of restrictions.
        """
        return asdict(restrictions)
    
    @staticmethod
    def assumptions_from_dict(data: Dict[str, Any]) -> InvestmentAssumptions:
        """Create assumptions from dictionary.
        
        Args:
            data: Dictionary with assumption values.
        
        Returns:
            InvestmentAssumptions instance.
        """
        return InvestmentAssumptions(**data)
    
    @staticmethod
    def restrictions_from_dict(data: Dict[str, Any]) -> InvestmentRestrictions:
        """Create restrictions from dictionary.
        
        Args:
            data: Dictionary with restriction values.
        
        Returns:
            InvestmentRestrictions instance.
        """
        return InvestmentRestrictions(**data)
    
    @staticmethod
    def get_assumption_descriptions() -> Dict[str, str]:
        """Get descriptions for all assumption fields.
        
        Returns:
            Dictionary mapping field names to descriptions.
        """
        return {
            "rental_yield": "Annual rental yield as percentage of property price (e.g., 0.028 = 2.8%)",
            "rent_increase_rate": "Annual rate at which rent increases (e.g., 0.03 = 3%)",
            "mortgage_rate": "Annual mortgage interest rate (e.g., 0.048 = 4.8%)",
            "early_repayment_rate": "Interest rate used for early repayment penalty calculation",
            "appreciation_rate": "Annual property value appreciation rate (e.g., 0.04 = 4%)",
            "portfolio_return_rate": "Expected annual return for alternative portfolio investment",
            "risk_free_rate": "Risk-free rate used for discounting future cash flows",
            "capital_gains_tax_rate": "Tax rate applied to capital gains (e.g., 0.25 = 25%)",
        }
    
    @staticmethod
    def get_restriction_descriptions() -> Dict[str, str]:
        """Get descriptions for all restriction fields.
        
        Returns:
            Dictionary mapping field names to descriptions.
        """
        return {
            "max_mortgage_to_income_ratio": "Maximum mortgage payment as fraction of monthly income",
            "min_down_payment_percentage": "Minimum down payment as fraction of property price",
            "max_loan_to_value": "Maximum loan amount as fraction of property value",
            "max_urban_renewal_value": "Maximum value that can be attributed to urban renewal",
            "require_positive_cash_flow": "Whether monthly cash flow must be positive",
        }

