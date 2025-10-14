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
from crewai import Crew, Agent, Task, Process, LLM
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

print(f"🔧 Demo 1 using storage directory: {os.environ.get('CREWAI_STORAGE_DIR', 'default')}")
print(f"📁 Storage directory contents: {os.listdir(demo1_storage_dir) if os.path.exists(demo1_storage_dir) else 'Directory not found'}")

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MemoryComparisonDemo:
    def __init__(self, red_port=8000, blue_port=8001):
        self.red_port = red_port
        self.blue_port = blue_port
        self.red_crew = None
        self.blue_crew = None
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
        
        # Initialize LLM using CrewAI's LLM wrapper (avoids langchain deprecations)
        llm = LLM(model="gpt-4o-mini")
        
        # Red.Co Agent (No Memory)
        red_agent = Agent(
            role=self.agents_config['agents']['red_co_support']['role'],
            goal=self.agents_config['agents']['red_co_support']['goal'],
            backstory=self.agents_config['agents']['red_co_support']['backstory'],
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=300,
            memory=False,
            respect_context_window=True,
            max_retry_limit=2
        )
        
        # Blue.Co Agent (With Memory)
        blue_agent = Agent(
            role=self.agents_config['agents']['blue_co_support']['role'],
            goal=self.agents_config['agents']['blue_co_support']['goal'],
            backstory=self.agents_config['agents']['blue_co_support']['backstory'],
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=300,
            memory=True,  # Re-enabled with default storage
            respect_context_window=True,
            max_retry_limit=2
        )
        
        # Create the SAME task for both agents - only difference is memory=True/False
        handle_cfg = self.tasks_config.get('tasks', {}).get('handle_customer_inquiry', {}) if isinstance(self.tasks_config, dict) else {}
        
        # Same task configuration for both agents
        task_description = handle_cfg.get('description', 'Handle customer support inquiry and provide helpful response')
        task_expected_output = handle_cfg.get('expected_output', 'A helpful and professional response to the customer\'s inquiry')
        
        red_task = Task(
            description=task_description,
            expected_output=task_expected_output,
            agent=red_agent,
            context=handle_cfg.get('context', []),
            output_file=handle_cfg.get('output_file'),
            human_input=handle_cfg.get('human_input', False)
        )
        
        blue_task = Task(
            description=task_description,
            expected_output=task_expected_output,
            agent=blue_agent,
            context=handle_cfg.get('context', []),
            output_file=handle_cfg.get('output_file'),
            human_input=handle_cfg.get('human_input', False)
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
            verbose=True
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
    
    def process_blue_co_message(self, message):
        """Process message through Blue.Co crew (with memory)"""
        try:
            # Update task description with the customer message
            original_description = self.tasks_config['tasks']['handle_customer_inquiry']['description']
            self.blue_crew.tasks[0].description = f"{original_description}\n\nCustomer inquiry: {message}"
            
            result = self.blue_crew.kickoff()
            
            # Handle different result formats
            if hasattr(result, 'raw'):
                response_text = result.raw
            elif hasattr(result, 'output'):
                response_text = result.output
            else:
                response_text = str(result)
            
            return {
                "response": response_text,
                "memory_used": True,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "memory_used": True,
                "timestamp": time.time(),
                "error": True
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

