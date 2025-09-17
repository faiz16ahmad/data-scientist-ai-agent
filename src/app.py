import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
import pandas as pd
from pathlib import Path

# Load environment variables
load_dotenv()

# Import our modules
from query_analyzer import analyze_query, process_clarification
from agent import get_agent
from utils import DataProcessor

# Set page config
st.set_page_config(
    page_title="Data Scientist AI Agent",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("🤖 Data Scientist AI Agent")
    st.write("Upload a CSV or Excel file and ask questions about your data in natural language.")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'state' not in st.session_state:
        st.session_state.state = 'IDLE'  # States: 'IDLE', 'AWAITING_CLARIFICATION', 'PROCESSING'
    if 'pending_query' not in st.session_state:
        st.session_state.pending_query = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("type") == "image":
                st.image(message["content"], caption="Generated Visualization")
            elif message.get("type") == "plotly_chart" and message.get("figure"):
                st.plotly_chart(message["figure"], use_container_width=True)
            elif message.get("type") == "chart" and message.get("figure"):
                st.pyplot(message["figure"])
            else:
                st.write(message["content"])
    
    # Handle different states
    if st.session_state.state == 'AWAITING_CLARIFICATION':
        show_clarification_ui()
    
    # File uploader
    if st.session_state.df is None:
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
                    "content": f"File uploaded successfully! Your dataset has {st.session_state.df.shape[0]} rows and {st.session_state.df.shape[1]} columns. You can now ask questions about your data."
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
        # Chat input
        if prompt := st.chat_input("Ask a question about your data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.pending_query = prompt
            st.session_state.state = 'PROCESSING'
            st.rerun()
    
    # Process user input
    if st.session_state.state == 'PROCESSING' and st.session_state.pending_query:
        asyncio.run(process_user_query())

def show_clarification_ui():
    """Show the clarification interface when a query is ambiguous."""
    if st.session_state.analysis_result:
        analysis = st.session_state.analysis_result
        
        st.info("🤔 I need some clarification to better help you.")
        st.write(analysis.clarification_question)
        
        if analysis.suggested_options:
            st.write("**Suggested options:**")
            cols = st.columns(len(analysis.suggested_options))
            
            for i, option in enumerate(analysis.suggested_options):
                with cols[i]:
                    if st.button(option, key=f"option_{i}"):
                        asyncio.run(handle_clarification(option))

async def handle_clarification(clarification: str):
    """Handle user's clarification response."""
    try:
        # Process the clarification
        response = await process_clarification(
            st.session_state.pending_query,
            clarification
        )
        
        # Create a synthesized query
        synthesized_query = f"{st.session_state.pending_query} - {clarification}"
        
        # Process with the main agent
        agent = get_agent(st.session_state.df)
        result = await agent.process_query(synthesized_query)
        
        # Display results
        if result["success"]:
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["response"]
            })
            
            # Display chart if generated
            if result["chart_path"] and os.path.exists(result["chart_path"]):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["chart_path"],
                    "type": "image"
                })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I encountered an error: {result['error']}"
            })
        
        # Reset state
        st.session_state.state = 'IDLE'
        st.session_state.pending_query = None
        st.session_state.analysis_result = None
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing clarification: {str(e)}")
        st.session_state.state = 'IDLE'

async def process_user_query():
    """Process the user's query through the agent system."""
    query = st.session_state.pending_query
    
    # Add conversation context for confirmation responses
    if len(st.session_state.messages) >= 2:
        # Get last few messages for better context
        recent_messages = st.session_state.messages[-4:]  # Last 4 messages for context
        context_parts = []
        
        for msg in recent_messages:
            if msg["role"] == "assistant":
                context_parts.append(f"Assistant: {msg['content']}")
            elif msg["role"] == "user":
                context_parts.append(f"User: {msg['content']}")
        
        # If user gives short responses, add conversation context
        short_responses = ["yes", "no", "ok", "sure", "proceed", "go ahead", "3d", "2d", "scatter", "line"]
        if any(word.lower() == query.lower().strip() for word in short_responses) and context_parts:
            context = "\n".join(context_parts)
            query = f"Conversation context:\n{context}\n\nCurrent user response: {query}\n\nPlease continue based on the conversation context above."
    
    with st.spinner("Processing your request..."):
        try:
            # Skip query analysis for now and go directly to the agent
            # This bypasses the clarification system temporarily
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
