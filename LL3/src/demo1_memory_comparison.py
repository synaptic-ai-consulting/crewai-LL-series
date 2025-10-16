#!/usr/bin/env python3
"""
Lightning Lesson 3 - Demo 1: Memory vs No-Memory Comparison
Red.Co (no memory) vs Blue.Co (with memory) side-by-side demonstration
"""

import os
import sys
import yaml
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CRITICAL: Set demo-specific storage directory BEFORE any CrewAI imports
project_root = Path(__file__).parent.parent
# Use demo1 subdirectory for Demo 1 storage
demo1_storage_dir = project_root / "storage" / "demo1"
os.makedirs(demo1_storage_dir, exist_ok=True)

# Set CREWAI_STORAGE_DIR to demo1 subdirectory following CrewAI documentation
os.environ["CREWAI_STORAGE_DIR"] = str(demo1_storage_dir)

# Now import CrewAI after storage directory is set
from crewai import Crew, Agent, Task, Process, LLM
from crewai.events import (
    BaseEventListener,
    MemoryQueryCompletedEvent,
    MemorySaveCompletedEvent,
    MemoryRetrievalCompletedEvent,
    MemoryQueryStartedEvent,
    MemorySaveStartedEvent,
    MemoryRetrievalStartedEvent
)
from crewai.utilities.prompts import Prompts

print(f"🔧 Demo 1 using storage directory: {os.environ.get('CREWAI_STORAGE_DIR', 'default')}")
print(f"📁 Storage directory contents: {os.listdir(demo1_storage_dir) if os.path.exists(demo1_storage_dir) else 'Directory not found'}")

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MemoryDebugListener(BaseEventListener):
    """Debug listener to track memory operations"""
    
    def __init__(self):
        super().__init__()
        self.events = []
        self.query_count = 0
        self.save_count = 0
        self.retrieval_count = 0
    
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(MemoryQueryStartedEvent)
        def on_memory_query_started(source, event: MemoryQueryStartedEvent):
            self.query_count += 1
            print(f"🔍 MEMORY QUERY STARTED #{self.query_count}: '{event.query[:50]}...' (limit: {event.limit})")
            self.events.append(f"QUERY_STARTED: {event.query[:50]}...")
        
        @crewai_event_bus.on(MemoryQueryCompletedEvent)
        def on_memory_query_completed(source, event: MemoryQueryCompletedEvent):
            results_count = len(event.results) if hasattr(event.results, "__len__") else 0
            print(f"🔍 MEMORY QUERY COMPLETED #{self.query_count}: Found {results_count} results in {event.query_time_ms:.2f}ms")
            if results_count > 0:
                print(f"   📄 Sample results:")
                for i, result in enumerate(event.results[:2]):  # Show first 2 results
                    print(f"      {i+1}. {str(result)[:100]}...")
            self.events.append(f"QUERY_COMPLETED: {results_count} results")
        
        @crewai_event_bus.on(MemorySaveStartedEvent)
        def on_memory_save_started(source, event: MemorySaveStartedEvent):
            self.save_count += 1
            print(f"🧠 MEMORY SAVE STARTED #{self.save_count}: Agent '{event.agent_role}' saving '{event.value[:50]}...'")
            self.events.append(f"SAVE_STARTED: {event.value[:50]}...")
        
        @crewai_event_bus.on(MemorySaveCompletedEvent)
        def on_memory_save_completed(source, event: MemorySaveCompletedEvent):
            print(f"🧠 MEMORY SAVE COMPLETED #{self.save_count}: Saved in {event.save_time_ms:.2f}ms")
            self.events.append(f"SAVE_COMPLETED: {event.save_time_ms:.2f}ms")
        
        @crewai_event_bus.on(MemoryRetrievalStartedEvent)
        def on_memory_retrieval_started(source, event: MemoryRetrievalStartedEvent):
            self.retrieval_count += 1
            print(f"📖 MEMORY RETRIEVAL STARTED #{self.retrieval_count}: Task {event.task_id}")
            self.events.append(f"RETRIEVAL_STARTED: Task {event.task_id}")
        
        @crewai_event_bus.on(MemoryRetrievalCompletedEvent)
        def on_memory_retrieval_completed(source, event: MemoryRetrievalCompletedEvent):
            print(f"📖 MEMORY RETRIEVAL COMPLETED #{self.retrieval_count}: Retrieved in {event.retrieval_time_ms:.2f}ms")
            print(f"   📄 Retrieved content: {event.memory_content[:200]}...")
            self.events.append(f"RETRIEVAL_COMPLETED: {event.retrieval_time_ms:.2f}ms")
    
    def get_summary(self):
        return {
            "queries": self.query_count,
            "saves": self.save_count,
            "retrievals": self.retrieval_count,
            "events": self.events
        }

class MemoryComparisonDemo:
    def __init__(self, red_port=8000, blue_port=8001):
        self.red_port = red_port
        self.blue_port = blue_port
        self.red_crew = None
        self.blue_crew = None
        self.memory_debug_listener = MemoryDebugListener()  # Add debug listener
        self.load_configs()
        self.setup_crews()
        
    def load_configs(self):
        """Load agent and task configurations from YAML files"""
        with open('config/agents.yaml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
    
    def setup_crews(self):
        """Setup Red.Co and Blue.Co crews with different memory settings"""
        
        # Initialize LLM using CrewAI's LLM wrapper 
        llm = LLM(model="gpt-4o-mini")
        
        # Red.Co Agent (No Memory)
        red_agent = Agent(
            role=self.agents_config['agents']['red_co_support']['role'],
            goal=self.agents_config['agents']['red_co_support']['goal'],
            backstory=self.agents_config['agents']['red_co_support']['backstory'],
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            max_execution_time=400,
            memory=False,
            respect_context_window=True,
            max_retry_limit=3
        )
        
        # Blue.Co Agent (With Memory) - Let CrewAI handle everything automatically
        blue_agent = Agent(
            role=self.agents_config['agents']['blue_co_support']['role'],
            goal=self.agents_config['agents']['blue_co_support']['goal'],
            backstory=self.agents_config['agents']['blue_co_support']['backstory'],
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            max_execution_time=400,
            memory=True,  # Enable CrewAI memory - let it handle injection automatically
            respect_context_window=True,
            max_retry_limit=3
            # No custom templates - let CrewAI use defaults and inject memories automatically
        )
        
        # Create the SAME task for both agents - only difference is memory=True/False
        # handle_cfg = self.tasks_config.get('tasks', {}).get('handle_customer_inquiry', {}) if isinstance(self.tasks_config, dict) else {}
        
        # Same task configuration for both agents
        # task_description = handle_cfg.get('description', 'Handle customer support inquiry and provide helpful response')
        # task_expected_output = handle_cfg.get('expected_output', 'A helpful and professional response to the customer\'s inquiry')
        
        red_task = Task(
            description=self.tasks_config['tasks']['handle_customer_inquiry']['description'],
            expected_output=self.tasks_config['tasks']['handle_customer_inquiry']['expected_output'],
            agent=red_agent,
            output_file=self.tasks_config['tasks']['handle_customer_inquiry'].get('output_file'),
            human_input=self.tasks_config['tasks']['handle_customer_inquiry'].get('human_input', False)
        )
        
        blue_task = Task(
            description=self.tasks_config['tasks']['handle_customer_inquiry']['description'],
            expected_output=self.tasks_config['tasks']['handle_customer_inquiry']['expected_output'],
            agent=blue_agent,
            output_file=self.tasks_config['tasks']['handle_customer_inquiry'].get('output_file'),
            human_input=self.tasks_config['tasks']['handle_customer_inquiry'].get('human_input', False)
        )
        
        # Create crews
        self.red_crew = Crew(
            agents=[red_agent],
            tasks=[red_task],
            process=Process.sequential,
            memory=False,  # No memory
            verbose=True
        )
        
        self.blue_crew = Crew(
            agents=[blue_agent],
            tasks=[blue_task],
            process=Process.sequential,
            memory=True,  # With memory
            verbose=True,
            event_listeners=[self.memory_debug_listener]  # Add debug listener
        )
    
    def process_red_co_message(self, message):
        """Process message through Red.Co crew (no memory)"""
        try:
            # Update the task with the customer's message
            original_description = self.tasks_config['tasks']['handle_customer_inquiry']['description']
            self.red_crew.tasks[0].description = f"{original_description}\n\nCustomer inquiry: {message}"

            result = self.red_crew.kickoff()

            if hasattr(result, 'raw'):
                response_text = result.raw
            elif hasattr(result, 'output'):
                response_text = result.output
            else:
                response_text = str(result)

            return {
                "response": response_text,
                "memory_used": False,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "memory_used": False,
                "timestamp": time.time(),
                "error": True
            }
    
    def debug_prompts(self, message):
        """Debug the actual prompts being sent to the LLM"""
        try:
            print(f"\n🔍 PROMPT DEBUG: Analyzing prompts for message: '{message}'")
            
            # Get the Blue.Co agent
            blue_agent = self.blue_crew.agents[0]
            
            # Create a temporary task with the same description
            temp_task = Task(
                description=f"""Customer inquiry: {message}

Handle this customer support inquiry using memory to provide context-aware responses.

Instructions:
1. Provide a helpful and professional response to the customer's inquiry
2. Use your Short-Term Memory and Entity Memory to maintain conversation context
3. Use your Long-Term Memory to apply learned patterns from similar interactions
4. For ambiguous follow-up questions, infer context from previous conversation turns
5. Demonstrate memory usage by referencing relevant past context when appropriate

Focus on showing how memory helps provide better, context-aware customer service.""",
                expected_output="A helpful and professional response to the customer's inquiry",
                agent=blue_agent
            )
            
            # Create the prompt generator
            prompt_generator = Prompts(
                agent=blue_agent,
                has_tools=len(blue_agent.tools) > 0,
                use_system_prompt=blue_agent.use_system_prompt
            )
            
            # Generate and inspect the actual prompt
            generated_prompt = prompt_generator.task_execution()
            
            print(f"🔍 PROMPT DEBUG: Generated prompt keys: {list(generated_prompt.keys())}")
            
            # Print the complete system prompt that will be sent to the LLM
            if "system" in generated_prompt:
                print("\n=== SYSTEM PROMPT ===")
                print(generated_prompt["system"])
                print("\n=== USER PROMPT ===")
                print(generated_prompt["user"])
            else:
                print("\n=== COMPLETE PROMPT ===")
                print(generated_prompt["prompt"])
            
            # Show task context
            print(f"\n=== TASK CONTEXT ===")
            print(f"Task Description: {temp_task.description}")
            print(f"Expected Output: {temp_task.expected_output}")
            
        except Exception as e:
            print(f"🔍 PROMPT DEBUG: Error analyzing prompts: {str(e)}")

    def process_blue_co_message(self, message):
        """Process message through Blue.Co crew (with memory)"""
        try:
            print(f"\n🔵 BLUE.CO DEBUG: Processing message: '{message}'")
            print(f"🔵 BLUE.CO DEBUG: Memory debug listener stats before: {self.memory_debug_listener.get_summary()}")
            
            # Debug the actual prompts being sent to LLM
            self.debug_prompts(message)
            
            # Let CrewAI handle memory injection automatically
            # No custom instructions - let the framework inject memories into context
            task_description = message
            
            print(f"🔵 BLUE.CO DEBUG: Task description length: {len(task_description)} chars")
            self.blue_crew.tasks[0].description = task_description
            
            print(f"🔵 BLUE.CO DEBUG: Starting crew.kickoff()...")
            result = self.blue_crew.kickoff()
            print(f"🔵 BLUE.CO DEBUG: Crew kickoff completed")
            print(f"🔵 BLUE.CO DEBUG: Memory debug listener stats after: {self.memory_debug_listener.get_summary()}")
            
            # Handle different result formats
            if hasattr(result, 'raw'):
                response_text = result.raw
            elif hasattr(result, 'output'):
                response_text = result.output
            else:
                response_text = str(result)
            
            print(f"🔵 BLUE.CO DEBUG: Response length: {len(response_text)} chars")
            print(f"🔵 BLUE.CO DEBUG: Response preview: {response_text[:100]}...")
            
            return {
                "response": response_text,
                "memory_used": True,
                "timestamp": time.time(),
                "debug_stats": self.memory_debug_listener.get_summary()
            }
        except Exception as e:
            print(f"🔵 BLUE.CO DEBUG: Error occurred: {str(e)}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "memory_used": True,
                "timestamp": time.time(),
                "error": True,
                "debug_stats": self.memory_debug_listener.get_summary()
            }
    
    def get_memory_info(self):
        """Get memory storage information for Blue.Co"""
        try:
            # Show the actual storage directory being used by Demo 1
            storage_path = os.environ.get('CREWAI_STORAGE_DIR', 'Default CrewAI storage location')
            
            return {
                "storage_path": storage_path,
                "memory_enabled": True,
                "memory_type": "CrewAI Basic Memory System",
                "demo": "Demo 1 - Memory Comparison",
                "note": "Using LL3/storage/demo1/ directory"
            }
        except Exception as e:
            return {
                "storage_path": "Unable to determine",
                "memory_enabled": True,
                "error": str(e)
            }

def create_apps():
    """Create Flask apps and demo instances for Red.Co and Blue.Co"""
    red_app = Flask(__name__, template_folder='../templates')
    blue_app = Flask(__name__, template_folder='../templates')

    red_demo = MemoryComparisonDemo()
    blue_demo = MemoryComparisonDemo()

    @red_app.route('/')
    def red_index():
        return render_template('red_co_chat.html', company="Red.Co", port=red_demo.red_port)

    @red_app.route('/chat', methods=['POST'])
    def red_chat():
        data = request.get_json(silent=True) or {}
        message = data.get('message', '')
        response = red_demo.process_red_co_message(message)
        return jsonify(response)

    @red_app.route('/memory-info')
    def red_memory_info():
        return jsonify({"memory_enabled": False, "storage_path": "No memory system"})

    @blue_app.route('/')
    def blue_index():
        return render_template('blue_co_chat.html', company="Blue.Co", port=blue_demo.blue_port)

    @blue_app.route('/chat', methods=['POST'])
    def blue_chat():
        data = request.get_json(silent=True) or {}
        message = data.get('message', '')
        response = blue_demo.process_blue_co_message(message)
        return jsonify(response)

    @blue_app.route('/memory-info')
    def blue_memory_info():
        return jsonify(blue_demo.get_memory_info())

    return red_app, blue_app, red_demo, blue_demo

def run_demo():
    """Run the memory comparison demo"""
    # Create apps and demo instances lazily to avoid import-time errors
    red_app, blue_app, red_demo, blue_demo = create_apps()
    print("🚀 Starting Lightning Lesson 3 - Demo 1: Memory Comparison")
    print(f"📱 Red.Co (No Memory): http://localhost:{red_demo.red_port}")
    print(f"📱 Blue.Co (With Memory): http://localhost:{red_demo.blue_port}")
    print(f"💾 Demo 1 Storage: {os.environ.get('CREWAI_STORAGE_DIR', 'default')}")
    print("\n💡 Demo Instructions:")
    print("1. Open both URLs in separate browser windows")
    print("2. Ask the same question in both chats (e.g., 'I need help with my order')")
    print("3. Ask a follow-up question in both chats (e.g., 'What's the status?')")
    print("4. Notice how Blue.Co remembers context while Red.Co doesn't")
    print("5. Check /memory-info endpoint on Blue.Co to see storage location")
    print("\nPress Ctrl+C to stop the demo")
    
    try:
        # Run both apps
        import threading
        
        red_thread = threading.Thread(target=lambda: red_app.run(host='0.0.0.0', port=red_demo.red_port, debug=False))
        blue_thread = threading.Thread(target=lambda: blue_app.run(host='0.0.0.0', port=blue_demo.blue_port, debug=False))
        
        red_thread.daemon = True
        blue_thread.daemon = True
        
        red_thread.start()
        blue_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
        print("✅ Thank you for trying Lightning Lesson 3 - Demo 1!")

if __name__ == "__main__":
    run_demo()

