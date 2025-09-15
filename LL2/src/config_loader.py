"""
Lightning Lesson 2: YAML Configuration Loader
Loads CrewAI configurations from YAML files following official guidelines
"""

import os
import yaml
from typing import Dict, Any, List
from pathlib import Path


class ConfigLoader:
    """Loads and manages CrewAI configurations from YAML files"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.agents_config = {}
        self.tasks_config = {}
        self.crews_config = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all configuration files"""
        try:
            # Load agents configuration
            agents_file = self.config_dir / "agents.yaml"
            if agents_file.exists():
                with open(agents_file, 'r', encoding='utf-8') as f:
                    self.agents_config = yaml.safe_load(f)
            
            # Load tasks configuration
            tasks_file = self.config_dir / "tasks.yaml"
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks_config = yaml.safe_load(f)
            
            # Load crews configuration
            crews_file = self.config_dir / "crews.yaml"
            if crews_file.exists():
                with open(crews_file, 'r', encoding='utf-8') as f:
                    self.crews_config = yaml.safe_load(f)
                    
        except Exception as e:
            print(f"Error loading configurations: {e}")
            raise
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return self.agents_config.get(agent_name, {})
    
    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """Get configuration for a specific task"""
        return self.tasks_config.get(task_name, {})
    
    def get_crew_config(self, crew_name: str) -> Dict[str, Any]:
        """Get configuration for a specific crew"""
        return self.crews_config.get(crew_name, {})
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent configurations"""
        return self.agents_config
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all task configurations"""
        return self.tasks_config
    
    def get_all_crews(self) -> Dict[str, Dict[str, Any]]:
        """Get all crew configurations"""
        return self.crews_config
    
    def get_agents_by_type(self, agent_type: str) -> List[str]:
        """Get agent names by type (e.g., 'marketing', 'legal', 'technical')"""
        agents = []
        for agent_name, config in self.agents_config.items():
            if agent_type in agent_name.lower():
                agents.append(agent_name)
        return agents
    
    def get_tasks_by_agent(self, agent_name: str) -> List[str]:
        """Get task names that use a specific agent"""
        tasks = []
        for task_name, config in self.tasks_config.items():
            if config.get('agent') == agent_name:
                tasks.append(task_name)
        return tasks
    
    def get_comparison_configs(self) -> Dict[str, Any]:
        """Get configurations for before/after comparison demo"""
        return {
            "default_agent": "default_marketing_agent",
            "persona_agent": "comparison_marketing_agent",
            "default_task": "comparison_email_task",
            "persona_task": "comparison_persona_task"
        }
    
    def get_persona_showcase_configs(self) -> Dict[str, List[str]]:
        """Get configurations for persona showcase demo"""
        return {
            "legal": {
                "agent": "legal_compliance_agent",
                "tasks": self.get_tasks_by_agent("legal_compliance_agent")
            },
            "marketing": {
                "agent": "creative_marketing_agent", 
                "tasks": self.get_tasks_by_agent("creative_marketing_agent")
            },
            "technical": {
                "agent": "technical_lead_agent",
                "tasks": self.get_tasks_by_agent("technical_lead_agent")
            }
        }
    
    def validate_configs(self) -> Dict[str, List[str]]:
        """Validate configuration consistency"""
        errors = []
        warnings = []
        
        # Check agent references in tasks
        for task_name, task_config in self.tasks_config.items():
            agent_name = task_config.get('agent')
            if agent_name and agent_name not in self.agents_config:
                errors.append(f"Task '{task_name}' references unknown agent '{agent_name}'")
        
        # Check agent references in crews
        for crew_name, crew_config in self.crews_config.items():
            for agent_name in crew_config.get('agents', []):
                if agent_name not in self.agents_config:
                    errors.append(f"Crew '{crew_name}' references unknown agent '{agent_name}'")
            
            for task_name in crew_config.get('tasks', []):
                if task_name not in self.tasks_config:
                    errors.append(f"Crew '{crew_name}' references unknown task '{task_name}'")
        
        # Check for missing prompt files
        for agent_name, agent_config in self.agents_config.items():
            prompt_file = agent_config.get('prompt_file')
            if prompt_file and not os.path.exists(prompt_file):
                warnings.append(f"Agent '{agent_name}' references missing prompt file '{prompt_file}'")
        
        return {"errors": errors, "warnings": warnings}
    
    def reload_configs(self):
        """Reload all configuration files"""
        self._load_configs()
    
    def save_config(self, config_type: str, config_name: str, config_data: Dict[str, Any]):
        """Save configuration data to YAML file"""
        config_file = self.config_dir / f"{config_type}.yaml"
        
        # Load existing config
        if config_type == "agents":
            config = self.agents_config
        elif config_type == "tasks":
            config = self.tasks_config
        elif config_type == "crews":
            config = self.crews_config
        else:
            raise ValueError(f"Unknown config type: {config_type}")
        
        # Update config
        config[config_name] = config_data
        
        # Save to file
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Reload configs
        self._load_configs()
