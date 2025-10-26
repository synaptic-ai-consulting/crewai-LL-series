"""
Demo 1: Open Source HITL - Basic Human-in-the-Loop
Simple demonstration of human_input=True in open source CrewAI
"""

import os
import sys
from crewai import Crew, Agent, Task
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_agents():
    """Load agents from YAML configuration."""
    with open('config/agents.yaml', 'r') as f:
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

def create_simple_hitl_task(agent):
    """Create a simple task with human input enabled."""
    return Task(
        description="Write a brief summary of the latest AI trends in 2-3 paragraphs. Focus on the most impactful developments.",
        expected_output="A concise 2-3 paragraph summary of current AI trends with key insights",
        agent=agent,
        human_input=True  # This enables HITL in open source CrewAI
    )

def run_opensource_hitl_demo():
    """Run Demo 1: Open Source HITL."""
    print("🚀 Demo 1: Open Source HITL - Basic Human-in-the-Loop")
    print("=" * 60)
    print("This demo shows how human_input=True works in open source CrewAI")
    print("The execution will pause and wait for human feedback in the console")
    print()
    
    # Load configuration
    agents = load_agents()
    researcher = agents['content_researcher']
    
    # Create a simple HITL task
    hitl_task = create_simple_hitl_task(researcher)
    
    print(f"👤 Agent: {researcher.role}")
    print(f"📋 Task: {hitl_task.description}")
    print(f"🎯 Expected Output: {hitl_task.expected_output}")
    print(f"🤖 Human Input Enabled: {hitl_task.human_input}")
    print()
    
    # Create crew
    crew = Crew(
        agents=[researcher],
        tasks=[hitl_task],
        verbose=True
    )
    
    print("💡 Key Points About Open Source HITL:")
    print("   • human_input=True pauses execution for console input")
    print("   • No webhook support - only interactive/CLI")
    print("   • Human provides feedback via console prompt")
    print("   • Execution resumes after human input")
    print()
    
    try:
        print("🚀 Starting crew execution...")
        print("⏸️  Execution will pause when human input is required")
        print()
        
        # This will actually pause for human input in open source CrewAI
        result = crew.kickoff(
            inputs={"topic": "AI Trends 2025"}
        )
        
        print("\n✅ Crew execution completed!")
        print(f"📊 Result type: {type(result)}")
        
        if hasattr(result, 'raw'):
            print(f"📝 Raw output length: {len(str(result.raw))}")
            print("\n📋 Final Output:")
            print("-" * 40)
            print(str(result.raw))
            print("-" * 40)
        
        return result
    
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
        return None
    except Exception as e:
        print(f"❌ Error during crew execution: {str(e)}")
        raise

def main():
    """Main function for Demo 1."""
    print("🎯 Demo 1: Open Source HITL")
    print("This demo shows basic human_input=True functionality")
    print("in open source CrewAI (console-based HITL)")
    print()
    
    try:
        result = run_opensource_hitl_demo()
        if result:
            print("\n🎯 Demo 1 completed successfully!")
            print("💡 This demonstrates basic HITL in open source CrewAI")
            print("   Next: Demo 2 will show enterprise webhook HITL")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
