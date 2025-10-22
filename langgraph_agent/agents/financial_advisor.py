"""Financial advisor agent for loan and budget calculations."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any
from langchain_aws import ChatBedrock
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from common.tools import RealEstateCalculator
import logging

logger = logging.getLogger(__name__)


def create_financial_advisor_agent(llm: ChatBedrock, calculator: RealEstateCalculator) -> AgentExecutor:
    """Create a financial advisor agent.

    Args:
        llm: Language model
        calculator: Real estate calculator

    Returns:
        Agent executor
    """

    def calculate_maximum_loan(input_str: str) -> str:
        """Calculate maximum loan. Format: property_price|annual_income|region_type|is_first_home"""
        try:
            parts = input_str.split("|")
            property_price = int(parts[0])
            annual_income = int(parts[1])
            region_type = parts[2]
            is_first_home = parts[3].lower() == "true"

            result = calculator.calculate_maximum_loan(
                property_price=property_price,
                annual_income=annual_income,
                region_type=region_type,
                is_first_home=is_first_home
            )

            output = [
                "\n=== 대출 계산 결과 ===",
                f"매매가격: {property_price:,}원",
                f"최대 대출 가능 금액: {result['max_loan_amount']:,}원",
                f"필요 자기자본: {property_price - result['max_loan_amount']:,}원",
                "",
                "규제 비율:",
                f"  - LTV: {result['ltv_ratio']:.1f}%",
                f"  - DTI: {result['dti_ratio']:.1f}%",
                f"  - DSR: {result['dsr_ratio']:.1f}%",
                f"  - 제한 요인: {result['limiting_factor']}",
                f"  - DSR 준수: {'예' if result['is_dsr_compliant'] else '아니오'}",
                "",
                "대출 상세:",
                f"  - 대출 금리: {result['interest_rate']}%",
                f"  - 대출 기간: {result['loan_term_years']}년",
                f"  - 월 상환액: {result['monthly_payment']:,}원",
                f"  - 총 이자: {result['total_interest']:,}원",
                f"  - 총 상환액: {result['max_loan_amount'] + result['total_interest']:,}원"
            ]

            return "\n".join(output)
        except Exception as e:
            return f"계산 중 오류: {e}"

    def calculate_brokerage_fee(price: str) -> str:
        """Calculate brokerage fee."""
        try:
            property_price = int(price)
            result = calculator.calculate_brokerage_fee(property_price)

            output = [
                "\n=== 중개수수료 계산 ===",
                f"매매가격: {result['property_price']:,}원",
                f"수수료율: {result['fee_rate']}%",
                f"중개수수료: {result['fee_amount']:,}원"
            ]

            if result['upper_limit']:
                output.append(f"법정 상한액: {result['upper_limit']:,}원")

            return "\n".join(output)
        except Exception as e:
            return f"계산 중 오류: {e}"

    def calculate_monthly_budget(input_str: str) -> str:
        """Calculate affordable monthly budget. Format: annual_income|other_expenses"""
        try:
            parts = input_str.split("|")
            annual_income = int(parts[0])
            other_expenses = int(parts[1]) if len(parts) > 1 else 0

            monthly_income = annual_income / 12

            # DSR 40% 기준 월 상환 가능액
            max_monthly_payment = (annual_income * 0.40) / 12 - (other_expenses / 12)

            # 권장 월 상환액 (소득의 30%)
            recommended_payment = monthly_income * 0.30

            output = [
                "\n=== 월 예산 분석 ===",
                f"월 소득: {int(monthly_income):,}원",
                f"DSR 40% 기준 최대 월 상환액: {int(max_monthly_payment):,}원",
                f"권장 월 상환액 (소득의 30%): {int(recommended_payment):,}원",
                "",
                "재무 건전성 평가:",
                f"  - 여유 자금 (월): {int(monthly_income - max_monthly_payment):,}원"
            ]

            return "\n".join(output)
        except Exception as e:
            return f"계산 중 오류: {e}"

    tools = [
        Tool(
            name="calculate_maximum_loan",
            func=calculate_maximum_loan,
            description="최대 대출 가능 금액을 계산합니다. 입력 형식: 매매가격|연소득|지역유형|생애최초여부 (예: 350000000|70000000|조정대상지역|true)"
        ),
        Tool(
            name="calculate_brokerage_fee",
            func=calculate_brokerage_fee,
            description="부동산 중개수수료를 계산합니다. 입력: 매매가격 (예: 350000000)"
        ),
        Tool(
            name="calculate_monthly_budget",
            func=calculate_monthly_budget,
            description="월 예산과 상환 능력을 분석합니다. 입력 형식: 연소득|기타지출 (예: 70000000|0)"
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 부동산 재무 설계 전문가입니다. 대출 계산과 재무 계획을 수립하는 역할을 합니다.

주요 업무:
1. 최대 대출 가능 금액 계산
2. 필요 자기자본 산정
3. 월 상환액 및 이자 계산
4. 중개수수료 계산
5. 재무 건전성 평가

계산 시 고려사항:
- LTV, DTI, DSR 규제 모두 고려
- 현실적인 금리 적용 (4.5% 기준)
- 30년 만기 기준
- 생애최초 구매자 혜택 고려

모든 금액은 원 단위로 정확히 계산하고, 월 상환 부담을 명확히 설명하세요."""),
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


def calculate_financial_plan(
    user_query: Dict[str, Any],
    policy_analysis: str,
    llm: ChatBedrock,
    calculator: RealEstateCalculator
) -> Dict[str, Any]:
    """Calculate financial plan.

    Args:
        user_query: User query
        policy_analysis: Policy analysis output
        llm: Language model
        calculator: Real estate calculator

    Returns:
        Financial plan results
    """
    agent = create_financial_advisor_agent(llm, calculator)

    # Determine region type from policy analysis
    region_type = "조정대상지역"  # Default
    if "투기과열지구" in policy_analysis:
        region_type = "투기과열지구"
    elif "일반지역" in policy_analysis:
        region_type = "일반지역"

    # Assume first home if age is 30s and first purchase
    is_first_home = user_query.get('age', 0) >= 20 and user_query.get('age', 0) <= 40

    target_price = (user_query.get('target_price_min', 0) + user_query.get('target_price_max', 0)) // 2

    financial_query = f"""
다음 사용자의 재무 계획을 수립해주세요:

[사용자 정보]
- 나이: {user_query.get('age')}세
- 연봉: {user_query.get('annual_income'):,}원
- 보유 예금: {user_query.get('savings'):,}원
- 목표 매매가: {target_price:,}원
- 지역 규제: {region_type}
- 생애최초 구매: {is_first_home}

[정책 분석 결과]
{policy_analysis}

다음을 계산해주세요:
1. 목표 매매가에서 최대 대출 가능 금액
2. 필요한 자기자본 (계약금, 중도금, 잔금 포함)
3. 월 상환액과 상환 부담
4. 중개수수료
5. 현재 보유 예금으로 구매 가능 여부
6. 부족한 금액이 있다면 추가 필요 자금

재무 건전성을 고려한 현실적인 조언을 제공해주세요.
"""

    try:
        result = agent.invoke({"input": financial_query})
        return {
            "success": True,
            "financial_output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    except Exception as e:
        logger.error(f"Financial advisor error: {e}")
        return {
            "success": False,
            "error": str(e),
            "financial_output": ""
        }
