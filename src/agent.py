import os
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class PythonREPLTool(BaseTool):
    """A tool for executing Python code in a REPL environment."""
    name: str = "python_repl"
    description: str = "Execute Python code and return the result"
    df: Optional[pd.DataFrame] = Field(default=None)
    current_figure: Optional[object] = Field(default=None)

    
    def _run(self, code: str) -> str:
        """Execute Python code and return the result."""
        if self.df is None:
            return "Error: No data available. Please upload a CSV file first."
        
        # Clean the code - remove markdown formatting if present
        code = code.strip()
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        code = code.strip()
        
        # Add fuzzy column matching function
        fuzzy_match_code = """
def find_best_column_match(target, columns):
    import difflib
    # Exact match first
    if target in columns:
        return target
    # Case insensitive match
    for col in columns:
        if target.lower() == col.lower():
            return col
    # Fuzzy match
    matches = difflib.get_close_matches(target.lower(), [c.lower() for c in columns], n=1, cutoff=0.6)
    if matches:
        for col in columns:
            if col.lower() == matches[0]:
                return col
    return None
"""
        
        # Initialize persistent variables storage
        if not hasattr(self, '_persistent_vars'):
            self._persistent_vars = {}
        
        # Create a safe execution environment
        import streamlit as st
        import sys
        from io import StringIO
        
        exec_globals = {
            'df': self.df,
            'pd': pd,
            'px': px,
            'go': go,
            'ff': ff,
            'np': __import__('numpy'),
            'tempfile': tempfile,
            'Path': Path,
            'os': os,
            'difflib': __import__('difflib'),
            'time': __import__('time'),
            'st': st
        }
        
        # Add persistent variables to globals BEFORE execution
        exec_globals.update(self._persistent_vars)
        
        exec_locals = {}
        
        # Capture stdout to get print statements and df.info() output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # First execute the fuzzy matching function
            exec(fuzzy_match_code, exec_globals, exec_locals)
            
            # Then execute the user code
            exec(code, exec_globals, exec_locals)
            
            # Update persistent variables with new ones from this execution
            for key, value in exec_locals.items():
                if not key.startswith('_') and key != 'find_best_column_match':
                    self._persistent_vars[key] = value
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Check if Plotly was used for plotting
            if ('px.' in code or 'go.' in code or 'ff.' in code) and ('fig' in exec_locals or 'figure' in exec_locals):
                # Get the Plotly figure from locals
                fig = exec_locals.get('fig') or exec_locals.get('figure')
                if fig is not None:
                    # Store figure reference for the agent to return
                    self.current_figure = fig
                    result = "Code executed successfully. Interactive visualization created."
                    if output.strip():
                        result += f"\n{output}"
                    return result
            else:
                # Return any variables that were created
                result_vars = {k: v for k, v in exec_locals.items() if not k.startswith('_') and k != 'find_best_column_match'}
                result = "Code executed successfully."
                if output.strip():
                    result += f"\n{output}"
                if result_vars:
                    result += f"\nResults: {result_vars}"
                return result
                    
        except Exception as e:
            return f"Error executing code: {str(e)}"
        finally:
            # Always restore stdout
            sys.stdout = old_stdout
    
    async def _arun(self, code: str) -> str:
        """Async version of _run."""
        return self._run(code)

class DataScientistAgent:
    """Main agent for data analysis and visualization."""
    
    def __init__(self, df: Optional[pd.DataFrame] = None):
        """Initialize the agent with a DataFrame."""
        self.df = df
        try:
            self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.1
        )
        except Exception as e:
            print(f"Warning: Could not initialize Google Generative AI: {str(e)}")
            print("Please set up your GOOGLE_API_KEY environment variable.")
            raise ValueError("Google API credentials not found. Please set GOOGLE_API_KEY environment variable.")
        
        # Create tools
        self.python_tool = PythonREPLTool(df=df)
        self.tools = [self.python_tool]
        
        # Create the agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors="Check your output and make sure it conforms!",
            max_iterations=15,
            return_intermediate_steps=True
        )
    
    def _create_agent(self):
        """Create the ReAct agent."""
        template = """You are an expert-level data scientist AI agent. Your purpose is to collaborate with the user to analyze a pandas DataFrame (loaded as `df`) by writing and executing Python code. You must be precise, efficient, and safe in your execution.

Your operation is guided by a core workflow and a set of expert guidelines.

### CORE WORKFLOW: The 5-Step Reasoning Process

You must follow these five steps for every user request. This is your primary reasoning loop.

**1. Grounding & Verification (The "Sanity Check"):**
* **Thought:** My first and most critical action is to ground myself in the data. I must verify the exact column names and data types before doing anything else. This prevents hallucinations and errors.
* **Action:** python_repl
* **Action Input:**
    ```python
actual_columns = df.columns.tolist()
    print(f"Verified Columns: {{actual_columns}}")
    print("---")
    df.info()
    ```

**2. Query Analysis & Planning (The "Blueprint"):**
* **Thought:** Now that I know the data's structure, I will act as a "Query Analyzer." I will analyze the user's request, map it to the available columns, and create a clear, step-by-step plan.
    * **Column Name Resolution:** I will intelligently match user terms to actual columns (e.g., "sales" -> "TotalSales"). If the mapping is obvious, I will proceed. If it's ambiguous (e.g., "sales" could be "TotalSales" or "UnitSales"), I will ask for clarification using "Final Answer". I will NEVER invent column names.
    * **My Plan:**
        * Step 1: [Describe the first action]
        * Step 2: [Describe the second action]
        * ...

**3. Step-by-Step Execution (The "Work"):**
* **Thought:** I will now execute my plan, one step at a time. I will focus on writing clean, efficient code for each action.
* **Action:** python_repl
* **Action Input:** [Code for the current step]
* **Observation:** [Result of the code]
* **(This Thought/Action/Action Input/Observation loop repeats for each step in my plan)**

**4. Self-Critique & Refinement (The "Quality Check"):**
* **Thought:** After executing my plan, I will review the output. Is the code correct? Does the visualization meet all guidelines? Does the result fully answer the user's question? If not, I will adjust my plan and re-execute the necessary steps.

**5. Deliver the Final Answer (The "Conclusion"):**
* **Thought:** I have completed the workflow and verified the result. I am now ready to provide the final answer.
* **Final Answer:** [The final, comprehensive answer to the user's original question, including any necessary text and the final visualization `fig` object if requested.]

---

### **EXPERT GUIDELINES & PROTOCOLS**

These are the specialized rules you must adhere to throughout the workflow. They are based on extensive experience with this environment.

**A. Visualization Rules (Plotly & Streamlit):**
1.  **Plotly Only:** Use Plotly (`px`, `go`) for all plots. NEVER use `matplotlib`.
2.  **Assign to `fig`:** The final visualization object MUST be assigned to a variable named `fig`. If creating multiple plots, overwrite `fig` so only the last one is kept.
3.  **NO `.show()`:** NEVER use `fig.show()`. The Streamlit environment handles rendering. Just creating the `fig` variable is sufficient.
4.  **Clarity and Quality:** Plots must be interactive and visually appealing with proper titles, labels, and colors.
5.  **Categorical Data:** When plotting a numerical vs. a categorical column, use `px.strip` instead of `px.scatter` to avoid unreadable overlaps.
6.  **Decision Trees:** Do not use `matplotlib`'s `plot_tree`. Instead, create a feature importance bar chart using `px.bar`.
7.  **SHAP Visualizations:** NEVER use `shap.waterfall_plot()`, `shap.summary_plot()`, or any SHAP matplotlib-based plots. These will cause parsing failures. Instead, always extract SHAP values as arrays and create Plotly visualizations using `px.bar` for feature importance or custom Plotly plots for SHAP explanations.

**B. Safety & Efficiency Protocols (Loop Prevention):**
1.  **BIAS FOR ACTION:** Code first, explain later. If you state a plan, execute it immediately. Avoid meta-commentary ("I will now...", "Next, I need to...").
2.  **ANTI-REPETITION:** If you find yourself writing the same code, comment, or `print` statement more than twice, STOP immediately. This indicates a loop.
3.  **EMERGENCY STOP:** If a loop is detected, break out by immediately using `Final Answer: Loop detected, stopping execution. Please review the request.` This is a critical safety measure.
4.  **ECONOMY OF CODE:** Use the simplest, most direct code that achieves the goal. Prefer a single line of `px` over a complex `go` object if it suffices.

**C. Code & Environment Rules:**
1.  **Variable Scope:** Define all variables within the same code block (`Action Input`) where they are used. Do not assume variables from previous actions persist.
2.  **Library Fallbacks:**
    * **SHAP vs. XGBoost:** NEVER use `shap.waterfall_plot()`, `shap.summary_plot()`, or any matplotlib-based SHAP plots. Always extract SHAP values as numpy arrays and create Plotly bar charts. If SHAP fails completely, fall back to using `model.feature_importances_` from trained models.
    * **LIME:** If LIME fails, use feature importances from trained models for explainability.
    * **Lifelines:** If lifelines is not available for survival analysis, create simple time-based analysis with pandas.
    * **Numpy:** If you encounter `numpy.exceptions` errors, use basic `import numpy as np` and standard patterns like `np.array`.
    * **Time Series Forecasting:** If statsmodels is not available, use simple moving averages or linear trend forecasting with pandas and numpy.
3.  **Strict Formatting:** Always use the exact `Action:`, `Action Input:`, and `Final Answer:` prefixes. The system depends on this format.
    * **CRITICAL:** Never use backticks around tool names. Write `Action: python_repl` NOT `Action: \`python_repl\``

**D. Time Series Forecasting Fallbacks:**
- **Primary:** Use statsmodels ARIMA for sophisticated forecasting
- **Fallback 1:** Use pandas rolling means and linear regression for trend forecasting
- **Fallback 2:** Use simple moving averages and extrapolation
- **Always:** Create visualizations comparing actual vs forecasted values

Available tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}
"""
        
        prompt = PromptTemplate.from_template(template)
        return create_react_agent(self.llm, self.tools, prompt)
    
    def update_dataframe(self, df: pd.DataFrame):
        """Update the DataFrame for the agent."""
        self.df = df
        self.python_tool.df = df
    
    async def process_query(self, query: str) -> dict:
        """Process a user query and return the result."""
        try:
            result = self.agent_executor.invoke({"input": query})
            
            # Check if a visualization was created
            chart_figure = None
            if hasattr(self.tools[0], 'current_figure'):
                chart_figure = self.tools[0].current_figure
                # Return the figure object (DO NOT use fig.show())
                self.tools[0].current_figure = None
            
            return {
                "success": True,
                "response": result["output"],
                "chart_figure": chart_figure
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}",
                "chart_figure": None
            }
    
    def process_query_sync(self, query: str) -> Dict[str, Any]:
        """Process a user query synchronously and return the result."""
        try:
            result = self.agent_executor.invoke({"input": query})
            
            # Check for generated visualizations
            chart_path = None
            if os.path.exists('temp_chart.png'):
                chart_path = 'temp_chart.png'
            
            return {
                "success": True,
                "response": result.get("output", ""),
                "chart_path": chart_path,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "chart_path": None,
                "error": str(e)
            }

# Create a global agent instance
agent_instance = None

def get_agent(df: Optional[pd.DataFrame] = None) -> DataScientistAgent:
    """Get or create the global agent instance."""
    global agent_instance
    if agent_instance is None:
        agent_instance = DataScientistAgent(df)
    elif df is not None:
        agent_instance.update_dataframe(df)
    return agent_instance
