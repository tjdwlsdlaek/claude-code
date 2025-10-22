"""Strategy coordinator agent for creating comprehensive purchase strategy."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)


def create_comprehensive_strategy(
    user_query: Dict[str, Any],
    research_output: str,
    policy_output: str,
    financial_output: str,
    tax_output: str,
    llm: ChatBedrock
) -> Dict[str, Any]:
    """Create comprehensive purchase strategy by coordinating all agent outputs.

    Args:
        user_query: User query
        research_output: Research agent output
        policy_output: Policy analyst output
        financial_output: Financial advisor output
        tax_output: Tax specialist output
        llm: Language model

    Returns:
        Comprehensive strategy
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 부동산 구매 전략을 총괄하는 코디네이터입니다.
여러 전문가들의 분석을 종합하여 30대 구매자를 위한 현실적이고 실행 가능한 주택 구매 전략을 수립합니다.

전략 수립 시 다음을 포함하세요:
1. 종합 요약 (3-5문장)
2. 현재 적용되는 주요 규제
3. 재무 상황 분석
4. 필요 자금 및 대출 계획
5. 세금 부담 분석
6. 단계별 실행 계획
7. 주요 위험 요소
8. 대안 전략
9. 추가 고려사항

현실적이고 구체적인 전략을 제시하되, 위험 요소도 명확히 알려주세요."""),
        ("user", """{input}""")
    ])

    target_price = (user_query.get('target_price_min', 0) + user_query.get('target_price_max', 0)) // 2

    strategy_input = f"""
다음 분석 결과를 종합하여 30대 구매자를 위한 주택 구매 종합 전략을 수립해주세요:

[사용자 정보]
- 나이: {user_query.get('age')}세
- 연봉: {user_query.get('annual_income'):,}원
- 보유 예금: {user_query.get('savings'):,}원
- 목표 지역: {user_query.get('target_region')}
- 목표 가격대: {target_price:,}원

[시장 조사 결과]
{research_output}

[정책 분석 결과]
{policy_output}

[재무 분석 결과]
{financial_output}

[세금 분석 결과]
{tax_output}

위 정보를 바탕으로 다음 형식의 종합 전략을 작성해주세요:

## 1. 전략 요약
- 핵심 메시지 3-5문장

## 2. 현황 분석
- 적용되는 주요 규제
- 현재 시장 상황
- 재무 상태 평가

## 3. 자금 계획
- 필요 자금 총액
- 대출 가능 금액
- 자기자본 필요액
- 월 상환 부담

## 4. 세금 계획
- 초기 납부 세금
- 연간 보유 세금
- 장기 세금 전략

## 5. 단계별 실행 계획
1단계: 준비 (현재~3개월)
2단계: 매물 탐색 (3~6개월)
3단계: 계약 및 대출 (6~9개월)
4단계: 잔금 및 입주 (9~12개월)

각 단계별 구체적인 액션 아이템 제시

## 6. 위험 요소 및 대응 방안
- 금리 인상 리스크
- 정책 변화 리스크
- 시장 하락 리스크
- 개인 재무 리스크

각 위험에 대한 대응 방안 제시

## 7. 대안 전략
- 현재 계획이 어려울 경우의 대안 2-3가지

## 8. 추가 고려사항
- 청약 가능 여부
- 신혼부부 특별공급 검토
- 전세 vs 매매 비교
- 지역 선택의 유연성

모든 금액은 구체적인 숫자로 제시하고, 실행 가능한 조언을 해주세요.
"""

    try:
        chain = prompt | llm
        result = chain.invoke({"input": strategy_input})

        return {
            "success": True,
            "strategy": result.content,
            "user_query": user_query
        }
    except Exception as e:
        logger.error(f"Strategy coordinator error: {e}")
        return {
            "success": False,
            "error": str(e),
            "strategy": ""
        }
