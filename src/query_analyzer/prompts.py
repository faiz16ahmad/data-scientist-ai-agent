from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# System message for intent classification
INTENT_CLASSIFICATION_SYSTEM = """You are an AI that classifies user queries about data analysis into specific intents.
Your task is to determine the user's intent from their query and identify if the query is clear enough to proceed.

Available intents:
- visualization: The user wants to create a chart or graph
- data_summary: The user wants statistical information about the data
- data_filter: The user wants to filter or subset the data
- data_transform: The user wants to transform or modify the data
- unclear: The intent is not clear or doesn't fit other categories

For visualization intents, check if the query specifies:
1. Chart type (bar, line, scatter, etc.)
2. X and Y axes (if applicable)
3. Any grouping or filtering criteria

For data_summary intents, check if the query specifies:
1. What statistics are needed (mean, median, count, etc.)
2. Which columns to summarize

For data_filter intents, check if the query specifies:
1. Filter conditions
2. Which columns to filter on

For data_transform intents, check if the query specifies:
1. What transformation to perform
2. Which columns to transform

If any of these required elements are missing, the query is considered ambiguous.
"""

# Human message template for intent classification
INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", INTENT_CLASSIFICATION_SYSTEM),
    ("human", """
    User query: {query}
    
    Analyze the query and provide a JSON response with the following structure:
    {{
        "intent": "one_of_the_intents_listed_above",
        "is_ambiguous": true/false,
        "required_parameters": ["list", "of", "required", "parameters"],
        "missing_parameters": ["list", "of", "missing", "parameters"],
        "clarification_question": "A question to ask the user to clarify their query, or null if not needed",
        "suggested_options": ["list", "of", "suggested", "options"],
        "confidence": 0.0-1.0
    }}
    """)
])

# System message for query clarification
QUERY_CLARIFICATION_SYSTEM = """You are an AI that helps clarify ambiguous data analysis queries.
Your task is to take the user's original query and their clarification response, and combine them into a clear, actionable query.
"""

# Human message template for query clarification
QUERY_CLARIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", QUERY_CLARIFICATION_SYSTEM),
    ("human", """
    Original query: {original_query}
    User's clarification: {clarification}
    
    Based on the original query and the user's clarification, provide a clear, actionable query that can be executed.
    
    Respond with a JSON object containing:
    {{
        "clarified_query": "The new, clear query",
        "parameters": {{
            // Any extracted parameters from the clarification
        }}
    }}
    """)
])
