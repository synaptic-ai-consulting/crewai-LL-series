#!/usr/bin/env python3
"""
Lightning Lesson 3 - Demo 1: Memory vs No-Memory Comparison
Red.Co (no memory) vs Blue.Co (with memory) side-by-side demonstration
"""

import os
import sys
import yaml
import time
from flask import Flask, render_template, request, jsonify
from crewai import Crew, Agent, Task, Process
from langchain.chat_models import ChatOpenAI
# Memory imports removed - using basic CrewAI memory functionality
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o")
        
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
            memory=True,
            respect_context_window=True,
            max_retry_limit=2
        )
        
        # Create tasks from YAML configuration
        red_task = Task(
            description=self.tasks_config['tasks']['handle_customer_inquiry']['description'],
            expected_output=self.tasks_config['tasks']['handle_customer_inquiry']['expected_output'],
            agent=red_agent,
            context=self.tasks_config['tasks']['handle_customer_inquiry'].get('context', []),
            output_file=self.tasks_config['tasks']['handle_customer_inquiry'].get('output_file'),
            human_input=self.tasks_config['tasks']['handle_customer_inquiry'].get('human_input', False)
        )
        
        blue_task = Task(
            description=self.tasks_config['tasks']['memory_demonstration']['description'],
            expected_output=self.tasks_config['tasks']['memory_demonstration']['expected_output'],
            agent=blue_agent,
            context=self.tasks_config['tasks']['memory_demonstration'].get('context', []),
            output_file=self.tasks_config['tasks']['memory_demonstration'].get('output_file'),
            human_input=self.tasks_config['tasks']['memory_demonstration'].get('human_input', False)
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
        """Process message through Red.Co crew (no memory) - simplified approach"""
        try:
            # Create a simple response without using CrewAI memory features
            # This simulates a basic customer support response without memory
            response_text = f"""Hello! I'm your Red.Co customer support specialist. 

Regarding your inquiry: "{message}"

At Red.Co, we offer a range of reliable technology products including:
- Smart home devices
- Personal electronics  
- Productivity tools
- Tech accessories

I don't have access to our previous conversations, so I'm starting fresh with your request. How can I help you today?

Note: I don't have memory capabilities, so each conversation starts from scratch."""
            
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
            original_description = self.tasks_config['tasks']['memory_demonstration']['description']
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
            # Basic memory info - CrewAI handles storage internally
            return {
                "storage_path": "Managed by CrewAI",
                "memory_enabled": True,
                "memory_type": "Basic CrewAI Memory"
            }
        except Exception as e:
            return {
                "storage_path": "Unable to determine",
                "memory_enabled": True,
                "error": str(e)
            }

# Create Flask app for Red.Co
red_app = Flask(__name__, template_folder='../templates')
red_demo = MemoryComparisonDemo()

@red_app.route('/')
def red_index():
    return render_template('red_co_chat.html', company="Red.Co", port=red_demo.red_port)

@red_app.route('/chat', methods=['POST'])
def red_chat():
    data = request.json
    message = data.get('message', '')
    response = red_demo.process_red_co_message(message)
    return jsonify(response)

@red_app.route('/memory-info')
def red_memory_info():
    return jsonify({"memory_enabled": False, "storage_path": "No memory system"})

# Create Flask app for Blue.Co
blue_app = Flask(__name__, template_folder='../templates')
blue_demo = MemoryComparisonDemo()

@blue_app.route('/')
def blue_index():
    return render_template('blue_co_chat.html', company="Blue.Co", port=blue_demo.blue_port)

@blue_app.route('/chat', methods=['POST'])
def blue_chat():
    data = request.json
    message = data.get('message', '')
    response = blue_demo.process_blue_co_message(message)
    return jsonify(response)

@blue_app.route('/memory-info')
def blue_memory_info():
    return jsonify(blue_demo.get_memory_info())

def run_demo():
    """Run the memory comparison demo"""
    print("🚀 Starting Lightning Lesson 3 - Demo 1: Memory Comparison")
    print(f"📱 Red.Co (No Memory): http://localhost:{red_demo.red_port}")
    print(f"📱 Blue.Co (With Memory): http://localhost:{red_demo.blue_port}")
    print("\n💡 Demo Instructions:")
    print("1. Open both URLs in separate browser windows")
    print("2. Ask the same question in both chats")
    print("3. Ask a follow-up question in both chats")
    print("4. Notice how Blue.Co remembers context while Red.Co doesn't")
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

