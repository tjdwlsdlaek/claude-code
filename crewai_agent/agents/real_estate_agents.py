"""Real estate agent definitions for CrewAI."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from crewai import Agent
from crewai_tools import tool
from common.tools import BraveSearchTool, RealEstateCalculator, TaxCalculator, PolicyAnalyzer
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Global tool instances
brave_search: Optional[BraveSearchTool] = None
calculator: Optional[RealEstateCalculator] = None
tax_calculator: Optional[TaxCalculator] = None
policy_analyzer: Optional[PolicyAnalyzer] = None


def initialize_tools(brave_api_key: str):
    """Initialize global tool instances."""
    global brave_search, calculator, tax_calculator, policy_analyzer
    brave_search = BraveSearchTool(api_key=brave_api_key)
    calculator = RealEstateCalculator()
    tax_calculator = TaxCalculator()
    policy_analyzer = PolicyAnalyzer()


@tool("search_real_estate_policy")
def search_policy_tool(query: str = "") -> str:
    """최신 부동산 정책을 검색합니다."""
    if not brave_search:
        return "도구가 초기화되지 않았습니다."

    results = brave_search.search_real_estate_policy()
    if not results:
        return "검색 결과를 찾을 수 없습니다."

    output = ["최신 부동산 정책:\n"]
    for i, result in enumerate(results[:5], 1):
        output.append(f"{i}. {result['title']}")
        output.append(f"   {result['description']}")
        output.append(f"   출처: {result['url']}\n")

    return "\n".join(output)


@tool("search_loan_regulations")
def search_loan_tool(region: str) -> str:
    """특정 지역의 대출 규제를 검색합니다."""
    if not brave_search:
        return "도구가 초기화되지 않았습니다."

    results = brave_search.search_loan_regulations(region)
    if not results:
        return f"{region}에 대한 검색 결과를 찾을 수 없습니다."

    output = [f"{region} 대출 규제:\n"]
    for i, result in enumerate(results[:5], 1):
        output.append(f"{i}. {result['title']}")
        output.append(f"   {result['description']}\n")

    return "\n".join(output)


@tool("determine_region_type")
def region_type_tool(region: str) -> str:
    """지역의 규제 유형을 판단합니다 (투기과열지구/조정대상지역/일반지역)."""
    if not policy_analyzer:
        return "도구가 초기화되지 않았습니다."

    region_type = policy_analyzer.determine_region_type(region)
    return f"{region}은(는) '{region_type}'입니다."


@tool("calculate_maximum_loan")
def loan_calculator_tool(property_price: int, annual_income: int, region_type: str, is_first_home: bool) -> str:
    """최대 대출 가능 금액을 계산합니다."""
    if not calculator:
        return "도구가 초기화되지 않았습니다."

    result = calculator.calculate_maximum_loan(
        property_price=property_price,
        annual_income=annual_income,
        region_type=region_type,
        is_first_home=is_first_home
    )

    output = [
        f"\n최대 대출: {result['max_loan_amount']:,}원",
        f"필요 자기자본: {property_price - result['max_loan_amount']:,}원",
        f"월 상환액: {result['monthly_payment']:,}원",
        f"LTV: {result['ltv_ratio']:.1f}%, DTI: {result['dti_ratio']:.1f}%, DSR: {result['dsr_ratio']:.1f}%"
    ]

    return "\n".join(output)


@tool("calculate_brokerage_fee")
def brokerage_tool(property_price: int) -> str:
    """부동산 중개수수료를 계산합니다."""
    if not calculator:
        return "도구가 초기화되지 않았습니다."

    result = calculator.calculate_brokerage_fee(property_price)
    return f"중개수수료: {result['fee_amount']:,}원 ({result['fee_rate']}%)"


@tool("calculate_acquisition_tax")
def acquisition_tax_tool(property_price: int, is_first_home: bool, is_adjusted: bool) -> str:
    """취득세를 계산합니다."""
    if not tax_calculator:
        return "도구가 초기화되지 않았습니다."

    result = tax_calculator.calculate_acquisition_tax(
        property_price,
        is_first_home,
        property_area_m2=84.0,
        is_adjusted_area=is_adjusted
    )

    output = [
        f"\n총 취득세: {result['total_acquisition_tax']:,}원",
        f"({result['exemption_desc']})"
    ]

    return "\n".join(output)


@tool("calculate_property_tax")
def property_tax_tool(property_price: int) -> str:
    """연간 재산세를 계산합니다."""
    if not tax_calculator:
        return "도구가 초기화되지 않았습니다."

    annual_tax = tax_calculator.calculate_property_tax_annual(property_price)
    return f"연간 재산세: {annual_tax:,}원 (월 {annual_tax // 12:,}원)"


def create_researcher(llm_config: Dict[str, Any]) -> Agent:
    """Create researcher agent."""
    return Agent(
        role="부동산 정책 연구원",
        goal="최신 부동산 정책, 규제, 시장 동향을 조사하고 정확한 정보를 수집합니다",
        backstory="""당신은 부동산 시장과 정책을 전문적으로 연구하는 전문가입니다.
        정부 정책, 대출 규제, 시장 동향에 대한 최신 정보를 수집하고 분석하는 데 탁월한 능력을 가지고 있습니다.
        모든 정보는 신뢰할 수 있는 출처에서 가져오며, 정확한 데이터를 제공합니다.""",
        tools=[search_policy_tool, search_loan_tool],
        verbose=True,
        llm=llm_config.get("model"),
        max_iter=5
    )


def create_policy_analyst(llm_config: Dict[str, Any]) -> Agent:
    """Create policy analyst agent."""
    return Agent(
        role="부동산 정책 분석가",
        goal="부동산 규제와 정책을 분석하고 사용자에게 적용되는 내용을 명확히 설명합니다",
        backstory="""당신은 복잡한 부동산 규제를 이해하고 해석하는 전문 분석가입니다.
        LTV, DTI, DSR과 같은 금융 규제부터 지역별 투기 규제까지 모든 정책을 꿰뚫고 있습니다.
        규제가 실제로 사용자에게 어떤 영향을 미치는지 명확하게 설명할 수 있습니다.""",
        tools=[region_type_tool],
        verbose=True,
        llm=llm_config.get("model"),
        max_iter=3
    )


def create_financial_advisor(llm_config: Dict[str, Any]) -> Agent:
    """Create financial advisor agent."""
    return Agent(
        role="부동산 재무 설계사",
        goal="대출 가능 금액을 계산하고 현실적인 재무 계획을 수립합니다",
        backstory="""당신은 부동산 구매를 위한 재무 계획을 전문으로 하는 설계사입니다.
        대출 규제를 고려한 정확한 대출 가능 금액 계산, 월 상환액 시뮬레이션,
        자기자본 필요액 산정 등 모든 재무적 측면을 다룹니다.
        사용자의 소득과 자산 상황에 맞는 현실적인 계획을 제시합니다.""",
        tools=[loan_calculator_tool, brokerage_tool],
        verbose=True,
        llm=llm_config.get("model"),
        max_iter=4
    )


def create_tax_specialist(llm_config: Dict[str, Any]) -> Agent:
    """Create tax specialist agent."""
    return Agent(
        role="부동산 세무 전문가",
        goal="부동산 관련 모든 세금을 계산하고 절세 방안을 제시합니다",
        backstory="""당신은 부동산 세무를 전문으로 하는 세무사입니다.
        취득세, 재산세, 종합부동산세, 양도소득세 등 모든 부동산 관련 세금에 정통합니다.
        생애최초 구매자 감면, 장기보유특별공제 등 각종 세금 혜택도 잘 알고 있어
        최적의 절세 전략을 제시할 수 있습니다.""",
        tools=[acquisition_tax_tool, property_tax_tool],
        verbose=True,
        llm=llm_config.get("model"),
        max_iter=4
    )


def create_strategy_coordinator(llm_config: Dict[str, Any]) -> Agent:
    """Create strategy coordinator agent."""
    return Agent(
        role="부동산 구매 전략 코디네이터",
        goal="모든 전문가의 의견을 종합하여 실행 가능한 주택 구매 전략을 수립합니다",
        backstory="""당신은 부동산 구매 프로세스 전체를 총괄하는 전략 코디네이터입니다.
        시장 조사, 정책 분석, 재무 계획, 세금 전략을 모두 고려하여
        30대 구매자가 실제로 실행할 수 있는 단계별 전략을 수립합니다.
        위험 요소를 명확히 알리고, 대안도 함께 제시하는 현실적인 조언자입니다.""",
        tools=[],
        verbose=True,
        llm=llm_config.get("model"),
        max_iter=3
    )
