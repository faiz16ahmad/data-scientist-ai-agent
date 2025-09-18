import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
import pandas as pd
from pathlib import Path

# Load environment variables
load_dotenv()

# Import our modules
from query_analyzer import analyze_query
from agent import get_agent
from utils import DataProcessor

# Set page config
st.set_page_config(
    page_title="Data Scientist AI Agent",
    page_icon="📊",
    layout="wide"
)

def generate_suggested_questions(df):
    """Generate 5 smart visualization questions based on the dataset."""
    questions = []
    
    # Get column information
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
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

def setup_quick_analysis_buttons():
    """Setup quick analysis buttons."""
    st.sidebar.subheader("🚀 Quick Analysis")
    
    if st.sidebar.button("📊 Basic Stats", key="quick_stats"):
        current_text = st.session_state.get('chat_input', '') or ''
        st.session_state.chat_input = current_text + " show basic statistics"
        st.rerun()
    
    if st.sidebar.button("🔗 Correlation", key="quick_corr"):
        current_text = st.session_state.get('chat_input', '') or ''
        st.session_state.chat_input = current_text + " show correlation matrix"
        st.rerun()
    
    if st.sidebar.button("📈 Value Counts", key="quick_counts"):
        current_text = st.session_state.get('chat_input', '') or ''
        st.session_state.chat_input = current_text + " show value counts"
        st.rerun()
    
    if st.sidebar.button("📊 Histogram", key="quick_hist"):
        current_text = st.session_state.get('chat_input', '') or ''
        st.session_state.chat_input = current_text + " create histogram"
        st.rerun()
    
    if st.sidebar.button("📈 Scatter Plot", key="quick_scatter"):
        current_text = st.session_state.get('chat_input', '') or ''
        st.session_state.chat_input = current_text + " create scatter plot"
        st.rerun()

def setup_column_selection_ui():
    """Setup interactive column picker interface in sidebar."""
    if st.session_state.get('df') is not None:
        # Sidebar for column picker
        st.sidebar.header("📝 Column Picker")
        st.sidebar.write("Click column names to add them to your query:")
        
        # Initialize current query in session state
        if 'current_query' not in st.session_state:
            st.session_state.current_query = ""
        
        # Initialize selected columns tracking
        if 'selected_columns' not in st.session_state:
            st.session_state.selected_columns = {'numeric': [], 'categorical': [], 'datetime': []}
        
        # Column categories for better UX
        numeric_cols = st.session_state.df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = st.session_state.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = st.session_state.df.select_dtypes(include=['datetime64']).columns.tolist()
        
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
                    st.rerun()
        
        # Query builder controls
        st.sidebar.subheader("🛠️ Query Builder")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🗑️ Clear", key="clear_query", help="Clear the current query"):
                st.session_state.chat_input = ""
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
                st.rerun()
        
        # Quick Analysis Buttons (always available)
        setup_quick_analysis_buttons()

    else:
        st.sidebar.info("🔄 Processing query...")

def main():
    st.title("🤖 Data Scientist AI Agent")
    st.write("Upload a CSV or Excel file and ask questions about your data in natural language.")
    
    # Initialize session state FIRST
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'state' not in st.session_state:
        st.session_state.state = 'IDLE'  # States: 'IDLE', 'PROCESSING'
    if 'pending_query' not in st.session_state:
        st.session_state.pending_query = None
    if 'selected_features' not in st.session_state:
        st.session_state.selected_features = {}
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = {'numeric': [], 'categorical': [], 'datetime': []}
    
    # Always show sidebar info
    if st.session_state.df is not None:
        setup_column_selection_ui()
    else:
        st.sidebar.header("📁 Upload Data")
        st.sidebar.info("Upload a CSV or Excel file to start analyzing your data with AI!")
    
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message.get("type") == "image":
                st.image(message["content"], caption="Generated Visualization")
            elif message.get("type") == "plotly_chart" and message.get("figure"):
                st.plotly_chart(message["figure"], use_container_width=True, key=f"plotly_chart_{i}")
            elif message.get("type") == "chart" and message.get("figure"):
                st.pyplot(message["figure"])
            elif message.get("type") == "suggestions":
                st.write(message["content"])
                # Display clickable suggested questions
                questions = message.get("questions", [])
                for j, question in enumerate(questions):
                    if st.button(f"💡 {question}", key=f"suggestion_{i}_{j}", help="Click to use this question"):
                        st.session_state.chat_input = question
                        st.rerun()
            else:
                st.write(message["content"])
    
    
    # File uploader
    if st.session_state.get('df') is None:
        uploaded_file = st.file_uploader("Upload your data file", type=['csv', 'xlsx', 'xls'])
        if uploaded_file is not None:
            try:
                # Determine file type and read accordingly
                file_extension = uploaded_file.name.split('.')[-1].lower()
                if file_extension == 'csv':
                    st.session_state.df = pd.read_csv(uploaded_file)
                elif file_extension in ['xlsx', 'xls']:
                    st.session_state.df = pd.read_excel(uploaded_file)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"File uploaded successfully! Your dataset has {st.session_state.df.shape[0]} rows and {st.session_state.df.shape[1]} columns. Here are some suggested questions to get you started:"
                })
                
                # Generate and show suggested questions
                suggested_questions = generate_suggested_questions(st.session_state.df)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "**🎯 Suggested Questions:**",
                    "type": "suggestions",
                    "questions": suggested_questions
                })
                
                # Show data preview
                with st.expander("Data Preview"):
                    st.dataframe(st.session_state.df.head())
                    st.write("**Column Information:**")
                    col_info = pd.DataFrame({
                        'Column': st.session_state.df.columns,
                        'Type': st.session_state.df.dtypes.astype(str),
                        'Non-Null Count': st.session_state.df.count(),
                        'Null Count': st.session_state.df.isnull().sum()
                    })
                    st.dataframe(col_info)
                
                st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    else:
        # Chat input with proper value handling
        placeholder_text = "Type your question or use column picker above (e.g., 'plot', 'correlation between', 'analyze')"
        
        # Use a text input instead of chat_input for better control
        user_input = st.text_input(
            "Ask a question about your data:",
            value=st.session_state.get('chat_input', ''),
            placeholder=placeholder_text,
            key="text_input_query"
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
                    
                    # Clear chat input after sending
                    st.session_state.chat_input = ""
                    
                    st.session_state.pending_query = final_query
                    st.session_state.messages.append({"role": "user", "content": final_query})
                    st.session_state.state = 'PROCESSING'
                    st.rerun()
    
    # Process user input
    if st.session_state.state == 'PROCESSING' and st.session_state.pending_query:
        asyncio.run(process_user_query())


async def process_user_query():
    """Process the user's query through the simplified workflow."""
    query = st.session_state.pending_query
    
    with st.spinner("Processing your request..."):
        try:
            # Step 1: Intent Classification
            analysis = await analyze_query(query)
            
            # Step 2: Decision Point
            if analysis.intent == "unclear":
                # Stop and give user a simple message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I'm sorry, I don't understand that request. Please try rephrasing, or use the column picker to help build your query."
                })
            else:
                # Intent is clear - proceed to main agent
                agent = get_agent(st.session_state.df)
                result = await agent.process_query(query)
                
                if result["success"]:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"]
                    })
                    
                    # Display chart if generated
                    if result.get("chart_figure"):
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "Interactive visualization generated",
                            "type": "plotly_chart",
                            "figure": result["chart_figure"]
                        })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"I encountered an error: {result['error']}"
                    })
        
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I encountered an error: {str(e)}"
            })
        
        # Reset state
        st.session_state.state = 'IDLE'
        st.session_state.pending_query = None
        st.rerun()

if __name__ == "__main__":
    main()
