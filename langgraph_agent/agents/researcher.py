"""Research agent for gathering real estate policy information."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from common.tools import BraveSearchTool
import logging

logger = logging.getLogger(__name__)


def create_researcher_agent(llm: ChatOpenAI, brave_search: BraveSearchTool) -> AgentExecutor:
    """Create a research agent for gathering real estate information.

    Args:
        llm: Language model
        brave_search: Brave Search tool

    Returns:
        Agent executor
    """

    # Define tools for the researcher
    def search_policies(query: str) -> str:
        """Search for real estate policies."""
        results = brave_search.search_real_estate_policy()
        if not results:
            return "검색 결과를 찾을 수 없습니다."

        output = ["최신 부동산 정책 검색 결과:\n"]
        for i, result in enumerate(results[:5], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   설명: {result['description']}")
            output.append(f"   URL: {result['url']}\n")

        return "\n".join(output)

    def search_loan_info(region: str) -> str:
        """Search for loan regulation information."""
        results = brave_search.search_loan_regulations(region)
        if not results:
            return "검색 결과를 찾을 수 없습니다."

        output = [f"{region} 지역 대출 규제 정보:\n"]
        for i, result in enumerate(results[:5], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   설명: {result['description']}")
            output.append(f"   URL: {result['url']}\n")

        return "\n".join(output)

    def search_market_trends(region: str) -> str:
        """Search for market trends."""
        results = brave_search.search_market_trends(region)
        if not results:
            return "검색 결과를 찾을 수 없습니다."

        output = [f"{region} 지역 시장 동향:\n"]
        for i, result in enumerate(results[:5], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   설명: {result['description']}")
            output.append(f"   URL: {result['url']}\n")

        return "\n".join(output)

    def search_tax_info() -> str:
        """Search for tax information."""
        results = brave_search.search_tax_info()
        if not results:
            return "검색 결과를 찾을 수 없습니다."

        output = ["부동산 세금 정보:\n"]
        for i, result in enumerate(results[:5], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   설명: {result['description']}")
            output.append(f"   URL: {result['url']}\n")

        return "\n".join(output)

    tools = [
        Tool(
            name="search_policies",
            func=search_policies,
            description="최신 부동산 정책과 규제를 검색합니다. 정부 발표 내용, 규제 변화 등을 찾을 때 사용하세요."
        ),
        Tool(
            name="search_loan_info",
            func=search_loan_info,
            description="특정 지역의 대출 규제 정보를 검색합니다. LTV, DTI, DSR 등의 정보를 찾을 때 사용하세요. 입력: 지역명 (예: 서울 강남구)"
        ),
        Tool(
            name="search_market_trends",
            func=search_market_trends,
            description="특정 지역의 부동산 시장 동향을 검색합니다. 시세, 전망 등을 찾을 때 사용하세요. 입력: 지역명 (예: 서울 강남구)"
        ),
        Tool(
            name="search_tax_info",
            func=search_tax_info,
            description="부동산 관련 세금 정보를 검색합니다. 취득세, 양도세 등의 정보를 찾을 때 사용하세요."
        )
    ]

    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 부동산 정책 연구원입니다. 최신 부동산 정책, 규제, 시장 동향을 조사하는 전문가입니다.

주요 업무:
1. 최신 부동산 정책 및 규제 조사
2. 지역별 대출 규제 정보 수집 (LTV, DTI, DSR)
3. 시장 동향 및 전망 분석
4. 세금 관련 최신 정보 수집

조사 시 다음을 포함하세요:
- 정책 시행일 및 적용 대상
- 지역별 규제 수준 (투기과열지구, 조정대상지역 등)
- 구체적인 수치와 기준
- 출처 URL

검색 결과를 기반으로 정확하고 최신의 정보를 제공하세요."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )

    return agent_executor


def research_real_estate_info(
    user_query: Dict[str, Any],
    llm: ChatOpenAI,
    brave_search: BraveSearchTool
) -> Dict[str, Any]:
    """Execute research for real estate information.

    Args:
        user_query: User query containing target region and other info
        llm: Language model
        brave_search: Brave Search tool

    Returns:
        Research results
    """
    agent = create_researcher_agent(llm, brave_search)

    query_text = f"""
다음 사용자의 부동산 구매를 위해 필요한 정보를 조사해주세요:

- 나이: {user_query.get('age')}세
- 연봉: {user_query.get('annual_income'):,}원
- 예금: {user_query.get('savings'):,}원
- 목표 지역: {user_query.get('target_region')}
- 목표 가격대: {user_query.get('target_price_min'):,}원 ~ {user_query.get('target_price_max'):,}원

조사 항목:
1. {user_query.get('target_region')} 지역의 현재 규제 수준 (투기과열지구/조정대상지역 여부)
2. 해당 지역의 대출 규제 (LTV, DTI, DSR 한도)
3. 최근 부동산 정책 변화
4. 시장 동향 및 전망
5. 세금 관련 최신 정보

각 항목별로 구체적인 수치와 출처를 포함해서 보고해주세요.
"""

    try:
        result = agent.invoke({"input": query_text})
        return {
            "success": True,
            "research_output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    except Exception as e:
        logger.error(f"Research agent error: {e}")
        return {
            "success": False,
            "error": str(e),
            "research_output": ""
        }
