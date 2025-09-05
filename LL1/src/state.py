"""
State management for Lightning Lesson 1 demo.
Defines the shared state model used across all three approaches.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class Lesson1State(BaseModel):
    """Shared state model for all demo approaches."""
    
    # Input parameters
    topic: str = ""
    audience: str = ""
    
    # Content generation
    outline: Optional[str] = None
    draft: Optional[str] = None
    review_comments: Optional[str] = None
    risk_level: Optional[str] = None
    final_content: Optional[str] = None
    
    # Workflow control
    compliance_status: str = "pending"
    current_stage: str = "initialized"
    
    # Metadata
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    error_log: Optional[str] = None
    performance_metrics: Dict[str, float] = {}
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom JSON serialization with datetime handling."""
        import json
        data = self.model_dump(**kwargs)
        return json.dumps(data, default=str)


class GuideOutline(BaseModel):
    """Structured output format for outline generation."""
    
    title: str
    introduction: str
    key_points: list[str]
    conclusion: str
    
    def to_markdown(self) -> str:
        """Convert outline to markdown format."""
        md = f"# {self.title}\n\n"
        md += f"## Introduction\n{self.introduction}\n\n"
        md += "## Key Points\n"
        for i, point in enumerate(self.key_points, 1):
            md += f"{i}. {point}\n"
        md += f"\n## Conclusion\n{self.conclusion}\n"
        return md


class ReviewResult(BaseModel):
    """Structured output format for review results."""
    
    compliance_score: int  # 1-10
    risk_level: str  # low, medium, high
    issues: list[str]
    recommendations: list[str]
    overall_feedback: str
    
    def to_text(self) -> str:
        """Convert review to readable text format."""
        text = f"Compliance Score: {self.compliance_score}/10\n"
        text += f"Risk Level: {self.risk_level.upper()}\n\n"
        
        if self.issues:
            text += "Issues Found:\n"
            for issue in self.issues:
                text += f"- {issue}\n"
            text += "\n"
        
        if self.recommendations:
            text += "Recommendations:\n"
            for rec in self.recommendations:
                text += f"- {rec}\n"
            text += "\n"
        
        text += f"Overall Feedback: {self.overall_feedback}\n"
        return text
