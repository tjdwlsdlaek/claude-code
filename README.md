# AI Agent Frameworks Comparison: Real Estate Policy Advisor

이 프로젝트는 **LangGraph**, **Crew.ai**, **Strands Agents** 3개의 AI 에이전트 프레임워크를 실제 애플리케이션을 통해 비교 분석합니다.

## 📋 프로젝트 개요

**목적**: 30대를 위한 현실적인 주택 구매 전략을 제시하는 AI 에이전트 시스템

**핵심 기능**:
- 최신 부동산 정책 및 규제 조사 (웹 검색)
- 정부 발표 규제 상세 분석
- 대출 전략 수립 (DSR, LTV, DTI 계산)
- 세금 시뮬레이션 (취득세, 양도세, 재산세)
- 부동산 중개수수료 계산
- 청약 자격 분석
- 종합 주택 구매 전략 제시

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
│   LangGraph    │ │    Crew.ai      │ │ Strands Agents │
│  Implementation│ │  Implementation │ │ Implementation │
└────────────────┘ └─────────────────┘ └────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │         Common Tools & Utils          │
        │  - Brave Search API                   │
        │  - Real Estate Calculator             │
        │  - Policy Analyzer                    │
        │  - Tax Calculator                     │
        └───────────────────────────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │          Amazon ECS Deployment        │
        └───────────────────────────────────────┘
```

## 🤖 에이전트 구성

각 프레임워크는 동일한 에이전트 역할을 구현합니다:

1. **Research Agent** (연구원)
   - 최신 부동산 정책 웹 검색
   - 정부 발표자료 수집
   - 시장 동향 조사

2. **Policy Analyst** (정책 분석가)
   - 규제 내용 상세 분석
   - 영향도 평가
   - 적용 대상 판단

3. **Financial Advisor** (재무 설계사)
   - 대출 한도 계산 (DSR, LTV, DTI)
   - 자금 계획 수립
   - 이자 부담 시뮬레이션

4. **Tax Specialist** (세무 전문가)
   - 취득세 계산
   - 양도세 시뮬레이션
   - 보유세 예측
   - 세금 절감 방안

5. **Strategy Coordinator** (전략 코디네이터)
   - 종합 분석 통합
   - 단계별 실행 전략 수립
   - 리스크 평가

## 📁 프로젝트 구조

```
.
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
│
├── common/                          # 공통 모듈
│   ├── tools/                       # 공통 도구
│   │   ├── brave_search.py         # Brave Search API 클라이언트
│   │   ├── real_estate_calculator.py  # 부동산 계산기
│   │   ├── tax_calculator.py       # 세금 계산기
│   │   └── policy_analyzer.py      # 정책 분석 도구
│   ├── models/                      # 데이터 모델
│   │   └── schemas.py
│   └── config.py
│
├── langgraph_agent/                 # LangGraph 구현
│   ├── Dockerfile
│   ├── app.py
│   ├── graph.py
│   ├── agents/
│   └── requirements.txt
│
├── crewai_agent/                    # Crew.ai 구현
│   ├── Dockerfile
│   ├── app.py
│   ├── crew.py
│   ├── agents/
│   ├── tasks/
│   └── requirements.txt
│
├── strands_agent/                   # Strands Agents 구현
│   ├── Dockerfile
│   ├── app.py
│   ├── workflow.py
│   ├── agents/
│   └── requirements.txt
│
├── ecs/                             # Amazon ECS 배포 설정
│   ├── task-definition-langgraph.json
│   ├── task-definition-crewai.json
│   ├── task-definition-strands.json
│   └── deploy.sh
│
└── docs/                            # 문서
    ├── comparison.md                # 프레임워크 비교 분석
    ├── architecture.md              # 아키텍처 설명
    └── deployment.md                # 배포 가이드
```

## 🚀 Quick Start

### 환경 설정

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 API 키 입력
```

### 로컬 실행

#### LangGraph
```bash
cd langgraph_agent
pip install -r requirements.txt
python app.py
```

#### Crew.ai
```bash
cd crewai_agent
pip install -r requirements.txt
python app.py
```

#### Strands Agents
```bash
cd strands_agent
pip install -r requirements.txt
python app.py
```

### Docker 실행

```bash
# 전체 실행
docker-compose up

# 개별 실행
docker-compose up langgraph
docker-compose up crewai
docker-compose up strands
```

### AWS ECS 배포

```bash
cd ecs
./deploy.sh <framework-name>
# framework-name: langgraph, crewai, strands
```

## 🔑 필요한 API 키

- **OpenAI API Key**: GPT-4 사용
- **Brave Search API Key**: 웹 검색 기능
- **AWS Credentials**: ECS 배포용

## 📊 비교 분석 항목

1. **개발 경험**
   - 코드 복잡도
   - 학습 곡선
   - 디버깅 용이성

2. **성능**
   - 응답 시간
   - 리소스 사용량
   - 확장성

3. **기능**
   - 에이전트 간 협업
   - 상태 관리
   - 에러 처리

4. **운영**
   - 모니터링
   - 로깅
   - 배포 복잡도

자세한 비교 분석은 [docs/comparison.md](docs/comparison.md)를 참고하세요.

## 🛠️ 기술 스택

- **AI Frameworks**: LangGraph, Crew.ai, Strands Agents
- **LLM**: OpenAI GPT-4
- **Search**: Brave Search API
- **Language**: Python 3.11+
- **Container**: Docker
- **Orchestration**: Amazon ECS
- **Infrastructure**: AWS (ECS, ECR, VPC)

## 📝 사용 예시

```python
# 사용자 쿼리 예시
query = """
30대 직장인입니다. 연봉 7천만원, 현재 예금 1억원 보유.
서울 강남구에 3억~4억대 아파트 구매를 고려 중입니다.
현재 부동산 규제와 대출 가능 여부, 그리고 구매 전략을 알려주세요.
"""

# 각 프레임워크의 응답에는 다음이 포함됩니다:
# 1. 현재 적용되는 부동산 규제 (투기과열지구, LTV/DTI 규제 등)
# 2. 대출 가능 금액 계산 (DSR 고려)
# 3. 예상 세금 (취득세, 재산세)
# 4. 중개수수료 계산
# 5. 단계별 구매 전략
# 6. 리스크 및 주의사항
```

## 📄 라이선스

MIT License

## 👥 기여

Issues와 Pull Requests를 환영합니다.

## 📞 문의

프로젝트 관련 문의사항은 Issues를 통해 등록해주세요.
