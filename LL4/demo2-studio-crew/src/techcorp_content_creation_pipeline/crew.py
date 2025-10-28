import os
import json
from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	SerperDevTool,
	ScrapeWebsiteTool
)



from pydantic import BaseModel
from jambo import SchemaConverter

@CrewBase
class TechcorpContentCreationPipelineCrew:
    """TechcorpContentCreationPipeline crew"""

    
    @agent
    def content_researcher(self) -> Agent:

        
        return Agent(
            config=self.agents_config["content_researcher"],
            
            
            tools=[
				SerperDevTool()
            ],
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
    def blog_writer(self) -> Agent:

        
        return Agent(
            config=self.agents_config["blog_writer"],
            
            
            tools=[
				ScrapeWebsiteTool()
            ],
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
    def editor(self) -> Agent:

        
        return Agent(
            config=self.agents_config["editor"],
            
            
            tools=[

            ],
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
    def research_topic_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["research_topic_analysis"],
            markdown=True,
            output_json=self._load_response_format("research_topic_analysis"),
            human_input=True  # Enable HITL for this task
        )
    
    @task
    def blog_post_creation(self) -> Task:
        return Task(
            config=self.tasks_config["blog_post_creation"],
            markdown=True,
            human_input=False  # This task doesn't need HITL
        )
    
    @task
    def editorial_review_and_refinement(self) -> Task:
        return Task(
            config=self.tasks_config["editorial_review_and_refinement"],
            markdown=True,
            human_input=True  # Enable HITL for this task
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the TechcorpContentCreationPipeline crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
