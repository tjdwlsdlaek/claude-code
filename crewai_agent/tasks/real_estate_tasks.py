"""Task definitions for real estate crew."""

from crewai import Task, Agent
from typing import Dict, Any


def create_research_task(agent: Agent, user_query: Dict[str, Any]) -> Task:
    """Create research task."""
    return Task(
        description=f"""다음 사용자의 부동산 구매를 위한 시장 조사를 수행하세요:

사용자 정보:
- 나이: {user_query['age']}세
- 연봉: {user_query['annual_income']:,}원
- 보유 예금: {user_query['savings']:,}원
- 목표 지역: {user_query['target_region']}
- 목표 가격대: {user_query['target_price_min']:,}원 ~ {user_query['target_price_max']:,}원

조사 항목:
1. {user_query['target_region']} 지역의 최신 부동산 정책 및 규제
2. 해당 지역의 대출 규제 현황 (LTV, DTI, DSR)
3. 최근 시장 동향 및 전망
4. 투기과열지구 또는 조정대상지역 지정 여부

각 항목에 대해 구체적인 수치와 출처를 포함하여 보고하세요.""",
        expected_output="""다음 형식으로 조사 결과를 제공하세요:

## 지역 규제 현황
- 규제 지역 분류
- 적용되는 규제 내용

## 대출 규제
- LTV 한도
- DTI 한도
- DSR 한도

## 시장 동향
- 최근 가격 추이
- 향후 전망

## 주요 정책 변화
- 최근 발표된 정책
- 향후 예정된 변화

각 항목별 출처 URL 포함""",
        agent=agent
    )


def create_policy_analysis_task(agent: Agent, user_query: Dict[str, Any]) -> Task:
    """Create policy analysis task."""
    target_price = (user_query['target_price_min'] + user_query['target_price_max']) // 2

    return Task(
        description=f"""이전 조사 결과를 바탕으로 사용자에게 적용되는 정책을 분석하세요:

사용자 정보:
- 목표 지역: {user_query['target_region']}
- 목표 매매가: {target_price:,}원
- 연소득: {user_query['annual_income']:,}원

분석 항목:
1. 지역의 정확한 규제 수준 판단 (투기과열지구/조정대상지역/일반지역)
2. 사용자에게 적용되는 LTV, DTI, DSR 한도
3. 생애최초 구매자 혜택 적용 가능 여부
4. 주의해야 할 규제 사항

각 항목을 명확하게 설명하세요.""",
        expected_output="""다음 형식으로 분석 결과를 제공하세요:

## 지역 규제 분류
- 규제 등급 및 근거

## 적용 대출 한도
- LTV: X%
- DTI: X%
- DSR: X%

## 생애최초 혜택
- 적용 가능 여부
- 혜택 내용

## 주의사항
- 추가 규제 사항
- 제한 조건""",
        agent=agent,
        context=[]  # Will be filled with previous task outputs
    )


def create_financial_planning_task(agent: Agent, user_query: Dict[str, Any]) -> Task:
    """Create financial planning task."""
    target_price = (user_query['target_price_min'] + user_query['target_price_max']) // 2

    return Task(
        description=f"""정책 분석 결과를 바탕으로 재무 계획을 수립하세요:

사용자 정보:
- 연소득: {user_query['annual_income']:,}원
- 보유 예금: {user_query['savings']:,}원
- 목표 매매가: {target_price:,}원

계산 항목:
1. 최대 대출 가능 금액 (LTV, DTI, DSR 모두 고려)
2. 필요한 자기자본 (계약금 10%, 중도금 10%, 잔금 80% 기준)
3. 월 상환액 및 연간 상환 부담
4. 중개수수료
5. 현재 보유 자금으로 구매 가능 여부

모든 계산 과정과 결과를 명확히 제시하세요.""",
        expected_output="""다음 형식으로 재무 계획을 제공하세요:

## 대출 계획
- 최대 대출 금액: X원
- 적용 금리: X%
- 대출 기간: X년
- 월 상환액: X원

## 필요 자금
- 계약금 (10%): X원
- 중도금 (10%): X원
- 잔금 (대출): X원
- 중개수수료: X원
- 초기 필요 자금 총액: X원

## 재무 평가
- 현재 보유 자금: X원
- 부족/여유 자금: X원
- 구매 가능 여부: 가능/불가능

## 월 상환 부담
- 월 상환액: X원
- 월 소득 대비 비율: X%
- 재무 건전성 평가""",
        agent=agent,
        context=[]
    )


def create_tax_calculation_task(agent: Agent, user_query: Dict[str, Any]) -> Task:
    """Create tax calculation task."""
    target_price = (user_query['target_price_min'] + user_query['target_price_max']) // 2
    is_first = user_query['age'] <= 40

    return Task(
        description=f"""부동산 취득 및 보유에 따른 세금을 계산하세요:

매매 정보:
- 매매가: {target_price:,}원
- 생애최초 구매: {is_first}
- 전용면적: 84㎡ (가정)

계산 항목:
1. 취득세 (생애최초 감면 고려)
2. 등록세
3. 인지세
4. 연간 재산세
5. 종합부동산세 해당 여부
6. 적용 가능한 세금 혜택

모든 세금을 정확히 계산하세요.""",
        expected_output="""다음 형식으로 세금 계산 결과를 제공하세요:

## 초기 납부 세금
- 취득세: X원
- 등록세: X원
- 인지세: X원
- 초기 세금 총액: X원

## 연간 보유 세금
- 재산세: X원 (월 X원)
- 종합부동산세: X원 (해당시)
- 연간 세금 총액: X원

## 세금 혜택
- 적용 가능한 감면
- 예상 절세액

## 장기 세금 전략
- 보유 기간별 양도세 시뮬레이션
- 절세 방안""",
        agent=agent,
        context=[]
    )


def create_strategy_task(agent: Agent, user_query: Dict[str, Any]) -> Task:
    """Create comprehensive strategy task."""
    return Task(
        description=f"""모든 전문가의 분석을 종합하여 실행 가능한 주택 구매 전략을 수립하세요:

사용자 기본 정보:
- 나이: {user_query['age']}세
- 연봉: {user_query['annual_income']:,}원
- 예금: {user_query['savings']:,}원
- 목표: {user_query['target_region']} 지역 주택 구매

전문가 분석 결과를 모두 고려하여 다음을 포함한 종합 전략을 작성하세요:

1. 전략 요약 (핵심 메시지 3-5문장)
2. 현황 분석 (규제, 시장, 재무 상태)
3. 자금 계획 (필요 자금, 대출, 세금)
4. 단계별 실행 계획 (12개월 로드맵)
5. 위험 요소 및 대응 방안
6. 대안 전략 (계획이 어려울 경우)
7. 추가 고려사항

30대 구매자가 실제로 실행할 수 있는 현실적이고 구체적인 전략을 제시하세요.""",
        expected_output="""다음 형식의 종합 전략을 작성하세요:

# 30대를 위한 주택 구매 종합 전략

## 1. 전략 요약
(핵심 메시지 3-5문장)

## 2. 현황 분석
### 적용 규제
- 규제 내용

### 시장 상황
- 현재 시장 동향

### 재무 상태
- 구매력 평가

## 3. 자금 계획
### 필요 자금
- 총 필요 금액
- 항목별 상세

### 대출 계획
- 대출 금액 및 조건
- 월 상환 계획

### 세금 부담
- 초기 세금
- 보유 세금

## 4. 단계별 실행 계획
### 1단계: 준비 (현재~3개월)
- 구체적 액션 아이템

### 2단계: 매물 탐색 (3~6개월)
- 구체적 액션 아이템

### 3단계: 계약 및 대출 (6~9개월)
- 구체적 액션 아이템

### 4단계: 잔금 및 입주 (9~12개월)
- 구체적 액션 아이템

## 5. 위험 요소 및 대응
- 주요 리스크
- 각 리스크별 대응 방안

## 6. 대안 전략
- 대안 1
- 대안 2
- 대안 3

## 7. 추가 고려사항
- 청약 검토
- 기타 주의사항

모든 금액은 구체적인 숫자로, 모든 계획은 실행 가능한 수준으로 작성""",
        agent=agent,
        context=[]
    )
