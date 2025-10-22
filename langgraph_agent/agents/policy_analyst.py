"""Policy analyst agent for analyzing regulations."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any
from langchain_aws import ChatBedrock
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from common.tools import PolicyAnalyzer
import logging

logger = logging.getLogger(__name__)


def create_policy_analyst_agent(llm: ChatBedrock, policy_analyzer: PolicyAnalyzer) -> AgentExecutor:
    """Create a policy analyst agent.

    Args:
        llm: Language model
        policy_analyzer: Policy analyzer tool

    Returns:
        Agent executor
    """

    def determine_region_type(region: str) -> str:
        """Determine region regulation type."""
        region_type = policy_analyzer.determine_region_type(region)
        return f"{region} 지역은 '{region_type}'으로 분류됩니다."

    def analyze_loan_eligibility(input_str: str) -> str:
        """Analyze loan eligibility. Input format: region_type|property_price|annual_income"""
        try:
            parts = input_str.split("|")
            region_type = parts[0]
            property_price = int(parts[1])
            annual_income = int(parts[2])

            result = policy_analyzer.analyze_loan_eligibility(
                region_type, property_price, annual_income
            )

            output = [
                f"\n대출 적격성 분석 ({region_type}):",
                f"- LTV 한도: {result['ltv_limit']}%",
                f"- DTI 한도: {result['dti_limit']}%",
                f"- DSR 한도: {result['dsr_limit']}%",
            ]

            if result['restrictions']:
                output.append("\n추가 제한사항:")
                for restriction in result['restrictions']:
                    output.append(f"  * {restriction}")

            output.append(f"\n대출 가능 여부: {'가능' if result['eligible'] else '제한적'}")

            return "\n".join(output)
        except Exception as e:
            return f"분석 중 오류 발생: {e}"

    tools = [
        Tool(
            name="determine_region_type",
            func=determine_region_type,
            description="지역의 규제 유형을 판단합니다 (투기과열지구/조정대상지역/일반지역). 입력: 지역명"
        ),
        Tool(
            name="analyze_loan_eligibility",
            func=analyze_loan_eligibility,
            description="대출 적격성을 분석합니다. 입력 형식: 지역유형|매매가격|연소득 (예: 조정대상지역|350000000|70000000)"
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 부동산 정책 분석 전문가입니다. 각종 규제와 정책을 분석하고 해석하는 역할을 합니다.

주요 업무:
1. 지역별 규제 수준 판단
2. 적용 가능한 대출 규제 분석
3. 정책 영향도 평가
4. 사용자에게 적용되는 규제 설명

분석 시 다음을 고려하세요:
- 투기과열지구: 가장 강한 규제 (LTV 50%, DTI 40%)
- 조정대상지역: 중간 규제 (LTV 50%, DTI 50%)
- 일반지역: 완화된 규제 (LTV 70%, DTI 60%)
- DSR 40%는 전 지역 공통 적용

정확한 규제 내용과 그 의미를 명확히 설명하세요."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True
    )

    return agent_executor


def analyze_policy(
    user_query: Dict[str, Any],
    research_output: str,
    llm: ChatBedrock,
    policy_analyzer: PolicyAnalyzer
) -> Dict[str, Any]:
    """Analyze policies based on research output.

    Args:
        user_query: User query
        research_output: Output from research agent
        llm: Language model
        policy_analyzer: Policy analyzer tool

    Returns:
        Policy analysis results
    """
    agent = create_policy_analyst_agent(llm, policy_analyzer)

    analysis_query = f"""
다음 연구 결과를 바탕으로 사용자에게 적용되는 정책을 분석해주세요:

[사용자 정보]
- 나이: {user_query.get('age')}세
- 연봉: {user_query.get('annual_income'):,}원
- 예금: {user_query.get('savings'):,}원
- 목표 지역: {user_query.get('target_region')}
- 목표 가격대: {user_query.get('target_price_min'):,}원 ~ {user_query.get('target_price_max'):,}원

[연구 결과]
{research_output}

다음을 분석해주세요:
1. 목표 지역의 정확한 규제 수준 (투기과열지구/조정대상지역/일반지역)
2. 적용되는 LTV, DTI, DSR 한도
3. 목표 가격대에서의 대출 가능 여부
4. 주의해야 할 규제 사항
5. 생애최초 구매자 혜택 적용 가능 여부

각 항목별로 구체적인 근거와 함께 설명해주세요.
"""

    try:
        result = agent.invoke({"input": analysis_query})
        return {
            "success": True,
            "analysis_output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    except Exception as e:
        logger.error(f"Policy analyst error: {e}")
        return {
            "success": False,
            "error": str(e),
            "analysis_output": ""
        }
