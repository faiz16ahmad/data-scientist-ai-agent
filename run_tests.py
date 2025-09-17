"""
Quick Test Runner Script
Run this to quickly test your AI agent
"""

import asyncio
import pandas as pd
import os
from dotenv import load_dotenv
from src.testing.test_runner import TestRunner

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found!")
        print("\n📝 Setup Instructions:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Create a .env file in the project root")
        print("3. Add: GOOGLE_API_KEY=your_api_key_here")
        print("4. Or set environment variable: set GOOGLE_API_KEY=your_key")
        print("\nSee SETUP_GUIDE.md for detailed instructions.")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    return True

async def main():
    print("🧪 AI Agent Testing Suite")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        return
    
    # Load your dataset
    try:
        df = pd.read_csv("sample_sales.csv")
        print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    except FileNotFoundError:
        print("❌ sample_sales.csv not found. Please ensure the file exists.")
        print("💡 You can use any CSV file - just update the filename in this script.")
        return
    
    # Create test runner with rate limiting
    try:
        # Use conservative rate limiting (8 requests per minute to be safe)
        runner = TestRunner(df, rate_limit_requests=8)
        print("✅ Test runner initialized successfully with rate limiting")
    except ValueError as e:
        print(f"❌ Failed to initialize test runner: {str(e)}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return
    
    # Ask user for test type
    print("\nSelect test type:")
    print("1. Quick Test (10 questions)")
    print("2. Full Test (50 questions)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n🚀 Running Quick Test (10 questions)...")
        await runner.run_quick_test(10)
    elif choice == "2":
        print("\n🚀 Running Full Test (50 questions)...")
        print("⚠️  This will take approximately 5-8 minutes due to API rate limits")
        await runner.run_all_tests()
    else:
        print("Invalid choice. Running quick test by default.")
        await runner.run_quick_test(10)
    
    # Get and display summary
    stats = runner.get_summary_stats()
    
    print("\n" + "="*60)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"📊 Total Tests: {stats['total_tests']}")
    print(f"✅ Passed: {stats['passed_tests']} ({stats['pass_rate']:.1f}%)")
    print(f"❌ Failed: {stats['failed_tests']}")
    print(f"📈 Average Score: {stats['average_score']:.1f}%")
    print(f"⏱️  Average Time: {stats['average_execution_time']:.1f}s")
    print(f"📊 Visualizations Created: {stats['visualizations_created']}")
    print(f"⚠️  Errors Encountered: {stats['errors_encountered']}")
    
    print(f"\n📊 Performance by Category:")
    for cat, data in stats['category_breakdown'].items():
        print(f"  {cat}: {data['passed']}/{data['total']} ({data['pass_rate']:.1f}%)")
    
    print(f"\n📊 Performance by Difficulty:")
    for diff, data in stats['difficulty_breakdown'].items():
        print(f"  {diff}: {data['passed']}/{data['total']} ({data['pass_rate']:.1f}%)")
    
    # Save results
    filename = runner.save_results()
    print(f"\n💾 Results saved to: {filename}")
    
    print(f"\n🎉 Testing completed! Use 'streamlit run src/testing/test_app.py' for detailed analysis.")

if __name__ == "__main__":
    asyncio.run(main())
