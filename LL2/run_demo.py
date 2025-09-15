#!/usr/bin/env python3
"""
Lightning Lesson 2 Demo Runner
Advanced Agent Persona Architecture with CrewAI

Usage:
    python run_demo.py                    # Run full demo
    python run_demo.py --comparison      # Run before/after comparison only
    python run_demo.py --showcase        # Run persona showcase only
    python run_demo.py --task "Your task" # Run with custom task
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.demo_runner import LightningLesson2Demo


def main():
    parser = argparse.ArgumentParser(description='Lightning Lesson 2 Demo Runner')
    parser.add_argument('--comparison', action='store_true', 
                       help='Run before/after comparison demo only')
    parser.add_argument('--showcase', action='store_true',
                       help='Run persona showcase demo only')
    parser.add_argument('--task', type=str,
                       help='Task name from config/tasks.yaml for the demo')
    parser.add_argument('--crew', type=str,
                       help='Crew name from config/crews.yaml to run')
    parser.add_argument('--list-configs', action='store_true',
                       help='List available agents, tasks, and crews')
    parser.add_argument('--validate', action='store_true',
                       help='Validate YAML configurations')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return 1
    
    demo = LightningLesson2Demo()
    
    try:
        if args.list_configs:
            # List available configurations
            print("📋 Available Configurations:")
            print("\n🤖 Agents:")
            for agent in demo.agents_manager.get_available_agents():
                print(f"  - {agent}")
            
            print("\n📝 Tasks:")
            for task in demo.agents_manager.get_available_tasks():
                print(f"  - {task}")
            
            print("\n🚀 Crews:")
            for crew in demo.agents_manager.get_available_crews():
                print(f"  - {crew}")
            return 0
            
        elif args.validate:
            # Validate configurations
            print("🔍 Validating YAML configurations...")
            validation_results = demo.agents_manager.validate_configurations()
            
            if validation_results["errors"]:
                print("❌ Configuration errors found:")
                for error in validation_results["errors"]:
                    print(f"  - {error}")
                return 1
            
            if validation_results["warnings"]:
                print("⚠️  Configuration warnings:")
                for warning in validation_results["warnings"]:
                    print(f"  - {warning}")
            
            print("✅ All configurations are valid!")
            return 0
            
        elif args.crew:
            # Run specific crew
            demo.run_crew_demo(args.crew)
            
        elif args.comparison:
            # Run comparison demo only
            demo.run_comparison_demo(args.task)
            
        elif args.showcase:
            # Run persona showcase only
            demo.run_persona_showcase(args.task)
                
        else:
            # Run full demo
            demo.run_comparison_demo(args.task)
            demo.run_persona_showcase(args.task)
        
        # Save results
        demo.save_results()
        print("\n✅ Demo completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
