from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

from .prompts import INTENT_CLASSIFICATION_PROMPT
from .schemas import QueryAnalysis

class QueryAnalyzer:
    def __init__(self, temperature: float = 0.1):
        """Initialize the simplified query analyzer.
        
        Args:
            temperature: Temperature for the language model (0.0 to 1.0)
        """
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=temperature
        )
        
        # Initialize the intent classification chain
        self.intent_chain = INTENT_CLASSIFICATION_PROMPT | self.llm | JsonOutputParser()
    
    async def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a user query to determine its intent.
        
        Args:
            query: The user's natural language query
            
        Returns:
            QueryAnalysis object containing the intent classification
        """
        try:
            # Run the intent classification chain
            result = await self.intent_chain.ainvoke({"query": query})
            
            # Convert the result to a QueryAnalysis object
            analysis = QueryAnalysis(**result)
            
            return analysis
            
        except Exception as e:
            # For now, let's be more generous and assume it's a visualization if it contains plot/chart keywords
            query_lower = query.lower()
            if any(keyword in query_lower for keyword in ['plot', 'chart', 'graph', 'visualize', 'show', 'create', 'over time', 'by', 'vs']):
                return QueryAnalysis(
                    intent="visualization",
                    confidence=0.7
                )
            elif any(keyword in query_lower for keyword in ['statistics', 'summary', 'analyze', 'count', 'mean', 'average', 'correlation']):
                return QueryAnalysis(
                    intent="data_summary",
                    confidence=0.7
                )
            else:
                # If there's an error, return unclear intent
                return QueryAnalysis(
                    intent="unclear",
                    confidence=0.0
                )

# Create a singleton instance of the QueryAnalyzer
analyzer = QueryAnalyzer()

# Public API function
async def analyze_query(query: str) -> QueryAnalysis:
    """Public function to analyze a query.
    
    Args:
        query: The user's natural language query
        
    Returns:
        QueryAnalysis object with the intent classification
    """
    return await analyzer.analyze_query(query)
