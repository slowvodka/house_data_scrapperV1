"""Tests for financial calculation functions.

Run only calculator tests with: pytest -m calculator
"""
import pytest
import numpy_financial as npf

from mortgage_return_scenario_calculator.financial import (
    calculate_pmt,
    calculate_fv,
    calculate_pv,
    calculate_compound_growth,
    calculate_compound_value,
    calculate_annualized_return,
    calculate_nper,
    calculate_ipmt,
    calculate_ppmt,
    calculate_npv,
    calculate_irr,
)


pytestmark = pytest.mark.calculator


class TestCalculatePmt:
    """Tests for the PMT (payment) function."""
    
    def test_basic_mortgage_payment(self):
        """Test basic mortgage payment calculation."""
        # 1M loan, 4.8% rate, 20 years
        payment = calculate_pmt(0.048, 240, 1_000_000)
        
        # Verify against numpy-financial directly
        expected = -npf.pmt(0.048/12, 240, 1_000_000)
        assert abs(payment - expected) < 0.01
    
    def test_zero_principal(self):
        """Test PMT with zero principal returns 0."""
        assert calculate_pmt(0.05, 120, 0) == 0.0
    
    def test_zero_rate(self):
        """Test PMT with zero rate (simple division)."""
        payment = calculate_pmt(0, 120, 120_000)
        assert payment == 1_000  # 120,000 / 120 months
    
    def test_short_term_loan(self):
        """Test short-term loan calculation."""
        # 500K loan, 5% rate, 5 years
        payment = calculate_pmt(0.05, 60, 500_000)
        expected = -npf.pmt(0.05/12, 60, 500_000)
        assert abs(payment - expected) < 0.01
    
    def test_high_rate_loan(self):
        """Test loan with high interest rate."""
        # 100K loan, 15% rate, 10 years
        payment = calculate_pmt(0.15, 120, 100_000)
        expected = -npf.pmt(0.15/12, 120, 100_000)
        assert abs(payment - expected) < 0.01


class TestCalculateFv:
    """Tests for the FV (future value) function."""
    
    def test_basic_future_value(self):
        """Test basic future value calculation."""
        # 1000/month for 15 years at 7% annual
        fv = calculate_fv(0.07/12, 180, -1000)
        expected = npf.fv(0.07/12, 180, -1000, 0)
        assert abs(fv - expected) < 0.01
    
    def test_with_present_value(self):
        """Test FV with initial present value."""
        fv = calculate_fv(0.07/12, 120, -500, -10000)
        expected = npf.fv(0.07/12, 120, -500, -10000)
        assert abs(fv - expected) < 0.01
    
    def test_zero_rate(self):
        """Test FV with zero rate."""
        fv = calculate_fv(0, 60, -1000, -10000)
        # Should be simple addition: 10000 + 60*1000 = 70000
        assert fv == 70000


class TestCalculatePv:
    """Tests for the PV (present value) function."""
    
    def test_basic_present_value(self):
        """Test basic present value calculation."""
        pv = calculate_pv(0.048/12, 60, 5000)
        expected = npf.pv(0.048/12, 60, 5000)
        assert abs(pv - expected) < 0.01
    
    def test_zero_rate(self):
        """Test PV with zero rate."""
        pv = calculate_pv(0, 60, -1000)
        assert pv == 60000  # 60 * 1000


class TestCalculateCompoundGrowth:
    """Tests for compound growth calculations."""
    
    def test_basic_compound_growth(self):
        """Test basic compound growth."""
        growth = calculate_compound_growth(1_000_000, 0.04, 15)
        expected = 1_000_000 * ((1.04 ** 15) - 1)
        assert abs(growth - expected) < 0.01
    
    def test_zero_years(self):
        """Test compound growth with zero years."""
        growth = calculate_compound_growth(1_000_000, 0.04, 0)
        assert growth == 0.0
    
    def test_zero_rate(self):
        """Test compound growth with zero rate."""
        growth = calculate_compound_growth(1_000_000, 0, 15)
        assert growth == 0.0


class TestCalculateCompoundValue:
    """Tests for compound value calculations."""
    
    def test_basic_compound_value(self):
        """Test basic compound value."""
        value = calculate_compound_value(1_000_000, 0.04, 15)
        expected = 1_000_000 * (1.04 ** 15)
        assert abs(value - expected) < 0.01
    
    def test_zero_years(self):
        """Test compound value with zero years returns principal."""
        value = calculate_compound_value(1_000_000, 0.04, 0)
        assert value == 1_000_000
    
    def test_zero_rate(self):
        """Test compound value with zero rate returns principal."""
        value = calculate_compound_value(1_000_000, 0, 15)
        assert value == 1_000_000


class TestCalculateAnnualizedReturn:
    """Tests for annualized return calculations."""
    
    def test_basic_annualized_return(self):
        """Test basic annualized return."""
        annual = calculate_annualized_return(0.8, 15)  # 80% over 15 years
        expected = (1.8 ** (1/15)) - 1
        assert abs(annual - expected) < 0.0001
    
    def test_zero_years(self):
        """Test annualized return with zero years."""
        annual = calculate_annualized_return(0.5, 0)
        assert annual == 0.0
    
    def test_zero_return(self):
        """Test annualized return with zero total return."""
        annual = calculate_annualized_return(0, 10)
        assert annual == 0.0


class TestCalculateNper:
    """Tests for number of periods calculation."""
    
    def test_basic_nper(self):
        """Test basic number of periods calculation."""
        nper = calculate_nper(0.05/12, -500, 10000)
        expected = npf.nper(0.05/12, -500, 10000)
        assert abs(nper - expected) < 0.01
    
    def test_zero_rate(self):
        """Test nper with zero rate."""
        nper = calculate_nper(0, -1000, 10000)
        assert nper == 10  # 10000 / 1000


class TestCalculateIpmt:
    """Tests for interest portion of payment."""
    
    def test_first_month_interest(self):
        """Test first month interest calculation."""
        ipmt = calculate_ipmt(0.048/12, 1, 240, 1_000_000)
        expected = -npf.ipmt(0.048/12, 1, 240, 1_000_000)
        assert abs(ipmt - expected) < 0.01
    
    def test_last_month_interest(self):
        """Test last month interest (should be minimal)."""
        ipmt = calculate_ipmt(0.048/12, 240, 240, 1_000_000)
        expected = -npf.ipmt(0.048/12, 240, 240, 1_000_000)
        assert abs(ipmt - expected) < 0.01
    
    def test_zero_rate(self):
        """Test ipmt with zero rate."""
        ipmt = calculate_ipmt(0, 1, 120, 1_000_000)
        assert ipmt == 0.0


class TestCalculatePpmt:
    """Tests for principal portion of payment."""
    
    def test_first_month_principal(self):
        """Test first month principal calculation."""
        ppmt = calculate_ppmt(0.048/12, 1, 240, 1_000_000)
        expected = -npf.ppmt(0.048/12, 1, 240, 1_000_000)
        assert abs(ppmt - expected) < 0.01
    
    def test_zero_rate(self):
        """Test ppmt with zero rate (equal principal payments)."""
        ppmt = calculate_ppmt(0, 1, 120, 120_000)
        assert ppmt == 1_000  # 120,000 / 120


class TestCalculateNpv:
    """Tests for Net Present Value calculation."""
    
    def test_basic_npv(self):
        """Test basic NPV calculation."""
        cashflows = [-100, 50, 50, 50]
        npv_result = calculate_npv(0.1, cashflows)
        expected = npf.npv(0.1, cashflows)
        assert abs(npv_result - expected) < 0.01
    
    def test_empty_cashflows(self):
        """Test NPV with empty cashflows."""
        assert calculate_npv(0.1, []) == 0.0


class TestCalculateIrr:
    """Tests for Internal Rate of Return calculation."""
    
    def test_basic_irr(self):
        """Test basic IRR calculation."""
        cashflows = [-100, 50, 50, 50]
        irr = calculate_irr(cashflows)
        expected = npf.irr(cashflows)
        assert abs(irr - expected) < 0.0001
    
    def test_empty_cashflows(self):
        """Test IRR with empty cashflows."""
        assert calculate_irr([]) == 0.0
    
    def test_single_value(self):
        """Test IRR with single value."""
        assert calculate_irr([100]) == 0.0

