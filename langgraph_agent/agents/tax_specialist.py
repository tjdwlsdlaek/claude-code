"""Tax specialist agent for tax calculations."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any
from langchain_aws import ChatBedrock
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from common.tools import TaxCalculator
import logging

logger = logging.getLogger(__name__)


def create_tax_specialist_agent(llm: ChatBedrock, tax_calculator: TaxCalculator) -> AgentExecutor:
    """Create a tax specialist agent.

    Args:
        llm: Language model
        tax_calculator: Tax calculator

    Returns:
        Agent executor
    """

    def calculate_acquisition_tax(input_str: str) -> str:
        """Calculate acquisition tax. Format: property_price|is_first_home|area_m2|is_adjusted"""
        try:
            parts = input_str.split("|")
            property_price = int(parts[0])
            is_first_home = parts[1].lower() == "true"
            area_m2 = float(parts[2]) if len(parts) > 2 else 85.0
            is_adjusted = parts[3].lower() == "true" if len(parts) > 3 else False

            result = tax_calculator.calculate_acquisition_tax(
                property_price, is_first_home, area_m2, is_adjusted
            )

            output = [
                "\n=== 취득세 계산 ===",
                f"매매가격: {property_price:,}원",
                f"기본 취득세: {result['acquisition_tax']:,}원 ({result['base_rate']}%)",
                f"지방교육세: {result['local_education_tax']:,}원",
            ]

            if result['agricultural_tax'] > 0:
                output.append(f"농어촌특별세: {result['agricultural_tax']:,}원")

            output.append(f"\n총 취득세: {result['total_acquisition_tax']:,}원")
            output.append(f"적용: {result['exemption_desc']}")

            return "\n".join(output)
        except Exception as e:
            return f"계산 중 오류: {e}"

    def calculate_annual_tax(price: str) -> str:
        """Calculate annual property tax."""
        try:
            property_price = int(price)
            annual_tax = tax_calculator.calculate_property_tax_annual(property_price)

            output = [
                "\n=== 연간 보유세 (재산세) ===",
                f"매매가격: {property_price:,}원",
                f"연간 재산세: {annual_tax:,}원",
                f"월 예상 부담: {annual_tax // 12:,}원"
            ]

            # Check comprehensive real estate tax
            comp_tax = tax_calculator.calculate_comprehensive_real_estate_tax(
                property_price, is_single_home=True
            )

            if comp_tax > 0:
                output.append(f"\n종합부동산세: {comp_tax:,}원")
                output.append(f"총 연간 보유세: {annual_tax + comp_tax:,}원")
            else:
                output.append("\n종합부동산세: 해당 없음 (공시가격 12억 이하)")

            return "\n".join(output)
        except Exception as e:
            return f"계산 중 오류: {e}"

    def calculate_transfer_tax(input_str: str) -> str:
        """Calculate transfer tax. Format: purchase_price|sale_price|holding_years|is_single"""
        try:
            parts = input_str.split("|")
            purchase_price = int(parts[0])
            sale_price = int(parts[1])
            holding_years = int(parts[2])
            is_single = parts[3].lower() == "true" if len(parts) > 3 else True

            result = tax_calculator.calculate_transfer_tax_estimate(
                purchase_price, sale_price, holding_years, is_single
            )

            if result['capital_gain'] <= 0:
                return "\n양도차익이 없어 양도세가 발생하지 않습니다."

            output = [
                "\n=== 양도소득세 예상 ===",
                f"구매가: {purchase_price:,}원",
                f"매도가: {sale_price:,}원",
                f"양도차익: {result['capital_gain']:,}원",
            ]

            if 'total_transfer_tax' in result:
                output.extend([
                    f"\n장기보유특별공제: {result.get('deduction_rate', 0)}%",
                    f"과세 대상 차익: {result.get('taxable_gain', 0):,}원",
                    f"양도소득세: {result.get('transfer_tax', 0):,}원",
                    f"지방소득세: {result.get('local_income_tax', 0):,}원",
                    f"\n총 양도세: {result['total_transfer_tax']:,}원",
                    f"실효세율: {result['effective_rate']:.2f}%"
                ])

            output.append(f"\n{result['exemption_desc']}")

            return "\n".join(output)
        except Exception as e:
            return f"계산 중 오류: {e}"

    def get_tax_benefits(input_str: str) -> str:
        """Get available tax benefits. Format: is_first|age|area|price"""
        try:
            parts = input_str.split("|")
            is_first = parts[0].lower() == "true"
            age = int(parts[1])
            area = float(parts[2])
            price = int(parts[3])

            benefits = tax_calculator.get_available_tax_benefits(
                is_first, age, area, price
            )

            output = ["\n=== 적용 가능한 세금 혜택 ==="]
            for i, benefit in enumerate(benefits, 1):
                output.append(f"{i}. {benefit}")

            return "\n".join(output)
        except Exception as e:
            return f"분석 중 오류: {e}"

    tools = [
        Tool(
            name="calculate_acquisition_tax",
            func=calculate_acquisition_tax,
            description="취득세를 계산합니다. 입력 형식: 매매가격|생애최초여부|전용면적|조정지역여부 (예: 350000000|true|84.5|true)"
        ),
        Tool(
            name="calculate_annual_tax",
            func=calculate_annual_tax,
            description="연간 보유세(재산세, 종부세)를 계산합니다. 입력: 매매가격 (예: 350000000)"
        ),
        Tool(
            name="calculate_transfer_tax",
            func=calculate_transfer_tax,
            description="양도소득세를 예상합니다. 입력 형식: 구매가|매도가|보유년수|1주택여부 (예: 350000000|400000000|5|true)"
        ),
        Tool(
            name="get_tax_benefits",
            func=get_tax_benefits,
            description="적용 가능한 세금 혜택을 조회합니다. 입력 형식: 생애최초|나이|면적|가격 (예: true|35|84.5|350000000)"
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 부동산 세무 전문가입니다. 각종 부동산 관련 세금을 계산하고 절세 방안을 조언합니다.

주요 업무:
1. 취득세 계산 및 감면 혜택 분석
2. 재산세, 종합부동산세 계산
3. 양도소득세 예상 및 절세 전략
4. 적용 가능한 세금 혜택 안내

세금 계산 시 고려사항:
- 생애최초 주택 구매 감면 (6억 이하, 85㎡ 이하)
- 1주택 양도세 비과세 (2년 보유, 공시가격 12억 이하)
- 장기보유특별공제
- 조정대상지역 중과세

모든 세금을 정확히 계산하고, 절세 방법을 구체적으로 안내하세요."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=4,
        handle_parsing_errors=True
    )

    return agent_executor


def calculate_taxes(
    user_query: Dict[str, Any],
    policy_analysis: str,
    llm: ChatBedrock,
    tax_calculator: TaxCalculator
) -> Dict[str, Any]:
    """Calculate all taxes.

    Args:
        user_query: User query
        policy_analysis: Policy analysis output
        llm: Language model
        tax_calculator: Tax calculator

    Returns:
        Tax calculation results
    """
    agent = create_tax_specialist_agent(llm, tax_calculator)

    is_first_home = user_query.get('age', 0) <= 40
    is_adjusted = "조정대상지역" in policy_analysis or "투기과열지구" in policy_analysis
    target_price = (user_query.get('target_price_min', 0) + user_query.get('target_price_max', 0)) // 2

    tax_query = f"""
다음 사용자의 부동산 취득 및 보유에 따른 세금을 계산해주세요:

[사용자 정보]
- 나이: {user_query.get('age')}세
- 목표 매매가: {target_price:,}원
- 생애최초 구매: {is_first_home}
- 조정대상지역: {is_adjusted}
- 전용면적: 84㎡ (가정)

다음을 계산해주세요:
1. 취득세 (생애최초 감면 고려)
2. 등록세 및 인지세
3. 연간 재산세 (월 부담액 포함)
4. 종합부동산세 해당 여부
5. 적용 가능한 세금 혜택
6. 향후 매도 시 양도세 (5년 보유, 20% 상승 가정)

초기 납부 세금과 보유 기간 동안의 세금 부담을 명확히 구분하여 설명해주세요.
"""

    try:
        result = agent.invoke({"input": tax_query})
        return {
            "success": True,
            "tax_output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    except Exception as e:
        logger.error(f"Tax specialist error: {e}")
        return {
            "success": False,
            "error": str(e),
            "tax_output": ""
        }
