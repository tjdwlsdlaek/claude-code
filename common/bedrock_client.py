"""Amazon Bedrock client utilities."""

import json
import boto3
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BedrockClient:
    """Client for Amazon Bedrock Claude models."""

    def __init__(
        self,
        model_id: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "us-east-1"
    ):
        """Initialize Bedrock client.

        Args:
            model_id: Bedrock model ID (e.g., us.anthropic.claude-3-7-sonnet-20250219-v1:0)
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
        """
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def invoke(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.1
    ) -> str:
        """Invoke Bedrock Claude model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling

        Returns:
            Generated text response
        """
        # Prepare request body for Claude 3
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system:
            body["system"] = system

        try:
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response["body"].read())

            # Extract text from response
            if "content" in response_body and len(response_body["content"]) > 0:
                return response_body["content"][0]["text"]
            else:
                logger.error(f"Unexpected response format: {response_body}")
                return ""

        except Exception as e:
            logger.error(f"Bedrock invocation error: {e}")
            raise

    def chat_completion(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.1
    ) -> str:
        """Simple chat completion interface.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Temperature for sampling

        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.invoke(messages, system=system, temperature=temperature)
