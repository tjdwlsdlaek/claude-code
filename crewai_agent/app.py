"""FastAPI application for CrewAI real estate advisor."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import uvicorn
from crew import run_real_estate_crew
from common.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CrewAI Real Estate Advisor",
    description="AI agent system for real estate purchase strategy using CrewAI",
    version="1.0.0"
)


class RealEstateQuery(BaseModel):
    """Request model for real estate query."""
    age: int = Field(..., description="나이", ge=20, le=100)
    annual_income: int = Field(..., description="연봉 (원)", gt=0)
    savings: int = Field(..., description="보유 예금 (원)", ge=0)
    target_region: str = Field(..., description="목표 지역")
    target_price_min: int = Field(..., description="목표 가격 최소 (원)", gt=0)
    target_price_max: int = Field(..., description="목표 가격 최대 (원)", gt=0)
    additional_info: Optional[str] = Field(None, description="추가 정보")


class StrategyResponse(BaseModel):
    """Response model for strategy."""
    framework: str
    strategy: str
    execution_time_seconds: float
    user_query: Dict[str, Any]
    errors: list
    intermediate_outputs: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "CrewAI Real Estate Advisor",
        "status": "running",
        "framework": "crewai",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze", response_model=StrategyResponse)
async def analyze_real_estate(query: RealEstateQuery):
    """Analyze real estate purchase strategy.

    Args:
        query: User query with financial and property information

    Returns:
        Comprehensive purchase strategy
    """
    try:
        logger.info(f"Received query for {query.target_region}, price range: {query.target_price_min:,}-{query.target_price_max:,}")

        # Convert query to dict
        query_dict = query.model_dump()

        # Run crew
        result = run_real_estate_crew(query_dict)

        logger.info(f"Strategy generated successfully in {result['execution_time_seconds']:.2f} seconds")

        return StrategyResponse(**result)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test")
async def test_with_example():
    """Test endpoint with example query."""
    example_query = {
        "age": 35,
        "annual_income": 70_000_000,
        "savings": 100_000_000,
        "target_region": "서울 강남구",
        "target_price_min": 300_000_000,
        "target_price_max": 400_000_000,
        "additional_info": "생애최초 구매"
    }

    try:
        result = run_real_estate_crew(example_query)
        return result
    except Exception as e:
        logger.error(f"Test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.app_port + 1,  # Different port from LangGraph
        reload=True,
        log_level=settings.log_level.lower()
    )
