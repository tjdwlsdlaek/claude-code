"""Task definitions for CrewAI."""

from .real_estate_tasks import (
    create_research_task,
    create_policy_analysis_task,
    create_financial_planning_task,
    create_tax_calculation_task,
    create_strategy_task
)

__all__ = [
    "create_research_task",
    "create_policy_analysis_task",
    "create_financial_planning_task",
    "create_tax_calculation_task",
    "create_strategy_task"
]
