#!/usr/bin/env python3
"""
Simple API Key Setup Helper
Helps you update your .env file with your real API keys
"""

import os
import getpass
from pathlib import Path

def update_env_file():
    """Interactive API key setup"""
    print("🔑 API KEY SETUP HELPER")
    print("=" * 40)
    print("This will help you update your .env file with your real API keys.")
    print("Press ENTER to skip any key you don't have yet.")
    print()
    
    # Read current .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Essential keys for zero-cost setup
    keys_to_update = {
        'OPENAI_API_KEY': '🤖 OpenAI (ChatGPT) API Key',
        'XAI_API_KEY': '🚀 Grok (xAI) API Key',
        'X_CONSUMER_KEY': '🐦 Twitter Consumer Key',
        'X_CONSUMER_SECRET': '🐦 Twitter Consumer Secret',
        'X_ACCESS_TOKEN': '🐦 Twitter Access Token',
        'X_ACCESS_TOKEN_SECRET': '🐦 Twitter Access Token Secret',
        'X_BEARER_TOKEN': '🐦 Twitter Bearer Token (for reading tweets)',
    }
    
    print("📝 UPDATING ESSENTIAL KEYS:")
    print("(The ones you need for the zero-cost bot)")
    print()
    
    updates_made = False
    
    for key, description in keys_to_update.items():
        current_value = "not set"
        if f"{key}=" in content:
            # Extract current value
            lines = content.split('\n')
            for line in lines:
                if line.startswith(f"{key}="):
                    current_value = line.split('=', 1)[1]
                    if current_value.startswith(('your_', 'sk-', 'Bearer ')):
                        current_value = "placeholder"
                    else:
                        current_value = f"set ({current_value[:10]}...)"
                    break
        
        print(f"\n{description}")
        print(f"Current: {current_value}")
        
        if 'Twitter' in description:
            print("💡 Get this from: https://developer.twitter.com/en/portal/dashboard")
        elif 'OpenAI' in description:
            print("💡 Get this from: https://platform.openai.com/api-keys")
        elif 'Grok' in description:
            print("💡 Get this from: https://console.x.ai/")
        
        new_value = input("Enter new value (or press ENTER to skip): ").strip()
        
        if new_value:
            # Update the content
            lines = content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={new_value}"
                    updated = True
                    break
            
            if updated:
                content = '\n'.join(lines)
                updates_made = True
                print(f"✅ Updated {key}")
            else:
                # Add new key if not found
                content += f"\n{key}={new_value}"
                updates_made = True
                print(f"✅ Added {key}")
    
    if updates_made:
        # Save updated content
        with open(env_file, 'w') as f:
            f.write(content)
        print("\n🎉 API keys updated successfully!")
        print("\n🔒 Security Note: Never share your .env file or commit it to git!")
    else:
        print("\n📝 No changes made.")
    
    print("\n🚀 Ready to launch your Mac app!")

def show_twitter_setup_guide():
    """Show how to get Twitter API keys"""
    print("\n" + "="*60)
    print("🐦 HOW TO GET TWITTER API KEYS")
    print("="*60)
    print("""
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Create a new App (or use existing)
3. Go to "Keys and Tokens" tab
4. Generate/Copy these keys:
   
   📋 COPY THESE:
   • Consumer Key (API Key) → X_CONSUMER_KEY
   • Consumer Secret (API Secret) → X_CONSUMER_SECRET
   • Access Token → X_ACCESS_TOKEN  
   • Access Token Secret → X_ACCESS_TOKEN_SECRET
   • Bearer Token → X_BEARER_TOKEN

5. Make sure your app has "Read and Write" permissions
6. Enable OAuth 1.0a and OAuth 2.0

💡 TIP: You can run the bot in simulation mode first to test
without real Twitter posting!
""")

if __name__ == "__main__":
    print("🆓 ZERO-COST TWITTER BOT - API SETUP")
    print()
    
    choice = input("What would you like to do?\n1. Update API keys\n2. Show Twitter setup guide\n3. Skip for now\nChoice (1-3): ").strip()
    
    if choice == "1":
        update_env_file()
    elif choice == "2":
        show_twitter_setup_guide()
        input("\nPress ENTER when you have your keys ready...")
        update_env_file()
    else:
        print("\n⏭️  Skipping API setup for now.")
        print("💡 You can run: python3 setup_keys.py anytime to set up keys")