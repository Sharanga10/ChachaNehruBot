#!/usr/bin/env python3
"""
Quick Launcher for Mac App with Twitter Timeline
Handles dependencies and launches the enhanced GUI
"""

import sys
import subprocess
import os
from pathlib import Path

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        'tkinter',  # Usually built-in with Python
        'pillow',   # For image handling
        'matplotlib',  # For charts
        'requests'  # For API calls
    ]
    
    print("🔍 Checking dependencies...")
    
    missing_packages = []
    
    # Check tkinter (built-in)
    try:
        import tkinter
        print("✅ tkinter: Available")
    except ImportError:
        print("❌ tkinter: Missing (install python3-tk)")
        missing_packages.append('python3-tk')
    
    # Check PIL/Pillow
    try:
        from PIL import Image, ImageTk
        print("✅ Pillow: Available")
    except ImportError:
        print("❌ Pillow: Missing")
        missing_packages.append('pillow')
    
    # Check matplotlib
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib: Available")
    except ImportError:
        print("❌ matplotlib: Missing")
        missing_packages.append('matplotlib')
    
    # Check requests
    try:
        import requests
        print("✅ requests: Available")
    except ImportError:
        print("❌ requests: Missing")
        missing_packages.append('requests')
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            # Try pip install
            for package in missing_packages:
                if package != 'python3-tk':  # Handle tkinter separately
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            
            if 'python3-tk' in missing_packages:
                print("⚠️  Please install python3-tk manually:")
                print("   macOS: brew install python-tk")
                print("   Ubuntu: sudo apt-get install python3-tk")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    print("✅ All dependencies satisfied!")
    return True

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Setting up environment...")
    
    # Check for API keys
    api_keys = {
        'OPENAI_API_KEY': 'ChatGPT API Key',
        'XAI_API_KEY': 'Grok API Key', 
        'SARVAM_API_KEY': 'Sarvam API Key',
        'NEWS_API_KEY': 'News API Key (optional)'
    }
    
    found_keys = 0
    for key, description in api_keys.items():
        if os.getenv(key):
            print(f"✅ {description}: Set")
            found_keys += 1
        else:
            print(f"⚠️  {description}: Not set")
    
    if found_keys == 0:
        print("\n📝 No API keys found. The app will run in demo mode.")
        print("   To enable full functionality, set your API keys:")
        print("   export OPENAI_API_KEY='your_key_here'")
        print("   export XAI_API_KEY='your_key_here'")
    elif found_keys < len(api_keys):
        print(f"\n📝 {found_keys}/{len(api_keys)} API keys configured.")
        print("   Some features may be limited.")
    else:
        print("\n✅ All API keys configured!")
    
    return True

def launch_app():
    """Launch the Mac app"""
    print("\n🚀 Launching Mac App with Twitter Timeline...")
    
    try:
        # Try to import and run the app
        from mac_app_with_timeline import main
        main()
    except ImportError:
        print("❌ Mac app module not found. Make sure mac_app_with_timeline.py exists.")
        return False
    except Exception as e:
        print(f"❌ Failed to launch app: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🍎 Zero-Cost Twitter Bot - Mac App Launcher")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return 1
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("\n❌ Dependency check failed. Please resolve issues above.")
        return 1
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed.")
        return 1
    
    # Launch app
    print("\n" + "=" * 50)
    if not launch_app():
        print("\n❌ Failed to launch app.")
        return 1
    
    print("\n👋 Thanks for using Zero-Cost Twitter Bot!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)