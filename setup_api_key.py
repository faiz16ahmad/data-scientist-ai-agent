"""
Simple script to help set up the Google API key
"""

import os

def setup_api_key():
    print("🔧 Google API Key Setup")
    print("=" * 30)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY' in content and 'your_api_key_here' not in content:
                print("✅ API key appears to be set in .env file")
                return
    
    print("\n📝 Steps to set up your Google API key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Click 'Create API Key'")
    print("3. Copy your API key")
    print("\n4. Choose how to set it up:")
    print("   Option A: Create .env file (Recommended)")
    print("   Option B: Set environment variable")
    
    choice = input("\nEnter 'A' for .env file or 'B' for environment variable: ").strip().upper()
    
    if choice == 'A':
        api_key = input("\nPaste your Google API key here: ").strip()
        if api_key and api_key != 'your_api_key_here':
            try:
                with open('.env', 'w') as f:
                    f.write(f"# Google Generative AI API Key\n")
                    f.write(f"GOOGLE_API_KEY={api_key}\n")
                print("\n✅ .env file created successfully!")
                print("You can now run: python run_tests.py")
            except Exception as e:
                print(f"\n❌ Error creating .env file: {e}")
        else:
            print("\n❌ Invalid API key provided")
    
    elif choice == 'B':
        api_key = input("\nPaste your Google API key here: ").strip()
        if api_key:
            print(f"\n📋 Copy and run this command in your terminal:")
            print(f"   Windows PowerShell: $env:GOOGLE_API_KEY=\"{api_key}\"")
            print(f"   Windows CMD: set GOOGLE_API_KEY={api_key}")
            print(f"   Linux/Mac: export GOOGLE_API_KEY=\"{api_key}\"")
        else:
            print("\n❌ Invalid API key provided")
    
    else:
        print("\n❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    setup_api_key()
