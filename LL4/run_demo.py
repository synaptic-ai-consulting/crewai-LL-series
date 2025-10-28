#!/usr/bin/env python3
"""
CrewAI HITL Demo Runner
Launches webhook server and runs selected demos
"""

import os
import sys
import argparse
import subprocess
import threading
import time
from pathlib import Path

def setup_environment():
    """Setup environment and install dependencies."""
    print("🔧 Setting up environment...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Please copy env.example to .env and configure your API keys.")
        print("   cp env.example .env")
        return False
    
    # Install requirements
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_webhook_server():
    """Start the webhook server in a separate thread."""
    print("🚀 Starting webhook server...")
    
    def run_server():
        # Change to the directory containing the webhook server
        import subprocess
        subprocess.run([sys.executable, 'src/webhook_server.py'], cwd=os.getcwd())
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    print("✅ Webhook server started on port 5000")

def run_demo(demo_number):
    """Run a specific demo."""
    demo_scripts = {
        1: 'src/demo1_opensource_hitl.py',
        2: 'src/demo2_amp_deploy_first.py',  # Config checker and setup instructions
        3: 'src/demo3_multi_agent_handoff.py'
    }
    
    if demo_number not in demo_scripts:
        print(f"❌ Demo {demo_number} not found")
        return False
    
    script_path = demo_scripts[demo_number]
    
    # Demo 2 just checks configuration and provides setup instructions
    if demo_number == 2:
        print("🔗 Demo 2: Enterprise AMP Deployment with HITL")
        print("   This will check your configuration and provide setup instructions")
    
    if not os.path.exists(script_path):
        print(f"❌ Demo script not found: {script_path}")
        return False
    
    print(f"🎯 Running Demo {demo_number}...")
    print(f"📄 Script: {script_path}")
    print("=" * 60)
    
    try:
        # Run the demo script
        result = subprocess.run([sys.executable, script_path], 
                               cwd=os.getcwd(),
                               capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Demo execution failed: {e}")
        return False

def list_demos():
    """List available demos."""
    print("📋 Available Demos:")
    print()
    print("1. Open Source HITL")
    print("   Local execution with basic human_input=True functionality")
    print("   Uses: Python Flask webhook server")
    print("   Best for: Development and testing")
    print()
    print("2. Enterprise AMP Deployment with HITL")
    print("   Production-ready multi-agent content pipeline")
    print("   Uses: CrewAI AMP, Node.js backend, React frontend, ngrok")
    print("   Best for: Production deployments")
    print("   Note: Requires separate setup (see LL4/README.md)")
    print()
    print("3. Multi-Agent Workflow")
    print("   Sequential agents with human gates")
    print("   Uses: Open source CrewAI")
    print()
    print("Usage: python run_demo.py --demo <number>")

def validate_setup():
    """Validate the demo setup."""
    print("🔍 Validating setup...")
    
    issues = []
    
    # Check required files
    required_files = [
        'src/webhook_server.py',
        'config/agents.yaml',
        'config/tasks.yaml',
        'requirements.txt',
        '.env'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing file: {file_path}")
    
    # Check environment variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv('OPENAI_API_KEY'):
            issues.append("OPENAI_API_KEY not set in .env file")
        
        # Check for CrewAI AMP API key (optional for Demo 2)
        crewai_api_key = os.getenv('CREWAI_API_KEY')
        if not crewai_api_key:
            print("💡 Note: CREWAI_API_KEY not set - Demo 2 will run in simulation mode")
    
    if issues:
        print("❌ Setup issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Setup validation passed")
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='CrewAI HITL Demo Runner')
    parser.add_argument('--demo', type=int, choices=[1, 2, 3], 
                       help='Run specific demo (1, 2, or 3)')
    parser.add_argument('--list-demos', action='store_true',
                       help='List available demos')
    parser.add_argument('--validate', action='store_true',
                       help='Validate demo setup')
    parser.add_argument('--setup', action='store_true',
                       help='Setup environment and dependencies')
    
    args = parser.parse_args()
    
    print("🚀 CrewAI HITL Demo Runner")
    print("=" * 40)
    
    if args.setup:
        if setup_environment():
            print("✅ Setup completed successfully!")
        else:
            print("❌ Setup failed")
            sys.exit(1)
        return
    
    if args.validate:
        if validate_setup():
            print("✅ Validation passed")
            sys.exit(0)
        else:
            print("❌ Validation failed")
            sys.exit(1)
    
    if args.list_demos:
        list_demos()
        return
    
    if args.demo:
        # Validate setup first
        if not validate_setup():
            print("❌ Setup validation failed. Run with --setup to fix issues.")
            sys.exit(1)
        
        # Only start webhook server for Demo 1
        if args.demo == 1:
            start_webhook_server()
            print(f"\n🌐 Webhook server running at: http://localhost:5000")
            print(f"🎯 Demo {args.demo} UI: http://localhost:5000/demo{args.demo}")
            print("\nPress Ctrl+C to stop the demo")
        elif args.demo == 2:
            print(f"\n📋 Demo 2 requires separate services:")
            print(f"   1. ngrok tunnel")
            print(f"   2. Node.js backend (demo2-backend)")
            print(f"   3. React frontend (demo2-frontend)")
            print(f"\n   See LL4/README.md for complete setup instructions")
        
        print("=" * 60)
        
        try:
            # Run the demo
            success = run_demo(args.demo)
            if success:
                print(f"\n✅ Demo {args.demo} completed successfully!")
            else:
                print(f"\n❌ Demo {args.demo} failed")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            sys.exit(1)
    else:
        print("🎯 CrewAI HITL Demos")
        print("\nAvailable commands:")
        print("  python run_demo.py --demo 1      # Open Source HITL - Local execution")
        print("  python run_demo.py --demo 2      # Enterprise AMP HITL - Check config")
        print("  python run_demo.py --demo 3      # Multi-Agent Workflow")
        print("  python run_demo.py --list-demos  # List all demos")
        print("  python run_demo.py --validate    # Validate setup")
        print("  python run_demo.py --setup       # Setup environment")
        print("\n💡 For Demo 2 full setup, see LL4/README.md")

if __name__ == "__main__":
    main()

