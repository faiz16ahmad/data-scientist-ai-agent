from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class QueryIntent(str, Enum):
    """Possible intents for user queries"""
    VISUALIZATION = "visualization"
    DATA_SUMMARY = "data_summary"
    DATA_FILTER = "data_filter"
    DATA_TRANSFORM = "data_transform"
    UNCLEAR = "unclear"

class QueryAnalysis(BaseModel):
    """Analysis result of a user query"""
    intent: QueryIntent = Field(..., description="The detected intent of the query")
    is_ambiguous: bool = Field(..., description="Whether the query is ambiguous")
    required_parameters: List[str] = Field(
        default_factory=list,
        description="List of parameters required to fulfill the query"
    )
    missing_parameters: List[str] = Field(
        default_factory=list,
        description="Parameters that are required but missing from the query"
    )
    clarification_question: Optional[str] = Field(
        None,
        description="Question to ask the user to clarify their query"
    )
    suggested_options: Optional[List[str]] = Field(
        None,
        description="Suggested options to help the user clarify their query"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the analysis (0.0 to 1.0)"
    )

class ClarificationResponse(BaseModel):
    """User's response to a clarification request"""
    original_query: str = Field(..., description="The original ambiguous query")
    clarification: str = Field(..., description="The user's clarification response")
    parameters: dict = Field(
        default_factory=dict,
        description="Extracted parameters from the clarification"
    )
