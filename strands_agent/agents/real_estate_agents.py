"""Agent implementations following Strands architecture pattern.

Strands pattern focuses on:
- Lightweight, single-purpose agents
- Explicit state passing
- Simple, composable workflows
- Direct LLM integration without heavy frameworks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any, Optional
from openai import OpenAI
from common.tools import BraveSearchTool, RealEstateCalculator, TaxCalculator, PolicyAnalyzer
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base agent class for Strands pattern."""

    def __init__(self, name: str, role: str, llm_client: OpenAI, model: str = "gpt-4-turbo-preview"):
        self.name = name
        self.role = role
        self.llm = llm_client
        self.model = model

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic. To be implemented by subclasses."""
        raise NotImplementedError


class ResearcherAgent(BaseAgent):
    """Research agent for gathering real estate information."""

    def __init__(self, llm_client: OpenAI, brave_search: BraveSearchTool, model: str = "gpt-4-turbo-preview"):
        super().__init__("Researcher", "부동산 정책 연구원", llm_client, model)
        self.brave_search = brave_search

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research."""
        user_query = context.get("user_query", {})
        region = user_query.get("target_region", "")

        logger.info(f"[{self.name}] Starting research for {region}")

        # Gather information
        policy_results = self.brave_search.search_real_estate_policy(region=region)
        loan_results = self.brave_search.search_loan_regulations(region=region)

        # Format results for LLM
        research_data = self._format_search_results(policy_results, loan_results)

        # Use LLM to synthesize findings
        prompt = f"""당신은 {self.role}입니다.

다음 검색 결과를 바탕으로 {region} 지역의 부동산 구매 관련 정보를 요약하세요:

{research_data}

사용자 정보:
- 나이: {user_query.get('age')}세
- 연봉: {user_query.get('annual_income'):,}원
- 목표 가격대: {user_query.get('target_price_min'):,}~{user_query.get('target_price_max'):,}원

다음 항목을 포함하여 보고하세요:
1. 지역 규제 수준 (투기과열지구/조정대상지역/일반지역)
2. 적용되는 대출 규제 (LTV, DTI, DSR)
3. 최근 정책 변화
4. 주의사항
"""

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        output = response.choices[0].message.content

        return {
            "agent": self.name,
            "output": output,
            "raw_data": {
                "policy_results": policy_results[:3],
                "loan_results": loan_results[:3]
            }
        }

    def _format_search_results(self, policy_results, loan_results):
        """Format search results for LLM."""
        output = ["=== 부동산 정책 정보 ===\n"]
        for i, result in enumerate(policy_results[:5], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   {result['description']}\n")

        output.append("\n=== 대출 규제 정보 ===\n")
        for i, result in enumerate(loan_results[:5], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   {result['description']}\n")

        return "\n".join(output)


class PolicyAnalystAgent(BaseAgent):
    """Policy analysis agent."""

    def __init__(self, llm_client: OpenAI, policy_analyzer: PolicyAnalyzer, model: str = "gpt-4-turbo-preview"):
        super().__init__("PolicyAnalyst", "부동산 정책 분석가", llm_client, model)
        self.policy_analyzer = policy_analyzer

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute policy analysis."""
        user_query = context.get("user_query", {})
        research_output = context.get("research_output", "")

        region = user_query.get("target_region", "")
        region_type = self.policy_analyzer.determine_region_type(region)

        logger.info(f"[{self.name}] Analyzing policies for {region} ({region_type})")

        prompt = f"""당신은 {self.role}입니다.

다음 연구 결과를 바탕으로 사용자에게 적용되는 정책을 분석하세요:

{research_output}

지역 분류: {region_type}

사용자 정보:
- 연봉: {user_query.get('annual_income'):,}원
- 목표 가격대: {user_query.get('target_price_min'):,}~{user_query.get('target_price_max'):,}원

다음을 분석하세요:
1. 적용되는 LTV, DTI, DSR 한도
2. 생애최초 구매자 혜택 가능 여부
3. 주요 규제 사항
4. 구매 시 주의사항
"""

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        output = response.choices[0].message.content

        return {
            "agent": self.name,
            "output": output,
            "region_type": region_type
        }


class FinancialAdvisorAgent(BaseAgent):
    """Financial planning agent."""

    def __init__(self, llm_client: OpenAI, calculator: RealEstateCalculator, model: str = "gpt-4-turbo-preview"):
        super().__init__("FinancialAdvisor", "재무 설계사", llm_client, model)
        self.calculator = calculator

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute financial planning."""
        user_query = context.get("user_query", {})
        region_type = context.get("region_type", "조정대상지역")

        logger.info(f"[{self.name}] Calculating financial plan")

        target_price = (user_query.get('target_price_min', 0) + user_query.get('target_price_max', 0)) // 2
        is_first_home = user_query.get('age', 0) <= 40

        # Calculate loan details
        loan_calc = self.calculator.calculate_maximum_loan(
            property_price=target_price,
            annual_income=user_query.get('annual_income', 0),
            region_type=region_type,
            is_first_home=is_first_home
        )

        # Calculate brokerage fee
        brokerage = self.calculator.calculate_brokerage_fee(target_price)

        # Format calculations for LLM
        calc_summary = f"""
=== 대출 계산 결과 ===
매매가: {target_price:,}원
최대 대출: {loan_calc['max_loan_amount']:,}원
필요 자기자본: {target_price - loan_calc['max_loan_amount']:,}원

LTV: {loan_calc['ltv_ratio']:.1f}%
DTI: {loan_calc['dti_ratio']:.1f}%
DSR: {loan_calc['dsr_ratio']:.1f}%

월 상환액: {loan_calc['monthly_payment']:,}원
총 이자: {loan_calc['total_interest']:,}원

중개수수료: {brokerage['fee_amount']:,}원

초기 필요 자금:
- 계약금 (10%): {int(target_price * 0.1):,}원
- 중도금 (10%): {int(target_price * 0.1):,}원
- 중개수수료: {brokerage['fee_amount']:,}원
"""

        prompt = f"""당신은 {self.role}입니다.

다음 계산 결과를 바탕으로 재무 계획을 수립하세요:

{calc_summary}

사용자 보유 자금: {user_query.get('savings'):,}원
월 소득: {user_query.get('annual_income') // 12:,}원

다음을 포함하세요:
1. 현재 보유 자금으로 구매 가능 여부
2. 월 상환 부담 평가
3. 추가 필요 자금 (있는 경우)
4. 재무 건전성 평가
"""

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        output = response.choices[0].message.content

        return {
            "agent": self.name,
            "output": output,
            "calculations": {
                "loan": loan_calc,
                "brokerage": brokerage
            }
        }


class TaxSpecialistAgent(BaseAgent):
    """Tax calculation agent."""

    def __init__(self, llm_client: OpenAI, tax_calculator: TaxCalculator, model: str = "gpt-4-turbo-preview"):
        super().__init__("TaxSpecialist", "세무 전문가", llm_client, model)
        self.tax_calculator = tax_calculator

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tax calculations."""
        user_query = context.get("user_query", {})
        region_type = context.get("region_type", "조정대상지역")

        logger.info(f"[{self.name}] Calculating taxes")

        target_price = (user_query.get('target_price_min', 0) + user_query.get('target_price_max', 0)) // 2
        is_first_home = user_query.get('age', 0) <= 40
        is_adjusted = region_type in ["투기과열지구", "조정대상지역"]

        # Calculate taxes
        acquisition = self.tax_calculator.calculate_acquisition_tax(
            target_price, is_first_home, 84.0, is_adjusted
        )
        property_tax = self.tax_calculator.calculate_property_tax_annual(target_price)
        benefits = self.tax_calculator.get_available_tax_benefits(
            is_first_home, user_query.get('age', 0), 84.0, target_price
        )

        tax_summary = f"""
=== 세금 계산 결과 ===
취득세: {acquisition['total_acquisition_tax']:,}원
연간 재산세: {property_tax:,}원 (월 {property_tax // 12:,}원)

세금 혜택:
{chr(10).join(f'- {b}' for b in benefits)}
"""

        prompt = f"""당신은 {self.role}입니다.

다음 세금 계산 결과를 설명하세요:

{tax_summary}

다음을 포함하세요:
1. 초기 납부 세금 총액
2. 연간 보유 세금
3. 적용 가능한 세금 혜택
4. 절세 방안
"""

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        output = response.choices[0].message.content

        return {
            "agent": self.name,
            "output": output,
            "calculations": {
                "acquisition_tax": acquisition,
                "property_tax": property_tax,
                "benefits": benefits
            }
        }


class StrategyCoordinatorAgent(BaseAgent):
    """Strategy coordination agent."""

    def __init__(self, llm_client: OpenAI, model: str = "gpt-4-turbo-preview"):
        super().__init__("StrategyCoordinator", "전략 코디네이터", llm_client, model)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive strategy."""
        user_query = context.get("user_query", {})
        research = context.get("research_output", "")
        policy = context.get("policy_output", "")
        financial = context.get("financial_output", "")
        tax = context.get("tax_output", "")

        logger.info(f"[{self.name}] Creating comprehensive strategy")

        prompt = f"""당신은 {self.role}입니다.

모든 전문가의 분석을 종합하여 30대를 위한 주택 구매 종합 전략을 수립하세요.

=== 사용자 정보 ===
- 나이: {user_query.get('age')}세
- 연봉: {user_query.get('annual_income'):,}원
- 보유 예금: {user_query.get('savings'):,}원
- 목표 지역: {user_query.get('target_region')}
- 목표 가격대: {user_query.get('target_price_min'):,}~{user_query.get('target_price_max'):,}원

=== 시장 조사 ===
{research}

=== 정책 분석 ===
{policy}

=== 재무 분석 ===
{financial}

=== 세금 분석 ===
{tax}

다음 형식으로 종합 전략을 작성하세요:

# 30대를 위한 주택 구매 종합 전략

## 1. 전략 요약
(핵심 메시지 3-5문장)

## 2. 현황 분석
- 적용 규제
- 재무 상태

## 3. 자금 계획
- 필요 자금 총액
- 대출 계획
- 세금 부담

## 4. 단계별 실행 계획
1단계: 준비 (현재~3개월)
2단계: 매물 탐색 (3~6개월)
3단계: 계약 및 대출 (6~9개월)
4단계: 잔금 및 입주 (9~12개월)

## 5. 위험 요소 및 대응
- 주요 리스크
- 대응 방안

## 6. 대안 전략
- 대안 2-3가지

## 7. 추가 고려사항

구체적이고 실행 가능한 전략을 제시하세요.
"""

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        output = response.choices[0].message.content

        return {
            "agent": self.name,
            "output": output
        }
