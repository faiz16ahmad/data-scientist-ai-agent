"""
Test Runner for AI Agent Evaluation
Executes test questions and evaluates responses
"""

import asyncio
import time
import json
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import sys
import os
from collections import deque

# Add parent directory to path to import agent
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agent import get_agent
from testing.test_questions import TestQuestionBank

class RateLimiter:
    """Rate limiter for API calls to respect Google's 15 requests/minute limit."""
    
    def __init__(self, max_requests: int = 12, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed (set to 12 to be safe with 15 limit)
            time_window: Time window in seconds (60 for per minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    async def wait_if_needed(self):
        """Wait if we're approaching the rate limit."""
        now = time.time()
        
        # Remove old requests outside the time window
        while self.requests and self.requests[0] <= now - self.time_window:
            self.requests.popleft()
        
        # If we're at the limit, wait
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0]) + 1
            if sleep_time > 0:
                print(f"⏳ Rate limit approached. Waiting {sleep_time:.1f} seconds...")
                await asyncio.sleep(sleep_time)
                # Clean up old requests after waiting
                now = time.time()
                while self.requests and self.requests[0] <= now - self.time_window:
                    self.requests.popleft()
        
        # Record this request
        self.requests.append(now)

class TestRunner:
    """Runs automated tests on the AI agent and evaluates results."""
    
    def __init__(self, dataframe: pd.DataFrame, rate_limit_requests: int = 10):
        self.df = dataframe
        self.agent = get_agent(dataframe)
        self.question_bank = TestQuestionBank()
        self.results = []
        self.rate_limiter = RateLimiter(max_requests=rate_limit_requests)
    
    async def run_single_test(self, question_data: Dict) -> Dict:
        """Run a single test question and evaluate the result."""
        # Apply rate limiting before making API call
        await self.rate_limiter.wait_if_needed()
        
        start_time = time.time()
        
        try:
            # Run the question through the agent
            result = await self.agent.process_query(question_data["question"])
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Evaluate the result
            evaluation = self._evaluate_response(question_data, result)
            
            test_result = {
                "question_id": question_data["id"],
                "question": question_data["question"],
                "category": question_data["category"],
                "difficulty": question_data["difficulty"],
                "expected_type": question_data["expected_type"],
                "execution_time": execution_time,
                "success": result["success"],
                "response": result["response"],
                "error": result.get("error", None),
                "has_visualization": result.get("chart_figure") is not None,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            }
            
            return test_result
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "question_id": question_data["id"],
                "question": question_data["question"],
                "category": question_data["category"],
                "difficulty": question_data["difficulty"],
                "expected_type": question_data["expected_type"],
                "execution_time": execution_time,
                "success": False,
                "response": f"Test execution failed: {str(e)}",
                "error": str(e),
                "has_visualization": False,
                "evaluation": {
                    "score": 0,
                    "criteria_met": 0,
                    "total_criteria": 4,
                    "details": {
                        "execution_success": False,
                        "response_quality": False,
                        "expected_output": False,
                        "format_compliance": False
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def _evaluate_response(self, question_data: Dict, result: Dict) -> Dict:
        """Evaluate the quality and correctness of the agent's response."""
        criteria = {
            "execution_success": False,
            "response_quality": False,
            "expected_output": False,
            "format_compliance": False
        }
        
        # 1. Execution Success (25 points)
        if result["success"]:
            criteria["execution_success"] = True
        
        # 2. Response Quality (25 points)
        response = result.get("response", "")
        if len(response) > 50 and not "error" in response.lower():
            criteria["response_quality"] = True
        
        # 3. Expected Output Type (25 points)
        expected_type = question_data["expected_type"]
        if expected_type == "visualization":
            if result.get("chart_figure") is not None or "fig" in response:
                criteria["expected_output"] = True
        elif expected_type == "calculation":
            if any(word in response.lower() for word in ["average", "total", "sum", "count", "mean", "median"]):
                criteria["expected_output"] = True
        elif expected_type == "analysis":
            if len(response) > 100 and any(word in response.lower() for word in ["analysis", "insight", "pattern", "trend", "correlation"]):
                criteria["expected_output"] = True
        elif expected_type == "info":
            if any(word in response.lower() for word in ["column", "row", "type", "data", "information"]):
                criteria["expected_output"] = True
        elif expected_type == "data":
            if "head" in response.lower() or "first" in response.lower() or "rows" in response.lower():
                criteria["expected_output"] = True
        elif expected_type == "model":
            if any(word in response.lower() for word in ["model", "predict", "accuracy", "feature", "cluster"]):
                criteria["expected_output"] = True
        
        # 4. Format Compliance (25 points)
        if "Final Answer:" in response or result.get("chart_figure") is not None:
            criteria["format_compliance"] = True
        
        # Calculate score
        criteria_met = sum(criteria.values())
        score = (criteria_met / len(criteria)) * 100
        
        return {
            "score": score,
            "criteria_met": criteria_met,
            "total_criteria": len(criteria),
            "details": criteria
        }
    
    async def run_all_tests(self, batch_size: int = 1) -> List[Dict]:
        """Run all test questions with rate limiting (sequential processing recommended)."""
        questions = self.question_bank.get_all_questions()
        
        print(f"Starting test run with {len(questions)} questions...")
        print(f"Rate limited to {self.rate_limiter.max_requests} requests per minute")
        print("⚠️  Using sequential processing to respect API rate limits")
        
        self.results = []
        
        for i, question_data in enumerate(questions, 1):
            print(f"Running Question {question_data['id']} ({i}/{len(questions)}): {question_data['question'][:60]}...")
            
            result = await self.run_single_test(question_data)
            self.results.append(result)
            
            status = "✅ PASS" if result["evaluation"]["score"] >= 75 else "❌ FAIL"
            print(f"  {status} (Score: {result['evaluation']['score']:.1f}%, Time: {result['execution_time']:.1f}s)")
            
            # Add a small delay between tests for additional safety
            if i < len(questions):  # Don't sleep after the last test
                await asyncio.sleep(1)
        
        return self.results
    
    async def run_quick_test(self, num_questions: int = 10) -> List[Dict]:
        """Run a quick test with a subset of questions."""
        questions = self.question_bank.get_all_questions()[:num_questions]
        
        print(f"Running quick test with {len(questions)} questions...")
        print(f"Rate limited to {self.rate_limiter.max_requests} requests per minute")
        
        results = []
        for i, question_data in enumerate(questions, 1):
            print(f"Running Question {question_data['id']} ({i}/{len(questions)}): {question_data['question'][:60]}...")
            
            result = await self.run_single_test(question_data)
            results.append(result)
            
            status = "✅ PASS" if result["evaluation"]["score"] >= 75 else "❌ FAIL"
            print(f"  {status} (Score: {result['evaluation']['score']:.1f}%, Time: {result['execution_time']:.1f}s)")
            
            # Add a small delay between tests for additional safety
            if i < len(questions):  # Don't sleep after the last test
                await asyncio.sleep(1)
        
        self.results = results
        return results
    
    def save_results(self, filename: str = None):
        """Save test results to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to {filename}")
        return filename
    
    def get_summary_stats(self) -> Dict:
        """Calculate summary statistics from test results."""
        if not self.results:
            return {}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["evaluation"]["score"] >= 75)
        
        avg_score = sum(r["evaluation"]["score"] for r in self.results) / total_tests
        avg_time = sum(r["execution_time"] for r in self.results) / total_tests
        
        category_stats = {}
        difficulty_stats = {}
        
        for result in self.results:
            # Category stats
            cat = result["category"]
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "avg_score": 0}
            category_stats[cat]["total"] += 1
            if result["evaluation"]["score"] >= 75:
                category_stats[cat]["passed"] += 1
            category_stats[cat]["avg_score"] += result["evaluation"]["score"]
        
        # Calculate averages for categories
        for cat in category_stats:
            category_stats[cat]["avg_score"] /= category_stats[cat]["total"]
            category_stats[cat]["pass_rate"] = (category_stats[cat]["passed"] / category_stats[cat]["total"]) * 100
        
        # Difficulty stats
        for result in self.results:
            diff = result["difficulty"]
            if diff not in difficulty_stats:
                difficulty_stats[diff] = {"total": 0, "passed": 0, "avg_score": 0}
            difficulty_stats[diff]["total"] += 1
            if result["evaluation"]["score"] >= 75:
                difficulty_stats[diff]["passed"] += 1
            difficulty_stats[diff]["avg_score"] += result["evaluation"]["score"]
        
        # Calculate averages for difficulty
        for diff in difficulty_stats:
            difficulty_stats[diff]["avg_score"] /= difficulty_stats[diff]["total"]
            difficulty_stats[diff]["pass_rate"] = (difficulty_stats[diff]["passed"] / difficulty_stats[diff]["total"]) * 100
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests) * 100,
            "average_score": avg_score,
            "average_execution_time": avg_time,
            "category_breakdown": category_stats,
            "difficulty_breakdown": difficulty_stats,
            "visualizations_created": sum(1 for r in self.results if r["has_visualization"]),
            "errors_encountered": sum(1 for r in self.results if r["error"] is not None)
        }

async def main():
    """Example usage of the test runner."""
    # Load sample data (you can replace this with your actual dataset)
    try:
        df = pd.read_csv("sample_sales.csv")
    except FileNotFoundError:
        print("Sample data file not found. Please ensure 'sample_sales.csv' exists.")
        return
    
    # Create test runner
    runner = TestRunner(df)
    
    # Run quick test (first 10 questions)
    print("Running quick test...")
    await runner.run_quick_test(10)
    
    # Get and print summary
    stats = runner.get_summary_stats()
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total Tests: {stats['total_tests']}")
    print(f"Passed: {stats['passed_tests']} ({stats['pass_rate']:.1f}%)")
    print(f"Failed: {stats['failed_tests']}")
    print(f"Average Score: {stats['average_score']:.1f}%")
    print(f"Average Time: {stats['average_execution_time']:.1f}s")
    print(f"Visualizations Created: {stats['visualizations_created']}")
    
    # Save results
    runner.save_results()

if __name__ == "__main__":
    asyncio.run(main())
