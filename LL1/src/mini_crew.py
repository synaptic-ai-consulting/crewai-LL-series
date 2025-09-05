"""
Mini crew implementation for hybrid approach.
Provides targeted collaboration for complex reasoning tasks.
"""

import time
from typing import Tuple, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from crewai import LLM
try:
    from .state import Lesson1State, GuideOutline, ReviewResult
except ImportError:
    from state import Lesson1State, GuideOutline, ReviewResult


def run_writer_reviewer_crew(topic: str, outline: str, audience: str) -> Tuple[str, str, str]:
    """
    Execute a focused crew for draft and review collaboration.
    
    Args:
        topic: The technical topic to write about
        outline: The structured outline to follow
        audience: Target audience for the content
        
    Returns:
        Tuple of (draft_content, review_comments, risk_level)
    """
    print("🤝 Starting mini crew collaboration...")
    start_time = time.time()
    
    # Create specialized agents
    writer = Agent(
        role="Technical Writer",
        goal="Create comprehensive, accurate technical content that educates and engages the target audience",
        backstory="""You are a senior technical writer with 15+ years of experience in enterprise 
        software documentation. You excel at breaking down complex technical concepts into clear, 
        actionable content. You have a conversational writing style and always include practical 
        examples that resonate with your target audience.""",
        verbose=True,
        allow_delegation=False
    )
    
    reviewer = Agent(
        role="Compliance Specialist",
        goal="Ensure all content meets enterprise compliance standards and provides specific, actionable feedback",
        backstory="""You are a senior compliance officer with expertise in enterprise security 
        standards, regulatory requirements, and content quality assurance. You are thorough, 
        detail-oriented, and always prioritize risk mitigation. You provide specific, actionable 
        feedback for improvement and assess risk levels accurately.""",
        verbose=True,
        allow_delegation=False
    )
    
    # Create focused tasks
    write_task = Task(
        description=f"""Write a comprehensive technical section on '{topic}' for {audience} using this outline:

        {outline}
        
        Requirements:
        - Write 3 well-structured paragraphs (4-6 sentences each)
        - Include practical examples and best practices
        - Use clear, professional language appropriate for {audience}
        - Ensure content is immediately actionable
        - Follow the outline structure but expand with detailed explanations
        
        Focus on making complex concepts accessible while maintaining technical accuracy.""",
        expected_output="Complete technical section with clear explanations, practical examples, and actionable advice",
        agent=writer,
        context=[]
    )
    
    review_task = Task(
        description=f"""Review the technical content for compliance, quality, and enterprise readiness:

        Review Criteria:
        1. Enterprise compliance standards adherence
        2. Technical accuracy and completeness
        3. Clarity and readability for {audience}
        4. Risk assessment (low/medium/high)
        5. Specific improvement recommendations
        
        Provide detailed feedback including:
        - Compliance score (1-10)
        - Risk level assessment (low/medium/high)
        - Specific issues found
        - Concrete recommendations for improvement
        - Overall quality assessment""",
        expected_output="Detailed review with compliance score, risk assessment, specific issues, and actionable recommendations",
        agent=reviewer,
        context=[write_task]
    )
    
    # Execute crew
    crew = Crew(
        agents=[writer, reviewer],
        tasks=[write_task, review_task],
        process=Process.sequential,
        verbose=True,
        memory=True
    )
    
    try:
        result = crew.kickoff()
        
        # Extract structured outputs
        draft = write_task.output.raw if write_task.output else ""
        review = review_task.output.raw if review_task.output else ""
        
        # Determine risk level from review
        review_text = str(review).lower()
        if "high" in review_text and "risk" in review_text:
            risk = "high"
        elif "medium" in review_text and "risk" in review_text:
            risk = "medium"
        else:
            risk = "low"
        
        execution_time = time.time() - start_time
        print(f"✅ Mini crew completed in {execution_time:.2f}s")
        
        return draft, review, risk
        
    except Exception as e:
        print(f"❌ Mini crew execution failed: {str(e)}")
        return f"Draft content for {topic}", f"Review failed: {str(e)}", "medium"


class MiniCrewPerformance:
    """Track performance metrics for mini crew operations."""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.execution_time: Optional[float] = None
        self.memory_usage: Optional[float] = None
        self.api_calls: int = 0
        self.tokens_used: int = 0
        self.success: bool = False
        self.metrics: Dict[str, Any] = {}
    
    def start_timing(self):
        """Start timing execution."""
        self.start_time = time.time()
    
    def end_timing(self):
        """End timing execution."""
        if self.start_time is not None:
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
        else:
            self.execution_time = None
    
    def track_api_call(self, tokens: int):
        """Track API call and token usage."""
        self.api_calls += 1
        self.tokens_used += tokens  # Allow negative tokens for testing
    
    def mark_success(self):
        """Mark execution as successful."""
        self.success = True
    
    def mark_failure(self):
        """Mark execution as failed."""
        self.success = False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "execution_time": self.execution_time,
            "api_calls": self.api_calls,
            "tokens_used": self.tokens_used,
            "success": self.success,
            "memory_usage": self.memory_usage
        }
    
    def reset_metrics(self):
        """Reset all metrics to initial state."""
        self.__init__()
    
    def reset(self):
        """Reset all metrics to initial state (alias for reset_metrics)."""
        self.reset_metrics()
    
    def track_execution(self, topic: str, execution_time: float, success: bool):
        """Track execution metrics."""
        self.metrics[topic] = {
            "execution_time": execution_time,
            "success": success,
            "timestamp": time.time()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {"message": "No executions tracked"}
        
        total_executions = len(self.metrics)
        successful_executions = sum(1 for m in self.metrics.values() if m["success"])
        avg_time = sum(m["execution_time"] for m in self.metrics.values()) / total_executions
        
        return {
            "total_executions": total_executions,
            "success_rate": successful_executions / total_executions,
            "average_execution_time": avg_time,
            "details": self.metrics
        }
