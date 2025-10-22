"""Brave Search API integration for web search."""

import os
import requests
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BraveSearchTool:
    """Brave Search API client for web search."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Brave Search client.

        Args:
            api_key: Brave Search API key. If not provided, reads from env.
        """
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            raise ValueError("Brave Search API key is required")

        self.base_url = "https://api.search.brave.com/res/v1"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

    def search(
        self,
        query: str,
        count: int = 10,
        country: str = "KR",
        search_lang: str = "ko",
        freshness: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search the web using Brave Search API.

        Args:
            query: Search query
            count: Number of results to return (max 20)
            country: Country code for localized results
            search_lang: Search language
            freshness: Time filter (e.g., "pd" for past day, "pw" for past week, "pm" for past month, "py" for past year)

        Returns:
            List of search results with title, description, and URL
        """
        try:
            params = {
                "q": query,
                "count": min(count, 20),
                "country": country,
                "search_lang": search_lang,
            }

            if freshness:
                params["freshness"] = freshness

            response = requests.get(
                f"{self.base_url}/web/search",
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            results = []

            # Extract web results
            if "web" in data and "results" in data["web"]:
                for item in data["web"]["results"]:
                    results.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "url": item.get("url", ""),
                        "age": item.get("age", ""),
                        "extra_snippets": item.get("extra_snippets", [])
                    })

            logger.info(f"Brave Search returned {len(results)} results for query: {query}")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Brave Search API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Brave Search: {e}")
            return []

    def search_real_estate_policy(
        self,
        region: Optional[str] = None,
        policy_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for recent real estate policies.

        Args:
            region: Specific region to search for (e.g., "서울", "경기")
            policy_type: Type of policy (e.g., "대출규제", "청약", "재개발")

        Returns:
            List of search results about real estate policies
        """
        query_parts = ["부동산 정책", "2024", "2025"]

        if region:
            query_parts.append(region)

        if policy_type:
            query_parts.append(policy_type)

        query = " ".join(query_parts)

        # Search for recent policies (past 3 months)
        return self.search(query=query, count=10, freshness="pm")

    def search_loan_regulations(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for loan regulations.

        Args:
            region: Specific region to search for

        Returns:
            List of search results about loan regulations
        """
        query_parts = ["주택담보대출", "LTV", "DTI", "DSR", "규제"]

        if region:
            query_parts.append(region)

        query = " ".join(query_parts)
        return self.search(query=query, count=10, freshness="pm")

    def search_tax_info(self) -> List[Dict[str, Any]]:
        """Search for recent tax information.

        Returns:
            List of search results about real estate taxes
        """
        query = "부동산 취득세 양도세 2024 2025"
        return self.search(query=query, count=10, freshness="py")

    def search_market_trends(self, region: str) -> List[Dict[str, Any]]:
        """Search for market trends in a specific region.

        Args:
            region: Region to search for

        Returns:
            List of search results about market trends
        """
        query = f"{region} 아파트 시세 전망 2024 2025"
        return self.search(query=query, count=10, freshness="pm")
