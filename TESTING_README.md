# 🧪 AI Agent Testing Suite

A comprehensive testing framework for thoroughly evaluating your Data Scientist AI Agent with 50 carefully crafted questions.

## 🎯 Overview

This testing suite provides:
- **50 diverse test questions** across 5 categories and 3 difficulty levels
- **Automated test execution** with concurrent processing
- **Detailed evaluation metrics** with 4-criteria scoring system
- **Visual analytics dashboard** for results analysis
- **Export capabilities** for reporting and tracking

## 🏗️ System Architecture

```
src/testing/
├── test_questions.py      # 50 test questions bank
├── test_runner.py         # Automated test execution
├── results_analyzer.py    # Results analysis & visualization
├── test_app.py           # Streamlit interface
└── __init__.py

run_tests.py              # Quick command-line runner
TESTING_README.md         # This documentation
```

## 📊 Test Categories

| Category | Questions | Description |
|----------|-----------|-------------|
| **Data Understanding** | 10 | Basic data exploration, column analysis, data types |
| **Basic Visualization** | 10 | Standard charts: bar, pie, scatter, line, histogram |
| **Advanced Analysis** | 10 | Statistical analysis, correlations, business insights |
| **Complex Visualization** | 10 | Advanced charts: sunburst, 3D, treemaps, dashboards |
| **Statistical Analysis** | 10 | ML models, clustering, predictions, advanced stats |

## 🎚️ Difficulty Levels

- **Easy** (17 questions): Basic operations, simple queries
- **Medium** (20 questions): Moderate complexity, some analysis required  
- **Hard** (13 questions): Complex analysis, advanced techniques

## 📏 Evaluation Criteria

Each test is scored on 4 criteria (25 points each):

1. **Execution Success** ✅ - Did the code run without errors?
2. **Response Quality** 📝 - Is the response comprehensive and meaningful?
3. **Expected Output** 🎯 - Does the output match the expected type?
4. **Format Compliance** 📋 - Does it follow the agent's format requirements?

**Pass Threshold**: 75% (3 out of 4 criteria must be met)

## 🚀 Quick Start

### Method 1: Command Line (Fastest)

```bash
# Activate your virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run quick test (10 questions)
python run_tests.py

# Follow the prompts to select test type
```

### Method 2: Streamlit Interface (Most Features)

```bash
# Launch the testing dashboard
streamlit run src/testing/test_app.py

# Upload your dataset and configure tests through the UI
```

### Method 3: Python Script (Most Control)

```python
import pandas as pd
import asyncio
from src.testing.test_runner import TestRunner

# Load your dataset
df = pd.read_csv("your_dataset.csv")

# Create and run tests
runner = TestRunner(df)

# Quick test (10 questions)
results = await runner.run_quick_test(10)

# Full test (50 questions)
results = await runner.run_all_tests(max_concurrent=3)

# Get summary statistics
stats = runner.get_summary_stats()
print(f"Pass Rate: {stats['pass_rate']:.1f}%")
```

## 📈 Results Analysis

### Automatic Metrics

- **Pass Rate**: Percentage of tests scoring ≥75%
- **Average Score**: Mean score across all tests
- **Execution Time**: Performance metrics
- **Category Breakdown**: Performance by test category
- **Difficulty Analysis**: Success rate by difficulty level
- **Error Patterns**: Common failure modes

### Visual Dashboards

- Score distribution histograms
- Category performance bar charts
- Execution time scatter plots
- Failed test analysis
- Trend comparisons over time

## 🎛️ Configuration Options

### Test Runner Options

```python
runner = TestRunner(dataframe)

# Quick test with custom question count
await runner.run_quick_test(num_questions=15)

# Full test with concurrency control
await runner.run_all_tests(max_concurrent=5)

# Custom test selection
questions = runner.question_bank.get_questions_by_category("basic_visualization")
# Run selected questions...
```

### Custom Question Filtering

```python
# Filter by category
questions = question_bank.get_questions_by_category("advanced_analysis")

# Filter by difficulty
hard_questions = question_bank.get_questions_by_difficulty("hard")

# Custom criteria
custom_questions = [q for q in questions if q["expected_type"] == "visualization"]
```

## 📊 Sample Results Output

```json
{
  "total_tests": 50,
  "passed_tests": 42,
  "pass_rate": 84.0,
  "average_score": 87.3,
  "average_execution_time": 12.5,
  "category_breakdown": {
    "data_understanding": {"pass_rate": 95.0, "avg_score": 92.1},
    "basic_visualization": {"pass_rate": 85.0, "avg_score": 88.5},
    "advanced_analysis": {"pass_rate": 80.0, "avg_score": 85.2},
    "complex_visualization": {"pass_rate": 75.0, "avg_score": 82.1},
    "statistical_analysis": {"pass_rate": 65.0, "avg_score": 78.8}
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root directory
   # Check that all dependencies are installed
   pip install -r requirements.txt
   ```

2. **Dataset Issues**
   ```python
   # Ensure your CSV has the expected columns
   # Check for data type compatibility
   print(df.info())
   ```

3. **Memory Issues with Large Datasets**
   ```python
   # Reduce concurrent tests
   await runner.run_all_tests(max_concurrent=1)
   
   # Or sample your dataset
   df_sample = df.sample(n=1000)
   ```

4. **API Rate Limits**
   ```python
   # Add delays between tests
   import time
   time.sleep(1)  # Add to test runner if needed
   ```

## 🔧 Customization

### Adding New Test Questions

```python
# In test_questions.py, add to the questions list:
{
    "id": 51,
    "question": "Your custom question here",
    "category": "custom_category",
    "expected_type": "visualization",  # or "analysis", "calculation", etc.
    "difficulty": "medium"
}
```

### Custom Evaluation Criteria

```python
# In test_runner.py, modify _evaluate_response method
def _evaluate_response(self, question_data, result):
    # Add your custom evaluation logic
    criteria = {
        "execution_success": self._check_execution(result),
        "custom_criterion": self._check_custom(result),
        # ... more criteria
    }
```

### Export Formats

```python
# Save results in different formats
runner.save_results("results.json")          # JSON (default)
pd.DataFrame(results).to_csv("results.csv")  # CSV
pd.DataFrame(results).to_excel("results.xlsx")  # Excel
```

## 📋 Best Practices

1. **Start Small**: Begin with quick tests before running the full suite
2. **Monitor Progress**: Use the Streamlit interface for real-time monitoring
3. **Version Control**: Save results with timestamps for comparison
4. **Iterative Improvement**: Use results to refine your agent's prompt
5. **Category Focus**: Identify and fix category-specific issues first
6. **Performance Optimization**: Monitor execution times and optimize accordingly

## 🎯 Success Targets

| Metric | Good | Excellent |
|--------|------|-----------|
| Overall Pass Rate | >75% | >90% |
| Data Understanding | >90% | >95% |
| Basic Visualization | >80% | >90% |
| Advanced Analysis | >70% | >85% |
| Complex Visualization | >60% | >80% |
| Statistical Analysis | >50% | >70% |
| Average Execution Time | <15s | <10s |

## 📞 Support

For issues or questions about the testing suite:

1. Check the troubleshooting section above
2. Review the test logs for specific error messages
3. Verify your dataset format and compatibility
4. Ensure all dependencies are properly installed

## 🔄 Version History

- **v1.0**: Initial release with 50 test questions
- Comprehensive evaluation framework
- Streamlit dashboard interface
- Automated result analysis

---

**Happy Testing!** 🧪🤖📊
