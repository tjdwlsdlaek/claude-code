"""Agent definitions for CrewAI."""

from .real_estate_agents import (
    create_researcher,
    create_policy_analyst,
    create_financial_advisor,
    create_tax_specialist,
    create_strategy_coordinator
)

__all__ = [
    "create_researcher",
    "create_policy_analyst",
    "create_financial_advisor",
    "create_tax_specialist",
    "create_strategy_coordinator"
]
