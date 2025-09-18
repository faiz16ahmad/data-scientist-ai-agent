from enum import Enum
from pydantic import BaseModel, Field

class QueryIntent(str, Enum):
    """Possible intents for user queries"""
    VISUALIZATION = "visualization"
    DATA_SUMMARY = "data_summary"
    UNCLEAR = "unclear"

class QueryAnalysis(BaseModel):
    """Simplified analysis result of a user query - only intent classification"""
    intent: QueryIntent = Field(..., description="The detected intent of the query")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the analysis (0.0 to 1.0)"
    )
