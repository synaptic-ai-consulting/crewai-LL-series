"""
Lightning Lesson 1: Flows vs Crews Demo Package

This package demonstrates three different approaches to AI orchestration:
1. Crew-only: Autonomous agents with minimal structure
2. Flow-only: Structured workflow with direct LLM calls  
3. Hybrid: Flow orchestration with targeted Crew collaboration

The demo shows when structure beats autonomy in enterprise AI applications.
"""

from .demo_runner import LightningLesson1Demo, main
from .crew_only import CrewOnlyDemo
from .flow_only import FlowOnlyDemo
from .hybrid_flow import HybridFlowDemo
from .state import Lesson1State, GuideOutline, ReviewResult
from .mini_crew import run_writer_reviewer_crew, MiniCrewPerformance

__version__ = "1.0.0"
__author__ = "CrewAI Lightning Lesson Series"

__all__ = [
    "LightningLesson1Demo",
    "CrewOnlyDemo", 
    "FlowOnlyDemo",
    "HybridFlowDemo",
    "Lesson1State",
    "GuideOutline", 
    "ReviewResult",
    "run_writer_reviewer_crew",
    "MiniCrewPerformance",
    "main"
]
