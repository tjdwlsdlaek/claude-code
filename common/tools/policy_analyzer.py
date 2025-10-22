"""Policy analysis and extraction tools."""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class PolicyAnalyzer:
    """Analyzer for real estate policy information."""

    # Keywords for policy types
    POLICY_KEYWORDS = {
        "대출규제": ["LTV", "DTI", "DSR", "대출", "담보대출", "주택담보대출"],
        "청약규제": ["청약", "특별공급", "일반공급", "청약가점", "당첨"],
        "투기규제": ["투기과열지구", "조정대상지역", "전매제한", "거래허가"],
        "재개발재건축": ["재개발", "재건축", "정비사업", "안전진단"],
        "세금정책": ["취득세", "양도세", "종부세", "재산세", "세금"],
        "임대규제": ["전월세", "임대차", "계약갱신", "전세", "월세"],
    }

    # Regulated regions (예시 - 실제로는 최신 정보 필요)
    SPECULATIVE_OVERHEATED_AREAS = [
        "서울 강남구", "서울 서초구", "서울 송파구", "서울 용산구",
    ]

    ADJUSTMENT_TARGET_AREAS = [
        "서울시", "경기 성남시", "경기 하남시", "경기 과천시",
        "경기 광명시", "경기 구리시"
    ]

    def __init__(self):
        """Initialize policy analyzer."""
        pass

    def classify_policy_type(self, text: str) -> str:
        """Classify policy type based on text content.

        Args:
            text: Policy text to classify

        Returns:
            Policy type classification
        """
        text_lower = text.lower()

        for policy_type, keywords in self.POLICY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return policy_type

        return "기타"

    def extract_policy_info(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and structure policy information from search results.

        Args:
            search_results: List of search results from Brave Search

        Returns:
            List of structured policy information
        """
        policies = []

        for result in search_results:
            title = result.get("title", "")
            description = result.get("description", "")
            url = result.get("url", "")
            age = result.get("age", "")

            # Combine title and description for analysis
            full_text = f"{title} {description}"

            # Classify policy type
            policy_type = self.classify_policy_type(full_text)

            # Assess impact level based on keywords
            impact_level = self._assess_impact_level(full_text)

            # Extract date if available
            effective_date = self._extract_date(full_text, age)

            policies.append({
                "policy_name": title,
                "description": description,
                "effective_date": effective_date,
                "regulation_type": policy_type,
                "impact_level": impact_level,
                "source_url": url,
                "age": age
            })

        return policies

    def _assess_impact_level(self, text: str) -> str:
        """Assess the impact level of a policy.

        Args:
            text: Policy text

        Returns:
            Impact level (상/중/하)
        """
        high_impact_keywords = [
            "강화", "규제", "전면", "중과", "확대", "상향",
            "투기과열지구", "조정대상지역", "제한"
        ]

        medium_impact_keywords = [
            "조정", "개선", "완화", "변경", "수정"
        ]

        text_lower = text.lower()

        # Count high impact keywords
        high_count = sum(1 for keyword in high_impact_keywords if keyword in text_lower)

        # Count medium impact keywords
        medium_count = sum(1 for keyword in medium_impact_keywords if keyword in text_lower)

        if high_count >= 2:
            return "상"
        elif high_count >= 1 or medium_count >= 2:
            return "중"
        else:
            return "하"

    def _extract_date(self, text: str, age: str) -> str:
        """Extract effective date from text.

        Args:
            text: Text containing date information
            age: Age of the article from search result

        Returns:
            Extracted date string
        """
        # Try to find date patterns (YYYY-MM-DD, YYYY.MM.DD, etc.)
        date_patterns = [
            r'20\d{2}[-./년]\s*\d{1,2}[-./월]\s*\d{1,2}',
            r'20\d{2}[-./년]\s*\d{1,2}',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        # If no specific date found, return age
        return age if age else "날짜 정보 없음"

    def determine_region_type(self, region: str) -> str:
        """Determine the regulation type for a region.

        Args:
            region: Region name

        Returns:
            Region type (투기과열지구/조정대상지역/일반지역)
        """
        # Check if in speculative overheated area
        for area in self.SPECULATIVE_OVERHEATED_AREAS:
            if area in region:
                return "투기과열지구"

        # Check if in adjustment target area
        for area in self.ADJUSTMENT_TARGET_AREAS:
            if area in region or region in area:
                return "조정대상지역"

        return "일반지역"

    def analyze_loan_eligibility(
        self,
        region_type: str,
        property_price: int,
        annual_income: int
    ) -> Dict[str, Any]:
        """Analyze loan eligibility based on current regulations.

        Args:
            region_type: Type of region
            property_price: Property price in KRW
            annual_income: Annual income in KRW

        Returns:
            Loan eligibility analysis
        """
        # LTV limits
        ltv_limits = {
            "투기과열지구": 50,
            "조정대상지역": 50,
            "일반지역": 70
        }

        # DTI limits
        dti_limits = {
            "투기과열지구": 40,
            "조정대상지역": 50,
            "일반지역": 60
        }

        ltv_limit = ltv_limits.get(region_type, 50)
        dti_limit = dti_limits.get(region_type, 40)

        # Check additional restrictions for high-value properties
        restrictions = []

        if property_price > 1_500_000_000:
            restrictions.append("15억 초과 고가 주택 - 추가 규제 적용")

        if property_price > 900_000_000 and region_type in ["투기과열지구", "조정대상지역"]:
            restrictions.append("9억 초과 규제지역 주택 - LTV/DTI 추가 제한")

        return {
            "region_type": region_type,
            "ltv_limit": ltv_limit,
            "dti_limit": dti_limit,
            "dsr_limit": 40,
            "restrictions": restrictions,
            "eligible": len(restrictions) == 0 or annual_income > 50_000_000
        }

    def generate_policy_summary(self, policies: List[Dict[str, Any]]) -> str:
        """Generate a summary of policies.

        Args:
            policies: List of policy information

        Returns:
            Summary text
        """
        if not policies:
            return "현재 검색된 정책 정보가 없습니다."

        # Group by policy type
        policy_groups: Dict[str, List[Dict[str, Any]]] = {}
        for policy in policies:
            policy_type = policy.get("regulation_type", "기타")
            if policy_type not in policy_groups:
                policy_groups[policy_type] = []
            policy_groups[policy_type].append(policy)

        # Generate summary
        summary_parts = ["=== 최신 부동산 정책 요약 ===\n"]

        for policy_type, policy_list in policy_groups.items():
            summary_parts.append(f"\n[{policy_type}] ({len(policy_list)}건)")
            for i, policy in enumerate(policy_list[:3], 1):  # Top 3 per category
                summary_parts.append(
                    f"{i}. {policy['policy_name']} "
                    f"(영향도: {policy['impact_level']}, {policy['effective_date']})"
                )

        return "\n".join(summary_parts)
