"""
Crew-only baseline approach for Lightning Lesson 1 demo.
Demonstrates autonomous agents with minimal structure.
"""

import time
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process
try:
    from .state import Lesson1State, GuideOutline, ReviewResult
except ImportError:
    from state import Lesson1State, GuideOutline, ReviewResult


class CrewOnlyDemo:
    """Crew-only implementation showing autonomous agent behavior."""
    
    def __init__(self, topic: str, audience: str):
        self.state = Lesson1State(topic=topic, audience=audience)
        self.performance_metrics: Dict[str, float] = {}
    
    def run_demo(self) -> Lesson1State:
        """Execute the crew-only demo workflow."""
        print("🚀 Starting Crew-Only Demo (Autonomous Approach)")
        print(f"Topic: {self.state.topic}")
        print(f"Audience: {self.state.audience}")
        print("-" * 50)
        
        # Stage 1: Create agents
        start_time = time.time()
        self._create_agents()
        self.performance_metrics["agent_creation"] = time.time() - start_time
        
        # Stage 2: Create composite task
        start_time = time.time()
        self._create_tasks()
        self.performance_metrics["task_creation"] = time.time() - start_time
        
        # Stage 3: Execute crew
        start_time = time.time()
        self._execute_crew()
        self.performance_metrics["crew_execution"] = time.time() - start_time
        
        # Stage 4: Process results
        start_time = time.time()
        self._process_results()
        self.performance_metrics["result_processing"] = time.time() - start_time
        
        self.state.performance_metrics = self.performance_metrics
        self.state.current_stage = "completed"
        
        # Save output to artifacts directory
        self._save_output_to_file()
        
        return self.state
    
    def _create_agents(self):
        """Create autonomous agents with minimal constraints."""
        print("📝 Creating autonomous agents...")
        
        self.writer = Agent(
            role="Technical Writer",
            goal="Write comprehensive, engaging technical content that educates and informs",
            backstory="""You are a senior technical writer with 15+ years of experience 
            in enterprise software documentation. You excel at breaking down complex 
            technical concepts into clear, actionable content. You have a conversational 
            writing style and always include practical examples.""",
            verbose=True,
            allow_delegation=False
        )
        
        self.reviewer = Agent(
            role="Compliance Specialist",
            goal="Ensure all content meets enterprise compliance and quality standards",
            backstory="""You are a senior compliance officer with expertise in enterprise 
            security standards, regulatory requirements, and content quality assurance. 
            You are thorough, detail-oriented, and always prioritize risk mitigation. 
            You provide specific, actionable feedback for improvement.""",
            verbose=True,
            allow_delegation=False
        )
        
        print("✅ Agents created successfully")
    
    def _create_tasks(self):
        """Create composite task for autonomous execution."""
        print("📋 Creating composite task...")
        
        # Single composite task - shows potential for chaos
        self.composite_task = Task(
            description=f"""
            Create a comprehensive technical guide section on '{self.state.topic}' 
            for {self.state.audience}.
            
            Requirements:
            1. Write a detailed 3-paragraph section with clear explanations
            2. Include practical examples and best practices
            3. Ensure content is enterprise-ready and compliant
            4. Review the content for quality and compliance issues
            5. Provide specific recommendations for improvement
            
            The content should be immediately usable by {self.state.audience} 
            in their daily work.
            """,
            expected_output="""A complete technical guide section that includes:
            - Well-structured content with clear explanations
            - Practical examples and best practices
            - Compliance review with specific recommendations
            - Risk assessment and quality metrics""",
            agent=self.writer,
            context=[],
            output_file="artifacts/crew_only_output.md"
        )
        
        print("✅ Composite task created")
    
    def _execute_crew(self):
        """Execute the crew with minimal orchestration."""
        print("🤖 Executing autonomous crew...")
        print("⚠️  Note: This approach can be unpredictable and hard to control")
        
        self.crew = Crew(
            agents=[self.writer, self.reviewer],
            tasks=[self.composite_task],
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True
        )
        
        try:
            result = self.crew.kickoff()
            self.crew_result = result
            print("✅ Crew execution completed")
        except Exception as e:
            print(f"❌ Crew execution failed: {str(e)}")
            self.state.error_log = str(e)
            self.crew_result = None
    
    def _process_results(self):
        """Process and extract results from crew execution."""
        print("📊 Processing results...")
        
        if self.crew_result:
            # Extract content from the composite task
            self.state.draft = str(self.crew_result)
            self.state.final_content = str(self.crew_result)
            self.state.compliance_status = "completed"
            self.state.current_stage = "completed"
            
            # Simulate review extraction (in real scenario, this would be more sophisticated)
            self.state.review_comments = "Content reviewed by autonomous crew"
            self.state.risk_level = "medium"  # Default for autonomous approach
            
            print("✅ Results processed successfully")
        else:
            print("❌ No results to process")
            self.state.compliance_status = "failed"
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for comparison."""
        total_time = sum(self.performance_metrics.values())
        
        return {
            "approach": "Crew-Only (Autonomous)",
            "total_time": total_time,
            "stages": self.performance_metrics,
            "state": self.state.model_dump(),
            "characteristics": [
                "High autonomy",
                "Variable output quality",
                "Difficult to predict timing",
                "Limited audit trail",
                "Potential for circular dependencies"
            ]
        }
    
    def _save_output_to_file(self):
        """Save crew output to artifacts directory."""
        try:
            from pathlib import Path
            import os
            
            # Ensure artifacts directory exists
            artifacts_dir = Path("artifacts")
            artifacts_dir.mkdir(exist_ok=True)
            
            # Generate output content
            output_content = f"""# Crew-Only Demo Output

## Topic: {self.state.topic}
## Audience: {self.state.audience}

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
            output_file = artifacts_dir / "crew_only_output.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            print(f"📁 Crew output saved to: {output_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save crew output: {str(e)}")
