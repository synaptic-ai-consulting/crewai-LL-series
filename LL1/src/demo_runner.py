"""
Demo runner for Lightning Lesson 1: Flows vs Crews comparison.
Executes all three approaches and provides detailed comparison.
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

try:
    from .crew_only import CrewOnlyDemo
    from .flow_only import FlowOnlyDemo
    from .hybrid_flow import HybridFlowDemo
    from .state import Lesson1State
except ImportError:
    from crew_only import CrewOnlyDemo
    from flow_only import FlowOnlyDemo
    from hybrid_flow import HybridFlowDemo
    from state import Lesson1State


class LightningLesson1Demo:
    """Main demo runner for Lightning Lesson 1."""
    
    def __init__(self, topic: str = "API Gateway Security Best Practices", 
                 audience: str = "Enterprise Developers"):
        self.topic = topic
        self.audience = audience
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_demos(self) -> Dict[str, Any]:
        """Execute all three demo approaches."""
        print("🚀 Starting Lightning Lesson 1 Demo: Flows vs Crews")
        print("=" * 60)
        print(f"Topic: {self.topic}")
        print(f"Audience: {self.audience}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Stage A: Crew-Only Demo
        print("\n" + "="*20 + " STAGE A: CREW-ONLY " + "="*20)
        crew_result = self._run_crew_demo()
        self.results["crew_only"] = crew_result
        
        # Stage B: Flow-Only Demo
        print("\n" + "="*20 + " STAGE B: FLOW-ONLY " + "="*20)
        flow_result = self._run_flow_demo()
        self.results["flow_only"] = flow_result
        
        # Stage C: Hybrid Demo
        print("\n" + "="*20 + " STAGE C: HYBRID " + "="*20)
        hybrid_result = self._run_hybrid_demo()
        self.results["hybrid"] = hybrid_result
        
        self.end_time = time.time()
        
        # Generate comparison
        comparison = self._generate_comparison()
        self.results["comparison"] = comparison
        
        return self.results
    
    def _run_crew_demo(self) -> Dict[str, Any]:
        """Execute crew-only demo."""
        print("🤖 Executing Crew-Only (Autonomous) Approach...")
        print("⚠️  This approach can be unpredictable and hard to control")
        
        try:
            demo = CrewOnlyDemo(self.topic, self.audience)
            state = demo.run_demo()
            summary = demo.get_performance_summary()
            
            print(f"✅ Crew-only demo completed in {summary['total_time']:.2f}s")
            return summary
            
        except Exception as e:
            print(f"❌ Crew-only demo failed: {str(e)}")
            return {
                "approach": "Crew-Only (Autonomous)",
                "error": str(e),
                "total_time": 0,
                "characteristics": ["High autonomy", "Unpredictable", "Difficult to control"]
            }
    
    def _run_flow_demo(self) -> Dict[str, Any]:
        """Execute flow-only demo."""
        print("📋 Executing Flow-Only (Structured) Approach...")
        print("✅ This approach provides precise control and predictability")
        
        try:
            demo = FlowOnlyDemo(self.topic, self.audience)
            state = demo.kickoff()
            summary = demo.get_performance_summary()
            
            print(f"✅ Flow-only demo completed in {summary['total_time']:.2f}s")
            return summary
            
        except Exception as e:
            print(f"❌ Flow-only demo failed: {str(e)}")
            return {
                "approach": "Flow-Only (Structured)",
                "error": str(e),
                "total_time": 0,
                "characteristics": ["Predictable", "Controlled", "Limited collaboration"]
            }
    
    def _run_hybrid_demo(self) -> Dict[str, Any]:
        """Execute hybrid demo."""
        print("🎯 Executing Hybrid (Orchestrated + Collaborative) Approach...")
        print("🚀 This approach combines structure with intelligent collaboration")
        
        try:
            demo = HybridFlowDemo(self.topic, self.audience)
            state = demo.kickoff()
            summary = demo.get_performance_summary()
            
            print(f"✅ Hybrid demo completed in {summary['total_time']:.2f}s")
            return summary
            
        except Exception as e:
            print(f"❌ Hybrid demo failed: {str(e)}")
            return {
                "approach": "Hybrid (Orchestrated + Collaborative)",
                "error": str(e),
                "total_time": 0,
                "characteristics": ["Structured", "Collaborative", "Optimal balance"]
            }
    
    def _generate_comparison(self) -> Dict[str, Any]:
        """Generate detailed comparison of all approaches."""
        print("\n" + "="*20 + " COMPARISON ANALYSIS " + "="*20)
        
        comparison = {
            "execution_summary": {
                "total_demo_time": self.end_time - self.start_time,
                "timestamp": datetime.now().isoformat(),
                "topic": self.topic,
                "audience": self.audience
            },
            "performance_metrics": {},
            "characteristics_comparison": {},
            "recommendations": {},
            "decision_framework": {}
        }
        
        # Performance comparison
        for approach, result in self.results.items():
            if approach != "comparison" and "error" not in result:
                comparison["performance_metrics"][approach] = {
                    "execution_time": result.get("total_time", 0),
                    "stages": result.get("stages", {}),
                    "success": True
                }
        
        # Characteristics comparison
        comparison["characteristics_comparison"] = {
            "crew_only": self.results.get("crew_only", {}).get("characteristics", []),
            "flow_only": self.results.get("flow_only", {}).get("characteristics", []),
            "hybrid": self.results.get("hybrid", {}).get("characteristics", [])
        }
        
        # Generate recommendations
        comparison["recommendations"] = self._generate_recommendations()
        
        # Decision framework
        comparison["decision_framework"] = self._generate_decision_framework()
        
        return comparison
    
    def _generate_recommendations(self) -> Dict[str, str]:
        """Generate recommendations based on demo results."""
        return {
            "use_crew_only": "When you need maximum creativity and can tolerate unpredictability",
            "use_flow_only": "When you need precise control and predictable execution",
            "use_hybrid": "When you need both structure and intelligent collaboration (recommended for enterprise)",
            "key_insight": "Structure beats autonomy when stakes are high - hybrid approaches provide the best balance"
        }
    
    def _generate_decision_framework(self) -> Dict[str, Any]:
        """Generate decision framework for choosing approaches."""
        return {
            "decision_matrix": {
                "scenario": ["Creative Tasks", "Compliance Workflows", "Complex Reasoning", "State Management", "Audit Trail"],
                "crew_only": ["✓", "✗", "✓", "✗", "✗"],
                "flow_only": ["✗", "✓", "✗", "✓", "✓"],
                "hybrid": ["✓", "✓", "✓", "✓", "✓"]
            },
            "enterprise_considerations": {
                "risk_tolerance": "Low risk tolerance favors Flow or Hybrid",
                "compliance_requirements": "High compliance needs favor Flow or Hybrid",
                "creativity_needs": "High creativity needs favor Crew or Hybrid",
                "maintenance_requirements": "Easy maintenance favors Flow or Hybrid"
            }
        }
    
    def save_results(self, filename: str = None) -> str:
        """Save demo results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"artifacts/ll1_demo_results_{timestamp}.json"
        
        filepath = Path(filename)
        
        # Prepare results for JSON serialization
        serializable_results = self._prepare_for_serialization(self.results)
        
        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"📁 Results saved to: {filepath}")
        return str(filepath)
    
    def _prepare_for_serialization(self, data: Any) -> Any:
        """Prepare data for JSON serialization."""
        if isinstance(data, dict):
            return {k: self._prepare_for_serialization(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_serialization(item) for item in data]
        elif hasattr(data, 'model_dump'):
            return data.model_dump()
        else:
            return data
    
    def save_results_to_file(self, filename: str = None) -> str:
        """Save demo results to file (alias for save_results)."""
        return self.save_results(filename)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary with timing and metadata."""
        total_time = 0.0
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
        
        summary = {
            "topic": self.topic,
            "audience": self.audience,
            "total_execution_time": total_time,
            "timestamp": datetime.now().isoformat(),
            "approaches_executed": list(self.results.keys()),
            "success_count": sum(1 for r in self.results.values() if "error" not in r),
            "total_count": len([k for k in self.results.keys() if k != "comparison"])
        }
        
        return summary
    
    def print_summary(self):
        """Print a summary of all results."""
        print("\n" + "="*60)
        print("🎯 LIGHTNING LESSON 1 DEMO SUMMARY")
        print("="*60)
        
        for approach, result in self.results.items():
            if approach != "comparison" and "error" not in result:
                print(f"\n📊 {result.get('approach', approach.upper())}")
                print(f"   Execution Time: {result.get('total_time', 0):.2f}s")
                print(f"   Characteristics: {', '.join(result.get('characteristics', []))}")
        
        if "comparison" in self.results:
            comp = self.results["comparison"]
            print(f"\n⏱️  Total Demo Time: {comp['execution_summary']['total_demo_time']:.2f}s")
            print(f"📅 Completed: {comp['execution_summary']['timestamp']}")


def main():
    """Main entry point for the demo."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    topic = os.getenv("DEMO_TOPIC", "API Gateway Security Best Practices")
    audience = os.getenv("DEMO_AUDIENCE", "Enterprise Developers")
    
    # Run the demo
    demo = LightningLesson1Demo(topic=topic, audience=audience)
    results = demo.run_all_demos()
    
    # Print summary
    demo.print_summary()
    
    # Save results
    demo.save_results()
    
    return results


if __name__ == "__main__":
    main()
