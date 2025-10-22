#!/bin/bash

# ECS Deployment Script for AI Agent Comparison
# Usage: ./deploy.sh <framework-name>
# framework-name: langgraph, crewai, strands, or all

set -e

# Configuration
AWS_REGION=${AWS_REGION:-ap-northeast-2}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
CLUSTER_NAME=${ECS_CLUSTER_NAME:-ai-agent-cluster}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check required environment variables
check_env() {
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        echo -e "${RED}Error: AWS_ACCOUNT_ID is not set${NC}"
        exit 1
    fi

    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}Error: OPENAI_API_KEY is not set${NC}"
        exit 1
    fi

    if [ -z "$BRAVE_SEARCH_API_KEY" ]; then
        echo -e "${RED}Error: BRAVE_SEARCH_API_KEY is not set${NC}"
        exit 1
    fi
}

# Create ECR repositories
create_ecr_repos() {
    echo -e "${YELLOW}Creating ECR repositories...${NC}"

    for framework in langgraph crewai strands; do
        repo_name="ai-agent-${framework}"

        if aws ecr describe-repositories --repository-names ${repo_name} --region ${AWS_REGION} 2>/dev/null; then
            echo -e "${GREEN}Repository ${repo_name} already exists${NC}"
        else
            aws ecr create-repository \
                --repository-name ${repo_name} \
                --region ${AWS_REGION} \
                --image-scanning-configuration scanOnPush=true
            echo -e "${GREEN}Created repository ${repo_name}${NC}"
        fi
    done
}

# Build and push Docker image
build_and_push() {
    local framework=$1
    local repo_name="ai-agent-${framework}"
    local image_uri="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${repo_name}:latest"

    echo -e "${YELLOW}Building ${framework} image...${NC}"

    # Login to ECR
    aws ecr get-login-password --region ${AWS_REGION} | \
        docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

    # Build image
    docker build -t ${repo_name}:latest -f ${framework}_agent/Dockerfile .

    # Tag image
    docker tag ${repo_name}:latest ${image_uri}

    # Push image
    echo -e "${YELLOW}Pushing ${framework} image...${NC}"
    docker push ${image_uri}

    echo -e "${GREEN}Successfully pushed ${image_uri}${NC}"
}

# Store secrets in AWS Secrets Manager
store_secrets() {
    echo -e "${YELLOW}Storing secrets in AWS Secrets Manager...${NC}"

    # OpenAI API Key
    if aws secretsmanager describe-secret --secret-id ai-agent/openai-api-key --region ${AWS_REGION} 2>/dev/null; then
        aws secretsmanager update-secret \
            --secret-id ai-agent/openai-api-key \
            --secret-string "${OPENAI_API_KEY}" \
            --region ${AWS_REGION}
    else
        aws secretsmanager create-secret \
            --name ai-agent/openai-api-key \
            --secret-string "${OPENAI_API_KEY}" \
            --region ${AWS_REGION}
    fi

    # Brave Search API Key
    if aws secretsmanager describe-secret --secret-id ai-agent/brave-api-key --region ${AWS_REGION} 2>/dev/null; then
        aws secretsmanager update-secret \
            --secret-id ai-agent/brave-api-key \
            --secret-string "${BRAVE_SEARCH_API_KEY}" \
            --region ${AWS_REGION}
    else
        aws secretsmanager create-secret \
            --name ai-agent/brave-api-key \
            --secret-string "${BRAVE_SEARCH_API_KEY}" \
            --region ${AWS_REGION}
    fi

    echo -e "${GREEN}Secrets stored successfully${NC}"
}

# Register task definition
register_task_definition() {
    local framework=$1
    local task_def_file="ecs/task-definition-${framework}.json"

    echo -e "${YELLOW}Registering ${framework} task definition...${NC}"

    # Replace environment variables in task definition
    cat ${task_def_file} | \
        sed "s/\${AWS_ACCOUNT_ID}/${AWS_ACCOUNT_ID}/g" | \
        sed "s/\${AWS_REGION}/${AWS_REGION}/g" > /tmp/task-def-${framework}.json

    aws ecs register-task-definition \
        --cli-input-json file:///tmp/task-def-${framework}.json \
        --region ${AWS_REGION}

    echo -e "${GREEN}Task definition registered for ${framework}${NC}"
}

# Create or update ECS service
create_or_update_service() {
    local framework=$1
    local service_name="${framework}-service"
    local task_family="${framework}-real-estate-advisor"

    echo -e "${YELLOW}Creating/updating ECS service for ${framework}...${NC}"

    # Check if service exists
    if aws ecs describe-services \
        --cluster ${CLUSTER_NAME} \
        --services ${service_name} \
        --region ${AWS_REGION} | grep -q "ACTIVE"; then

        # Update existing service
        aws ecs update-service \
            --cluster ${CLUSTER_NAME} \
            --service ${service_name} \
            --task-definition ${task_family} \
            --desired-count 1 \
            --region ${AWS_REGION}

        echo -e "${GREEN}Service ${service_name} updated${NC}"
    else
        echo -e "${YELLOW}Service does not exist. Please create it manually through AWS Console or provide VPC configuration${NC}"
        echo -e "${YELLOW}Required: VPC ID, Subnet IDs, Security Group ID${NC}"
    fi
}

# Deploy specific framework
deploy_framework() {
    local framework=$1

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deploying ${framework}...${NC}"
    echo -e "${GREEN}========================================${NC}"

    build_and_push ${framework}
    register_task_definition ${framework}
    create_or_update_service ${framework}

    echo -e "${GREEN}${framework} deployment completed!${NC}\n"
}

# Main script
main() {
    local framework=${1:-all}

    echo -e "${GREEN}AI Agent Comparison - ECS Deployment${NC}"
    echo -e "${GREEN}=====================================${NC}\n"

    # Check environment
    check_env

    # Create ECR repositories
    create_ecr_repos

    # Store secrets
    store_secrets

    # Deploy frameworks
    if [ "$framework" = "all" ]; then
        for fw in langgraph crewai strands; do
            deploy_framework ${fw}
        done
    else
        if [[ "$framework" =~ ^(langgraph|crewai|strands)$ ]]; then
            deploy_framework ${framework}
        else
            echo -e "${RED}Error: Invalid framework name. Use: langgraph, crewai, strands, or all${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment completed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\n${YELLOW}Note: Make sure to create ECS cluster '${CLUSTER_NAME}' if it doesn't exist${NC}"
    echo -e "${YELLOW}Note: Configure load balancers and networking as needed${NC}"
}

# Run main function
main "$@"
