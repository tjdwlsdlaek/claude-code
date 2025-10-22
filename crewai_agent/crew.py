"""CrewAI crew definition and execution."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from crewai import Crew, Process
from typing import Dict, Any
import logging
import time
from common.config import get_settings
from agents.real_estate_agents import (
    create_researcher,
    create_policy_analyst,
    create_financial_advisor,
    create_tax_specialist,
    create_strategy_coordinator,
    initialize_tools
)
from tasks.real_estate_tasks import (
    create_research_task,
    create_policy_analysis_task,
    create_financial_planning_task,
    create_tax_calculation_task,
    create_strategy_task
)

logger = logging.getLogger(__name__)


def create_real_estate_crew(user_query: Dict[str, Any]) -> Crew:
    """Create CrewAI crew for real estate advisory.

    Args:
        user_query: User query dictionary

    Returns:
        Crew instance
    """
    settings = get_settings()

    # Initialize tools
    initialize_tools(settings.brave_search_api_key)

    # LLM configuration
    llm_config = {
        "model": settings.openai_model,
        "api_key": settings.openai_api_key,
        "temperature": 0.1
    }

    # Create agents
    researcher = create_researcher(llm_config)
    policy_analyst = create_policy_analyst(llm_config)
    financial_advisor = create_financial_advisor(llm_config)
    tax_specialist = create_tax_specialist(llm_config)
    coordinator = create_strategy_coordinator(llm_config)

    # Create tasks
    research_task = create_research_task(researcher, user_query)
    policy_task = create_policy_analysis_task(policy_analyst, user_query)
    financial_task = create_financial_planning_task(financial_advisor, user_query)
    tax_task = create_tax_calculation_task(tax_specialist, user_query)
    strategy_task = create_strategy_task(coordinator, user_query)

    # Set task context (dependencies)
    policy_task.context = [research_task]
    financial_task.context = [research_task, policy_task]
    tax_task.context = [policy_task]
    strategy_task.context = [research_task, policy_task, financial_task, tax_task]

    # Create crew
    crew = Crew(
        agents=[researcher, policy_analyst, financial_advisor, tax_specialist, coordinator],
        tasks=[research_task, policy_task, financial_task, tax_task, strategy_task],
        process=Process.sequential,
        verbose=True
    )

    return crew


def run_real_estate_crew(user_query: Dict[str, Any]) -> Dict[str, Any]:
    """Run the real estate advisory crew.

    Args:
        user_query: User query dictionary

    Returns:
        Strategy and metadata
    """
    start_time = time.time()

    try:
        logger.info("Creating CrewAI crew...")
        crew = create_real_estate_crew(user_query)

        logger.info("Starting crew execution...")
        result = crew.kickoff()

        end_time = time.time()
        execution_time = end_time - start_time

        return {
            "framework": "crewai",
            "strategy": str(result),
            "execution_time_seconds": execution_time,
            "user_query": user_query,
            "errors": [],
            "intermediate_outputs": {}
        }

    except Exception as e:
        logger.error(f"Crew execution error: {e}")
        end_time = time.time()

        return {
            "framework": "crewai",
            "strategy": f"실행 중 오류 발생: {str(e)}",
            "execution_time_seconds": end_time - start_time,
            "user_query": user_query,
            "errors": [str(e)],
            "intermediate_outputs": {}
        }
