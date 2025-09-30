"""
Lightning Lesson 2 Demo Runner
Demonstrates before/after comparison of default vs persona-engineered agents using YAML configurations
"""

import os
import json
import warnings
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Suppress annoying warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")

from .agents import LightningLesson2Agents


class LightningLesson2Demo:
    """Demo runner for Lightning Lesson 2: Advanced Agent Persona Architecture"""
    
    def __init__(self, config_dir: str = "config"):
        load_dotenv()
        self.results = []
        self.agents_manager = LightningLesson2Agents(config_dir)
        
        # Load CrewAI configuration from environment
        self.crewai_verbose = self._get_boolean_env("CREWAI_VERBOSE", False)
        self.crewai_memory = self._get_boolean_env("CREWAI_MEMORY", False)
        
        # Check for required environment variables
        self._check_environment()
    
    def _get_boolean_env(self, var_name: str, default: bool = False) -> bool:
        """Get boolean value from environment variable"""
        value = os.getenv(var_name, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _check_environment(self):
        """Check for required environment variables"""
        required_vars = ["OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print("❌ Missing required environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\nPlease set these variables in your .env file or environment.")
            print("Example .env file:")
            print("OPENAI_API_KEY=your_openai_api_key_here")
            print("OPENAI_MODEL_NAME=gpt-4o-mini")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Environment variables configured correctly")
        print(f"   CREWAI_VERBOSE: {self.crewai_verbose}")
        print(f"   CREWAI_MEMORY: {self.crewai_memory}")
        
    def run_comparison_demo(self, task_name: str = None) -> Dict[str, Any]:
        """Run before/after comparison demo"""
        print("🚀 Starting Lightning Lesson 2 Demo: Agent Persona Architecture")
        print("=" * 60)
        
        # Create comparison agents
        agents = self.agents_manager.create_comparison_agents()
        
        # Get task configuration
        if task_name:
            task_config = self.agents_manager.config_loader.get_task_config(task_name)
            task_description = task_config.get("description", task_name)
        else:
            task_description = "Write a product launch email for our new AI tool"
        
        print(f"\n📝 Task: {task_description}")
        print("\n" + "="*60)
        
        # Run default agent
        print("\n🤖 DEFAULT AGENT RESPONSE:")
        print("-" * 40)
        default_response = self._execute_agent_task(agents["default"], task_description)
        print(default_response)
        
        print("\n" + "="*60)
        
        # Run persona-engineered agent
        print("\n🎭 PERSONA-ENGINEERED AGENT RESPONSE:")
        print("-" * 40)
        persona_response = self._execute_agent_task(agents["persona"], task_description)
        print(persona_response)
        
        # Store results
        demo_result = {
            "timestamp": datetime.now().isoformat(),
            "task": task_description,
            "default_response": default_response,
            "persona_response": persona_response,
            "comparison_notes": self._analyze_differences(default_response, persona_response)
        }
        
        self.results.append(demo_result)
        return demo_result
    
    def run_persona_showcase(self, task_name: str = None) -> Dict[str, Any]:
        """Run showcase of all persona types"""
        print("\n🎭 PERSONA SHOWCASE")
        print("=" * 60)
        
        agents = self.agents_manager.create_all_personas()
        persona_responses = {}
        
        # Get task configuration
        if task_name:
            task_config = self.agents_manager.config_loader.get_task_config(task_name)
            task_description = task_config.get("description", task_name)
        else:
            task_description = "Write a product launch email for our new AI tool"
        
        for persona_name, agent in agents.items():
            print(f"\n🔹 {persona_name.upper()} PERSONA:")
            print("-" * 40)
            
            response = self._execute_agent_task(agent, task_description)
            persona_responses[persona_name] = response
            print(response)
            print("\n" + "="*60)
        
        showcase_result = {
            "timestamp": datetime.now().isoformat(),
            "task": task_description,
            "persona_responses": persona_responses
        }
        
        self.results.append(showcase_result)
        return showcase_result
    
    def run_prompt_inspection_demo(self) -> Dict[str, Any]:
        """Demonstrate CrewAI's automatic prompt injection"""
        print("\n🔍 CREWAI PROMPT INSPECTION DEMO")
        print("=" * 60)
        
        # Create agents for inspection
        agents = self.agents_manager.create_prompt_inspection_agents()
        inspection_results = {}
        
        for agent_name, agent in agents.items():
            print(f"\n📋 {agent_name.upper().replace('_', ' ')} AGENT PROMPT INSPECTION:")
            print("-" * 40)
            
            # Inspect what CrewAI actually sends
            prompt_info = self.agents_manager.inspect_prompts(agent)
            
            if "error" in prompt_info:
                print(f"❌ Error: {prompt_info['error']}")
                inspection_results[agent_name] = {"error": prompt_info["error"]}
            else:
                print("=== AGENT CONFIGURATION ===")
                agent_info = prompt_info.get("agent_info", {})
                print(f"Role: {agent_info.get('role', 'Unknown')}")
                print(f"Goal: {agent_info.get('goal', 'Unknown')}")
                print(f"Has Tools: {agent_info.get('has_tools', False)}")
                
                # Show the actual system prompt that would be sent to the LLM
                if prompt_info.get('system_prompt'):
                    print(f"\n=== SYSTEM PROMPT SENT TO LLM ===")
                    print(prompt_info['system_prompt'])
                
                # Show the user prompt if available
                if prompt_info.get('user_prompt'):
                    print(f"\n=== USER PROMPT SENT TO LLM ===")
                    print(prompt_info['user_prompt'])
                
                # Show task context
                task_context = prompt_info.get('task_context', {})
                if task_context:
                    print(f"\n=== TASK CONTEXT ===")
                    print(f"Task Description: {task_context.get('description', '')}")
                    print(f"Expected Output: {task_context.get('expected_output', '')}")
                
                inspection_results[agent_name] = prompt_info
            
            print("\n" + "="*60)
        
        inspection_result = {
            "timestamp": datetime.now().isoformat(),
            "inspection_results": inspection_results
        }
        
        self.results.append(inspection_result)
        return inspection_result
    
    def run_customization_approaches_demo(self) -> Dict[str, Any]:
        """Demonstrate different prompt customization approaches"""
        print("\n⚙️ PROMPT CUSTOMIZATION APPROACHES DEMO")
        print("=" * 60)
        
        # Create crews for different approaches
        crews = self.agents_manager.create_customization_demo_crews()
        customization_results = {}
        
        task_description = "Write a product launch email for our new AI tool"
        
        for crew_name, crew in crews.items():
            print(f"\n🔧 {crew_name.upper()} APPROACH:")
            print("-" * 40)
            
            try:
                # Create a simple task for the crew
                from crewai import Task
                task = Task(
                    description=task_description,
                    expected_output="A compelling product launch email",
                    agent=crew.agents[0] if crew.agents else None
                )
                
                # Execute the crew
                result = crew.kickoff()
                
                if hasattr(result, 'raw'):
                    response = str(result.raw)
                else:
                    response = str(result)
                
                print(response)
                customization_results[crew_name] = {
                    "success": True,
                    "response": response
                }
                
            except Exception as e:
                error_msg = f"Error executing {crew_name}: {str(e)}"
                print(f"❌ {error_msg}")
                customization_results[crew_name] = {
                    "success": False,
                    "error": error_msg
                }
            
            print("\n" + "="*60)
        
        customization_result = {
            "timestamp": datetime.now().isoformat(),
            "task": task_description,
            "customization_results": customization_results
        }
        
        self.results.append(customization_result)
        return customization_result
    
    def run_crew_demo(self, crew_name: str) -> Dict[str, Any]:
        """Run demo using a specific crew configuration"""
        print(f"\n🚀 CREW DEMO: {crew_name.upper()}")
        print("=" * 60)
        
        try:
            crew = self.agents_manager.factory.create_crew(crew_name)
            result = crew.kickoff()
            
            crew_result = {
                "timestamp": datetime.now().isoformat(),
                "crew_name": crew_name,
                "result": str(result)
            }
            
            self.results.append(crew_result)
            return crew_result
            
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "crew_name": crew_name,
                "error": str(e)
            }
            self.results.append(error_result)
            return error_result
    
    def _execute_agent_task(self, agent, task: str) -> str:
        """Execute task with agent using CrewAI"""
        try:
            # Create a task for the agent to execute
            from crewai import Task
            
            task_obj = Task(
                description=task,
                expected_output="A detailed, professional response that demonstrates the agent's persona and expertise",
                agent=agent
            )
            
            # Create a simple crew with just this agent and task
            from crewai import Crew
            crew = Crew(
                agents=[agent],
                tasks=[task_obj],
                verbose=self.crewai_verbose,  # Use environment variable
                memory=self.crewai_memory     # Use environment variable
            )
            
            # Execute the crew and get the result
            result = crew.kickoff()
            
            # Extract the actual response from the result
            if hasattr(result, 'raw'):
                return str(result.raw)
            else:
                return str(result)
                
        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            
            # Provide specific guidance based on error type
            if "API key" in str(e).lower() or "authentication" in str(e).lower():
                error_msg += "\n\n🔑 API Key Issue: Please check your OPENAI_API_KEY environment variable."
            elif "rate limit" in str(e).lower():
                error_msg += "\n\n⏱️ Rate Limit: Please wait a moment and try again."
            elif "model" in str(e).lower():
                error_msg += "\n\n🤖 Model Issue: Please check your OPENAI_MODEL_NAME environment variable."
            else:
                error_msg += "\n\n💡 Troubleshooting: Check your internet connection and API key configuration."
            
            return error_msg
    
    def _analyze_differences(self, default_response: str, persona_response: str) -> Dict[str, str]:
        """Analyze differences between responses"""
        # Basic analysis based on response characteristics
        default_length = len(default_response)
        persona_length = len(persona_response)
        
        # Look for persona-specific language patterns
        persona_indicators = []
        if "brand" in persona_response.lower():
            persona_indicators.append("Brand-focused language")
        if "audience" in persona_response.lower() or "target" in persona_response.lower():
            persona_indicators.append("Audience-centric approach")
        if "creative" in persona_response.lower() or "innovative" in persona_response.lower():
            persona_indicators.append("Creative thinking")
        if "compliance" in persona_response.lower() or "legal" in persona_response.lower():
            persona_indicators.append("Legal/compliance awareness")
        if "technical" in persona_response.lower() or "architecture" in persona_response.lower():
            persona_indicators.append("Technical expertise")
        
        return {
            "default_characteristics": f"Generic response ({default_length} chars), lacks specialized expertise",
            "persona_characteristics": f"Specialized response ({persona_length} chars) with professional focus",
            "key_differences": [
                f"Persona response is {persona_length - default_length:+d} characters {'longer' if persona_length > default_length else 'shorter'}",
                "Persona response demonstrates domain-specific expertise",
                "Persona response shows consistent professional voice",
                "Persona response adapts communication style to context"
            ] + persona_indicators
        }
    
    def save_results(self, filename: str = None):
        """Save demo results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"artifacts/ll2_demo_results_{timestamp}.json"
        
        os.makedirs("artifacts", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename


def run_demo():
    """Main demo execution function"""
    demo = LightningLesson2Demo()
    
    # Demo tasks
    tasks = [
        "Write a product launch email for our new AI tool",
        "Review our data privacy policy for compliance issues",
        "Design a technical architecture for a scalable web application"
    ]
    
    print("🎯 Lightning Lesson 2: CrewAI Prompt Customization & Persona Architecture")
    print("=" * 80)
    
    # Run prompt inspection demo
    demo.run_prompt_inspection_demo()
    
    # Run customization approaches demo
    demo.run_customization_approaches_demo()
    
    # Run comparison demo for first task
    demo.run_comparison_demo(tasks[0])
    
    # Run persona showcase for all tasks
    for task in tasks:
        demo.run_persona_showcase(task)
    
    # Save results
    demo.save_results()
    
    print("\n✅ Demo completed successfully!")
    print("\nKey Takeaways:")
    print("• CrewAI automatically injects instructions you might not know about")
    print("• Multiple customization approaches for different use cases")
    print("• Production systems need full prompt transparency")
    print("• Model-specific optimization improves performance")
    print("• Enterprise-ready solutions vs generic AI tools")


if __name__ == "__main__":
    run_demo()
