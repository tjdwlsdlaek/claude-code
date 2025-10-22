
# 시스템 아키텍처

본 문서는 부동산 구매 전략 AI 에이전트 시스템의 전체 아키텍처를 설명합니다.

## 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 인터페이스                           │
│                   (Web App / API Client)                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌───▼──────┐ ┌──▼───────┐
│  LangGraph  │ │ Crew.ai  │ │ Strands  │
│    :8000    │ │  :8001   │ │  :8002   │
└───────┬─────┘ └────┬─────┘ └────┬─────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────▼────────────┐
        │   Common Tools Layer    │
        │  - Brave Search API     │
        │  - Real Estate Calc     │
        │  - Tax Calculator       │
        │  - Policy Analyzer      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   External Services     │
        │  - OpenAI GPT-4         │
        │  - Brave Search         │
        └─────────────────────────┘
```

## 레이어별 상세 설명

### 1. API Layer

각 프레임워크는 독립적인 FastAPI 애플리케이션으로 실행됩니다.

**엔드포인트**:
- `GET /`: 서비스 정보
- `GET /health`: 헬스 체크
- `POST /analyze`: 부동산 분석 실행
- `POST /test`: 테스트 쿼리

**포트**:
- LangGraph: 8000
- Crew.ai: 8001
- Strands: 8002

### 2. Agent Orchestration Layer

#### LangGraph Architecture

```
┌────────────────────────────────────────────────┐
│            StateGraph Workflow                 │
│                                                │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐ │
│  │Research │───▶│ Policy   │───▶│Financial │ │
│  │ Agent   │    │ Analyst  │    │ Advisor  │ │
│  └─────────┘    └──────────┘    └──────────┘ │
│                                                │
│  ┌─────────┐    ┌──────────┐                 │
│  │   Tax   │───▶│Strategy  │                 │
│  │Specialist│    │Coordinator│                │
│  └─────────┘    └──────────┘                 │
│                                                │
│  State: AgentState (TypedDict)                │
│  - user_query                                 │
│  - research_output                            │
│  - policy_output                              │
│  - financial_output                           │
│  - tax_output                                 │
│  - final_strategy                             │
└────────────────────────────────────────────────┘
```

#### Crew.ai Architecture

```
┌────────────────────────────────────────────────┐
│                Crew Structure                  │
│                                                │
│  Agents:                   Tasks:              │
│  ┌──────────────┐         ┌──────────────┐   │
│  │ Researcher   │────────▶│ Research     │   │
│  └──────────────┘         └──────┬───────┘   │
│                                   │            │
│  ┌──────────────┐         ┌──────▼───────┐   │
│  │Policy Analyst│────────▶│ Analysis     │   │
│  └──────────────┘         └──────┬───────┘   │
│                                   │            │
│  ┌──────────────┐         ┌──────▼───────┐   │
│  │Financial Adv.│────────▶│ Financial    │   │
│  └──────────────┘         └──────┬───────┘   │
│                                   │            │
│  ┌──────────────┐         ┌──────▼───────┐   │
│  │Tax Specialist│────────▶│ Tax Calc     │   │
│  └──────────────┘         └──────┬───────┘   │
│                                   │            │
│  ┌──────────────┐         ┌──────▼───────┐   │
│  │ Coordinator  │────────▶│ Strategy     │   │
│  └──────────────┘         └──────────────┘   │
│                                                │
│  Process: Sequential                          │
└────────────────────────────────────────────────┘
```

#### Strands Architecture

```
┌────────────────────────────────────────────────┐
│           Workflow Orchestrator                │
│                                                │
│  Context = {}                                  │
│                                                │
│  ┌────────────────────────────────────┐       │
│  │ 1. researcher.execute(context)     │       │
│  │    → context['research_output']    │       │
│  └────────────┬───────────────────────┘       │
│               │                                │
│  ┌────────────▼───────────────────────┐       │
│  │ 2. analyst.execute(context)        │       │
│  │    → context['policy_output']      │       │
│  └────────────┬───────────────────────┘       │
│               │                                │
│  ┌────────────▼───────────────────────┐       │
│  │ 3. advisor.execute(context)        │       │
│  │    → context['financial_output']   │       │
│  └────────────┬───────────────────────┘       │
│               │                                │
│  ┌────────────▼───────────────────────┐       │
│  │ 4. tax_specialist.execute(context) │       │
│  │    → context['tax_output']         │       │
│  └────────────┬───────────────────────┘       │
│               │                                │
│  ┌────────────▼───────────────────────┐       │
│  │ 5. coordinator.execute(context)    │       │
│  │    → final_strategy                │       │
│  └────────────────────────────────────┘       │
│                                                │
│  Execution: Sequential, Explicit               │
└────────────────────────────────────────────────┘
```

### 3. Common Tools Layer

모든 프레임워크가 공유하는 도구들:

```python
common/
├── tools/
│   ├── brave_search.py         # 웹 검색
│   ├── real_estate_calculator.py  # 대출 계산
│   ├── tax_calculator.py       # 세금 계산
│   └── policy_analyzer.py      # 정책 분석
├── models/
│   └── schemas.py              # 데이터 모델
└── config.py                   # 설정 관리
```

**주요 기능**:

1. **Brave Search Tool**
   - 최신 부동산 정책 검색
   - 대출 규제 정보 검색
   - 시장 동향 조사
   - 세금 정보 검색

2. **Real Estate Calculator**
   - LTV/DTI/DSR 계산
   - 최대 대출 금액 산출
   - 월 상환액 계산
   - 중개수수료 계산

3. **Tax Calculator**
   - 취득세 계산
   - 재산세 계산
   - 종합부동산세 계산
   - 양도소득세 예상
   - 세금 혜택 분석

4. **Policy Analyzer**
   - 지역 규제 분류
   - 정책 영향도 평가
   - 대출 적격성 분석
   - 정책 요약

### 4. Data Flow

#### 요청 처리 흐름

```
1. User Request
   ↓
2. API Endpoint (/analyze)
   ↓
3. Query Validation (Pydantic)
   ↓
4. Framework-specific Workflow
   ├─ LangGraph: StateGraph.invoke()
   ├─ Crew.ai: Crew.kickoff()
   └─ Strands: Workflow.run()
   ↓
5. Agent Execution (순차적)
   ├─ Research: Web Search → 정책 조사
   ├─ Policy: 규제 분석
   ├─ Financial: 대출 계산
   ├─ Tax: 세금 계산
   └─ Strategy: 종합 전략 수립
   ↓
6. Response Generation
   ↓
7. Return to User
```

#### 데이터 구조

**Request**:
```json
{
  "age": 35,
  "annual_income": 70000000,
  "savings": 100000000,
  "target_region": "서울 강남구",
  "target_price_min": 300000000,
  "target_price_max": 400000000,
  "additional_info": "생애최초 구매"
}
```

**Response**:
```json
{
  "framework": "langgraph",
  "strategy": "종합 전략 텍스트...",
  "execution_time_seconds": 45.2,
  "user_query": {...},
  "errors": [],
  "intermediate_outputs": {
    "research": "...",
    "policy": "...",
    "financial": "...",
    "tax": "..."
  }
}
```

## 배포 아키텍처 (AWS ECS)

```
┌────────────────────────────────────────────────────┐
│                    Internet                        │
└─────────────────────┬──────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────┐
│          Application Load Balancer                 │
│                                                     │
│  Listener Rules:                                   │
│  - /langgraph/* → Target Group 1 (8000)           │
│  - /crewai/*    → Target Group 2 (8001)           │
│  - /strands/*   → Target Group 3 (8002)           │
└─────────────────────┬──────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼──────┐ ┌───▼──────┐
│ECS Service 1 │ │ECS Service│ │ECS Service│
│ (LangGraph)  │ │ (Crew.ai) │ │ (Strands) │
│              │ │           │ │           │
│ ┌──────────┐ │ │┌──────────┐│ │┌──────────┐
│ │ Task 1   │ │ ││ Task 1   ││ ││ Task 1   │
│ │Container │ │ ││Container ││ ││Container │
│ └──────────┘ │ │└──────────┘│ │└──────────┘
└──────────────┘ └───────────┘ └───────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
┌─────────────────────▼──────────────────────────────┐
│              AWS Secrets Manager                   │
│  - OpenAI API Key                                  │
│  - Brave Search API Key                            │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│              Amazon ECR                            │
│  - ai-agent-langgraph:latest                      │
│  - ai-agent-crewai:latest                         │
│  - ai-agent-strands:latest                        │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│            CloudWatch Logs                         │
│  - /ecs/langgraph-agent                           │
│  - /ecs/crewai-agent                              │
│  - /ecs/strands-agent                             │
└────────────────────────────────────────────────────┘
```

### 컨테이너 사양

**기본 설정** (Task Definition):
- CPU: 512 (0.5 vCPU)
- Memory: 1024 MB
- Network Mode: awsvpc
- Launch Type: Fargate

**환경 변수**:
- `APP_PORT`: 8000/8001/8002
- `LOG_LEVEL`: INFO
- `OPENAI_MODEL`: gpt-4-turbo-preview

**Secrets** (AWS Secrets Manager):
- `OPENAI_API_KEY`
- `BRAVE_SEARCH_API_KEY`

## 보안 고려사항

### 1. API Key 관리
- AWS Secrets Manager 사용
- 환경 변수로 주입
- 코드에 하드코딩 금지

### 2. 네트워크 보안
- VPC 내부에서만 통신
- Security Group으로 포트 제한
- ALB를 통한 외부 접근만 허용

### 3. 컨테이너 보안
- 최소 권한 원칙
- Read-only 파일시스템 (가능한 경우)
- 정기적인 이미지 스캔

### 4. 로깅 및 모니터링
- CloudWatch Logs로 중앙 집중식 로깅
- 에러 추적
- 성능 모니터링

## 확장성

### 수평 확장
- ECS Service Auto Scaling
- CPU/Memory 기반 자동 스케일링
- Target Tracking Scaling Policy

### 수직 확장
- Task Definition CPU/Memory 증가
- 더 큰 Fargate 컴퓨팅 리소스

### 캐싱 전략
- Brave Search 결과 캐싱 (15분)
- 정책 정보 캐싱
- Redis/ElastiCache 도입 가능

## 모니터링 및 관찰성

### 메트릭
- 요청 수
- 응답 시간
- 에러 율
- CPU/Memory 사용률

### 로깅
- 구조화된 JSON 로깅
- Request ID 추적
- Agent별 실행 시간

### 알람
- 높은 에러 율
- 느린 응답 시간
- 리소스 부족

## 비용 최적화

### Compute
- Fargate Spot 사용 고려
- 적절한 CPU/Memory 크기 조정
- Auto Scaling으로 유휴 리소스 최소화

### Storage
- ECR Lifecycle Policy
- CloudWatch Logs 보관 기간 설정

### Network
- NAT Gateway 대신 VPC Endpoints (가능한 경우)
- 불필요한 데이터 전송 최소화

## 재해 복구

### Backup
- ECR 이미지 버전 관리
- Task Definition 버전 관리
- Secrets Manager 자동 백업

### 복구 절차
1. 이전 Task Definition으로 롤백
2. 이전 ECR 이미지로 재배포
3. CloudWatch Logs로 원인 분석
