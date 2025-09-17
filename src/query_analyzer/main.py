from typing import Dict, Any, Optional
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

from .prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    QUERY_CLARIFICATION_PROMPT
)
from .schemas import QueryAnalysis, ClarificationResponse

class QueryAnalyzer:
    def __init__(self, model_name: str = "gemini-pro", temperature: float = 0.1):
        """Initialize the query analyzer with a language model.
        
        Args:
            model_name: Name of the language model to use
            temperature: Temperature for the language model (0.0 to 1.0)
        """
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=temperature
        )
        
        # Initialize the chains
        self.intent_chain = INTENT_CLASSIFICATION_PROMPT | self.llm | JsonOutputParser()
        self.clarification_chain = QUERY_CLARIFICATION_PROMPT | self.llm | JsonOutputParser()
    
    async def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a user query to determine its intent and clarity.
        
        Args:
            query: The user's natural language query
            
        Returns:
            QueryAnalysis object containing the analysis results
        """
        try:
            # Run the intent classification chain
            result = await self.intent_chain.ainvoke({"query": query})
            
            # Convert the result to a QueryAnalysis object
            analysis = QueryAnalysis(**result)
            
            return analysis
            
        except Exception as e:
            # If there's an error, return a default analysis
            return QueryAnalysis(
                intent="unclear",
                is_ambiguous=True,
                required_parameters=[],
                missing_parameters=[],
                clarification_question="I'm having trouble understanding your request. Could you please rephrase it?",
                suggested_options=[],
                confidence=0.0
            )
    
    async def process_clarification(
        self, 
        original_query: str, 
        clarification: str
    ) -> ClarificationResponse:
        """Process a user's clarification to their original query.
        
        Args:
            original_query: The user's original ambiguous query
            clarification: The user's clarification response
            
        Returns:
            ClarificationResponse with the clarified query and extracted parameters
        """
        try:
            # Run the clarification chain
            result = await self.clarification_chain.ainvoke({
                "original_query": original_query,
                "clarification": clarification
            })
            
            # Convert the result to a ClarificationResponse object
            response = ClarificationResponse(
                original_query=original_query,
                clarification=clarification,
                parameters=result.get("parameters", {})
            )
            
            return response
            
        except Exception as e:
            # If there's an error, return a default response
            return ClarificationResponse(
                original_query=original_query,
                clarification=clarification,
                parameters={}
            )

# Create a singleton instance of the QueryAnalyzer
analyzer = QueryAnalyzer()

# Public API functions
async def analyze_query(query: str) -> QueryAnalysis:
    """Public function to analyze a query.
    
    Args:
        query: The user's natural language query
        
    Returns:
        QueryAnalysis object with the analysis results
    """
    return await analyzer.analyze_query(query)

async def process_clarification(original_query: str, clarification: str) -> ClarificationResponse:
    """Public function to process a clarification.
    
    Args:
        original_query: The original ambiguous query
        clarification: The user's clarification response
        
    Returns:
        ClarificationResponse with the clarified query and parameters
    """
    return await analyzer.process_clarification(original_query, clarification)
