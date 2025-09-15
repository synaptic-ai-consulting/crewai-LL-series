"""
Lightning Lesson 2: Advanced Agent Persona Architecture
Agent implementations using YAML configurations following CrewAI guidelines
"""

import os
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from .config_loader import ConfigLoader


class YAMLAgentFactory:
    """Factory for creating agents from YAML configurations"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            temperature=0.7
        )
    
    def create_agent(self, agent_name: str) -> Agent:
        """Create agent from YAML configuration"""
        agent_config = self.config_loader.get_agent_config(agent_name)
        
        if not agent_config:
            raise ValueError(f"Agent configuration not found: {agent_name}")
        
        # Extract agent parameters
        role = agent_config.get("role", "")
        goal = agent_config.get("goal", "")
        backstory = agent_config.get("backstory", "")
        prompt_file = agent_config.get("prompt_file")
        verbose = agent_config.get("verbose", True)
        allow_delegation = agent_config.get("allow_delegation", False)
        max_iter = agent_config.get("max_iter", 3)
        memory = agent_config.get("memory", True)
        
        # Create agent with or without prompt_file
        agent_params = {
            "role": role,
            "goal": goal,
            "backstory": backstory,
            "llm": self.llm,
            "verbose": verbose,
            "allow_delegation": allow_delegation,
            "max_iter": max_iter,
            "memory": memory
        }
        
        if prompt_file:
            agent_params["prompt_file"] = prompt_file
        
        return Agent(**agent_params)
    
    def create_task(self, task_name: str) -> Task:
        """Create task from YAML configuration"""
        task_config = self.config_loader.get_task_config(task_name)
        
        if not task_config:
            raise ValueError(f"Task configuration not found: {task_name}")
        
        # Extract task parameters
        description = task_config.get("description", "")
        expected_output = task_config.get("expected_output", "")
        context = task_config.get("context", "")
        agent_name = task_config.get("agent")
        
        # Create task
        task_params = {
            "description": description,
            "expected_output": expected_output,
            "context": context
        }
        
        # Add agent if specified
        if agent_name:
            agent = self.create_agent(agent_name)
            task_params["agent"] = agent
        
        return Task(**task_params)
    
    def create_crew(self, crew_name: str) -> Crew:
        """Create crew from YAML configuration"""
        crew_config = self.config_loader.get_crew_config(crew_name)
        
        if not crew_config:
            raise ValueError(f"Crew configuration not found: {crew_name}")
        
        # Extract crew parameters
        agent_names = crew_config.get("agents", [])
        task_names = crew_config.get("tasks", [])
        process = crew_config.get("process", "sequential")
        verbose = crew_config.get("verbose", True)
        memory = crew_config.get("memory", True)
        
        # Create agents and tasks
        agents = [self.create_agent(agent_name) for agent_name in agent_names]
        tasks = [self.create_task(task_name) for task_name in task_names]
        
        return Crew(
            agents=agents,
            tasks=tasks,
            process=process,
            verbose=verbose,
            memory=memory
        )


class LightningLesson2Agents:
    """Main class for managing Lightning Lesson 2 agents and crews"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_loader = ConfigLoader(config_dir)
        self.factory = YAMLAgentFactory(self.config_loader)
    
    def create_comparison_agents(self) -> Dict[str, Agent]:
        """Create default vs persona-engineered agents for comparison"""
        comparison_configs = self.config_loader.get_comparison_configs()
        
        return {
            "default": self.factory.create_agent(comparison_configs["default_agent"]),
            "persona": self.factory.create_agent(comparison_configs["persona_agent"])
        }
    
    def create_all_personas(self) -> Dict[str, Agent]:
        """Create all persona-engineered agents"""
        persona_configs = self.config_loader.get_persona_showcase_configs()
        
        agents = {}
        for persona_type, config in persona_configs.items():
            agents[persona_type] = self.factory.create_agent(config["agent"])
        
        return agents
    
    def create_comparison_crew(self) -> Crew:
        """Create crew for before/after comparison demo"""
        return self.factory.create_crew("default_marketing_crew")
    
    def create_persona_crew(self) -> Crew:
        """Create crew for persona-engineered demo"""
        return self.factory.create_crew("persona_marketing_crew")
    
    def create_persona_showcase_crews(self) -> Dict[str, Crew]:
        """Create crews for persona showcase demo"""
        crews = {}
        persona_configs = self.config_loader.get_persona_showcase_configs()
        
        for persona_type, config in persona_configs.items():
            crew_name = f"{persona_type}_crew"
            crews[persona_type] = self.factory.create_crew(crew_name)
        
        return crews
    
    def get_available_agents(self) -> list:
        """Get list of available agent names"""
        return list(self.config_loader.get_all_agents().keys())
    
    def get_available_tasks(self) -> list:
        """Get list of available task names"""
        return list(self.config_loader.get_all_tasks().keys())
    
    def get_available_crews(self) -> list:
        """Get list of available crew names"""
        return list(self.config_loader.get_all_crews().keys())
    
    def validate_configurations(self) -> Dict[str, list]:
        """Validate all configurations"""
        return self.config_loader.validate_configs()
