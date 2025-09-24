import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import pandas as pd
import requests
import uuid
import json
import plotly
import plotly.graph_objects as go
import re

# Load environment variables
load_dotenv()

API_URL = "http://127.0.0.1:8000"  # URL of your FastAPI backend

# Set page config
st.set_page_config(
    page_title="Data Scientist AI Agent",
    page_icon="📊",
    layout="wide"
)

# --- Session State Initialization ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df_uploaded' not in st.session_state:
    st.session_state.df_uploaded = False
if 'data_info' not in st.session_state:
    st.session_state.data_info = None
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

def check_api_connection():
    """Check if the FastAPI server is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def upload_file_to_api(uploaded_file):
    """Upload file to the FastAPI backend."""
    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        response = requests.post(
            f"{API_URL}/upload/?session_id={st.session_state.session_id}", 
            files=files,
            timeout=30
        )
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_data_info():
    """Get data information from the API."""
    try:
        response = requests.get(f"{API_URL}/session/{st.session_state.session_id}/data_info")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def analyze_query_with_api(query):
    """Analyze query intent using the API."""
    try:
        payload = {"query": query}
        response = requests.post(f"{API_URL}/analyze_query/", json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def process_query_with_api(query):
    """Process query using the API."""
    try:
        payload = {"query": query, "session_id": st.session_state.session_id}
        response = requests.post(f"{API_URL}/process_query/", json=payload, timeout=60)
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def extract_code_blocks(text):
    """Extract code blocks from text and return (clean_text, code_blocks)."""
    # Pattern to match code blocks (```python ... ``` or ``` ... ```)
    code_pattern = r'```(?:python)?\s*\n?(.*?)\n?```'
    code_blocks = re.findall(code_pattern, text, re.DOTALL)
    
    # Filter out useless code blocks and duplicates
    meaningful_blocks = []
    seen_blocks = set()
    
    for block in code_blocks:
        block = block.strip()
        
        # Skip empty or very short blocks
        if len(block) < 10:
            continue
            
        # Skip blocks that are just single variable assignments (like just "fig")
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*$', block):
            continue
            
        # Skip blocks that are just "fig" or similar single assignments
        if block in ['fig', 'result', 'df', 'fig1', 'fig2', 'fig3']:
            continue
            
        # Skip blocks that are just variable assignments without meaningful code
        if (block.startswith('fig') and 
            not re.search(r'import\s+', block) and 
            not re.search(r'px\.', block) and
            not re.search(r'pd\.', block)):
            continue
            
        # Must contain substantial code (imports, function calls, etc.)
        if (re.search(r'import\s+', block) or 
            re.search(r'def\s+', block) or 
            re.search(r'class\s+', block) or
            re.search(r'px\.', block) or
            re.search(r'pd\.', block) or
            re.search(r'\.\w+\s*\(', block) or
            re.search(r'=\s*\w+\s*\(', block) or
            re.search(r'for\s+', block) or
            re.search(r'if\s+', block) or
            re.search(r'#', block) or
            re.search(r'x=', block) or
            re.search(r'y=', block) or
            re.search(r'color=', block) or
            re.search(r'title=', block) or
            re.search(r'facet_', block) or
            re.search(r'hover_data', block)):
            
            # Avoid duplicates by checking if we've seen this block before
            block_hash = hash(block)
            if block_hash not in seen_blocks:
                meaningful_blocks.append(block)
                seen_blocks.add(block_hash)
    
    # Remove code blocks from the original text
    clean_text = re.sub(code_pattern, '', text, flags=re.DOTALL)
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text).strip()
    
    return clean_text, meaningful_blocks

def display_message_with_code(content, message_type=None):
    """Display a message with collapsible code blocks."""
    if message_type == "visualization" and "json" in content:
        # Handle visualization messages separately
        return
    
    # Extract code blocks
    clean_text, code_blocks = extract_code_blocks(content)
    
    # Debug: Show what we found
    if st.session_state.get('debug_mode', False):
        st.write(f"**Debug:** Found {len(code_blocks)} code blocks")
        for i, block in enumerate(code_blocks):
            st.write(f"Block {i+1}: {len(block)} chars")
    
    # Display the clean text if it exists
    if clean_text.strip():
        st.write(clean_text)
    
    # Display code blocks in collapsible expanders
    if code_blocks:
        # If we have multiple blocks, prioritize the most complete one
        if len(code_blocks) > 1:
            # Sort by length (longest first) to show the most complete code first
            code_blocks.sort(key=len, reverse=True)
            
        # Only show the first (most complete) code block to avoid duplicates
        if code_blocks:
            with st.expander("💻 View Code Block 1", expanded=True):  # Expand by default
                st.code(code_blocks[0].strip(), language="python")
    else:
        # If no meaningful code blocks, show a helpful message
        with st.expander("💻 View Code Block 1", expanded=False):
            st.info("🔍 No significant code blocks found in this response. The AI agent may have used internal processing or returned a simple result.")
            st.code("# This response didn't contain detailed code implementation\n# The visualization was generated using internal AI processing", language="python")

def generate_suggested_questions(data_info):
    """Generate 5 smart visualization questions based on the dataset."""
    if not data_info:
        return []
    
    questions = []
    numeric_cols = data_info.get('numeric_columns', [])
    categorical_cols = data_info.get('categorical_columns', [])
    datetime_cols = data_info.get('datetime_columns', [])
    
    # Question 1: Basic overview
    if len(numeric_cols) > 0:
        questions.append(f"Show me basic statistics for {numeric_cols[0]}")
    
    # Question 2: Distribution analysis
    if len(numeric_cols) > 0:
        questions.append(f"Create a histogram of {numeric_cols[0]}")
    
    # Question 3: Categorical analysis
    if len(categorical_cols) > 0:
        questions.append(f"Show value counts for {categorical_cols[0]}")
    
    # Question 4: Correlation analysis
    if len(numeric_cols) >= 2:
        questions.append(f"Show correlation between {numeric_cols[0]} and {numeric_cols[1]}")
    
    # Question 5: Time series or comparison
    if len(datetime_cols) > 0 and len(numeric_cols) > 0:
        questions.append(f"Plot {numeric_cols[0]} over time using {datetime_cols[0]}")
    elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
        questions.append(f"Create a bar chart of {numeric_cols[0]} by {categorical_cols[0]}")
    elif len(numeric_cols) >= 2:
        questions.append(f"Create a scatter plot of {numeric_cols[0]} vs {numeric_cols[1]}")
    else:
        questions.append("Show me the top 10 rows of data")
    
    return questions[:5]  # Return exactly 5 questions

def setup_column_selection_ui():
    """Setup interactive column picker interface in sidebar."""
    if st.session_state.data_info:
        # Sidebar for column picker
        st.sidebar.header("📝 Column Picker")
        st.sidebar.write("Click column names to add them to your query:")
        
        # Column categories for better UX
        numeric_cols = st.session_state.data_info.get('numeric_columns', [])
        categorical_cols = st.session_state.data_info.get('categorical_columns', [])
        datetime_cols = st.session_state.data_info.get('datetime_columns', [])
        
        # Debug info (remove in production)
        st.sidebar.write(f"**Debug:** Found {len(numeric_cols)} numeric, {len(categorical_cols)} categorical, {len(datetime_cols)} datetime columns")
        
        # Debug toggle
        if st.sidebar.checkbox("🐛 Debug Mode", value=False):
            st.session_state.debug_mode = True
        else:
            st.session_state.debug_mode = False
        
        # If no categorized columns, fallback to all columns
        if not numeric_cols and not categorical_cols and not datetime_cols:
            all_cols = st.session_state.data_info.get('columns', [])
            st.sidebar.write("**All Columns:**")
            for col in all_cols:
                if st.sidebar.button(f"📋 {col}", key=f"all_{col}", help=f"Click to add '{col}' to your query"):
                    current_text = st.session_state.get('chat_input', '') or ''
                    if current_text.strip():
                        new_text = current_text + f" {col}"
                    else:
                        new_text = col
                    st.session_state.chat_input = new_text
                    st.session_state.input_key += 1
                    st.rerun()
        else:
            # Clickable column buttons - always additive
            st.sidebar.subheader("📊 Numeric Columns")
            for col in numeric_cols:
                if st.sidebar.button(f"📊 {col}", key=f"num_{col}", help=f"Click to add '{col}' to your query"):
                    # Get current chat input value
                    current_text = st.session_state.get('chat_input', '') or ''
                    
                    # Always add column to chat input (no selection tracking)
                    if current_text.strip():
                        new_text = current_text + f" {col}"
                    else:
                        new_text = col
                    st.session_state.chat_input = new_text
                    st.session_state.input_key += 1
                    st.rerun()
        
            st.sidebar.subheader("🏷️ Categorical Columns")
            for col in categorical_cols:
                if st.sidebar.button(f"🏷️ {col}", key=f"cat_{col}", help=f"Click to add '{col}' to your query"):
                    # Get current chat input value
                    current_text = st.session_state.get('chat_input', '') or ''
                    
                    # Always add column to chat input (no selection tracking)
                    if current_text.strip():
                        new_text = current_text + f" {col}"
                    else:
                        new_text = col
                    st.session_state.chat_input = new_text
                    st.session_state.input_key += 1
                    st.rerun()
            
            if datetime_cols:
                st.sidebar.subheader("📅 DateTime Columns")
                for col in datetime_cols:
                    if st.sidebar.button(f"📅 {col}", key=f"dt_{col}", help=f"Click to add '{col}' to your query"):
                        # Get current chat input value
                        current_text = st.session_state.get('chat_input', '') or ''
                        
                        # Always add column to chat input (no selection tracking)
                        if current_text.strip():
                            new_text = current_text + f" {col}"
                        else:
                            new_text = col
                        st.session_state.chat_input = new_text
                        st.session_state.input_key += 1
                        st.rerun()
        
            # Query builder controls
            st.sidebar.subheader("🛠️ Query Builder")
            col1, col2 = st.sidebar.columns(2)
        
            with col1:
                if st.button("🗑️ Clear", key="clear_query", help="Clear the current query"):
                    st.session_state.chat_input = ""
                    st.session_state.input_key += 1
                    st.rerun()
            
            with col2:
                if st.button("⬅️ Undo", key="undo_query", help="Remove last word"):
                    # Get current chat input
                    current_text = st.session_state.get('chat_input', '') or ''
                    if current_text.strip():
                        # Remove last word from chat input
                        words = current_text.strip().split()
                        if words:
                            new_text = " ".join(words[:-1])
                            st.session_state.chat_input = new_text
                            st.session_state.input_key += 1
                    st.rerun()
        
            # Quick Analysis Buttons
            st.sidebar.subheader("🚀 Quick Analysis")
            
            if st.sidebar.button("📊 Basic Stats", key="quick_stats"):
                current_text = st.session_state.get('chat_input', '') or ''
                st.session_state.chat_input = current_text + " show basic statistics"
                st.session_state.input_key += 1
                st.rerun()
            
            if st.sidebar.button("🔗 Correlation", key="quick_corr"):
                current_text = st.session_state.get('chat_input', '') or ''
                st.session_state.chat_input = current_text + " show correlation matrix"
                st.session_state.input_key += 1
                st.rerun()
            
            if st.sidebar.button("📈 Value Counts", key="quick_counts"):
                current_text = st.session_state.get('chat_input', '') or ''
                st.session_state.chat_input = current_text + " show value counts"
                st.session_state.input_key += 1
                st.rerun()
            
            if st.sidebar.button("📊 Histogram", key="quick_hist"):
                current_text = st.session_state.get('chat_input', '') or ''
                st.session_state.chat_input = current_text + " create histogram"
                st.session_state.input_key += 1
                st.rerun()
            
            if st.sidebar.button("📈 Scatter Plot", key="quick_scatter"):
                current_text = st.session_state.get('chat_input', '') or ''
                st.session_state.chat_input = current_text + " create scatter plot"
                st.session_state.input_key += 1
                st.rerun()

    else:
        st.sidebar.info("🔄 Processing query...")

def main():
    st.title("🤖 Data Scientist AI Agent (Client-Server Edition)")
    st.write("Upload a CSV or Excel file and ask questions about your data in natural language.")
    
    # Check API connection
    if not check_api_connection():
        st.error("🚨 **Connection Error**: The FastAPI server is not running. Please start it with: `uvicorn api:app --reload`")
        st.stop()
    
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message.get("type") == "suggestions":
                st.write(message["content"])
                # Display clickable suggested questions
                questions = message.get("questions", [])
                for j, question in enumerate(questions):
                    if st.button(f"💡 {question}", key=f"suggestion_{i}_{j}", help="Click to use this question"):
                        st.session_state.chat_input = question
                        st.session_state.input_key += 1
                        st.rerun()
            elif message.get("type") == "visualization" and message.get("json"):
                st.write(message["content"])
                # Display the interactive visualization using Plotly
                chart_data = json.loads(message["json"])
                fig = go.Figure(chart_data)
                st.plotly_chart(fig, use_container_width=True, key=f"plotly_chart_{i}")
            else:
                # Use the new function to display messages with collapsible code
                display_message_with_code(message["content"], message.get("type"))
    
    # Always show sidebar info
    if st.session_state.df_uploaded and st.session_state.data_info:
        setup_column_selection_ui()
    else:
        st.sidebar.header("📁 Upload Data")
        st.sidebar.info("Upload a CSV or Excel file to start analyzing your data with AI!")
    
    # File uploader
    if not st.session_state.df_uploaded:
        uploaded_file = st.file_uploader("Upload your data file", type=['csv', 'xlsx', 'xls'])
        if uploaded_file:
            with st.spinner("Uploading and processing file..."):
                response = upload_file_to_api(uploaded_file)
                if response and response.status_code == 200:
                    result = response.json()
                    st.session_state.df_uploaded = True
                    st.session_state.data_info = result
                    
                    st.success(f"✅ File uploaded successfully! Your dataset has {result['shape'][0]} rows and {result['shape'][1]} columns.")
                    
                    # Add welcome message
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"File uploaded successfully! Your dataset has {result['shape'][0]} rows and {result['shape'][1]} columns. Here are some suggested questions to get you started:"
                    })
                    
                    # Generate and show suggested questions
                    suggested_questions = generate_suggested_questions(result)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "**🎯 Suggested Questions:**",
                        "type": "suggestions",
                        "questions": suggested_questions
                    })
                    
                    # Show data preview
                    with st.expander("📊 Data Preview"):
                        st.write("**Dataset Information:**")
                        st.json({
                            "Shape": result['shape'],
                            "Columns": result['columns'],
                            "Data Types": result['dtypes']
                        })
                    
                    st.rerun()
                elif response:
                    st.error(f"❌ Error uploading file: {response.text}")
                else:
                    st.error("❌ Failed to connect to the API server.")
    
    # Chat input
    if st.session_state.df_uploaded:
        # Chat input with proper value handling
        placeholder_text = "Type your question or use column picker above (e.g., 'plot', 'correlation between', 'analyze')"
        
        # Use a text input instead of chat_input for better control
        user_input = st.text_input(
            "Ask a question about your data:",
            value=st.session_state.get('chat_input', ''),
            placeholder=placeholder_text,
            key=f"text_input_query_{st.session_state.input_key}"
        )
        
        # Update session state when user types
        if user_input != st.session_state.get('chat_input', ''):
            st.session_state.chat_input = user_input
        
        # Send button
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Send", key="send_button", type="primary"):
                if st.session_state.chat_input.strip():
                    final_query = st.session_state.chat_input.strip()
                    
                    # Clear chat input after sending and increment key to force reset
                    st.session_state.chat_input = ""
                    st.session_state.input_key += 1
                    
                    # Add user message
                    st.session_state.messages.append({"role": "user", "content": final_query})
                    
                    # Process the query
                    with st.spinner("Processing your request..."):
                        # First, analyze the query intent
                        analysis = analyze_query_with_api(final_query)
                        
                        if analysis and analysis.get("intent") == "unclear":
                            # Intent is unclear - show simple message
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "I'm sorry, I don't understand that request. Please try rephrasing, or use the column picker to help build your query."
                            })
                        else:
                            # Intent is clear - process with agent
                            response = process_query_with_api(final_query)
                            
                            if response and response.status_code == 200:
                                result = response.json()
                                assistant_response = result.get("response", "I'm sorry, I couldn't get a response.")
                                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                                
                                if result.get("visualization_generated"):
                                    # Display the visualization JSON
                                    if result.get("visualization_json"):
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "📊 **Interactive visualization generated!**",
                                            "type": "visualization",
                                            "json": result["visualization_json"]
                                        })
                                    else:
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "📊 **Interactive visualization generated!**"
                                        })
                            elif response:
                                st.error(f"❌ Error from API: {response.text}")
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": f"Error from API: {response.text}"
                                })
                            else:
                                st.error("❌ Failed to connect to the API server.")
                    
                    # Force rerun to update the UI and clear the input
                    st.rerun()

if __name__ == "__main__":
    main()