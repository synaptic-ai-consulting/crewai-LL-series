"""
Flow-only structured approach for Lightning Lesson 1 demo.
Demonstrates precise control with direct LLM orchestration.
"""

import time
from typing import Dict, Any
from crewai.flow import Flow, start, listen, router
from crewai import LLM
try:
    from .state import Lesson1State, GuideOutline, ReviewResult
except ImportError:
    from state import Lesson1State, GuideOutline, ReviewResult


class FlowOnlyDemo(Flow[Lesson1State]):
    """Flow-only implementation showing structured LLM orchestration."""
    
    def __init__(self, topic: str, audience: str):
        self.performance_metrics: Dict[str, float] = {}
        self.llm = LLM(model="gpt-4o", temperature=0.0)
        self.topic = topic
        self.audience = audience
        initial_state = Lesson1State(topic=topic, audience=audience)
        super().__init__(initial_state=initial_state)
    
    @start()
    def initialize_topic(self):
        """Initialize the topic and audience."""
        print("🚀 Starting Flow-Only Demo (Structured Approach)")
        
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
        """Create structured outline using direct LLM call."""
        print("📝 Creating structured outline...")
        start_time = time.time()
        
        try:
            messages = [{
                "role": "user", 
                "content": f"""Create a structured outline for a technical guide section on '{state.topic}' 
                targeted at {state.audience}. 
                
                The outline should include:
                1. A clear title
                2. An introduction paragraph
                3. 3-5 key points with specific details
                4. A conclusion paragraph
                
                Format as structured data with title, introduction, key_points (list), and conclusion."""
            }]
            
            # Use structured output for consistency
            response = self.llm.call(messages=messages)
            # Convert Mock objects to strings for testing
            self.state.outline = str(response) if hasattr(response, '__call__') else response
            self.state.current_stage = "outline_created"
            
            self.performance_metrics["outline_creation"] = time.time() - start_time
            print("✅ Outline created successfully")
            
        except Exception as e:
            print(f"❌ Outline creation failed: {str(e)}")
            self.state.error_log = str(e)
            self.state.outline = f"Basic outline for {state.topic}"
        
        return self.state
    
    @listen(create_outline)
    def draft_content(self, state):
        """Draft content using structured outline."""
        print("✍️ Drafting content...")
        start_time = time.time()
        
        try:
            messages = [{
                "role": "user",
                "content": f"""Write a comprehensive 3-paragraph technical guide section based on this outline:
                
                {state.outline}
                
                Requirements:
                - Target audience: {state.audience}
                - Include practical examples
                - Use clear, professional language
                - Ensure enterprise-readiness
                - Each paragraph should be 4-6 sentences
                
                Write the complete section now."""
            }]
            
            response = self.llm.call(messages=messages)
            # Convert Mock objects to strings for testing
            self.state.draft = str(response) if hasattr(response, '__call__') else response
            self.state.current_stage = "draft_created"
            
            self.performance_metrics["content_drafting"] = time.time() - start_time
            print("✅ Content drafted successfully")
            
        except Exception as e:
            print(f"❌ Content drafting failed: {str(e)}")
            self.state.error_log = str(e)
            self.state.draft = f"Draft content for {state.topic}"
        
        return self.state
    
    @listen(draft_content)
    def compliance_review(self, state):
        """Perform compliance review using structured LLM call."""
        print("🔍 Performing compliance review...")
        start_time = time.time()
        
        try:
            messages = [{
                "role": "user",
                "content": f"""Review this technical content for compliance and quality:
                
                Content:
                {state.draft}
                
                Review criteria:
                1. Enterprise compliance standards
                2. Technical accuracy
                3. Clarity and readability
                4. Risk assessment (low/medium/high)
                5. Specific improvement recommendations
                
                Provide a structured review with:
                - Compliance score (1-10)
                - Risk level (low/medium/high)
                - List of issues found
                - Specific recommendations
                - Overall feedback"""
            }]
            
            review_response = self.llm.call(messages=messages)
            # Convert Mock objects to strings for testing
            self.state.review_comments = str(review_response) if hasattr(review_response, '__call__') else review_response
            
            # Extract risk level from response
            review_text = str(review_response).lower()
            if "high" in review_text:
                self.state.risk_level = "high"
            elif "medium" in review_text:
                self.state.risk_level = "medium"
            else:
                self.state.risk_level = "low"
            
            self.state.current_stage = "reviewed"
            
            self.performance_metrics["compliance_review"] = time.time() - start_time
            print("✅ Compliance review completed")
            
        except Exception as e:
            print(f"❌ Compliance review failed: {str(e)}")
            self.state.error_log = str(e)
            self.state.review_comments = "Review failed"
            self.state.risk_level = "medium"
        
        return self.state
    
    @listen(compliance_review)
    def risk_assessment(self, state):
        """Assess risk level and apply fixes if needed."""
        print(f"🎯 Risk assessment: {state.risk_level}")
        
        if state.risk_level == "high":
            print("⚠️ High risk detected - applying fixes")
            # Apply compliance fixes inline
            try:
                messages = [{
                    "role": "user",
                    "content": f"""Fix the compliance issues in this content based on the review:
                    
                    Content: {state.draft}
                    Review: {state.review_comments}
                    
                    Requirements:
                    - Address all compliance concerns
                    - Maintain technical accuracy
                    - Ensure enterprise-ready quality
                    - Preserve the practical examples and actionable advice
                    
                    Provide the revised content that addresses all concerns while maintaining quality."""
                }]
                
                response = self.llm.call(messages=messages)
                # Convert Mock objects to strings for testing
                self.state.final_content = str(response) if hasattr(response, '__call__') else response
                self.state.compliance_status = "approved"
                self.state.current_stage = "fixed_and_approved"
                print("✅ Compliance fixes applied")
                
            except Exception as e:
                print(f"❌ Compliance fix failed: {str(e)}")
                self.state.error_log = str(e)
                self.state.final_content = state.draft
                self.state.compliance_status = "approved"
        else:
            print("✅ Low/medium risk - proceeding to finalization")
            self.state.final_content = state.draft
            self.state.compliance_status = "approved"
            self.state.current_stage = "finalized"
        
        return self.state
    
    def compliance_fix(self, state):
        """Fix compliance issues (alias for risk_assessment with high risk handling)."""
        return self.risk_assessment(state)
    
    @listen(risk_assessment)
    def finalize_content(self, state):
        """Finalize content for approved items."""
        print("✅ Finalizing approved content...")
        start_time = time.time()
        
        # Content is already finalized in risk_assessment, just update metrics
        self.performance_metrics["finalization"] = time.time() - start_time
        print("✅ Content finalized")
        
        return self.state
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for comparison."""
        total_time = sum(self.performance_metrics.values())
        
        return {
            "approach": "Flow-Only (Structured)",
            "total_time": total_time,
            "stages": self.performance_metrics,
            "state": self.state.model_dump(),
            "characteristics": [
                "Predictable execution",
                "Clear state transitions",
                "Easy to debug and audit",
                "Deterministic outputs",
                "Limited creative collaboration"
            ]
        }
    
    def kickoff(self):
        """Execute the complete flow workflow."""
        try:
            # Initialize the topic
            self.initialize_topic()
            
            # Create outline
            self.create_outline(self.state)
            
            # Draft content
            self.draft_content(self.state)
            
            # Perform compliance review
            self.compliance_review(self.state)
            
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
            print(f"❌ Flow execution failed: {str(e)}")
            self.state.error_log = str(e)
            return f"Flow execution failed: {str(e)}"
    
    def _save_output_to_file(self):
        """Save flow output to artifacts directory."""
        try:
            from pathlib import Path
            import os
            
            # Ensure artifacts directory exists
            artifacts_dir = Path("artifacts")
            artifacts_dir.mkdir(exist_ok=True)
            
            # Generate output content
            output_content = f"""# Flow-Only Demo Output

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

## Generated at
{self.state.created_at}
"""
            
            # Save to file
            output_file = artifacts_dir / "flow_only_output.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            print(f"📁 Flow output saved to: {output_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save flow output: {str(e)}")
