"""Financial calculation functions.

This module provides Excel-compatible financial functions using numpy-financial:
- PMT: Calculate monthly payment
- FV: Calculate future value
- PV: Calculate present value
- Compound growth calculations
"""

import numpy_financial as npf


def calculate_pmt(rate: float, nper: int, pv: float) -> float:
    """Calculate periodic payment (Excel PMT function).
    
    Calculates the monthly payment for a loan based on constant payments
    and a constant interest rate. Uses numpy-financial for accuracy.
    
    Args:
        rate: Annual interest rate as decimal (e.g., 0.048 for 4.8%).
              Will be converted to monthly rate internally.
        nper: Total number of payment periods (months).
        pv: Present value (loan amount, positive).
    
    Returns:
        Monthly payment amount (positive value).
    
    Example:
        >>> calculate_pmt(0.048, 240, 1_000_000)  # 4.8% rate, 20 years, 1M loan
        6542.44  # Approximate monthly payment
    """
    if pv == 0:
        return 0.0
    
    if rate == 0:
        return pv / nper
    
    monthly_rate = rate / 12
    # npf.pmt returns negative value for payment, so we negate it
    payment = -npf.pmt(monthly_rate, nper, pv)
    
    return payment


def calculate_fv(rate: float, nper: int, pmt: float, pv: float = 0) -> float:
    """Calculate future value (Excel FV function).
    
    Calculates the future value of an investment based on periodic,
    constant payments and a constant interest rate. Uses numpy-financial.
    
    Args:
        rate: Interest rate per period as decimal.
        nper: Total number of payment periods.
        pmt: Payment made each period (negative for deposits).
        pv: Present value / initial investment (default 0).
    
    Returns:
        Future value of the investment.
    
    Example:
        >>> calculate_fv(0.07/12, 180, -1000)  # 7% annual, 15 years, 1000/month
        317,163.59  # Approximate future value
    """
    if rate == 0:
        return -(pv + pmt * nper)
    
    # npf.fv returns the future value
    fv = npf.fv(rate, nper, pmt, pv)
    return fv


def calculate_pv(rate: float, nper: int, pmt: float) -> float:
    """Calculate present value (Excel PV function).
    
    Calculates the present value of a loan or investment based on
    a constant interest rate. Uses numpy-financial.
    
    Args:
        rate: Interest rate per period as decimal.
        nper: Total number of payment periods.
        pmt: Payment made each period.
    
    Returns:
        Present value.
    
    Example:
        >>> calculate_pv(0.048/12, 60, 5000)  # 4.8% annual, 5 years, 5000/month
        265,988.48  # Approximate present value
    """
    if rate == 0:
        return -pmt * nper
    
    pv = npf.pv(rate, nper, pmt)
    return pv


def calculate_compound_growth(principal: float, rate: float, years: float) -> float:
    """Calculate compound growth over a period using npf.fv.
    
    Calculates the growth amount (not total value) from compound interest.
    
    Args:
        principal: Initial amount.
        rate: Annual growth rate as decimal.
        years: Number of years.
    
    Returns:
        Growth amount (final - principal).
    
    Example:
        >>> calculate_compound_growth(1_000_000, 0.04, 15)  # 4% for 15 years
        800,943.69  # Approximate growth
    """
    if years <= 0 or rate == 0:
        return 0.0
    
    # npf.fv with pv=-principal, pmt=0 gives future value
    # Growth = FV - principal
    future_value = npf.fv(rate, years, 0, -principal)
    return future_value - principal


def calculate_compound_value(principal: float, rate: float, years: float) -> float:
    """Calculate total value after compound growth using npf.fv.
    
    Args:
        principal: Initial amount.
        rate: Annual growth rate as decimal.
        years: Number of years.
    
    Returns:
        Total value (principal + growth).
    
    Example:
        >>> calculate_compound_value(1_000_000, 0.04, 15)
        1,800,943.69  # Approximate total value
    """
    if years <= 0:
        return principal
    if rate == 0:
        return principal
    
    # npf.fv with pv=-principal, pmt=0 gives future value directly
    return npf.fv(rate, years, 0, -principal)


def calculate_annualized_return(total_return: float, years: float) -> float:
    """Calculate annualized return from total return using npf.rate.
    
    Converts a total return over multiple years to an equivalent
    annual return rate.
    
    Args:
        total_return: Total return as decimal (e.g., 0.5 for 50%).
        years: Number of years.
    
    Returns:
        Annualized return as decimal.
    
    Example:
        >>> calculate_annualized_return(0.8, 15)  # 80% over 15 years
        0.0398  # ~4% annual return
    """
    if years <= 0:
        return 0.0
    if total_return == 0:
        return 0.0
    
    # npf.rate finds the rate that grows pv to fv over nper periods
    # pv=-1, fv=1+total_return, pmt=0, nper=years
    return npf.rate(years, 0, -1, 1 + total_return)


def calculate_nper(rate: float, pmt: float, pv: float, fv: float = 0) -> float:
    """Calculate number of periods using npf.nper.
    
    Calculates the number of payment periods for a loan or investment.
    
    Args:
        rate: Interest rate per period as decimal.
        pmt: Payment made each period.
        pv: Present value.
        fv: Future value (default 0).
    
    Returns:
        Number of periods.
    
    Example:
        >>> calculate_nper(0.05/12, -500, 10000)  # 5% annual, $500/month, $10000 loan
        21.07  # ~21 months to pay off
    """
    if rate == 0:
        if pmt == 0:
            return 0.0
        return -(pv + fv) / pmt
    
    return npf.nper(rate, pmt, pv, fv)


def calculate_ipmt(rate: float, per: int, nper: int, pv: float) -> float:
    """Calculate interest portion of payment for a specific period using npf.ipmt.
    
    Args:
        rate: Interest rate per period as decimal.
        per: Period number (1-indexed).
        nper: Total number of periods.
        pv: Present value (loan amount).
    
    Returns:
        Interest portion of payment (positive value).
    
    Example:
        >>> calculate_ipmt(0.048/12, 1, 240, 1_000_000)  # First month interest
        4000.00  # First month interest payment
    """
    if rate == 0 or pv == 0:
        return 0.0
    
    # npf.ipmt returns negative for interest paid, so negate
    return -npf.ipmt(rate, per, nper, pv)


def calculate_ppmt(rate: float, per: int, nper: int, pv: float) -> float:
    """Calculate principal portion of payment for a specific period using npf.ppmt.
    
    Args:
        rate: Interest rate per period as decimal.
        per: Period number (1-indexed).
        nper: Total number of periods.
        pv: Present value (loan amount).
    
    Returns:
        Principal portion of payment (positive value).
    
    Example:
        >>> calculate_ppmt(0.048/12, 1, 240, 1_000_000)  # First month principal
        2542.44  # First month principal payment
    """
    if rate == 0:
        return pv / nper if nper > 0 else 0.0
    if pv == 0:
        return 0.0
    
    # npf.ppmt returns negative for principal paid, so negate
    return -npf.ppmt(rate, per, nper, pv)


def calculate_npv(rate: float, cashflows: list[float]) -> float:
    """Calculate Net Present Value using npf.npv.
    
    Args:
        rate: Discount rate per period.
        cashflows: List of cash flows (first value is at period 1).
    
    Returns:
        Net present value.
    
    Example:
        >>> calculate_npv(0.1, [-100, 50, 50, 50])
        24.34  # NPV at 10% discount rate
    """
    if not cashflows:
        return 0.0
    
    return npf.npv(rate, cashflows)


def calculate_irr(cashflows: list[float]) -> float:
    """Calculate Internal Rate of Return using npf.irr.
    
    Args:
        cashflows: List of cash flows (typically starts with negative initial investment).
    
    Returns:
        Internal rate of return as decimal.
    
    Example:
        >>> calculate_irr([-100, 50, 50, 50])
        0.2338  # ~23.38% IRR
    """
    if not cashflows or len(cashflows) < 2:
        return 0.0
    
    result = npf.irr(cashflows)
    # npf.irr may return nan if no solution
    if result != result:  # Check for NaN
        return 0.0
    return result

