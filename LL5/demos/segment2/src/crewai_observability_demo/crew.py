import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	ScrapeWebsiteTool
)





@CrewBase
class CrewaiObservabilityDemoCrew:
    """CrewaiObservabilityDemo crew"""

    
    @agent
    def research_analyst(self) -> Agent:
        
        return Agent(
            config=self.agents_config["research_analyst"],
            
            
            tools=[				ScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def content_synthesizer(self) -> Agent:
        
        return Agent(
            config=self.agents_config["content_synthesizer"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def analyze_crewai_observability_features(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_crewai_observability_features"],
            markdown=False,
            
            
        )
    
    @task
    def draft_executive_memo(self) -> Task:
        return Task(
            config=self.tasks_config["draft_executive_memo"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the CrewaiObservabilityDemo crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            tracing=True,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
