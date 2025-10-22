"""LangGraph workflow definition."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from typing import TypedDict, Annotated, Dict, Any
import operator
from langgraph.graph import Graph, StateGraph, END
from langchain_openai import ChatOpenAI
from common.tools import BraveSearchTool, RealEstateCalculator, TaxCalculator, PolicyAnalyzer
from common.config import get_settings
from .agents.researcher import research_real_estate_info
from .agents.policy_analyst import analyze_policy
from .agents.financial_advisor import calculate_financial_plan
from .agents.tax_specialist import calculate_taxes
from .agents.strategy_coordinator import create_comprehensive_strategy
import logging
import time

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State of the agent workflow."""
    user_query: Dict[str, Any]
    research_output: str
    policy_output: str
    financial_output: str
    tax_output: str
    final_strategy: str
    errors: Annotated[list, operator.add]
    start_time: float
    end_time: float


def create_real_estate_graph() -> StateGraph:
    """Create LangGraph workflow for real estate advisor.

    Returns:
        StateGraph workflow
    """
    settings = get_settings()

    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.1,
        api_key=settings.openai_api_key
    )

    # Initialize tools
    brave_search = BraveSearchTool(api_key=settings.brave_search_api_key)
    calculator = RealEstateCalculator()
    tax_calculator = TaxCalculator()
    policy_analyzer = PolicyAnalyzer()

    # Define node functions
    def research_node(state: AgentState) -> AgentState:
        """Research node: Gather information."""
        logger.info("Starting research phase...")
        try:
            result = research_real_estate_info(
                state["user_query"],
                llm,
                brave_search
            )
            if result["success"]:
                state["research_output"] = result["research_output"]
            else:
                state["errors"].append(f"Research error: {result.get('error', 'Unknown')}")
                state["research_output"] = "연구 단계에서 오류가 발생했습니다."
        except Exception as e:
            logger.error(f"Research node error: {e}")
            state["errors"].append(f"Research error: {str(e)}")
            state["research_output"] = "연구 단계에서 오류가 발생했습니다."

        return state

    def policy_node(state: AgentState) -> AgentState:
        """Policy analysis node."""
        logger.info("Starting policy analysis...")
        try:
            result = analyze_policy(
                state["user_query"],
                state["research_output"],
                llm,
                policy_analyzer
            )
            if result["success"]:
                state["policy_output"] = result["analysis_output"]
            else:
                state["errors"].append(f"Policy error: {result.get('error', 'Unknown')}")
                state["policy_output"] = "정책 분석 단계에서 오류가 발생했습니다."
        except Exception as e:
            logger.error(f"Policy node error: {e}")
            state["errors"].append(f"Policy error: {str(e)}")
            state["policy_output"] = "정책 분석 단계에서 오류가 발생했습니다."

        return state

    def financial_node(state: AgentState) -> AgentState:
        """Financial planning node."""
        logger.info("Starting financial planning...")
        try:
            result = calculate_financial_plan(
                state["user_query"],
                state["policy_output"],
                llm,
                calculator
            )
            if result["success"]:
                state["financial_output"] = result["financial_output"]
            else:
                state["errors"].append(f"Financial error: {result.get('error', 'Unknown')}")
                state["financial_output"] = "재무 계획 단계에서 오류가 발생했습니다."
        except Exception as e:
            logger.error(f"Financial node error: {e}")
            state["errors"].append(f"Financial error: {str(e)}")
            state["financial_output"] = "재무 계획 단계에서 오류가 발생했습니다."

        return state

    def tax_node(state: AgentState) -> AgentState:
        """Tax calculation node."""
        logger.info("Starting tax calculation...")
        try:
            result = calculate_taxes(
                state["user_query"],
                state["policy_output"],
                llm,
                tax_calculator
            )
            if result["success"]:
                state["tax_output"] = result["tax_output"]
            else:
                state["errors"].append(f"Tax error: {result.get('error', 'Unknown')}")
                state["tax_output"] = "세금 계산 단계에서 오류가 발생했습니다."
        except Exception as e:
            logger.error(f"Tax node error: {e}")
            state["errors"].append(f"Tax error: {str(e)}")
            state["tax_output"] = "세금 계산 단계에서 오류가 발생했습니다."

        return state

    def strategy_node(state: AgentState) -> AgentState:
        """Strategy coordination node."""
        logger.info("Creating comprehensive strategy...")
        try:
            result = create_comprehensive_strategy(
                state["user_query"],
                state["research_output"],
                state["policy_output"],
                state["financial_output"],
                state["tax_output"],
                llm
            )
            if result["success"]:
                state["final_strategy"] = result["strategy"]
            else:
                state["errors"].append(f"Strategy error: {result.get('error', 'Unknown')}")
                state["final_strategy"] = "전략 수립 단계에서 오류가 발생했습니다."

            state["end_time"] = time.time()
        except Exception as e:
            logger.error(f"Strategy node error: {e}")
            state["errors"].append(f"Strategy error: {str(e)}")
            state["final_strategy"] = "전략 수립 단계에서 오류가 발생했습니다."
            state["end_time"] = time.time()

        return state

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("financial", financial_node)
    workflow.add_node("tax", tax_node)
    workflow.add_node("strategy", strategy_node)

    # Set entry point
    workflow.set_entry_point("research")

    # Add edges (sequential flow)
    workflow.add_edge("research", "policy")
    workflow.add_edge("policy", "financial")
    workflow.add_edge("financial", "tax")
    workflow.add_edge("tax", "strategy")
    workflow.add_edge("strategy", END)

    # Compile graph
    app = workflow.compile()

    return app


def run_real_estate_advisor(user_query: Dict[str, Any]) -> Dict[str, Any]:
    """Run the real estate advisor workflow.

    Args:
        user_query: User query dictionary

    Returns:
        Final strategy and metadata
    """
    app = create_real_estate_graph()

    initial_state: AgentState = {
        "user_query": user_query,
        "research_output": "",
        "policy_output": "",
        "financial_output": "",
        "tax_output": "",
        "final_strategy": "",
        "errors": [],
        "start_time": time.time(),
        "end_time": 0.0
    }

    try:
        final_state = app.invoke(initial_state)

        execution_time = final_state["end_time"] - final_state["start_time"]

        return {
            "framework": "langgraph",
            "strategy": final_state["final_strategy"],
            "execution_time_seconds": execution_time,
            "user_query": user_query,
            "errors": final_state.get("errors", []),
            "intermediate_outputs": {
                "research": final_state["research_output"],
                "policy": final_state["policy_output"],
                "financial": final_state["financial_output"],
                "tax": final_state["tax_output"]
            }
        }
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        return {
            "framework": "langgraph",
            "strategy": f"워크플로우 실행 중 오류 발생: {str(e)}",
            "execution_time_seconds": 0.0,
            "user_query": user_query,
            "errors": [str(e)],
            "intermediate_outputs": {}
        }
