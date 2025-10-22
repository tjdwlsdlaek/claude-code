# AI Agent Frameworks Comparison: Real Estate Policy Advisor

> ⚠️ **중요**: 이 프로젝트는 **Amazon Bedrock Claude Sonnet 3.7**을 사용합니다.
> API Key 설정 방법은 **[SETUP.md](SETUP.md)**를 먼저 확인하세요!

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

**사용 LLM**: Amazon Bedrock Claude Sonnet 3.7
- Model ID: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
- Region: `us-east-1`

## 🚀 Quick Start

### 1. API Keys 설정 (필수)

**⚠️ Public Repository이므로 export 방식으로 설정합니다**

```bash
# AWS Bedrock 자격 증명
export AWS_ACCESS_KEY_ID="your_aws_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# Brave Search API
export BRAVE_SEARCH_API_KEY="your_brave_search_api_key"

# 애플리케이션 설정 (선택)
export APP_PORT=8000
export LOG_LEVEL="INFO"
```

상세한 설정 방법은 **[SETUP.md](SETUP.md)** 참고

### 2. 의존성 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 공통 의존성 설치
pip install -r requirements.txt

# 특정 프레임워크 의존성 설치
pip install -r langgraph_agent/requirements.txt  # LangGraph
pip install -r crewai_agent/requirements.txt     # Crew.ai
pip install -r strands_agent/requirements.txt    # Strands
```

### 3. 실행

#### LangGraph 실행
```bash
cd langgraph_agent
python app.py
# http://localhost:8000
```

#### Crew.ai 실행
```bash
cd crewai_agent
python app.py
# http://localhost:8001
```

#### Strands Agents 실행
```bash
cd strands_agent
python app.py
# http://localhost:8002
```

### 4. Docker로 실행

```bash
# 모든 프레임워크 동시 실행
docker-compose up

# 개별 실행
docker-compose up langgraph  # http://localhost:8000
docker-compose up crewai     # http://localhost:8001
docker-compose up strands    # http://localhost:8002
```

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
        └───────────────────┬───────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │       Amazon Bedrock Claude 3.7       │
        │      (us.anthropic.claude-3-7...)     │
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

## 📝 사용 예시

### API 호출

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "annual_income": 70000000,
    "savings": 100000000,
    "target_region": "서울 강남구",
    "target_price_min": 300000000,
    "target_price_max": 400000000,
    "additional_info": "생애최초 구매"
  }'
```

### 예상 응답

```json
{
  "framework": "langgraph",
  "strategy": "# 30대를 위한 주택 구매 종합 전략\n\n## 1. 전략 요약\n...",
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

## 🔑 필요한 API 키

| 항목 | 설명 | 획득 방법 |
|------|------|-----------|
| **AWS Access Key** | Bedrock 접근용 | [SETUP.md](SETUP.md#1-aws-bedrock-자격-증명) |
| **AWS Secret Key** | Bedrock 접근용 | 위와 동일 |
| **Brave Search API** | 웹 검색용 | https://brave.com/search/api/ |

**중요**: 모든 API Key는 export 명령어로 설정합니다. .env 파일을 사용할 수도 있지만, **절대로 git에 commit하지 마세요!**

## 📊 프레임워크 비교

| 프레임워크 | 학습 난이도 | 개발 속도 | 성능 | 확장성 | 추천 용도 |
|-----------|------------|----------|------|--------|----------|
| **LangGraph** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 복잡한 엔터프라이즈 시스템 |
| **Crew.ai** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 빠른 프로토타입/MVP |
| **Strands** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 성능 중심 단순 워크플로우 |

상세한 비교 분석은 [docs/comparison.md](docs/comparison.md) 참고

## 🐳 Docker 배포

### 로컬 Docker

```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d
```

### AWS ECS 배포

```bash
cd ecs

# 환경 변수 설정
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1

# 전체 배포
./deploy.sh all

# 개별 배포
./deploy.sh langgraph
./deploy.sh crewai
./deploy.sh strands
```

상세한 배포 가이드는 [docs/deployment.md](docs/deployment.md) 참고

## 📁 프로젝트 구조

```
.
├── README.md                   # 이 파일
├── SETUP.md                    # API Key 설정 가이드 (필독!)
├── requirements.txt            # 공통 의존성
├── .env.example               # 환경 변수 예시
├── docker-compose.yml         # Docker Compose 설정
│
├── common/                    # 공통 모듈
│   ├── tools/                 # 공통 도구
│   │   ├── brave_search.py
│   │   ├── real_estate_calculator.py
│   │   ├── tax_calculator.py
│   │   └── policy_analyzer.py
│   ├── models/schemas.py
│   ├── config.py
│   └── bedrock_client.py      # Bedrock 클라이언트
│
├── langgraph_agent/           # LangGraph 구현
│   ├── Dockerfile
│   ├── app.py
│   ├── graph.py
│   └── agents/
│
├── crewai_agent/              # Crew.ai 구현
│   ├── Dockerfile
│   ├── app.py
│   ├── crew.py
│   ├── agents/
│   └── tasks/
│
├── strands_agent/             # Strands 구현
│   ├── Dockerfile
│   ├── app.py
│   ├── workflow.py
│   └── agents/
│
├── ecs/                       # AWS ECS 배포
│   ├── deploy.sh
│   └── task-definition-*.json
│
└── docs/                      # 문서
    ├── comparison.md          # 프레임워크 비교
    ├── architecture.md        # 아키텍처 설명
    └── deployment.md          # 배포 가이드
```

## 🛠️ 기술 스택

- **AI Framework**: LangGraph, Crew.ai, Custom Strands Pattern
- **LLM**: Amazon Bedrock Claude Sonnet 3.7
- **Search**: Brave Search API
- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Container**: Docker & Docker Compose
- **Cloud**: AWS (Bedrock, ECS, ECR, Secrets Manager)

## 🧪 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 테스트 엔드포인트
curl -X POST http://localhost:8000/test

# 실제 분석 요청
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d @example_query.json
```

## 📚 문서

- **[SETUP.md](SETUP.md)**: API Key 설정 가이드 (필독!)
- **[docs/comparison.md](docs/comparison.md)**: 프레임워크 상세 비교
- **[docs/architecture.md](docs/architecture.md)**: 시스템 아키텍처
- **[docs/deployment.md](docs/deployment.md)**: 배포 가이드

## 🔒 보안 주의사항

**⚠️ 이 Repository는 Public입니다!**

- ❌ API Key를 코드에 절대 포함하지 마세요
- ❌ .env 파일을 git에 commit하지 마세요
- ✅ 항상 export 명령어로 환경 변수 설정
- ✅ .gitignore에 .env가 포함되어 있는지 확인
- ✅ commit 전에 git status로 확인
- ✅ AWS IAM에서 최소 권한 원칙 적용

## 🆘 문제 해결

### AWS Credentials 오류

```bash
# 환경 변수 확인
env | grep AWS

# AWS CLI 테스트
aws bedrock list-foundation-models --region us-east-1
```

### Bedrock 모델 접근 오류

AWS Console → Bedrock → Model access에서 Claude 3.7 모델 활성화 필요

### 의존성 오류

```bash
pip install --upgrade -r requirements.txt
pip install --upgrade boto3 langchain-aws
```

더 많은 문제 해결 방법은 [docs/deployment.md#트러블슈팅](docs/deployment.md#트러블슈팅) 참고

## 📄 라이선스

MIT License

## 👥 기여

Issues와 Pull Requests를 환영합니다.

**기여 시 주의사항**:
- API Key가 포함되지 않았는지 확인
- .env 파일이 commit되지 않았는지 확인
- 코드 리뷰 전에 보안 체크

## 📞 문의

프로젝트 관련 문의사항은 Issues를 통해 등록해주세요.

---

**시작하기**: [SETUP.md](SETUP.md) → 환경 설정 → Quick Start 실행
