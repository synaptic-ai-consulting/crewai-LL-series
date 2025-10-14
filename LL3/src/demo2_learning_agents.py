#!/usr/bin/env python3
"""
Lightning Lesson 3 - Demo 2: Learning Agents with Memory Events
Customer Support Agent that learns from multiple customer interactions
"""

import os
import sys
from pathlib import Path

# CRITICAL: Set environment variable BEFORE any CrewAI imports
project_root = Path(__file__).parent.parent
# Use a dedicated subdirectory for Demo 2 to avoid cross-demo memory pollution
storage_dir = project_root / "storage" / "demo2"
os.makedirs(storage_dir, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)

# Display storage location for demo transparency
print(f"🔧 Using custom storage directory: {os.environ.get('CREWAI_STORAGE_DIR', 'default')}")

# Debug: Check if storage directory exists and is writable
storage_path = os.environ.get('CREWAI_STORAGE_DIR', './storage/demo2')
if os.path.exists(storage_path):
    print(f"✅ Storage directory exists: {storage_path}")
    print(f"📁 Storage contents: {os.listdir(storage_path)}")
else:
    print(f"❌ Storage directory does not exist: {storage_path}")
    print(f"🔧 Creating storage directory...")
    os.makedirs(storage_path, exist_ok=True)
    print(f"✅ Storage directory created: {storage_path}")

# Now import CrewAI and other modules
import yaml
import time
import json
from flask import Flask, render_template, request, jsonify
from crewai import Crew, Agent, Task, Process
from crewai.memory import ShortTermMemory, LongTermMemory, EntityMemory
from crewai.events import (
    BaseEventListener,
    MemoryQueryCompletedEvent,
    MemorySaveCompletedEvent,
    MemoryRetrievalCompletedEvent,
    MemoryQueryStartedEvent,
    MemorySaveStartedEvent,
    MemoryRetrievalStartedEvent
)
from crewai import LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MemoryLearningListener(BaseEventListener):
    """Real CrewAI Memory Event Listener for Learning Demo"""
    
    def __init__(self):
        super().__init__()
        self.events = []
        self.query_times = []
        self.save_times = []
        self.retrieval_times = []
    
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(MemoryQueryStartedEvent)
        def on_memory_query_started(source, event: MemoryQueryStartedEvent):
            event_data = {
                "timestamp": time.time(),
                "type": "MEMORY_QUERY_STARTED",
                "query": event.query,
                "limit": event.limit,
                "score_threshold": event.score_threshold,
                "message": f"🔍 MEMORY QUERY STARTED: '{event.query[:30]}...'"
            }
            self.events.append(event_data)
            print(f"🔍 MEMORY QUERY STARTED: '{event.query[:30]}...'")
        
        @crewai_event_bus.on(MemoryQueryCompletedEvent)
        def on_memory_query_completed(source, event: MemoryQueryCompletedEvent):
            self.query_times.append(event.query_time_ms)
            event_data = {
                "timestamp": time.time(),
                "type": "MEMORY_QUERY_COMPLETED",
                "query": event.query,
                "results_count": len(event.results) if hasattr(event.results, "__len__") else 0,
                "query_time_ms": event.query_time_ms,
                "message": f"🔍 MEMORY QUERY COMPLETED: Found {len(event.results) if hasattr(event.results, '__len__') else 0} similar memories in {event.query_time_ms:.2f}ms"
            }
            self.events.append(event_data)
            print(f"🔍 MEMORY QUERY COMPLETED: Found {len(event.results) if hasattr(event.results, '__len__') else 0} similar memories in {event.query_time_ms:.2f}ms")
        
        @crewai_event_bus.on(MemorySaveStartedEvent)
        def on_memory_save_started(source, event: MemorySaveStartedEvent):
            event_data = {
                "timestamp": time.time(),
                "type": "MEMORY_SAVE_STARTED",
                "value": event.value[:50] + "..." if len(event.value) > 50 else event.value,
                "agent_role": event.agent_role,
                "message": f"🧠 MEMORY SAVE STARTED: Agent '{event.agent_role}' learning '{event.value[:30]}...'"
            }
            self.events.append(event_data)
            print(f"🧠 MEMORY SAVE STARTED: Agent '{event.agent_role}' learning '{event.value[:30]}...'")
        
        @crewai_event_bus.on(MemorySaveCompletedEvent)
        def on_memory_save_completed(source, event: MemorySaveCompletedEvent):
            self.save_times.append(event.save_time_ms)
            event_data = {
                "timestamp": time.time(),
                "type": "MEMORY_SAVE_COMPLETED",
                "value": event.value[:50] + "..." if len(event.value) > 50 else event.value,
                "agent_role": event.agent_role,
                "save_time_ms": event.save_time_ms,
                "message": f"🧠 MEMORY SAVE COMPLETED: Agent '{event.agent_role}' learned '{event.value[:30]}...' in {event.save_time_ms:.2f}ms"
            }
            self.events.append(event_data)
            print(f"🧠 MEMORY SAVE COMPLETED: Agent '{event.agent_role}' learned '{event.value[:30]}...' in {event.save_time_ms:.2f}ms")
        
        @crewai_event_bus.on(MemoryRetrievalStartedEvent)
        def on_memory_retrieval_started(source, event: MemoryRetrievalStartedEvent):
            event_data = {
                "timestamp": time.time(),
                "type": "MEMORY_RETRIEVAL_STARTED",
                "task_id": event.task_id,
                "message": f"📖 MEMORY RETRIEVAL STARTED: Task {event.task_id}"
            }
            self.events.append(event_data)
            print(f"📖 MEMORY RETRIEVAL STARTED: Task {event.task_id}")
        
        @crewai_event_bus.on(MemoryRetrievalCompletedEvent)
        def on_memory_retrieval_completed(source, event: MemoryRetrievalCompletedEvent):
            self.retrieval_times.append(event.retrieval_time_ms)
            event_data = {
                "timestamp": time.time(),
                "type": "MEMORY_RETRIEVAL_COMPLETED",
                "task_id": event.task_id,
                "memory_content": event.memory_content[:50] + "..." if len(event.memory_content) > 50 else event.memory_content,
                "retrieval_time_ms": event.retrieval_time_ms,
                "message": f"📖 MEMORY RETRIEVAL COMPLETED: Applied learned pattern in {event.retrieval_time_ms:.2f}ms"
            }
            self.events.append(event_data)
            print(f"📖 MEMORY RETRIEVAL COMPLETED: Applied learned pattern in {event.retrieval_time_ms:.2f}ms")
    
    def get_recent_events(self, limit=10):
        """Get recent memory events for UI display"""
        return self.events[-limit:] if self.events else []
    
    def get_performance_stats(self):
        """Get performance statistics"""
        return {
            "avg_query_time": sum(self.query_times) / len(self.query_times) if self.query_times else 0,
            "avg_save_time": sum(self.save_times) / len(self.save_times) if self.save_times else 0,
            "avg_retrieval_time": sum(self.retrieval_times) / len(self.retrieval_times) if self.retrieval_times else 0,
            "total_events": len(self.events)
        }
    
    def check_storage_files(self):
        """Check if memory files are being created in storage directory"""
        storage_path = os.environ.get('CREWAI_STORAGE_DIR', './storage')
        if os.path.exists(storage_path):
            files = os.listdir(storage_path)
            print(f"📁 Storage directory contents: {files}")
            return files
        else:
            print(f"❌ Storage directory not found: {storage_path}")
            return []

class LearningAgentDemo:
    def __init__(self, port=8002, company_name="TechCorp"):
        self.port = port
        self.company_name = company_name
        self.learning_crew = None
        self.memory_listener = MemoryLearningListener()
        self.customer_scenarios = [
            "My delivery is 3 days late, this is unacceptable!",
            "My package hasn't arrived yet, I'm frustrated",
            "Where is my order? It's been a week!",
            "I need help with a billing issue",
            "Can you help me track my shipment?"
        ]
        self.current_scenario = 0
        self.conversation_count = 0  # Simple conversation counter
        self.learning_progress = {
            "delivery_issues": 0,
            "billing_issues": 0,
            "tracking_issues": 0,
            "total_conversations": 0
        }
        self.load_configs()
        self.setup_learning_crew()
    
    def load_configs(self):
        """Load agent and task configurations from YAML files"""
        with open('config/agents.yaml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
    
    def setup_learning_crew(self):
        """Setup learning agent with basic CrewAI memory capabilities"""
        
        # Initialize LLM
        llm = LLM(model="gpt-4o-mini")
        
        # Learning Agent (With Basic Memory and Custom Templates)
        learning_agent = Agent(
            role=self.agents_config['agents']['learning_agent']['role'],
            goal=self.agents_config['agents']['learning_agent']['goal'],
            backstory=self.agents_config['agents']['learning_agent']['backstory'],
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            max_execution_time=400,
            memory=True,  # Basic CrewAI memory
            respect_context_window=True,
            max_retry_limit=3,
            system_template="prompts/learning_agent.txt",  # Use custom system template
            use_system_prompt=True  # Ensure system prompt is used
        )
        
        # Learning Task
        learning_task = Task(
            description=self.tasks_config['tasks']['learn_resolution_pattern']['description'],
            expected_output=self.tasks_config['tasks']['learn_resolution_pattern']['expected_output'],
            agent=learning_agent,
            output_file=self.tasks_config['tasks']['learn_resolution_pattern'].get('output_file'),
            human_input=self.tasks_config['tasks']['learn_resolution_pattern'].get('human_input', False)
        )
        
        # Create learning crew with real memory, event listener, and custom prompts
        self.learning_crew = Crew(
            agents=[learning_agent],
            tasks=[learning_task],
            process=Process.sequential,
            memory=True,  # Enable CrewAI memory
            verbose=True,
            event_listeners=[self.memory_listener],  # Add memory event listener
            prompt_file="prompts/custom_prompts.json"  # Use custom prompts for chat behavior
        )
    
    def process_customer_message(self, message):
        """Process customer message through learning agent with Long-Term Memory focus"""
        try:
            # Track learning progress based on message type
            self.track_learning_progress(message)
            self.conversation_count += 1
            
            # Get learning context for Long-Term Memory demonstration
            learning_context = self.get_learning_context()
            
            task_description = f"""Handle customer support inquiry using Long-Term Memory to improve responses.

LEARNING PROGRESS: {learning_context}

Current customer message: {message}

Instructions:
1. Provide a helpful and professional response to the customer's inquiry
2. Show empathy and understanding for their situation
3. Offer practical solutions or next steps
4. Use your Long-Term Memory to provide better responses based on previous similar interactions
5. Demonstrate learning and improvement through memory retrieval

Focus on showing how Long-Term Memory helps you provide better customer service over time."""
            
            self.learning_crew.tasks[0].description = task_description
            
            # Execute crew with real memory events automatically tracked
            result = self.learning_crew.kickoff()
            
            # Check if memory files were created
            self.memory_listener.check_storage_files()
            
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
                "learning_events": self.memory_listener.get_recent_events(5),
                "performance_stats": self.memory_listener.get_performance_stats(),
                "conversation_count": self.conversation_count,
                "learning_progress": self.learning_progress,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "memory_used": True,
                "learning_events": self.memory_listener.get_recent_events(5),
                "performance_stats": self.memory_listener.get_performance_stats(),
                "conversation_count": self.conversation_count,
                "learning_progress": self.learning_progress,
                "timestamp": time.time(),
                "error": True
            }
    
    def track_learning_progress(self, message):
        """Track learning progress based on message type"""
        message_lower = message.lower()
        if "delivery" in message_lower or "package" in message_lower or "late" in message_lower:
            self.learning_progress["delivery_issues"] += 1
        elif "billing" in message_lower or "charge" in message_lower or "payment" in message_lower:
            self.learning_progress["billing_issues"] += 1
        elif "track" in message_lower or "where" in message_lower or "shipment" in message_lower:
            self.learning_progress["tracking_issues"] += 1
        
        self.learning_progress["total_conversations"] += 1
    
    def get_learning_context(self):
        """Get learning progress context for Long-Term Memory demonstration"""
        return f"""Learning Progress Summary:
- Delivery Issues Handled: {self.learning_progress['delivery_issues']}
- Billing Issues Handled: {self.learning_progress['billing_issues']}
- Tracking Issues Handled: {self.learning_progress['tracking_issues']}
- Total Conversations: {self.learning_progress['total_conversations']}

Use your Long-Term Memory to retrieve insights from previous similar conversations and provide improved responses."""
    
    
    def get_next_scenario(self):
        """Get next scenario for demo"""
        if self.current_scenario < len(self.customer_scenarios) - 1:
            self.current_scenario += 1
        else:
            self.current_scenario = 0  # Loop back to first scenario
        return self.customer_scenarios[self.current_scenario]
    
    def get_previous_scenario(self):
        """Get previous scenario for demo"""
        if self.current_scenario > 0:
            self.current_scenario -= 1
        else:
            self.current_scenario = len(self.customer_scenarios) - 1  # Loop to last scenario
        return self.customer_scenarios[self.current_scenario]
    
    def get_current_scenario(self):
        """Get current scenario without changing position"""
        return self.customer_scenarios[self.current_scenario]
    
    def reset_scenarios(self):
        """Reset scenarios for new demo run"""
        self.current_scenario = 0
        self.conversation_count = 0
        self.learning_progress = {
            "delivery_issues": 0,
            "billing_issues": 0,
            "tracking_issues": 0,
            "total_conversations": 0
        }
        # Reset memory listener events
        self.memory_listener.events = []
        self.memory_listener.query_times = []
        self.memory_listener.save_times = []
        self.memory_listener.retrieval_times = []

# Create Flask app for Learning Agent Demo
app = Flask(__name__, template_folder='../templates')
demo = LearningAgentDemo()

@app.route('/')
def index():
    return render_template('learning_chat.html', company=demo.company_name, port=demo.port)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    response = demo.process_customer_message(message)
    return jsonify(response)

@app.route('/next-scenario', methods=['POST'])
def next_scenario():
    scenario = demo.get_next_scenario()
    return jsonify({"scenario": scenario, "current_index": demo.current_scenario, "total_scenarios": len(demo.customer_scenarios)})

@app.route('/previous-scenario', methods=['POST'])
def previous_scenario():
    scenario = demo.get_previous_scenario()
    return jsonify({"scenario": scenario, "current_index": demo.current_scenario, "total_scenarios": len(demo.customer_scenarios)})

@app.route('/current-scenario', methods=['GET'])
def current_scenario():
    scenario = demo.get_current_scenario()
    return jsonify({"scenario": scenario, "current_index": demo.current_scenario, "total_scenarios": len(demo.customer_scenarios)})

@app.route('/reset', methods=['POST'])
def reset_demo():
    demo.reset_scenarios()
    return jsonify({"message": "Demo reset successfully"})

@app.route('/memory-events')
def memory_events():
    return jsonify(demo.memory_listener.get_recent_events(20))

@app.route('/performance-stats')
def performance_stats():
    return jsonify(demo.memory_listener.get_performance_stats())

@app.route('/storage-info')
def storage_info():
    """Display storage location information for demo transparency"""
    from crewai.utilities.paths import db_storage_path
    storage_path = db_storage_path()
    return jsonify({
        "storage_path": str(storage_path),
        "custom_storage_dir": os.environ.get('CREWAI_STORAGE_DIR'),
        "storage_exists": os.path.exists(storage_path),
        "storage_contents": list(os.listdir(storage_path)) if os.path.exists(storage_path) else []
    })

@app.route('/memory-inspect', methods=['GET'])
def memory_inspect():
    """Inspect memory contents for demo purposes"""
    storage_path = os.environ.get('CREWAI_STORAGE_DIR', './storage')
    inspection_results = {
        "storage_path": storage_path,
        "long_term_memory": {},
        "task_outputs": {},
        "chromadb_collections": [],
        "errors": []
    }
    
    # Inspect Long-term Memory SQLite database
    ltm_db_path = os.path.join(storage_path, "long_term_memory_storage.db")
    if os.path.exists(ltm_db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(ltm_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                inspection_results["long_term_memory"][table_name] = count
            
            conn.close()
        except Exception as e:
            inspection_results["errors"].append(f"LTM DB error: {str(e)}")
    
    # Inspect Task Outputs SQLite database
    task_db_path = os.path.join(storage_path, "latest_kickoff_task_outputs.db")
    if os.path.exists(task_db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(task_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                inspection_results["task_outputs"][table_name] = count
            
            conn.close()
        except Exception as e:
            inspection_results["errors"].append(f"Task DB error: {str(e)}")
    
    # Inspect ChromaDB collections
    try:
        import chromadb
        client = chromadb.PersistentClient(path=storage_path)
        collections = client.list_collections()
        
        for collection in collections:
            try:
                count = collection.count()
                inspection_results["chromadb_collections"].append({
                    "name": collection.name,
                    "id": collection.id,
                    "document_count": count
                })
            except Exception as e:
                inspection_results["chromadb_collections"].append({
                    "name": collection.name,
                    "id": collection.id,
                    "error": str(e)
                })
    except Exception as e:
        inspection_results["errors"].append(f"ChromaDB error: {str(e)}")
    
    return jsonify(inspection_results)

@app.route('/learning-demo', methods=['POST'])
def learning_demo():
    """Demonstrate learning across multiple customers"""
    data = request.json
    demo_type = data.get('type', 'sequential')
    
    if demo_type == 'sequential':
        # Demonstrate learning progression across conversations
        responses = []
        scenarios = [
            "My delivery is 3 days late, this is unacceptable!",
            "My package hasn't arrived yet, I'm frustrated", 
            "Where is my order? It's been a week!"
        ]
        
        for i, scenario in enumerate(scenarios):
            response = demo.process_customer_message(scenario)
            responses.append({
                "conversation": i + 1,
                "scenario": scenario,
                "response": response
            })
            time.sleep(0.5)  # Small delay between conversations
        
        return jsonify({
            "demo_type": "sequential",
            "responses": responses,
            "learning_progress": demo.learning_progress,
            "message": "Compare responses across conversations to see Long-Term Memory learning!"
        })
    
    elif demo_type == 'repeat':
        # Demonstrate learning by repeating same scenario
        scenario = data.get('scenario', 'My delivery is 3 days late, this is unacceptable!')
        
        response1 = demo.process_customer_message(scenario)
        time.sleep(1)
        response2 = demo.process_customer_message(scenario)
        
        return jsonify({
            "demo_type": "repeat",
            "first_response": response1,
            "second_response": response2,
            "learning_progress": demo.learning_progress,
            "message": "Compare the two responses to see Long-Term Memory learning!"
        })
    
    return jsonify({"error": "Invalid demo type"})

def run_demo():
    """Run the learning agents demo"""
    print("🚀 Starting Lightning Lesson 3 - Demo 2: Learning Agents with Memory Events")
    print(f"📱 Learning Agent Demo: http://localhost:{demo.port}")
    print("\n💡 Demo Instructions:")
    print("1. Open the URL in your browser")
    print("2. Try the customer scenarios using the 'Next Scenario' button")
    print("3. Watch the Memory Events panel for real-time learning")
    print("4. Notice how the agent learns from each interaction")
    print("\nPress Ctrl+C to stop the demo")
    
    try:
        app.run(host='0.0.0.0', port=demo.port, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
        print("✅ Thank you for trying Lightning Lesson 3 - Demo 2!")

if __name__ == "__main__":
    run_demo()
