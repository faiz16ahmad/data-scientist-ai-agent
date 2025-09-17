"""
Streamlit Test Application
Main interface for running and analyzing AI agent tests
"""

import streamlit as st
import pandas as pd
import asyncio
import json
import os
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from testing.test_runner import TestRunner
from testing.results_analyzer import TestResultsAnalyzer
from testing.test_questions import TestQuestionBank

def run_async(coro):
    """Helper function to run async code in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def main():
    st.set_page_config(
        page_title="AI Agent Testing Suite",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 AI Agent Testing Suite")
    st.markdown("Comprehensive testing and evaluation system for your data scientist AI agent")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Test Setup & Run", "Results Analysis", "Question Bank", "Help"]
    )
    
    if page == "Test Setup & Run":
        show_test_setup_page()
    elif page == "Results Analysis":
        show_results_analysis_page()
    elif page == "Question Bank":
        show_question_bank_page()
    elif page == "Help":
        show_help_page()

def show_test_setup_page():
    """Show the test setup and execution page."""
    st.header("🚀 Test Setup & Execution")
    
    # Data upload section
    st.subheader("1. Upload Your Dataset")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload the dataset you want to test the AI agent with"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Dataset loaded successfully! Shape: {df.shape}")
            
            # Show data preview
            with st.expander("Data Preview"):
                st.dataframe(df.head())
                st.write("**Column Information:**")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null Count': df.count(),
                    'Null Count': df.isnull().sum()
                })
                st.dataframe(col_info)
            
            # Test configuration
            st.subheader("2. Configure Test Run")
            
            col1, col2 = st.columns(2)
            
            with col1:
                test_type = st.selectbox(
                    "Test Type",
                    ["Quick Test (10 questions)", "Full Test (50 questions)", "Custom Selection"]
                )
                
                if test_type == "Custom Selection":
                    question_bank = TestQuestionBank()
                    categories = list(set(q["category"] for q in question_bank.get_all_questions()))
                    selected_categories = st.multiselect("Select Categories", categories)
                    
                    difficulties = list(set(q["difficulty"] for q in question_bank.get_all_questions()))
                    selected_difficulties = st.multiselect("Select Difficulties", difficulties)
            
            with col2:
                rate_limit = st.slider(
                    "API Rate Limit (requests/min)",
                    min_value=5,
                    max_value=12,
                    value=8,
                    help="Conservative rate limiting for Google API (free tier: 15/min)"
                )
                
                save_results = st.checkbox("Save Results Automatically", value=True)
            
            # Run tests
            if st.button("🚀 Start Test Run", type="primary"):
                run_tests(df, test_type, rate_limit, save_results, 
                         selected_categories if test_type == "Custom Selection" else None,
                         selected_difficulties if test_type == "Custom Selection" else None)
        
        except Exception as e:
            st.error(f"Error loading dataset: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin testing")

def run_tests(df, test_type, rate_limit, save_results, selected_categories=None, selected_difficulties=None):
    """Run the actual tests."""
    
    with st.spinner("Initializing test runner..."):
        runner = TestRunner(df, rate_limit_requests=rate_limit)
    
    # Determine which tests to run
    if test_type == "Quick Test (10 questions)":
        with st.spinner("Running quick test (10 questions)..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            async def run_with_progress():
                results = []
                questions = runner.question_bank.get_all_questions()[:10]
                
                for i, question in enumerate(questions):
                    status_text.text(f"Running Question {i+1}/10: {question['question'][:50]}...")
                    result = await runner.run_single_test(question)
                    results.append(result)
                    progress_bar.progress((i + 1) / 10)
                
                return results
            
            results = run_async(run_with_progress())
            runner.results = results
    
    elif test_type == "Full Test (50 questions)":
        st.warning("⚠️ Full test will take 5-8 minutes due to API rate limits")
        with st.spinner("Running full test suite (50 questions)..."):
            results = run_async(runner.run_all_tests())
    
    else:  # Custom selection
        question_bank = TestQuestionBank()
        questions = question_bank.get_all_questions()
        
        # Filter questions
        if selected_categories:
            questions = [q for q in questions if q["category"] in selected_categories]
        if selected_difficulties:
            questions = [q for q in questions if q["difficulty"] in selected_difficulties]
        
        with st.spinner(f"Running custom test ({len(questions)} questions)..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            async def run_custom_with_progress():
                results = []
                for i, question in enumerate(questions):
                    status_text.text(f"Running Question {i+1}/{len(questions)}: {question['question'][:50]}...")
                    result = await runner.run_single_test(question)
                    results.append(result)
                    progress_bar.progress((i + 1) / len(questions))
                return results
            
            results = run_async(run_custom_with_progress())
            runner.results = results
    
    # Show results
    show_test_results(runner, save_results)

def show_test_results(runner, save_results):
    """Display test results."""
    st.success("Tests completed!")
    
    # Get summary stats
    stats = runner.get_summary_stats()
    
    # Display summary metrics
    st.subheader("📊 Test Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tests", stats['total_tests'])
    
    with col2:
        st.metric("Pass Rate", f"{stats['pass_rate']:.1f}%")
    
    with col3:
        st.metric("Avg Score", f"{stats['average_score']:.1f}%")
    
    with col4:
        st.metric("Avg Time", f"{stats['average_execution_time']:.1f}s")
    
    # Category breakdown
    if stats['category_breakdown']:
        st.subheader("📈 Performance by Category")
        category_data = []
        for cat, data in stats['category_breakdown'].items():
            category_data.append({
                'Category': cat,
                'Total Tests': data['total'],
                'Passed': data['passed'],
                'Pass Rate': f"{data['pass_rate']:.1f}%",
                'Avg Score': f"{data['avg_score']:.1f}%"
            })
        
        st.dataframe(pd.DataFrame(category_data), use_container_width=True)
    
    # Save results if requested
    if save_results:
        filename = runner.save_results()
        st.success(f"Results saved to {filename}")
        
        # Provide download link
        with open(filename, 'r') as f:
            st.download_button(
                label="📥 Download Results JSON",
                data=f.read(),
                file_name=filename,
                mime="application/json"
            )
    
    # Store results in session state for analysis
    st.session_state['test_results'] = runner.results

def show_results_analysis_page():
    """Show the results analysis page."""
    st.header("📊 Results Analysis")
    
    # Check if we have results in session state
    if 'test_results' in st.session_state:
        st.success("Using results from current session")
        analyzer = TestResultsAnalyzer(results_data=st.session_state['test_results'])
        analyzer.create_overview_dashboard()
    else:
        # File upload for external results
        st.subheader("Upload Results File")
        uploaded_file = st.file_uploader(
            "Choose a test results JSON file",
            type=['json'],
            help="Upload a JSON file generated by the test runner"
        )
        
        if uploaded_file is not None:
            try:
                results_data = json.load(uploaded_file)
                analyzer = TestResultsAnalyzer(results_data=results_data)
                analyzer.create_overview_dashboard()
            except Exception as e:
                st.error(f"Error loading results file: {str(e)}")
        else:
            st.info("Please upload a test results JSON file or run tests first.")

def show_question_bank_page():
    """Show the question bank management page."""
    st.header("❓ Question Bank")
    
    question_bank = TestQuestionBank()
    questions = question_bank.get_all_questions()
    
    st.write(f"Total Questions: {len(questions)}")
    
    # Category breakdown
    categories = {}
    difficulties = {}
    
    for q in questions:
        categories[q["category"]] = categories.get(q["category"], 0) + 1
        difficulties[q["difficulty"]] = difficulties.get(q["difficulty"], 0) + 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Questions by Category")
        for cat, count in categories.items():
            st.write(f"- **{cat}**: {count} questions")
    
    with col2:
        st.subheader("Questions by Difficulty")
        for diff, count in difficulties.items():
            st.write(f"- **{diff}**: {count} questions")
    
    # Question browser
    st.subheader("Browse Questions")
    
    category_filter = st.selectbox(
        "Filter by Category",
        ["All"] + list(categories.keys())
    )
    
    difficulty_filter = st.selectbox(
        "Filter by Difficulty",
        ["All"] + list(difficulties.keys())
    )
    
    # Filter questions
    filtered_questions = questions
    if category_filter != "All":
        filtered_questions = [q for q in filtered_questions if q["category"] == category_filter]
    if difficulty_filter != "All":
        filtered_questions = [q for q in filtered_questions if q["difficulty"] == difficulty_filter]
    
    # Display questions
    for q in filtered_questions:
        with st.expander(f"Q{q['id']}: {q['question'][:60]}..."):
            st.write(f"**Full Question:** {q['question']}")
            st.write(f"**Category:** {q['category']}")
            st.write(f"**Difficulty:** {q['difficulty']}")
            st.write(f"**Expected Type:** {q['expected_type']}")

def show_help_page():
    """Show the help and documentation page."""
    st.header("📚 Help & Documentation")
    
    st.markdown("""
    ## Overview
    
    This testing suite allows you to comprehensively evaluate your AI data scientist agent with 50 carefully crafted questions across different categories and difficulty levels.
    
    ## Test Categories
    
    1. **Data Understanding** (10 questions)
       - Basic data exploration and information retrieval
       - Column analysis, data types, missing values
    
    2. **Basic Visualization** (10 questions)
       - Standard charts: bar, pie, scatter, line, histogram
       - Basic plotting functionality
    
    3. **Advanced Analysis** (10 questions)
       - Statistical analysis, correlations, trends
       - Business insights and data interpretation
    
    4. **Complex Visualization** (10 questions)
       - Advanced charts: sunburst, 3D plots, treemaps
       - Multi-panel dashboards and interactive visualizations
    
    5. **Statistical Analysis** (10 questions)
       - Machine learning models, clustering, predictions
       - Advanced statistical tests and methods
    
    ## Difficulty Levels
    
    - **Easy**: Basic operations, simple queries
    - **Medium**: Moderate complexity, some analysis required
    - **Hard**: Complex analysis, advanced techniques
    
    ## Evaluation Criteria
    
    Each test is evaluated on 4 criteria (25 points each):
    
    1. **Execution Success**: Did the code run without errors?
    2. **Response Quality**: Is the response comprehensive and meaningful?
    3. **Expected Output**: Does the output match the expected type?
    4. **Format Compliance**: Does it follow the agent's format requirements?
    
    **Pass Threshold**: 75% (3 out of 4 criteria)
    
    ## Usage Tips
    
    1. **Start with Quick Test**: Run 10 questions first to identify major issues
    2. **Use Concurrent Testing**: Set max concurrent to 3-5 for faster execution
    3. **Analyze Results**: Use the Results Analysis page to identify patterns
    4. **Custom Testing**: Focus on specific categories or difficulties
    5. **Iterative Improvement**: Use results to improve your agent's prompt
    
    ## File Formats
    
    - **Input**: CSV files for datasets
    - **Output**: JSON files with detailed test results
    - **Analysis**: Interactive dashboards and visualizations
    
    ## Best Practices
    
    1. Test with representative datasets
    2. Run tests after any prompt changes
    3. Monitor performance trends over time
    4. Focus on fixing systematic failures first
    5. Use category analysis to identify weak areas
    """)

if __name__ == "__main__":
    main()
