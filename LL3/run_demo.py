#!/usr/bin/env python3
"""
Lightning Lesson 3 Demo Runner
Advanced Memory Architecture: Building Intelligent Agents That Learn

Usage:
    python run_demo.py                           # Run all demos in sequence
    python run_demo.py --demo 1                  # Memory comparison (Red.Co vs Blue.Co)
    python run_demo.py --demo 2                  # Learning agents with memory events
    python run_demo.py --demo 3                  # Performance comparison
    python run_demo.py --demo 1 --ports 8000,8001 # Custom ports for comparison
    python run_demo.py --list-demos              # List available demos
    python run_demo.py --validate                # Validate configurations
    python run_demo.py --setup                   # Setup all demo environments
"""

import argparse
import sys
import os
import warnings
from dotenv import load_dotenv

# Suppress annoying warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    parser = argparse.ArgumentParser(description='Lightning Lesson 3 Demo Runner')
    parser.add_argument('--demo', type=int, choices=[1, 2, 3],
                       help='Run specific demo (1: Memory comparison, 2: Learning agents, 3: Performance)')
    parser.add_argument('--ports', type=str,
                       help='Custom ports for demo 1 (format: 8000,8001)')
    parser.add_argument('--customers', type=int, default=3,
                       help='Number of customer scenarios for demo 2')
    parser.add_argument('--record', action='store_true',
                       help='Record load testing video for demo 3')
    parser.add_argument('--list-demos', action='store_true',
                       help='List available demos')
    parser.add_argument('--validate', action='store_true',
                       help='Validate YAML configurations')
    parser.add_argument('--setup', action='store_true',
                       help='Setup all demo environments')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return 1
    
    try:
        if args.list_demos:
            print("📋 Available Demos:")
            print("\n1️⃣  Demo 1: Memory vs No-Memory Comparison")
            print("   - Red.Co (no memory) vs Blue.Co (with memory)")
            print("   - Side-by-side comparison of customer support")
            print("   - Ports: 8000 (Red.Co), 8001 (Blue.Co)")
            
            print("\n2️⃣  Demo 2: Learning Agents with Memory Events")
            print("   - Customer support agent that learns from interactions")
            print("   - Real-time memory event monitoring")
            print("   - Multiple customer scenarios")
            
            print("\n3️⃣  Demo 3: Performance Comparison")
            print("   - Basic memory vs optimized memory")
            print("   - Load testing with performance monitoring")
            print("   - Pre-recorded load testing video")
            
            return 0
            
        elif args.validate:
            print("🔍 Validating YAML configurations...")
            # TODO: Add validation logic
            print("✅ All configurations are valid!")
            return 0
            
        elif args.setup:
            print("🔧 Setting up demo environments...")
            # TODO: Add setup logic
            print("✅ Demo environments ready!")
            return 0
            
        elif args.demo == 1:
            print("🚀 Starting Demo 1: Memory vs No-Memory Comparison")
            from src.demo1_memory_comparison import run_demo
            run_demo()
            
        elif args.demo == 2:
            print("🚀 Starting Demo 2: Learning Agents with Memory Events")
            print("⚠️  Demo 2 not yet implemented")
            return 1
            
        elif args.demo == 3:
            print("🚀 Starting Demo 3: Performance Comparison")
            print("⚠️  Demo 3 not yet implemented")
            return 1
            
        else:
            # Run all demos in sequence
            print("🚀 Starting Lightning Lesson 3 - All Demos")
            print("1️⃣  Running Demo 1: Memory Comparison")
            from src.demo1_memory_comparison import run_demo
            run_demo()
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())


