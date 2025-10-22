# 🚀 환경 설정 가이드 (Amazon Bedrock Claude 3.7 사용)

이 프로젝트는 **Amazon Bedrock Claude Sonnet 3.7**을 사용합니다.

## ⚠️ 중요: API Key 보안

**절대로 API Key를 Repository에 commit하지 마세요!**

이 Repository는 Public이므로, 모든 API Key는 export 명령어로 설정합니다.

## 📋 필수 API Keys

### 1. AWS Bedrock 자격 증명

```bash
# AWS Access Key 설정
export AWS_ACCESS_KEY_ID="your_aws_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
export AWS_REGION="us-east-1"

# Bedrock Model ID
export BEDROCK_MODEL_ID="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
```

**AWS 자격 증명 얻는 방법**:
1. AWS Console → IAM → Users → 사용자 선택
2. "Security credentials" 탭
3. "Create access key" 클릭
4. Access Key ID와 Secret Access Key 저장

**필요한 IAM 권한**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    }
  ]
}
```

### 2. Brave Search API Key

```bash
export BRAVE_SEARCH_API_KEY="your_brave_search_api_key"
```

**Brave Search API Key 얻는 방법**:
1. https://brave.com/search/api/ 접속
2. 회원가입 및 무료 플랜 선택
3. API Key 발급

## 🔧 환경 설정 방법

### 방법 1: 명령어로 직접 설정 (권장)

터미널에서 직접 export:

```bash
# AWS Bedrock
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="wJalr..."
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# Brave Search
export BRAVE_SEARCH_API_KEY="BSA..."

# 애플리케이션 설정
export APP_PORT=8000
export LOG_LEVEL="INFO"
```

설정 확인:

```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $BRAVE_SEARCH_API_KEY
```

### 방법 2: .env 파일 사용 (로컬 개발용)

**주의**: .env 파일은 절대로 git에 commit되지 않도록 .gitignore에 추가되어 있습니다.

```bash
# .env.example을 복사
cp .env.example .env

# .env 파일 편집
nano .env
```

**.env 파일 내용**:
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalr...
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
BRAVE_SEARCH_API_KEY=BSA...
APP_PORT=8000
LOG_LEVEL=INFO
```

### 방법 3: Shell Profile에 영구 저장

매번 export하기 번거롭다면:

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
echo 'export AWS_ACCESS_KEY_ID="AKIA..."' >> ~/.bashrc
echo 'export AWS_SECRET_ACCESS_KEY="wJalr..."' >> ~/.bashrc
echo 'export AWS_REGION="us-east-1"' >> ~/.bashrc
echo 'export BEDROCK_MODEL_ID="us.anthropic.claude-3-7-sonnet-20250219-v1:0"' >> ~/.bashrc
echo 'export BRAVE_SEARCH_API_KEY="BSA..."' >> ~/.bashrc

# 적용
source ~/.bashrc
```

## 🐳 Docker 사용 시

Docker Compose를 사용할 경우, 환경 변수를 전달:

```bash
# docker-compose.yml에서 환경 변수 사용
docker-compose up

# 또는 직접 전달
docker run -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
           -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
           -e AWS_REGION=$AWS_REGION \
           -e BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID \
           -e BRAVE_SEARCH_API_KEY=$BRAVE_SEARCH_API_KEY \
           langgraph-agent
```

## 🔒 보안 체크리스트

- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인
- [ ] git status로 .env 파일이 추적되지 않는지 확인
- [ ] API Key가 코드에 하드코딩되어 있지 않은지 확인
- [ ] Public Repository에 commit하기 전 git log 확인
- [ ] AWS IAM에서 최소 권한 원칙 적용
- [ ] 정기적으로 Access Key 로테이션

## 🧪 설정 테스트

환경 변수가 올바르게 설정되었는지 테스트:

```bash
python -c "
import os
from common.config import get_settings

settings = get_settings()
print(f'AWS Region: {settings.aws_region}')
print(f'Bedrock Model: {settings.bedrock_model_id}')
print(f'Brave API Key: {settings.brave_search_api_key[:10]}...')
print('✅ 모든 설정이 정상입니다!')
"
```

## 🆘 문제 해결

### "AWS credentials not found" 오류

```bash
# AWS CLI 설정 확인
aws configure list

# 환경 변수 확인
env | grep AWS
```

### "모델 권한 없음" 오류

AWS Console → Bedrock → Model access에서 Claude 3.7 모델 활성화 필요

### "ImportError: No module named boto3" 오류

```bash
pip install -r requirements.txt
```

## 📚 추가 자료

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 3.7 Model Card](https://www.anthropic.com/claude)
- [Brave Search API Docs](https://brave.com/search/api/)
- [환경 변수 보안 Best Practices](https://12factor.net/config)

---

**다음 단계**: [README.md](README.md)로 돌아가서 애플리케이션 실행 방법 확인
