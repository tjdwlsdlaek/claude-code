"""Pydantic schemas for data validation."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class UserQuery(BaseModel):
    """User query schema."""

    age: int = Field(..., description="사용자 나이")
    annual_income: int = Field(..., description="연봉 (원)")
    savings: int = Field(..., description="보유 예금 (원)")
    target_region: str = Field(..., description="목표 지역")
    target_price_min: int = Field(..., description="목표 가격 최소 (원)")
    target_price_max: int = Field(..., description="목표 가격 최대 (원)")
    additional_info: Optional[str] = Field(None, description="추가 정보")


class PolicyInfo(BaseModel):
    """Real estate policy information."""

    policy_name: str = Field(..., description="정책명")
    description: str = Field(..., description="정책 설명")
    effective_date: Optional[str] = Field(None, description="시행일")
    target_region: Optional[str] = Field(None, description="적용 지역")
    regulation_type: str = Field(..., description="규제 유형 (대출규제, 청약규제 등)")
    impact_level: str = Field(..., description="영향도 (상/중/하)")
    source_url: Optional[str] = Field(None, description="출처 URL")


class LoanCalculation(BaseModel):
    """Loan calculation result."""

    ltv_ratio: float = Field(..., description="LTV 비율 (%)")
    dti_ratio: float = Field(..., description="DTI 비율 (%)")
    dsr_ratio: float = Field(..., description="DSR 비율 (%)")
    max_loan_amount: int = Field(..., description="최대 대출 가능 금액 (원)")
    monthly_payment: int = Field(..., description="월 상환액 (원)")
    interest_rate: float = Field(..., description="적용 금리 (%)")
    loan_term_years: int = Field(..., description="대출 기간 (년)")
    total_interest: int = Field(..., description="총 이자 (원)")
    is_dsr_compliant: bool = Field(..., description="DSR 규제 준수 여부")


class TaxCalculation(BaseModel):
    """Tax calculation result."""

    acquisition_tax: int = Field(..., description="취득세 (원)")
    property_tax_annual: int = Field(..., description="연간 재산세 (원)")
    registration_tax: int = Field(..., description="등록세 (원)")
    stamp_duty: int = Field(..., description="인지세 (원)")
    total_initial_tax: int = Field(..., description="초기 납부 총 세금 (원)")
    transfer_tax_estimate: Optional[int] = Field(None, description="향후 양도세 예상 (원)")
    tax_benefits: List[str] = Field(default_factory=list, description="적용 가능한 세금 혜택")


class BrokerageFee(BaseModel):
    """Brokerage fee calculation."""

    property_price: int = Field(..., description="매매가 (원)")
    fee_rate: float = Field(..., description="중개수수료율 (%)")
    fee_amount: int = Field(..., description="중개수수료 (원)")
    upper_limit: int = Field(..., description="법정 상한액 (원)")


class RealEstateStrategy(BaseModel):
    """Comprehensive real estate purchase strategy."""

    # 전체 요약
    summary: str = Field(..., description="전략 요약")

    # 현황 분석
    current_regulations: List[PolicyInfo] = Field(..., description="적용되는 현행 규제")

    # 재무 분석
    loan_calculation: LoanCalculation = Field(..., description="대출 계산 결과")
    tax_calculation: TaxCalculation = Field(..., description="세금 계산 결과")
    brokerage_fee: BrokerageFee = Field(..., description="중개수수료")

    # 필요 자금
    total_initial_cost: int = Field(..., description="초기 필요 자금 총액 (원)")
    down_payment: int = Field(..., description="계약금 (원)")
    intermediate_payment: int = Field(..., description="중도금 (원)")
    balance_payment: int = Field(..., description="잔금 (원)")

    # 단계별 전략
    step_by_step_plan: List[Dict[str, str]] = Field(..., description="단계별 실행 계획")

    # 위험 요소
    risks: List[str] = Field(..., description="주요 위험 요소")

    # 대안 제시
    alternatives: List[str] = Field(..., description="대안 전략")

    # 추가 고려사항
    additional_considerations: List[str] = Field(..., description="추가 고려사항")

    # 생성 시각
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시각")


class AgentResponse(BaseModel):
    """Agent response wrapper."""

    framework: str = Field(..., description="사용된 프레임워크 (langgraph/crewai/strands)")
    query: UserQuery = Field(..., description="사용자 쿼리")
    strategy: RealEstateStrategy = Field(..., description="생성된 전략")
    execution_time_seconds: float = Field(..., description="실행 시간 (초)")
    tokens_used: Optional[int] = Field(None, description="사용된 토큰 수")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")
