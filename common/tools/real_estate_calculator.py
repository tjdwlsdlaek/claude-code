"""Real estate loan and financial calculations."""

import math
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RealEstateCalculator:
    """Calculator for real estate loans and financial metrics."""

    # 2024년 기준 규제 지역별 LTV/DTI 한도
    LTV_LIMITS = {
        "투기과열지구": 0.50,  # 50%
        "조정대상지역": 0.50,  # 50%
        "일반지역": 0.70,      # 70%
        "생애최초": 0.80       # 80% (생애최초 특례)
    }

    DTI_LIMITS = {
        "투기과열지구": 0.40,  # 40%
        "조정대상지역": 0.50,  # 50%
        "일반지역": 0.60       # 60%
    }

    # DSR 한도 (총부채원리금상환비율)
    DSR_LIMIT = 0.40  # 40%

    def __init__(self):
        """Initialize calculator."""
        pass

    def calculate_ltv(
        self,
        property_price: int,
        region_type: str = "조정대상지역",
        is_first_home: bool = False
    ) -> Tuple[float, int]:
        """Calculate LTV and maximum loan amount.

        Args:
            property_price: Property price in KRW
            region_type: Type of region (투기과열지구, 조정대상지역, 일반지역)
            is_first_home: Whether this is first home purchase

        Returns:
            Tuple of (LTV ratio, max loan amount)
        """
        if is_first_home and property_price <= 600_000_000:  # 6억 이하 생애최초
            ltv_ratio = self.LTV_LIMITS["생애최초"]
        else:
            ltv_ratio = self.LTV_LIMITS.get(region_type, 0.50)

        max_loan = int(property_price * ltv_ratio)
        return ltv_ratio, max_loan

    def calculate_dti(
        self,
        annual_income: int,
        property_price: int,
        interest_rate: float,
        loan_term_years: int,
        region_type: str = "조정대상지역",
        other_debt_payment: int = 0
    ) -> Tuple[float, int]:
        """Calculate DTI and maximum loan amount.

        Args:
            annual_income: Annual income in KRW
            property_price: Property price in KRW
            interest_rate: Annual interest rate (e.g., 4.5 for 4.5%)
            loan_term_years: Loan term in years
            region_type: Type of region
            other_debt_payment: Annual payment for other debts

        Returns:
            Tuple of (DTI ratio, max loan amount under DTI)
        """
        dti_limit = self.DTI_LIMITS.get(region_type, 0.40)
        max_annual_payment = annual_income * dti_limit - other_debt_payment

        # Calculate maximum loan amount based on monthly payment limit
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term_years * 12
        max_monthly_payment = max_annual_payment / 12

        if monthly_rate > 0:
            # Use loan payment formula: P = L[c(1 + c)^n]/[(1 + c)^n - 1]
            # Solving for L (loan amount): L = P * [(1 + c)^n - 1] / [c(1 + c)^n]
            max_loan = max_monthly_payment * (
                (math.pow(1 + monthly_rate, num_payments) - 1) /
                (monthly_rate * math.pow(1 + monthly_rate, num_payments))
            )
        else:
            max_loan = max_monthly_payment * num_payments

        max_loan = int(max_loan)
        dti_ratio = (other_debt_payment + (max_loan / loan_term_years)) / annual_income

        return dti_ratio, max_loan

    def calculate_dsr(
        self,
        annual_income: int,
        loan_amount: int,
        interest_rate: float,
        loan_term_years: int,
        other_debt_payment: int = 0
    ) -> Tuple[float, bool]:
        """Calculate DSR (Debt Service Ratio).

        Args:
            annual_income: Annual income in KRW
            loan_amount: Desired loan amount in KRW
            interest_rate: Annual interest rate (e.g., 4.5 for 4.5%)
            loan_term_years: Loan term in years
            other_debt_payment: Annual payment for other debts

        Returns:
            Tuple of (DSR ratio, whether it complies with regulation)
        """
        # Calculate annual payment for the loan
        monthly_payment = self.calculate_monthly_payment(
            loan_amount, interest_rate, loan_term_years
        )
        annual_loan_payment = monthly_payment * 12

        # DSR = (총 부채 원리금 상환액) / 연소득
        total_annual_payment = annual_loan_payment + other_debt_payment
        dsr_ratio = total_annual_payment / annual_income if annual_income > 0 else 0

        is_compliant = dsr_ratio <= self.DSR_LIMIT

        return dsr_ratio, is_compliant

    def calculate_monthly_payment(
        self,
        loan_amount: int,
        interest_rate: float,
        loan_term_years: int
    ) -> int:
        """Calculate monthly loan payment.

        Args:
            loan_amount: Loan amount in KRW
            interest_rate: Annual interest rate (e.g., 4.5 for 4.5%)
            loan_term_years: Loan term in years

        Returns:
            Monthly payment amount
        """
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term_years * 12

        if monthly_rate > 0:
            # Monthly payment formula: P = L[c(1 + c)^n]/[(1 + c)^n - 1]
            monthly_payment = loan_amount * (
                monthly_rate * math.pow(1 + monthly_rate, num_payments)
            ) / (math.pow(1 + monthly_rate, num_payments) - 1)
        else:
            monthly_payment = loan_amount / num_payments

        return int(monthly_payment)

    def calculate_total_interest(
        self,
        loan_amount: int,
        interest_rate: float,
        loan_term_years: int
    ) -> int:
        """Calculate total interest over loan term.

        Args:
            loan_amount: Loan amount in KRW
            interest_rate: Annual interest rate
            loan_term_years: Loan term in years

        Returns:
            Total interest amount
        """
        monthly_payment = self.calculate_monthly_payment(
            loan_amount, interest_rate, loan_term_years
        )
        total_payment = monthly_payment * loan_term_years * 12
        total_interest = total_payment - loan_amount

        return int(total_interest)

    def calculate_maximum_loan(
        self,
        property_price: int,
        annual_income: int,
        interest_rate: float = 4.5,
        loan_term_years: int = 30,
        region_type: str = "조정대상지역",
        is_first_home: bool = False,
        other_debt_payment: int = 0
    ) -> Dict:
        """Calculate maximum possible loan considering all regulations.

        Args:
            property_price: Property price in KRW
            annual_income: Annual income in KRW
            interest_rate: Annual interest rate
            loan_term_years: Loan term in years
            region_type: Type of region
            is_first_home: Whether this is first home purchase
            other_debt_payment: Annual payment for other debts

        Returns:
            Dictionary with loan calculation details
        """
        # Calculate LTV limit
        ltv_ratio, ltv_max_loan = self.calculate_ltv(
            property_price, region_type, is_first_home
        )

        # Calculate DTI limit
        dti_ratio, dti_max_loan = self.calculate_dti(
            annual_income, property_price, interest_rate,
            loan_term_years, region_type, other_debt_payment
        )

        # Maximum loan is the minimum of LTV and DTI
        max_loan_amount = min(ltv_max_loan, dti_max_loan)

        # Check DSR compliance
        dsr_ratio, is_dsr_compliant = self.calculate_dsr(
            annual_income, max_loan_amount, interest_rate,
            loan_term_years, other_debt_payment
        )

        # If DSR is not compliant, reduce loan amount
        if not is_dsr_compliant:
            # Binary search for maximum loan that satisfies DSR
            low, high = 0, max_loan_amount
            while high - low > 100_000:  # 10만원 단위로 조정
                mid = (low + high) // 2
                dsr, compliant = self.calculate_dsr(
                    annual_income, mid, interest_rate,
                    loan_term_years, other_debt_payment
                )
                if compliant:
                    low = mid
                else:
                    high = mid
            max_loan_amount = low
            dsr_ratio, is_dsr_compliant = self.calculate_dsr(
                annual_income, max_loan_amount, interest_rate,
                loan_term_years, other_debt_payment
            )

        # Calculate payment details
        monthly_payment = self.calculate_monthly_payment(
            max_loan_amount, interest_rate, loan_term_years
        )
        total_interest = self.calculate_total_interest(
            max_loan_amount, interest_rate, loan_term_years
        )

        return {
            "ltv_ratio": ltv_ratio * 100,
            "dti_ratio": dti_ratio * 100,
            "dsr_ratio": dsr_ratio * 100,
            "max_loan_amount": max_loan_amount,
            "monthly_payment": monthly_payment,
            "interest_rate": interest_rate,
            "loan_term_years": loan_term_years,
            "total_interest": total_interest,
            "is_dsr_compliant": is_dsr_compliant,
            "limiting_factor": "LTV" if ltv_max_loan < dti_max_loan else "DTI"
        }

    def calculate_brokerage_fee(self, property_price: int) -> Dict:
        """Calculate real estate brokerage fee.

        Args:
            property_price: Property price in KRW

        Returns:
            Dictionary with fee calculation details
        """
        # 2024년 주택 매매 중개보수 요율 (상한)
        if property_price < 50_000_000:
            rate = 0.006  # 0.6%
            upper_limit = 250_000
        elif property_price < 200_000_000:
            rate = 0.005  # 0.5%
            upper_limit = 800_000
        elif property_price < 600_000_000:
            rate = 0.004  # 0.4%
            upper_limit = None  # No upper limit
        elif property_price < 900_000_000:
            rate = 0.005  # 0.5%
            upper_limit = None
        else:
            rate = 0.009  # 0.9%
            upper_limit = None

        fee_amount = int(property_price * rate)

        if upper_limit and fee_amount > upper_limit:
            fee_amount = upper_limit

        return {
            "property_price": property_price,
            "fee_rate": rate * 100,
            "fee_amount": fee_amount,
            "upper_limit": upper_limit
        }
