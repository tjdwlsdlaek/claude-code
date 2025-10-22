# 배포 가이드

본 문서는 부동산 구매 전략 AI 에이전트 시스템을 로컬 및 AWS ECS에 배포하는 방법을 설명합니다.

## 목차

1. [사전 준비](#사전-준비)
2. [로컬 배포](#로컬-배포)
3. [Docker 배포](#docker-배포)
4. [AWS ECS 배포](#aws-ecs-배포)
5. [환경 변수 설정](#환경-변수-설정)
6. [테스트](#테스트)
7. [트러블슈팅](#트러블슈팅)

---

## 사전 준비

### 필수 요구사항

1. **Python 3.11+**
   ```bash
   python --version
   # Python 3.11.0 이상
   ```

2. **Docker & Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **AWS CLI** (ECS 배포 시)
   ```bash
   aws --version
   aws configure
   ```

### API Keys

다음 API 키가 필요합니다:

1. **OpenAI API Key**
   - https://platform.openai.com/api-keys
   - GPT-4 접근 권한 필요

2. **Brave Search API Key**
   - https://brave.com/search/api/
   - 무료 티어 사용 가능

---

## 로컬 배포

### 1. Repository Clone

```bash
git clone <repository-url>
cd claude-code
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**.env 파일**:
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
BRAVE_SEARCH_API_KEY=BSA...
APP_PORT=8000
LOG_LEVEL=INFO
```

### 3. LangGraph 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r langgraph_agent/requirements.txt

# 실행
cd langgraph_agent
python app.py
```

서비스 접근: http://localhost:8000

### 4. Crew.ai 실행

```bash
# 새 터미널
source venv/bin/activate
pip install -r crewai_agent/requirements.txt

cd crewai_agent
python app.py
```

서비스 접근: http://localhost:8001

### 5. Strands 실행

```bash
# 새 터미널
source venv/bin/activate
pip install -r strands_agent/requirements.txt

cd strands_agent
python app.py
```

서비스 접근: http://localhost:8002

---

## Docker 배포

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 편집
```

### 2. 전체 서비스 실행

```bash
# 모든 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 3. 개별 서비스 실행

```bash
# LangGraph만 실행
docker-compose up langgraph

# Crew.ai만 실행
docker-compose up crewai

# Strands만 실행
docker-compose up strands
```

### 4. 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f langgraph
```

### 5. 서비스 중지

```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

---

## AWS ECS 배포

### 전제 조건

1. **AWS 계정**
2. **IAM 권한**:
   - ECS 전체 권한
   - ECR 전체 권한
   - Secrets Manager 읽기/쓰기
   - CloudWatch Logs 권한

3. **AWS CLI 설정**:
   ```bash
   aws configure
   # AWS Access Key ID
   # AWS Secret Access Key
   # Region: ap-northeast-2
   ```

### 1. 환경 변수 설정

```bash
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=ap-northeast-2
export ECS_CLUSTER_NAME=ai-agent-cluster
export OPENAI_API_KEY=sk-...
export BRAVE_SEARCH_API_KEY=BSA...
```

### 2. ECS 클러스터 생성

```bash
# Fargate 클러스터 생성
aws ecs create-cluster \
  --cluster-name ${ECS_CLUSTER_NAME} \
  --region ${AWS_REGION}
```

### 3. VPC 및 네트워크 설정

```bash
# VPC, Subnet, Security Group 생성
# (AWS Console 또는 CloudFormation 사용 권장)

# 필요한 정보:
# - VPC ID
# - Public Subnet IDs (최소 2개)
# - Security Group ID (포트 8000-8002 허용)
```

### 4. 배포 스크립트 실행

```bash
cd ecs

# 전체 배포
./deploy.sh all

# 개별 배포
./deploy.sh langgraph
./deploy.sh crewai
./deploy.sh strands
```

배포 스크립트는 다음을 수행합니다:
1. ECR Repository 생성
2. Docker 이미지 빌드
3. ECR에 이미지 푸시
4. Secrets Manager에 API 키 저장
5. ECS Task Definition 등록

### 5. ECS 서비스 생성

```bash
# LangGraph 서비스
aws ecs create-service \
  --cluster ${ECS_CLUSTER_NAME} \
  --service-name langgraph-service \
  --task-definition langgraph-real-estate-advisor \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region ${AWS_REGION}

# Crew.ai 서비스
aws ecs create-service \
  --cluster ${ECS_CLUSTER_NAME} \
  --service-name crewai-service \
  --task-definition crewai-real-estate-advisor \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region ${AWS_REGION}

# Strands 서비스
aws ecs create-service \
  --cluster ${ECS_CLUSTER_NAME} \
  --service-name strands-service \
  --task-definition strands-real-estate-advisor \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region ${AWS_REGION}
```

### 6. Application Load Balancer 설정 (선택)

```bash
# ALB 생성
aws elbv2 create-load-balancer \
  --name ai-agent-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --region ${AWS_REGION}

# Target Group 생성 (각 서비스별)
aws elbv2 create-target-group \
  --name langgraph-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health \
  --region ${AWS_REGION}

# ECS 서비스를 Target Group에 연결
```

### 7. 배포 확인

```bash
# 서비스 상태 확인
aws ecs describe-services \
  --cluster ${ECS_CLUSTER_NAME} \
  --services langgraph-service crewai-service strands-service \
  --region ${AWS_REGION}

# Task 확인
aws ecs list-tasks \
  --cluster ${ECS_CLUSTER_NAME} \
  --region ${AWS_REGION}

# 로그 확인
aws logs tail /ecs/langgraph-agent --follow
```

---

## 환경 변수 설정

### 필수 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | `sk-...` |
| `BRAVE_SEARCH_API_KEY` | Brave Search API 키 | `BSA...` |
| `OPENAI_MODEL` | 사용할 모델 | `gpt-4-turbo-preview` |
| `APP_PORT` | 애플리케이션 포트 | `8000` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |

### AWS 관련 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `AWS_REGION` | AWS 리전 | `ap-northeast-2` |
| `AWS_ACCOUNT_ID` | AWS 계정 ID | `123456789012` |
| `ECS_CLUSTER_NAME` | ECS 클러스터 이름 | `ai-agent-cluster` |

---

## 테스트

### 헬스 체크

```bash
# LangGraph
curl http://localhost:8000/health

# Crew.ai
curl http://localhost:8001/health

# Strands
curl http://localhost:8002/health
```

### 테스트 엔드포인트

```bash
# LangGraph
curl -X POST http://localhost:8000/test

# Crew.ai
curl -X POST http://localhost:8001/test

# Strands
curl -X POST http://localhost:8002/test
```

### 실제 분석 요청

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

---

## 트러블슈팅

### 문제: Docker 빌드 실패

```bash
# 캐시 없이 빌드
docker-compose build --no-cache

# 개별 빌드
docker build -t langgraph-agent -f langgraph_agent/Dockerfile .
```

### 문제: API 키 오류

```bash
# 환경 변수 확인
echo $OPENAI_API_KEY
echo $BRAVE_SEARCH_API_KEY

# .env 파일 확인
cat .env
```

### 문제: 포트 충돌

```bash
# 사용 중인 포트 확인
lsof -i :8000
lsof -i :8001
lsof -i :8002

# 프로세스 종료
kill -9 <PID>
```

### 문제: ECS Task 시작 실패

```bash
# Task 상태 확인
aws ecs describe-tasks \
  --cluster ${ECS_CLUSTER_NAME} \
  --tasks <task-id> \
  --region ${AWS_REGION}

# 로그 확인
aws logs tail /ecs/langgraph-agent --follow

# Stopped Reason 확인
aws ecs describe-tasks \
  --cluster ${ECS_CLUSTER_NAME} \
  --tasks <task-id> \
  --query 'tasks[0].stoppedReason'
```

### 문제: Secrets Manager 접근 오류

```bash
# IAM 역할 확인
aws iam get-role --role-name ecsTaskExecutionRole

# Secret 확인
aws secretsmanager get-secret-value \
  --secret-id ai-agent/openai-api-key \
  --region ${AWS_REGION}
```

### 문제: 느린 응답 시간

1. **LLM 모델 변경**:
   ```bash
   OPENAI_MODEL=gpt-3.5-turbo  # 더 빠름
   ```

2. **병렬 처리 활성화** (LangGraph):
   - 그래프에서 병렬 노드 추가

3. **리소스 증가** (ECS):
   - CPU: 1024 (1 vCPU)
   - Memory: 2048 MB

### 문제: 메모리 부족

```bash
# Docker 메모리 제한 증가
docker-compose.yml에서:
  mem_limit: 2g

# ECS Task Definition에서:
  "memory": "2048"
```

---

## 모니터링 및 유지보수

### 로그 수집

```bash
# Docker Compose
docker-compose logs -f --tail=100

# ECS
aws logs tail /ecs/langgraph-agent --follow --since 1h
```

### 메트릭 수집

CloudWatch에서 다음 메트릭 모니터링:
- CPUUtilization
- MemoryUtilization
- RequestCount
- ResponseTime
- ErrorCount

### 업데이트 배포

```bash
# 새 이미지 빌드 및 푸시
cd ecs
./deploy.sh <framework-name>

# ECS 서비스 업데이트 (자동)
# 또는 수동:
aws ecs update-service \
  --cluster ${ECS_CLUSTER_NAME} \
  --service <service-name> \
  --force-new-deployment
```

---

## 비용 예상 (AWS ECS)

### Fargate 비용 (ap-northeast-2)

**설정**: 0.5 vCPU, 1GB Memory, 3 Tasks

- vCPU: $0.04656 per vCPU hour
- Memory: $0.00511 per GB hour

**월 비용 계산**:
```
vCPU 비용 = 0.5 * $0.04656 * 24 * 30 * 3 = $50.33
Memory 비용 = 1 * $0.00511 * 24 * 30 * 3 = $11.04
Total = $61.37/월
```

### 추가 비용

- CloudWatch Logs: ~$5/월
- Secrets Manager: $0.40/월/secret
- ECR Storage: ~$1/월
- Data Transfer: 변동

**총 예상 비용**: ~$70-80/월

---

## 참고 자료

- [Docker Documentation](https://docs.docker.com/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- 본 프로젝트 README.md
- docs/comparison.md
- docs/architecture.md
