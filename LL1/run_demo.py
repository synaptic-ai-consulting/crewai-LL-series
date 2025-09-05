#!/usr/bin/env python3
"""
Quick demo runner script for Lightning Lesson 1.
This script provides a simple way to run the demo with different configurations.
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.demo_runner import LightningLesson1Demo


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Lightning Lesson 1 Demo: Flows vs Crews",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_demo.py
  python run_demo.py --topic "Database Security" --audience "DevOps Engineers"
  python run_demo.py --approach hybrid
  python run_demo.py --save-results --output results.json
        """
    )
    
    parser.add_argument(
        "--topic",
        default="API Gateway Security Best Practices",
        help="Topic for the technical guide (default: API Gateway Security Best Practices)"
    )
    
    parser.add_argument(
        "--audience", 
        default="Enterprise Developers",
        help="Target audience for the content (default: Enterprise Developers)"
    )
    
    parser.add_argument(
        "--approach",
        choices=["crew", "flow", "hybrid", "all"],
        default="all",
        help="Which approach to run (default: all)"
    )
    
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Save results to JSON file"
    )
    
    parser.add_argument(
        "--output",
        default=None,
        help="Output filename for results (default: auto-generated)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = LightningLesson1Demo(topic=args.topic, audience=args.audience)
    
    if args.verbose:
        print(f"🚀 Running Lightning Lesson 1 Demo")
        print(f"📝 Topic: {args.topic}")
        print(f"👥 Audience: {args.audience}")
        print(f"🎯 Approach: {args.approach}")
        print("-" * 50)
    
    try:
        if args.approach == "all":
            # Run all approaches
            results = demo.run_all_demos()
        else:
            # Run specific approach
            if args.approach == "crew":
                result = demo._run_crew_demo()
                results = {"crew_only": result}
            elif args.approach == "flow":
                result = demo._run_flow_demo()
                results = {"flow_only": result}
            elif args.approach == "hybrid":
                result = demo._run_hybrid_demo()
                results = {"hybrid": result}
        
        # Print summary
        demo.print_summary()
        
        # Save results if requested or if running all approaches
        if args.save_results or args.approach == "all":
            output_file = demo.save_results(args.output)
            print(f"📁 Results saved to: {output_file}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
