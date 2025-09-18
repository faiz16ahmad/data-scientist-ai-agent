from langchain.prompts import ChatPromptTemplate

# Simplified intent classification system
INTENT_CLASSIFICATION_SYSTEM = """You are an AI that classifies user queries about data analysis into simple intent categories.

Available intents:
- visualization: The user wants to create a chart, graph, or any visual representation of data. This includes requests like "plot", "chart", "graph", "visualize", "show me a", "create a", "draw", "display", "over time", "by", "vs", "against", etc.
- data_summary: The user wants statistical information, summaries, or analysis of the data. This includes requests like "statistics", "summary", "describe", "analyze", "count", "mean", "average", "correlation", "distribution", etc.
- unclear: Only use this for truly unclear requests like random text, single words without context, or requests that have nothing to do with data analysis.

IMPORTANT: Be VERY generous with classification. If a query mentions any data columns, chart types, or analysis terms, classify it as visualization or data_summary rather than unclear. Only use "unclear" for completely nonsensical or irrelevant requests.

Examples of what should be "visualization":
- "Plot Quantity over time using OrderDate" → visualization
- "Create a bar chart of sales" → visualization  
- "Show me a scatter plot" → visualization
- "Graph revenue by month" → visualization
- "Visualize the data" → visualization

Examples of what should be "data_summary":
- "Show basic statistics" → data_summary
- "What's the average price?" → data_summary
- "Count the records" → data_summary
- "Analyze the correlation" → data_summary

Examples of what should be "unclear":
- "asdfghjkl" → unclear
- "hello" → unclear
- "what is the weather?" → unclear
"""

# Simplified intent classification prompt
INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", INTENT_CLASSIFICATION_SYSTEM),
    ("human", """
    User query: {query}
    
    Classify this query and respond with JSON. Remember to be VERY generous - if the query mentions any data analysis terms, columns, or chart types, classify it as visualization or data_summary rather than unclear.
    
    {{
        "intent": "visualization" | "data_summary" | "unclear",
        "confidence": 0.0-1.0
    }}
    """)
])
