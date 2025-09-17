"""
Results Analyzer for Test Results
Creates visualizations and detailed analysis of test performance
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List
from datetime import datetime

class TestResultsAnalyzer:
    """Analyzes and visualizes test results."""
    
    def __init__(self, results_file: str = None, results_data: List[Dict] = None):
        if results_file:
            with open(results_file, 'r') as f:
                self.results = json.load(f)
        elif results_data:
            self.results = results_data
        else:
            raise ValueError("Either results_file or results_data must be provided")
        
        self.df = pd.DataFrame(self.results)
    
    def create_overview_dashboard(self):
        """Create a comprehensive overview dashboard."""
        if len(self.results) == 0:
            st.error("No test results to analyze")
            return
        
        # Calculate summary stats
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["evaluation"]["score"] >= 75)
        avg_score = sum(r["evaluation"]["score"] for r in self.results) / total_tests
        avg_time = sum(r["execution_time"] for r in self.results) / total_tests
        
        # Header metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Tests",
                value=total_tests
            )
        
        with col2:
            st.metric(
                label="Pass Rate",
                value=f"{(passed_tests/total_tests)*100:.1f}%",
                delta=f"{passed_tests}/{total_tests}"
            )
        
        with col3:
            st.metric(
                label="Average Score",
                value=f"{avg_score:.1f}%"
            )
        
        with col4:
            st.metric(
                label="Avg Execution Time",
                value=f"{avg_time:.1f}s"
            )
        
        st.markdown("---")
        
        # Create visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            self._create_category_performance_chart()
        
        with col2:
            self._create_difficulty_performance_chart()
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._create_score_distribution_chart()
        
        with col2:
            self._create_execution_time_chart()
        
        # Detailed results table
        st.markdown("## Detailed Results")
        self._create_detailed_results_table()
        
        # Failed tests analysis
        st.markdown("## Failed Tests Analysis")
        self._analyze_failed_tests()
    
    def _create_category_performance_chart(self):
        """Create category performance bar chart."""
        category_stats = self.df.groupby('category').agg({
            'evaluation': lambda x: [r['score'] for r in x],
            'question_id': 'count'
        }).reset_index()
        
        category_stats['avg_score'] = category_stats['evaluation'].apply(lambda x: sum(x) / len(x))
        category_stats['pass_rate'] = category_stats['evaluation'].apply(
            lambda x: sum(1 for score in x if score >= 75) / len(x) * 100
        )
        
        fig = px.bar(
            category_stats,
            x='category',
            y='avg_score',
            title='Average Score by Category',
            labels={'avg_score': 'Average Score (%)', 'category': 'Category'},
            text='avg_score'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_difficulty_performance_chart(self):
        """Create difficulty performance chart."""
        difficulty_stats = self.df.groupby('difficulty').agg({
            'evaluation': lambda x: [r['score'] for r in x],
            'question_id': 'count'
        }).reset_index()
        
        difficulty_stats['avg_score'] = difficulty_stats['evaluation'].apply(lambda x: sum(x) / len(x))
        
        fig = px.bar(
            difficulty_stats,
            x='difficulty',
            y='avg_score',
            title='Average Score by Difficulty',
            labels={'avg_score': 'Average Score (%)', 'difficulty': 'Difficulty'},
            color='difficulty',
            text='avg_score'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_score_distribution_chart(self):
        """Create score distribution histogram."""
        scores = [r['evaluation']['score'] for r in self.results]
        
        fig = px.histogram(
            x=scores,
            nbins=10,
            title='Score Distribution',
            labels={'x': 'Score (%)', 'y': 'Number of Tests'},
            range_x=[0, 100]
        )
        
        # Add pass/fail line
        fig.add_vline(x=75, line_dash="dash", line_color="red", 
                     annotation_text="Pass Threshold (75%)")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_execution_time_chart(self):
        """Create execution time analysis chart."""
        fig = px.scatter(
            self.df,
            x='question_id',
            y='execution_time',
            color='category',
            size=[r['evaluation']['score'] for r in self.results],
            title='Execution Time by Question',
            labels={'execution_time': 'Execution Time (s)', 'question_id': 'Question ID'},
            hover_data=['difficulty', 'question']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_detailed_results_table(self):
        """Create a detailed results table."""
        # Prepare data for table
        table_data = []
        for result in self.results:
            table_data.append({
                'ID': result['question_id'],
                'Question': result['question'][:50] + '...' if len(result['question']) > 50 else result['question'],
                'Category': result['category'],
                'Difficulty': result['difficulty'],
                'Score': f"{result['evaluation']['score']:.1f}%",
                'Time (s)': f"{result['execution_time']:.1f}",
                'Status': '✅ PASS' if result['evaluation']['score'] >= 75 else '❌ FAIL',
                'Has Viz': '📊' if result['has_visualization'] else '📝',
                'Error': '⚠️' if result['error'] else '✅'
            })
        
        df_table = pd.DataFrame(table_data)
        
        # Color-code the dataframe
        def highlight_status(val):
            if val == '✅ PASS':
                return 'background-color: #d4edda'
            elif val == '❌ FAIL':
                return 'background-color: #f8d7da'
            return ''
        
        styled_df = df_table.style.applymap(highlight_status, subset=['Status'])
        
        st.dataframe(styled_df, use_container_width=True)
    
    def _analyze_failed_tests(self):
        """Analyze failed tests to identify patterns."""
        failed_tests = [r for r in self.results if r['evaluation']['score'] < 75]
        
        if not failed_tests:
            st.success("🎉 All tests passed!")
            return
        
        st.warning(f"Found {len(failed_tests)} failed tests")
        
        # Analyze failure patterns
        failure_by_category = {}
        failure_by_difficulty = {}
        common_errors = {}
        
        for test in failed_tests:
            # Category failures
            cat = test['category']
            failure_by_category[cat] = failure_by_category.get(cat, 0) + 1
            
            # Difficulty failures
            diff = test['difficulty']
            failure_by_difficulty[diff] = failure_by_difficulty.get(diff, 0) + 1
            
            # Common errors
            if test['error']:
                error_type = test['error'].split(':')[0] if ':' in test['error'] else test['error'][:50]
                common_errors[error_type] = common_errors.get(error_type, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Failures by Category")
            if failure_by_category:
                fig = px.bar(
                    x=list(failure_by_category.keys()),
                    y=list(failure_by_category.values()),
                    title="Failed Tests by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Failures by Difficulty")
            if failure_by_difficulty:
                fig = px.pie(
                    values=list(failure_by_difficulty.values()),
                    names=list(failure_by_difficulty.keys()),
                    title="Failed Tests by Difficulty"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Show common errors
        if common_errors:
            st.subheader("Common Error Types")
            error_df = pd.DataFrame([
                {"Error Type": k, "Count": v} 
                for k, v in sorted(common_errors.items(), key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(error_df, use_container_width=True)
        
        # Show worst performing questions
        st.subheader("Lowest Scoring Questions")
        worst_tests = sorted(failed_tests, key=lambda x: x['evaluation']['score'])[:5]
        
        for test in worst_tests:
            with st.expander(f"Question {test['question_id']}: {test['question'][:60]}... (Score: {test['evaluation']['score']:.1f}%)"):
                st.write(f"**Category:** {test['category']}")
                st.write(f"**Difficulty:** {test['difficulty']}")
                st.write(f"**Expected Type:** {test['expected_type']}")
                st.write(f"**Execution Time:** {test['execution_time']:.1f}s")
                
                if test['error']:
                    st.error(f"**Error:** {test['error']}")
                
                st.write(f"**Response:** {test['response'][:200]}...")
                
                # Show evaluation details
                details = test['evaluation']['details']
                st.write("**Evaluation Details:**")
                for criterion, passed in details.items():
                    icon = "✅" if passed else "❌"
                    st.write(f"  {icon} {criterion.replace('_', ' ').title()}")
    
    def create_comparison_report(self, baseline_results: List[Dict] = None):
        """Create a comparison report between current and baseline results."""
        if not baseline_results:
            st.info("No baseline results provided for comparison")
            return
        
        # Calculate current stats
        current_pass_rate = sum(1 for r in self.results if r['evaluation']['score'] >= 75) / len(self.results) * 100
        current_avg_score = sum(r['evaluation']['score'] for r in self.results) / len(self.results)
        
        # Calculate baseline stats
        baseline_pass_rate = sum(1 for r in baseline_results if r['evaluation']['score'] >= 75) / len(baseline_results) * 100
        baseline_avg_score = sum(r['evaluation']['score'] for r in baseline_results) / len(baseline_results)
        
        # Show comparison metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Pass Rate",
                value=f"{current_pass_rate:.1f}%",
                delta=f"{current_pass_rate - baseline_pass_rate:.1f}%"
            )
        
        with col2:
            st.metric(
                label="Average Score",
                value=f"{current_avg_score:.1f}%",
                delta=f"{current_avg_score - baseline_avg_score:.1f}%"
            )
    
    def export_report(self, filename: str = None):
        """Export a comprehensive report to HTML."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.html"
        
        # This would generate an HTML report
        # Implementation details would depend on specific requirements
        print(f"Report export functionality would save to {filename}")

def main():
    """Streamlit app for analyzing test results."""
    st.set_page_config(
        page_title="AI Agent Test Results",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🤖 AI Agent Test Results Analysis")
    
    # File uploader for results
    uploaded_file = st.file_uploader(
        "Upload Test Results JSON",
        type=['json'],
        help="Upload the JSON file generated by the test runner"
    )
    
    if uploaded_file is not None:
        try:
            results_data = json.load(uploaded_file)
            analyzer = TestResultsAnalyzer(results_data=results_data)
            analyzer.create_overview_dashboard()
        except Exception as e:
            st.error(f"Error loading results file: {str(e)}")
    else:
        st.info("Please upload a test results JSON file to begin analysis.")

if __name__ == "__main__":
    main()
