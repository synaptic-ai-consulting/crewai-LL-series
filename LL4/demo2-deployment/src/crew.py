"""
Demo 2: Enterprise Webhook HITL - Full Content Pipeline
Deployment-ready version for CrewAI AMP
"""

import os
import yaml
from crewai import Crew, Agent, Task
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_agents():
    """Load agents from YAML configuration."""
    with open('../config/agents.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    agents = {}
    for agent_id, agent_config in config['agents'].items():
        # Handle environment variable substitution
        llm_model = agent_config.get('llm', 'openai')
        if llm_model.startswith('${') and llm_model.endswith('}'):
            env_var = llm_model[2:-1]  # Remove ${ and }
            llm_model = os.getenv(env_var, 'gpt-3.5-turbo')
        
        agents[agent_id] = Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            verbose=agent_config.get('verbose', True),
            llm=llm_model
        )
    
    return agents

def load_tasks(agents):
    """Load tasks from YAML configuration."""
    with open('../config/tasks.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tasks = {}
    for task_id, task_config in config['tasks'].items():
        agent = agents.get(task_config['agent'])
        if not agent:
            raise ValueError(f"Agent {task_config['agent']} not found")
        
        tasks[task_id] = Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=agent,
            human_input=task_config.get('human_input', False)
        )
    
    return tasks

# Load configuration
agents = load_agents()
tasks = load_tasks(agents)

# Get all agents for the content pipeline
researcher = agents['content_researcher']
writer = agents['blog_writer']
editor = agents['editor']

# Get all tasks for the content pipeline
research_task = tasks['research_task']
writing_task = tasks['writing_task']
editing_task = tasks['editing_task']

# Create crew with all agents and tasks
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    verbose=True
)

# This is what will be deployed and executed
if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "AI Business Automation"})
    print("Crew execution completed!")
    print(f"Result: {result}")
