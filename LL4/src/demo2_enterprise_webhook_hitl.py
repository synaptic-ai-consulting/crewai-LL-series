"""
Demo 2: Enterprise Webhook HITL - Advanced Human-in-the-Loop
Content Research Approval with Webhook Integration and UI Feedback
"""

import os
import sys
import time
import requests
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

def load_tasks(agents):
    """Load tasks from YAML configuration."""
    with open('config/tasks.yaml', 'r') as f:
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

def simulate_hitl_pause_and_webhook(result):
    """Simulate HITL pause and send webhook notification to Flask server."""
    print("⏸️  HITL PAUSE: Task completed, waiting for human feedback...")
    print("📤 Sending webhook notification to Flask server...")
    
    webhook_url = "http://localhost:5000/hitl"
    webhook_token = os.getenv('WEBHOOK_SECRET_TOKEN', 'demo-secret-token')
    
    # Prepare webhook payload
    task_output = str(result.raw) if hasattr(result, 'raw') else str(result)
    print(f"📝 Task output length: {len(task_output)} characters")
    
    payload = {
        "execution_id": "demo-execution-123",
        "task_id": "research_task",
        "task_output": task_output,
        "agent_role": "Content Researcher",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    headers = {
        "Authorization": f"Bearer {webhook_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📤 Sending webhook notification to {webhook_url}")
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("✅ Webhook notification sent successfully!")
            print("🌐 Check the web UI at http://localhost:5000/demo1")
            print("💬 Provide feedback in the web UI to continue...")
            
            # Simulate waiting for human feedback
            print("\n" + "="*60)
            print("🤖 SIMULATED HITL PAUSE - Waiting for Human Feedback")
            print("="*60)
            print("In enterprise CrewAI, execution would pause here")
            print("and wait for human feedback via webhook resume API")
            print("\n📋 Task Output Preview:")
            print("-" * 40)
            print(task_output[:500] + "..." if len(task_output) > 500 else task_output)
            print("-" * 40)
            print("\n💡 This demonstrates the HITL concept:")
            print("   1. Agent completes task")
            print("   2. System pauses execution")
            print("   3. Human reviews output via web UI")
            print("   4. Human provides feedback")
            print("   5. System resumes with feedback context")
            print("\n⏳ Simulating human review process...")
            time.sleep(3)  # Simulate human review time
            print("✅ Human feedback received - continuing execution...")
            
        else:
            print(f"⚠️ Webhook notification failed: {response.status_code}")
            print("💡 Make sure the webhook server is running on port 5000")
            print("🔄 Continuing with simulated HITL pause...")
            simulate_console_hitl_pause(task_output)
    
    except requests.exceptions.ConnectionError:
        print("⚠️ Could not connect to webhook server")
        print("💡 Make sure to run: python run_demo.py --demo 2")
        print("   This will start both the webhook server and the demo")
        print("🔄 Continuing with simulated HITL pause...")
        simulate_console_hitl_pause(task_output)
    
    except Exception as e:
        print(f"⚠️ Webhook notification error: {str(e)}")
        print("💡 The demo will continue without webhook integration")
        print("🔄 Continuing with simulated HITL pause...")
        simulate_console_hitl_pause(task_output)

def simulate_console_hitl_pause(task_output):
    """Simulate HITL pause with console interaction when webhook unavailable."""
    print("\n" + "="*60)
    print("🤖 SIMULATED HITL PAUSE - Console Interaction")
    print("="*60)
    print("In enterprise CrewAI, execution would pause here")
    print("and wait for human feedback via webhook resume API")
    print("\n📋 Task Output Preview:")
    print("-" * 40)
    print(task_output[:500] + "..." if len(task_output) > 500 else task_output)
    print("-" * 40)
    print("\n💡 This demonstrates the HITL concept:")
    print("   1. Agent completes task")
    print("   2. System pauses execution")
    print("   3. Human reviews output")
    print("   4. Human provides feedback")
    print("   5. System resumes with feedback context")
    print("\n🤔 Simulated human review process...")
    print("   (In real HITL, human would review via web UI)")
    time.sleep(2)  # Simulate human review time
    print("✅ Human feedback received - continuing execution...")

def run_enterprise_webhook_hitl_demo():
    """Run Demo 2: Enterprise Webhook HITL."""
    print("🚀 Demo 2: Enterprise Webhook HITL - Advanced Human-in-the-Loop")
    print("=" * 60)
    
    # Load configuration
    agents = load_agents()
    tasks = load_tasks(agents)
    
    # Get the researcher agent and research task
    researcher = agents['content_researcher']
    research_task = tasks['research_task']
    
    print(f"👤 Agent: {researcher.role}")
    print(f"📋 Task: {research_task.description[:100]}...")
    print(f"🎯 Expected Output: {research_task.expected_output}")
    print(f"🤖 Human Input Enabled: {research_task.human_input}")
    print()
    
    # Create crew
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True
    )
    
    print("💡 This demo shows enterprise webhook HITL capabilities")
    print("   Requires CrewAI AMP (enterprise) account")
    print("   Features: Real webhooks, UI integration, pause/resume")
    print()
    
    try:
        # Run crew execution
        print("🚀 Kicking off crew execution...")
        print("💡 Note: In enterprise CrewAI, this would pause for human input")
        print("   when it encounters a task with human_input=True")
        print()
        
        # Try enterprise webhook HITL first, fallback to simulation
        try:
            # Enterprise webhook HITL (requires CrewAI AMP)
            result = crew.kickoff(
                inputs={"topic": "AI Business Automation"},
                humanInputWebhook={
                    "url": "http://localhost:5000/hitl",
                    "authentication": {
                        "strategy": "bearer",
                        "token": "demo-secret-token"
                    }
                }
            )
            print("✅ Enterprise webhook HITL configured successfully!")
            print("🎯 CrewAI will pause execution and send webhook notifications")
            
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                print("⚠️ Enterprise webhook HITL not available")
                print("💡 Falling back to simulation mode")
                print("🔄 Run with CrewAI AMP for real webhook HITL")
                
                # Fallback: Run crew normally and simulate webhook
                result = crew.kickoff(
                    inputs={"topic": "AI Business Automation"}
                )
            else:
                raise e
        
        print("✅ Crew execution completed!")
        print(f"📊 Result type: {type(result)}")
        
        if hasattr(result, 'raw'):
            print(f"📝 Raw output length: {len(str(result.raw))}")
        
        # Simulate HITL pause and webhook notification
        print("\n🤖 Simulating HITL pause and webhook notification...")
        simulate_hitl_pause_and_webhook(result)
        
        print("\n🎯 Demo 2 completed successfully!")
        print("💡 This demonstrates enterprise webhook HITL capabilities")
        print("   With CrewAI AMP: Real pause/resume via webhooks")
        print("   Without AMP: Educational simulation of the workflow")
        
        return result
    
    except Exception as e:
        print(f"❌ Error during crew execution: {str(e)}")
        raise


def main():
    """Main function for Demo 2."""
    print("🎯 Demo 2: Enterprise Webhook HITL")
    print("This demo shows advanced Human-in-the-Loop with webhook integration")
    print("Requires CrewAI AMP (enterprise) for full functionality")
    print()
    
    try:
        result = run_enterprise_webhook_hitl_demo()
        print("\n🎉 Demo 2 completed successfully!")
        print("Check the webhook server logs for HITL notifications")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

