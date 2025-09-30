#!/usr/bin/env python3
"""
Lightning Lesson 2 Setup Script
Quick setup for the Advanced Agent Persona Architecture demo
"""

import os
import shutil
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    print("\n🔧 Setting up environment...")
    
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env and add your OpenAI API key")
        else:
            print("❌ env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_artifacts_directory():
    """Create artifacts directory"""
    print("\n📁 Creating artifacts directory...")
    try:
        os.makedirs('artifacts', exist_ok=True)
        print("✅ Artifacts directory created")
        return True
    except Exception as e:
        print(f"❌ Failed to create artifacts directory: {e}")
        return False

def run_tests():
    """Run test suite"""
    print("\n🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "test_demo.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Lightning Lesson 2 Setup")
    print("Advanced Agent Persona Architecture Demo")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Create artifacts directory
    if not create_artifacts_directory():
        return False
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Setup completed but some tests failed")
        print("You may need to fix issues before running the demo")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run the demo: python run_demo.py")
    print("3. Try different options:")
    print("   - python run_demo.py --comparison")
    print("   - python run_demo.py --showcase")
    print("   - python run_demo.py --task 'Your custom task'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
