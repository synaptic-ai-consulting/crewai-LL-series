"""
Demo 1: Open Source HITL - Iterative Refinement Pattern
Demonstrates iterative refinement with human feedback in open source CrewAI
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

def create_iterative_refinement_task(agent, topic, iteration=1, previous_feedback=""):
    """Create a task for iterative refinement with human feedback."""
    if iteration == 1:
        description = f"Write a comprehensive summary of the latest {topic} trends. Focus on the most impactful developments and their business implications."
        expected_output = f"A detailed summary of current {topic} trends with business insights"
    else:
        description = f"Refine and improve the {topic} summary based on the previous feedback. Incorporate the suggestions: '{previous_feedback}'. Make the content more engaging and comprehensive."
        expected_output = f"An improved and refined summary of {topic} trends incorporating human feedback"
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        human_input=True  # This enables HITL in open source CrewAI
    )

def get_user_topic():
    """Prompt user for a topic."""
    print("📝 Please enter a topic for the research:")
    print("   Examples: AI, Machine Learning, Blockchain, Cybersecurity, etc.")
    print()
    
    while True:
        topic = input("🎯 Topic: ").strip()
        if topic:
            print(f"✅ Selected topic: {topic}")
            return topic
        else:
            print("❌ Please enter a valid topic")

def run_opensource_hitl_demo():
    """Run Demo 1: Open Source HITL with Iterative Refinement."""
    print("🚀 Demo 1: Open Source HITL - Iterative Refinement Pattern")
    print("=" * 60)
    print("This demo shows iterative refinement with human feedback")
    print("in open source CrewAI using console-based HITL")
    print()
    
    # Get topic from user
    topic = get_user_topic()
    print()
    
    # Load configuration
    agents = load_agents()
    researcher = agents['content_researcher']
    
    print(f"👤 Agent: {researcher.role}")
    print()
    
    print("💡 Iterative Refinement Pattern:")
    print("   • Multiple iterations with human feedback")
    print("   • Each iteration improves based on previous feedback")
    print("   • Human provides specific improvement suggestions")
    print("   • Process continues until satisfied with output")
    print()
    
    # Iterative refinement loop
    max_iterations = 3
    feedback_history = []
    
    for iteration in range(1, max_iterations + 1):
        print(f"🔄 === ITERATION {iteration} ===")
        
        # Create task for this iteration
        previous_feedback = feedback_history[-1] if feedback_history else ""
        hitl_task = create_iterative_refinement_task(researcher, topic, iteration, previous_feedback)
        
        print(f"📋 Task: {hitl_task.description}")
        print(f"🎯 Expected Output: {hitl_task.expected_output}")
        print()
        
        # Create crew for this iteration
        crew = Crew(
            agents=[researcher],
            tasks=[hitl_task],
            verbose=True
        )
        
        try:
            print(f"🚀 Starting iteration {iteration}...")
            print("⏸️  Execution will pause for human feedback")
            print()
            
            # This will pause for human input in open source CrewAI
            result = crew.kickoff(
                inputs={"topic": topic, "iteration": iteration}
            )
            
            print(f"\n✅ Iteration {iteration} completed!")
            
            if hasattr(result, 'raw'):
                output = str(result.raw)
                print(f"📝 Output length: {len(output)} characters")
                print("\n📋 Current Output:")
                print("-" * 40)
                print(output[:500] + "..." if len(output) > 500 else output)
                print("-" * 40)
                
                # Ask for feedback
                print(f"\n🤔 Human Review for Iteration {iteration}:")
                print("Please provide feedback to improve the content:")
                print("   • What should be added or removed?")
                print("   • How can it be more engaging?")
                print("   • Any specific improvements needed?")
                print()
                
                feedback = input("💬 Your feedback (or 'done' to finish): ").strip()
                
                if feedback.lower() == 'done':
                    print("✅ Content approved! Iterative refinement complete.")
                    break
                elif feedback:
                    feedback_history.append(feedback)
                    print(f"✅ Feedback recorded: {feedback}")
                    print("🔄 Will incorporate this feedback in next iteration")
                else:
                    print("⚠️ No feedback provided, continuing to next iteration")
                
                print()
                
                # Check if this is the last iteration
                if iteration == max_iterations:
                    print("🏁 Maximum iterations reached")
                    print("💡 This demonstrates the iterative refinement pattern")
                    break
            else:
                print("⚠️ No output received from crew")
                break
                
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted by user")
            return None
        except Exception as e:
            print(f"❌ Error during iteration {iteration}: {str(e)}")
            raise
    
    print("\n🎯 Iterative Refinement Demo completed!")
    print(f"📊 Total iterations: {len(feedback_history) + 1}")
    print(f"💬 Feedback cycles: {len(feedback_history)}")
    
    return result

def main():
    """Main function for Demo 1."""
    print("🎯 Demo 1: Open Source HITL - Iterative Refinement")
    print("This demo shows iterative refinement with human feedback")
    print("in open source CrewAI (console-based HITL)")
    print("You'll be prompted to enter a topic and provide feedback")
    print()
    
    try:
        result = run_opensource_hitl_demo()
        if result:
            print("\n🎯 Demo 1 completed successfully!")
            print("💡 This demonstrates iterative refinement in open source CrewAI")
            print("   Next: Demo 2 will show enterprise webhook HITL")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
