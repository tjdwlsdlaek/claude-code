"""Workflow orchestration for Strands-style agents."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from typing import Dict, Any
from openai import OpenAI
import logging
import time
from common.config import get_settings
from common.tools import BraveSearchTool, RealEstateCalculator, TaxCalculator, PolicyAnalyzer
from agents.real_estate_agents import (
    ResearcherAgent,
    PolicyAnalystAgent,
    FinancialAdvisorAgent,
    TaxSpecialistAgent,
    StrategyCoordinatorAgent
)

logger = logging.getLogger(__name__)


class RealEstateWorkflow:
    """Workflow orchestrator for real estate advisory agents."""

    def __init__(self):
        """Initialize workflow with tools and agents."""
        settings = get_settings()

        # Initialize LLM client
        self.llm_client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

        # Initialize tools
        self.brave_search = BraveSearchTool(api_key=settings.brave_search_api_key)
        self.calculator = RealEstateCalculator()
        self.tax_calculator = TaxCalculator()
        self.policy_analyzer = PolicyAnalyzer()

        # Initialize agents
        self.researcher = ResearcherAgent(self.llm_client, self.brave_search, self.model)
        self.policy_analyst = PolicyAnalystAgent(self.llm_client, self.policy_analyzer, self.model)
        self.financial_advisor = FinancialAdvisorAgent(self.llm_client, self.calculator, self.model)
        self.tax_specialist = TaxSpecialistAgent(self.llm_client, self.tax_calculator, self.model)
        self.coordinator = StrategyCoordinatorAgent(self.llm_client, self.model)

    def run(self, user_query: Dict[str, Any]) -> Dict[str, Any]:
        """Run the workflow.

        Args:
            user_query: User query dictionary

        Returns:
            Final strategy and metadata
        """
        start_time = time.time()
        errors = []
        intermediate_outputs = {}

        try:
            # Initialize context
            context = {
                "user_query": user_query
            }

            # Step 1: Research
            logger.info("Step 1: Research")
            try:
                research_result = self.researcher.execute(context)
                context["research_output"] = research_result["output"]
                intermediate_outputs["research"] = research_result["output"]
            except Exception as e:
                logger.error(f"Research error: {e}")
                errors.append(f"Research: {str(e)}")
                context["research_output"] = "연구 단계에서 오류가 발생했습니다."

            # Step 2: Policy Analysis
            logger.info("Step 2: Policy Analysis")
            try:
                policy_result = self.policy_analyst.execute(context)
                context["policy_output"] = policy_result["output"]
                context["region_type"] = policy_result.get("region_type", "조정대상지역")
                intermediate_outputs["policy"] = policy_result["output"]
            except Exception as e:
                logger.error(f"Policy analysis error: {e}")
                errors.append(f"Policy: {str(e)}")
                context["policy_output"] = "정책 분석 단계에서 오류가 발생했습니다."
                context["region_type"] = "조정대상지역"

            # Step 3: Financial Planning
            logger.info("Step 3: Financial Planning")
            try:
                financial_result = self.financial_advisor.execute(context)
                context["financial_output"] = financial_result["output"]
                intermediate_outputs["financial"] = financial_result["output"]
            except Exception as e:
                logger.error(f"Financial planning error: {e}")
                errors.append(f"Financial: {str(e)}")
                context["financial_output"] = "재무 계획 단계에서 오류가 발생했습니다."

            # Step 4: Tax Calculation
            logger.info("Step 4: Tax Calculation")
            try:
                tax_result = self.tax_specialist.execute(context)
                context["tax_output"] = tax_result["output"]
                intermediate_outputs["tax"] = tax_result["output"]
            except Exception as e:
                logger.error(f"Tax calculation error: {e}")
                errors.append(f"Tax: {str(e)}")
                context["tax_output"] = "세금 계산 단계에서 오류가 발생했습니다."

            # Step 5: Strategy Coordination
            logger.info("Step 5: Strategy Coordination")
            try:
                strategy_result = self.coordinator.execute(context)
                final_strategy = strategy_result["output"]
            except Exception as e:
                logger.error(f"Strategy coordination error: {e}")
                errors.append(f"Strategy: {str(e)}")
                final_strategy = "전략 수립 단계에서 오류가 발생했습니다."

            end_time = time.time()
            execution_time = end_time - start_time

            return {
                "framework": "strands",
                "strategy": final_strategy,
                "execution_time_seconds": execution_time,
                "user_query": user_query,
                "errors": errors,
                "intermediate_outputs": intermediate_outputs
            }

        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            end_time = time.time()

            return {
                "framework": "strands",
                "strategy": f"워크플로우 실행 중 오류 발생: {str(e)}",
                "execution_time_seconds": end_time - start_time,
                "user_query": user_query,
                "errors": errors + [str(e)],
                "intermediate_outputs": intermediate_outputs
            }


def run_real_estate_workflow(user_query: Dict[str, Any]) -> Dict[str, Any]:
    """Run the real estate workflow.

    Args:
        user_query: User query dictionary

    Returns:
        Strategy and metadata
    """
    workflow = RealEstateWorkflow()
    return workflow.run(user_query)
