"""
Hybrid orchestrated approach for Lightning Lesson 1 demo.
Combines Flow structure with targeted Crew collaboration.
"""

import time
from typing import Dict, Any
from crewai.flow import Flow, start, listen, router
from crewai import LLM
try:
    from .state import Lesson1State, GuideOutline, ReviewResult
    from .mini_crew import run_writer_reviewer_crew, MiniCrewPerformance
except ImportError:
    from state import Lesson1State, GuideOutline, ReviewResult
    from mini_crew import run_writer_reviewer_crew, MiniCrewPerformance


class HybridFlowDemo(Flow[Lesson1State]):
    """Hybrid implementation combining Flow orchestration with Crew collaboration."""
    
    def __init__(self, topic: str, audience: str):
        self.performance_metrics: Dict[str, float] = {}
        self.llm = LLM(model="gpt-4o", temperature=0.0)
        self.crew_performance = MiniCrewPerformance()
        self.topic = topic
        self.audience = audience
        initial_state = Lesson1State(topic=topic, audience=audience)
        super().__init__(initial_state=initial_state)
    
    @start()
    def initialize_topic(self):
        """Initialize the topic and audience."""
        print("🚀 Starting Hybrid Flow Demo (Orchestrated + Collaborative)")
        
        # Set the topic and audience in the Flow state
        self.state.topic = self.topic
        self.state.audience = self.audience
        
        print(f"Topic: {self.state.topic}")
        print(f"Audience: {self.state.audience}")
        print("-" * 50)
        
        self.state.current_stage = "initialized"
        print("✅ Topic initialized")
        return self.state
    
    @listen(initialize_topic)
    def create_outline(self, state):
        """Create structured outline using direct LLM call for precision."""
        print("📝 Creating structured outline (Flow-controlled)...")
        start_time = time.time()
        
        try:
            messages = [{
                "role": "user", 
                "content": f"""Create a structured outline for a technical guide section on '{state.topic}' 
                targeted at {state.audience}. 
                
                The outline should include:
                1. A clear, compelling title
                2. An introduction paragraph (2-3 sentences)
                3. 3-5 key points with specific details and examples
                4. A conclusion paragraph (2-3 sentences)
                
                Format as structured data with title, introduction, key_points (list), and conclusion.
                Ensure the outline is enterprise-ready and immediately actionable."""
            }]
            
            response = self.llm.call(messages=messages)
            # Convert Mock objects to strings for testing
            self.state.outline = str(response) if hasattr(response, '__call__') else response
            self.state.current_stage = "outline_created"
            
            self.performance_metrics["outline_creation"] = time.time() - start_time
            print("✅ Structured outline created")
            
        except Exception as e:
            print(f"❌ Outline creation failed: {str(e)}")
            self.state.error_log = str(e)
            self.state.outline = f"Basic outline for {state.topic}"
        
        return self.state
    
    @listen(create_outline)
    def collaborative_draft_review(self, state):
        """Use mini crew for complex draft and review collaboration."""
        print("🤝 Orchestrating mini crew for draft and review...")
        start_time = time.time()
        
        try:
            # Call mini crew for complex collaboration
            draft, review, risk = run_writer_reviewer_crew(
                topic=state.topic,
                outline=state.outline,
                audience=state.audience
            )
            
            # Update state with crew results
            self.state.draft = draft
            self.state.review_comments = review
            self.state.risk_level = risk
            self.state.current_stage = "draft_reviewed"
            
            # Track crew performance
            execution_time = time.time() - start_time
            self.crew_performance.track_execution(
                topic=state.topic,
                execution_time=execution_time,
                success=True
            )
            
            self.performance_metrics["collaborative_draft_review"] = execution_time
            print(f"✅ Mini crew collaboration completed (Risk: {risk})")
            
        except Exception as e:
            print(f"❌ Mini crew collaboration failed: {str(e)}")
            self.state.error_log = str(e)
            self.state.draft = f"Draft content for {state.topic}"
            self.state.review_comments = "Review failed"
            self.state.risk_level = "medium"
            
            self.crew_performance.track_execution(
                topic=state.topic,
                execution_time=time.time() - start_time,
                success=False
            )
        
        return self.state
    
    @router(collaborative_draft_review)
    def risk_assessment(self, state):
        """Route based on risk level assessment."""
        print(f"🎯 Risk assessment: {state.risk_level}")
        
        if state.risk_level == "high":
            print("⚠️ High risk detected - routing to compliance fix")
            return "high_risk"
        else:
            print("✅ Low/medium risk - routing to approval")
            return "approved"
    
    @listen(risk_assessment)
    def compliance_fix(self, state):
        """Fix compliance issues using structured LLM approach."""
        print("🔧 Applying compliance fixes (Flow-controlled)...")
        start_time = time.time()
        
        try:
            # Handle case where state might be a string (from Flow routing)
            if isinstance(state, str):
                state = self.state
            
            messages = [{
                "role": "user",
                "content": f"""Fix the compliance issues in this content based on the review:
                
                Original Content:
                {state.draft}
                
                Review Comments:
                {state.review_comments}
                
                Requirements:
                - Address all compliance issues identified
                - Maintain technical accuracy and clarity
                - Keep the same target audience: {state.audience}
                - Ensure enterprise-ready quality
                - Preserve the practical examples and actionable advice
                
                Provide the revised content that addresses all concerns while maintaining quality."""
            }]
            
            response = self.llm.call(messages=messages)
            # Convert Mock objects to strings for testing
            self.state.final_content = str(response) if hasattr(response, '__call__') else response
            self.state.compliance_status = "approved"
            self.state.current_stage = "fixed_and_approved"
            
            self.performance_metrics["compliance_fix"] = time.time() - start_time
            print("✅ Compliance fixes applied")
            
        except Exception as e:
            print(f"❌ Compliance fix failed: {str(e)}")
            self.state.error_log = str(e)
            self.state.final_content = state.draft
            self.state.compliance_status = "approved"
        
        return self.state
    
    @listen(risk_assessment)
    def finalize_content(self, state):
        """Finalize content for approved items."""
        print("✅ Finalizing approved content...")
        start_time = time.time()
        
        # Handle case where state might be a string (from Flow routing)
        if isinstance(state, str):
            state = self.state
            
        self.state.final_content = state.draft
        self.state.compliance_status = "approved"
        self.state.current_stage = "finalized"
        
        self.performance_metrics["finalization"] = time.time() - start_time
        print("✅ Content finalized")
        
        return self.state
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        total_time = sum(self.performance_metrics.values())
        crew_summary = self.crew_performance.get_summary()
        
        return {
            "approach": "Hybrid (Orchestrated + Collaborative)",
            "total_time": total_time,
            "stages": self.performance_metrics,
            "crew_performance": crew_summary,
            "state": self.state.model_dump(),
            "characteristics": [
                "Structured orchestration",
                "Targeted collaboration",
                "Predictable execution path",
                "Rich creative output",
                "Complete audit trail",
                "Optimal resource usage"
            ]
        }
    
    def get_architecture_benefits(self) -> Dict[str, str]:
        """Get architectural benefits of hybrid approach."""
        return {
            "Flow Benefits": "Precise control, state management, error handling, audit trail",
            "Crew Benefits": "Complex reasoning, creative collaboration, specialized expertise",
            "Hybrid Value": "Best of both worlds - structure where needed, intelligence where valuable",
            "Enterprise Ready": "Scalable, maintainable, debuggable, and cost-effective"
        }
    
    def kickoff(self):
        """Execute the complete hybrid flow workflow."""
        try:
            # Initialize the topic
            self.initialize_topic()
            
            # Create outline using Flow
            self.create_outline(self.state)
            
            # Use mini crew for collaborative draft and review
            self.collaborative_draft_review(self.state)
            
            # Assess risk and apply fixes if needed
            if self.state.risk_level == "high":
                self.compliance_fix(self.state)
            else:
                self.finalize_content(self.state)
            
            # Save output to artifacts directory
            self._save_output_to_file()
            
            # Generate final summary
            return self.get_performance_summary()
            
        except Exception as e:
            print(f"❌ Hybrid flow execution failed: {str(e)}")
            self.state.error_log = str(e)
            return f"Hybrid flow execution failed: {str(e)}"
    
    def _save_output_to_file(self):
        """Save hybrid flow output to artifacts directory."""
        try:
            from pathlib import Path
            import os
            
            # Ensure artifacts directory exists
            artifacts_dir = Path("artifacts")
            artifacts_dir.mkdir(exist_ok=True)
            
            # Generate output content
            output_content = f"""# Hybrid Flow Demo Output

## Topic: {self.state.topic}
## Audience: {self.state.audience}

## Generated Outline
{self.state.outline or 'Not generated'}

## Draft Content
{self.state.draft or 'Not generated'}

## Review Comments
{self.state.review_comments or 'Not generated'}

## Risk Level
{self.state.risk_level or 'Not assessed'}

## Final Content
{self.state.final_content or 'Not generated'}

## Compliance Status
{self.state.compliance_status or 'Not determined'}

## Performance Metrics
{self.performance_metrics}

## Crew Performance
{self.crew_performance.get_summary() if hasattr(self.crew_performance, 'get_summary') else 'Not available'}

## Generated at
{self.state.created_at}
"""
            
            # Save to file
            output_file = artifacts_dir / "hybrid_flow_output.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            print(f"📁 Hybrid flow output saved to: {output_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save hybrid flow output: {str(e)}")