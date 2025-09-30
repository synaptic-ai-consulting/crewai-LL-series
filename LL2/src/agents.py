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
        """Create agent from YAML configuration with prompt customization support"""
        agent_config = self.config_loader.get_agent_config(agent_name)
        
        if not agent_config:
            raise ValueError(f"Agent configuration not found: {agent_name}")
        
        # Extract agent parameters
        role = agent_config.get("role", "")
        goal = agent_config.get("goal", "")
        backstory = agent_config.get("backstory", "")
        verbose = agent_config.get("verbose", True)
        allow_delegation = agent_config.get("allow_delegation", False)
        max_iter = agent_config.get("max_iter", 3)
        memory = agent_config.get("memory", True)
        
        # Extract prompt customization parameters
        system_template = agent_config.get("system_template")
        prompt_template = agent_config.get("prompt_template")
        response_template = agent_config.get("response_template")
        
        # Load custom templates from files if specified
        if system_template and system_template.endswith('.txt'):
            # Resolve relative path from project root
            if not os.path.isabs(system_template):
                # Assume we're in LL2 directory, so prompts/ is relative to current working directory
                system_template = self._load_template_file(system_template)
            else:
                system_template = self._load_template_file(system_template)
        
        # Create agent with custom templates
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
        
        # Add custom templates if provided
        if system_template:
            agent_params["system_template"] = system_template
        if prompt_template:
            agent_params["prompt_template"] = prompt_template
        if response_template:
            agent_params["response_template"] = response_template
        
        return Agent(**agent_params)
    
    def _load_template_file(self, template_path: str) -> str:
        """Load template content from file"""
        try:
            print(f"Debug: Loading template from: {template_path}")
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"Debug: Successfully loaded template, length: {len(content)}")
                return content
        except FileNotFoundError:
            print(f"Warning: Template file not found: {template_path}")
            return None
        except Exception as e:
            print(f"Warning: Error loading template file {template_path}: {e}")
            return None
    
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
        """Create crew from YAML configuration with prompt customization support"""
        crew_config = self.config_loader.get_crew_config(crew_name)
        
        if not crew_config:
            raise ValueError(f"Crew configuration not found: {crew_name}")
        
        # Extract crew parameters
        agent_names = crew_config.get("agents", [])
        task_names = crew_config.get("tasks", [])
        process = crew_config.get("process", "sequential")
        verbose = crew_config.get("verbose", True)
        memory = crew_config.get("memory", True)
        prompt_file = crew_config.get("prompt_file")
        
        # Create agents and tasks
        agents = [self.create_agent(agent_name) for agent_name in agent_names]
        tasks = [self.create_task(task_name) for task_name in task_names]
        
        # Create crew with optional prompt_file
        crew_params = {
            "agents": agents,
            "tasks": tasks,
            "process": process,
            "verbose": verbose,
            "memory": memory
        }
        
        if prompt_file:
            crew_params["prompt_file"] = prompt_file
        
        return Crew(**crew_params)


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
    
    def create_prompt_inspection_agents(self) -> Dict[str, Agent]:
        """Create agents for prompt inspection demo"""
        # Create default agent (no tools)
        default_agent = self.factory.create_agent("prompt_inspection_default")

        # Create agent with tools to show different injection behavior
        tools_agent = self.factory.create_agent("prompt_inspection_with_tools")
        
        # Add some basic tools to the tools agent to demonstrate different injection
        try:
            from crewai_tools import DirectoryReadTool, FileReadTool
            tools_agent.tools = [DirectoryReadTool(), FileReadTool()]
        except ImportError:
            # If crewai_tools is not available, create a mock tool
            class MockTool:
                def __init__(self, name):
                    self.name = name
                def __str__(self):
                    return self.name
            
            tools_agent.tools = [MockTool("file_reader"), MockTool("directory_scanner")]
        
        return {
            "default": default_agent,
            "with_tools": tools_agent
        }
    
    def create_customization_demo_crews(self) -> Dict[str, Crew]:
        """Create crews for different customization approaches"""
        return {
            "crew_customization": self.factory.create_crew("crew_customization_demo"),
            "llama_demo": self.factory.create_crew("llama_demo_crew"),
            "prompt_inspection": self.factory.create_crew("prompt_inspection_crew")
        }
    
    def inspect_prompts(self, agent: Agent) -> Dict[str, str]:
        """Inspect what CrewAI actually sends to the LLM using the Prompts utility"""
        try:
            from crewai.utilities.prompts import Prompts
            from crewai import Task
            
            # Create a sample task for prompt generation
            task = Task(
                description="Sample task for prompt inspection",
                expected_output="Sample output for inspection",
                agent=agent
            )
            
            # Create the prompt generator using CrewAI's utility
            prompt_generator = Prompts(
                agent=agent,
                has_tools=len(agent.tools) > 0,
                use_system_prompt=agent.use_system_prompt
            )
            
            # Generate and inspect the actual prompt
            generated_prompt = prompt_generator.task_execution()
            
            # Extract agent info
            agent_info = {
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "has_tools": len(agent.tools) > 0,
                "use_system_prompt": agent.use_system_prompt
            }
            
            # Extract the system prompt content
            system_prompt = ""
            user_prompt = ""
            
            if isinstance(generated_prompt, dict):
                system_prompt = generated_prompt.get("system", "")
                user_prompt = generated_prompt.get("user", "")
                if not system_prompt and "prompt" in generated_prompt:
                    system_prompt = generated_prompt["prompt"]
            elif isinstance(generated_prompt, str):
                system_prompt = generated_prompt
            
            return {
                "agent_info": agent_info,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "task_context": {
                    "description": task.description,
                    "expected_output": task.expected_output
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
