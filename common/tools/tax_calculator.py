"""Tax calculation tools for real estate transactions."""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class TaxCalculator:
    """Calculator for real estate related taxes."""

    def __init__(self):
        """Initialize tax calculator."""
        pass

    def calculate_acquisition_tax(
        self,
        property_price: int,
        is_first_home: bool = False,
        property_area_m2: float = 85.0,
        is_adjusted_area: bool = False
    ) -> Dict:
        """Calculate acquisition tax (취득세).

        Args:
            property_price: Property price in KRW
            is_first_home: Whether this is first home purchase
            property_area_m2: Property area in square meters (전용면적)
            is_adjusted_area: Whether the property is in adjusted target area (조정대상지역)

        Returns:
            Dictionary with tax calculation details
        """
        # Base rates
        if property_price <= 600_000_000 and is_first_home and property_area_m2 <= 85:
            # 생애최초 주택 취득세 감면
            base_rate = 0.01  # 1% (with possible exemptions)
            exemption_desc = "생애최초 주택 감면 적용"
        elif is_adjusted_area:
            # 조정대상지역 중과세
            if property_price <= 600_000_000:
                base_rate = 0.01  # 1%
            elif property_price <= 900_000_000:
                base_rate = 0.013  # 1~3% (progressive)
            else:
                base_rate = 0.03  # 3%
            exemption_desc = "조정대상지역 세율 적용"
        else:
            # 일반 세율
            if property_price <= 600_000_000:
                base_rate = 0.01  # 1%
            elif property_price <= 900_000_000:
                base_rate = 0.013  # 1~3% (progressive)
            else:
                base_rate = 0.03  # 3%
            exemption_desc = "일반 세율 적용"

        # Calculate acquisition tax
        acquisition_tax = int(property_price * base_rate)

        # Add local education tax (지방교육세) - 10% of acquisition tax
        local_education_tax = int(acquisition_tax * 0.1)

        # Add agricultural special tax (농어촌특별세) for high-value properties
        if property_price > 600_000_000 and not is_first_home:
            agricultural_tax = int(acquisition_tax * 0.2)
        else:
            agricultural_tax = 0

        total_acquisition_tax = acquisition_tax + local_education_tax + agricultural_tax

        return {
            "acquisition_tax": acquisition_tax,
            "local_education_tax": local_education_tax,
            "agricultural_tax": agricultural_tax,
            "total_acquisition_tax": total_acquisition_tax,
            "base_rate": base_rate * 100,
            "exemption_desc": exemption_desc
        }

    def calculate_registration_tax(self, property_price: int) -> int:
        """Calculate registration tax (등록세).

        Args:
            property_price: Property price in KRW

        Returns:
            Registration tax amount
        """
        # 등록세는 취득세에 포함되어 있음 (2021년 이후)
        # 등록면허세 (Registration license tax)
        base_tax = int(property_price * 0.002)  # 0.2%
        local_education_tax = int(base_tax * 0.2)  # 20% of registration tax

        return base_tax + local_education_tax

    def calculate_stamp_duty(self, property_price: int) -> int:
        """Calculate stamp duty (인지세).

        Args:
            property_price: Property price in KRW

        Returns:
            Stamp duty amount
        """
        # 인지세 (Stamp duty) for property transaction
        if property_price < 50_000_000:
            return 0
        elif property_price < 100_000_000:
            return 50_000
        else:
            return 150_000

    def calculate_property_tax_annual(
        self,
        property_price: int,
        official_price_ratio: float = 0.6
    ) -> int:
        """Calculate annual property tax (재산세).

        Args:
            property_price: Property price in KRW
            official_price_ratio: Ratio of official price to market price (usually 0.6-0.7)

        Returns:
            Annual property tax amount
        """
        # Calculate based on official price (공시가격)
        official_price = int(property_price * official_price_ratio)

        # Property tax rates (progressive)
        if official_price <= 60_000_000:
            rate = 0.001  # 0.1%
        elif official_price <= 150_000_000:
            rate = 0.0015  # 0.15%
        elif official_price <= 300_000_000:
            rate = 0.0025  # 0.25%
        else:
            rate = 0.004  # 0.4%

        property_tax = int(official_price * rate)

        # Add local education tax (20% of property tax)
        local_education_tax = int(property_tax * 0.2)

        # Add urban planning tax (typically 0.14% of official price for urban areas)
        urban_planning_tax = int(official_price * 0.0014)

        total_annual_tax = property_tax + local_education_tax + urban_planning_tax

        return total_annual_tax

    def calculate_comprehensive_real_estate_tax(
        self,
        property_price: int,
        is_single_home: bool = True,
        official_price_ratio: float = 0.6
    ) -> int:
        """Calculate comprehensive real estate tax (종합부동산세).

        Args:
            property_price: Property price in KRW
            is_single_home: Whether this is the only home owned
            official_price_ratio: Ratio of official price to market price

        Returns:
            Comprehensive real estate tax amount (0 if below threshold)
        """
        official_price = int(property_price * official_price_ratio)

        # Threshold for comprehensive real estate tax
        if is_single_home:
            threshold = 1_200_000_000  # 12억 (1 home)
        else:
            threshold = 600_000_000  # 6억 (multiple homes)

        if official_price <= threshold:
            return 0

        # Calculate tax on amount exceeding threshold
        taxable_amount = official_price - threshold

        # Progressive tax rates
        if taxable_amount <= 300_000_000:
            rate = 0.006  # 0.6%
        elif taxable_amount <= 600_000_000:
            rate = 0.008  # 0.8%
        elif taxable_amount <= 1_200_000_000:
            rate = 0.012  # 1.2%
        else:
            rate = 0.016  # 1.6%

        comprehensive_tax = int(taxable_amount * rate)

        return comprehensive_tax

    def calculate_transfer_tax_estimate(
        self,
        purchase_price: int,
        expected_sale_price: int,
        holding_period_years: int,
        is_single_home: bool = True
    ) -> Dict:
        """Estimate transfer tax (양도소득세).

        Args:
            purchase_price: Original purchase price in KRW
            expected_sale_price: Expected sale price in KRW
            holding_period_years: Years of holding the property
            is_single_home: Whether this is the only home owned

        Returns:
            Dictionary with transfer tax estimation
        """
        # Calculate capital gain
        capital_gain = expected_sale_price - purchase_price

        if capital_gain <= 0:
            return {
                "capital_gain": capital_gain,
                "transfer_tax": 0,
                "effective_rate": 0,
                "exemption_desc": "양도차익 없음"
            }

        # Check for exemptions
        if is_single_home and holding_period_years >= 2:
            # 1 home, held for more than 2 years - may be exempt
            return {
                "capital_gain": capital_gain,
                "transfer_tax": 0,
                "effective_rate": 0,
                "exemption_desc": "1주택 2년 이상 보유 비과세 (공시가격 12억 이하 기준)"
            }

        # Calculate long-term holding deduction
        if holding_period_years >= 3:
            deduction_rate = min(0.10 * (holding_period_years - 2), 0.30)  # Max 30%
        else:
            deduction_rate = 0

        # Calculate taxable gain
        taxable_gain = int(capital_gain * (1 - deduction_rate))

        # Progressive tax rates for transfer tax
        if taxable_gain <= 12_000_000:
            rate = 0.06  # 6%
        elif taxable_gain <= 46_000_000:
            rate = 0.15  # 15%
        elif taxable_gain <= 88_000_000:
            rate = 0.24  # 24%
        elif taxable_gain <= 150_000_000:
            rate = 0.35  # 35%
        elif taxable_gain <= 300_000_000:
            rate = 0.38  # 38%
        elif taxable_gain <= 500_000_000:
            rate = 0.40  # 40%
        else:
            rate = 0.45  # 45%

        transfer_tax = int(taxable_gain * rate)

        # Add local income tax (10% of transfer tax)
        local_income_tax = int(transfer_tax * 0.1)
        total_transfer_tax = transfer_tax + local_income_tax

        return {
            "capital_gain": capital_gain,
            "deduction_rate": deduction_rate * 100,
            "taxable_gain": taxable_gain,
            "transfer_tax": transfer_tax,
            "local_income_tax": local_income_tax,
            "total_transfer_tax": total_transfer_tax,
            "effective_rate": (total_transfer_tax / capital_gain * 100) if capital_gain > 0 else 0,
            "exemption_desc": f"{int(deduction_rate * 100)}% 장기보유특별공제 적용"
        }

    def get_available_tax_benefits(
        self,
        is_first_home: bool,
        age: int,
        property_area_m2: float,
        property_price: int
    ) -> List[str]:
        """Get list of available tax benefits.

        Args:
            is_first_home: Whether this is first home purchase
            age: Buyer's age
            property_area_m2: Property area in square meters
            property_price: Property price in KRW

        Returns:
            List of available tax benefits
        """
        benefits = []

        # 생애최초 주택 구입 감면
        if is_first_home and property_price <= 600_000_000 and property_area_m2 <= 85:
            benefits.append("생애최초 주택 구입 취득세 감면 (최대 200만원)")

        # 신혼부부 특례
        if age <= 40 and is_first_home:
            benefits.append("신혼부부 취득세 감면 검토 가능")

        # 장기보유 특별공제 (향후)
        benefits.append("3년 이상 보유시 양도세 장기보유특별공제 적용 가능")

        # 1주택 비과세
        if is_first_home:
            benefits.append("2년 이상 보유 후 매도시 1주택 양도세 비과세 가능 (공시가격 12억 이하)")

        return benefits
