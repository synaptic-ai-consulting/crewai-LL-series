"""
Demo 2: Enterprise Webhook HITL - Full Content Pipeline
Web UI integration with deployed CrewAI AMP crew
"""

import os
import sys
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CrewAIAMPClient:
    """Client for interacting with deployed CrewAI AMP crew."""
    
    def __init__(self, crew_url, crew_token):
        self.crew_url = crew_url
        self.crew_token = crew_token
        self.headers = {
            'Authorization': f'Bearer {crew_token}',
            'Content-Type': 'application/json'
        }
    
    def start_execution(self, inputs):
        """Start crew execution with given inputs."""
        url = f"{self.crew_url}/api/crews/run"
        payload = {"inputs": inputs}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error starting execution: {e}")
            return None
    
    def get_execution_status(self, execution_id):
        """Get status of execution."""
        url = f"{self.crew_url}/api/crews/status/{execution_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting status: {e}")
            return None
    
    def resume_execution(self, execution_id, feedback=None):
        """Resume execution with optional feedback."""
        url = f"{self.crew_url}/api/crews/resume/{execution_id}"
        payload = {"feedback": feedback} if feedback else {}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error resuming execution: {e}")
            return None

class Demo2WebUI:
    """Web UI for Demo 2 HITL workflow."""
    
    def __init__(self, crew_client):
        self.crew_client = crew_client
        self.current_execution = None
        self.webhook_port = os.getenv('WEBHOOK_PORT', '5000')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET_TKN', 'demo-secret-token')
    
    def start_content_pipeline(self, topic):
        """Start the content pipeline with given topic."""
        print(f"🚀 Starting content pipeline for topic: '{topic}'")
        print("=" * 60)
        
        # Start execution
        result = self.crew_client.start_execution({"topic": topic})
        if not result:
            print("❌ Failed to start execution")
            return False
        
        self.current_execution = result
        execution_id = result.get('execution_id')
        
        print(f"✅ Execution started: {execution_id}")
        print(f"🌐 Monitor at: http://localhost:{self.webhook_port}/demo2")
        print(f"📊 Execution URL: {self.crew_client.crew_url}/executions/{execution_id}")
        print()
        
        # Monitor execution
        return self.monitor_execution(execution_id)
    
    def monitor_execution(self, execution_id):
        """Monitor execution and handle HITL pauses."""
        print("🔄 Monitoring execution...")
        
        while True:
            status = self.crew_client.get_execution_status(execution_id)
            if not status:
                print("❌ Failed to get execution status")
                return False
            
            execution_status = status.get('status', 'unknown')
            print(f"📊 Status: {execution_status}")
            
            if execution_status == 'completed':
                print("✅ Execution completed successfully!")
                print(f"📄 Final output: {status.get('output', 'No output available')}")
                return True
            
            elif execution_status == 'failed':
                print("❌ Execution failed")
                print(f"💥 Error: {status.get('error', 'Unknown error')}")
                return False
            
            elif execution_status == 'pending_human_input':
                print("⏸️ Execution paused for human input")
                return self.handle_human_input(execution_id, status)
            
            elif execution_status == 'running':
                print("🔄 Execution in progress...")
                time.sleep(5)  # Wait 5 seconds before checking again
            
            else:
                print(f"❓ Unknown status: {execution_status}")
                time.sleep(5)
    
    def handle_human_input(self, execution_id, status):
        """Handle human input at HITL pause points."""
        pause_point = status.get('pause_point', 'unknown')
        output_data = status.get('output', {})
        
        print(f"👤 Human input required at: {pause_point}")
        print("=" * 40)
        
        if pause_point == 'Human Research Review Gate':
            return self.handle_research_review(execution_id, output_data)
        elif pause_point == 'Human Final Approval Gate':
            return self.handle_final_approval(execution_id, output_data)
        else:
            return self.handle_generic_review(execution_id, output_data, pause_point)
    
    def handle_research_review(self, execution_id, research_data):
        """Handle research review checkpoint."""
        print("📊 RESEARCH REVIEW CHECKPOINT")
        print("=" * 40)
        
        # Display research findings
        print("🔍 Research Findings:")
        print("-" * 20)
        if isinstance(research_data, dict):
            for key, value in research_data.items():
                print(f"{key}: {value}")
        else:
            print(research_data)
        
        print()
        print("Options:")
        print("1. ✅ Approve - Continue to blog post creation")
        print("2. 🔄 Revise - Request research revision")
        print("3. ❌ Reject - Stop execution")
        
        while True:
            choice = input("\nEnter your choice (1/2/3): ").strip()
            
            if choice == '1':
                print("✅ Research approved! Continuing to blog post creation...")
                result = self.crew_client.resume_execution(execution_id)
                return self.monitor_execution(execution_id)
            
            elif choice == '2':
                feedback = input("📝 Enter revision feedback: ").strip()
                if feedback:
                    print("🔄 Requesting research revision...")
                    result = self.crew_client.resume_execution(execution_id, feedback)
                    return self.monitor_execution(execution_id)
                else:
                    print("⚠️ Please provide feedback for revision")
            
            elif choice == '3':
                print("❌ Execution rejected by user")
                return False
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3")
    
    def handle_final_approval(self, execution_id, content_data):
        """Handle final approval checkpoint."""
        print("📝 FINAL APPROVAL CHECKPOINT")
        print("=" * 40)
        
        # Display final content
        print("📄 Final Blog Post:")
        print("-" * 20)
        if isinstance(content_data, dict):
            for key, value in content_data.items():
                print(f"{key}: {value}")
        else:
            print(content_data)
        
        print()
        print("Options:")
        print("1. ✅ Approve - Publish content")
        print("2. 🔄 Revise - Request final revision")
        print("3. ❌ Reject - Discard content")
        
        while True:
            choice = input("\nEnter your choice (1/2/3): ").strip()
            
            if choice == '1':
                print("✅ Content approved! Publishing...")
                result = self.crew_client.resume_execution(execution_id)
                return self.monitor_execution(execution_id)
            
            elif choice == '2':
                feedback = input("📝 Enter revision feedback: ").strip()
                if feedback:
                    print("🔄 Requesting final revision...")
                    result = self.crew_client.resume_execution(execution_id, feedback)
                    return self.monitor_execution(execution_id)
                else:
                    print("⚠️ Please provide feedback for revision")
            
            elif choice == '3':
                print("❌ Content rejected by user")
                return False
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3")
    
    def handle_generic_review(self, execution_id, data, pause_point):
        """Handle generic review checkpoint."""
        print(f"👤 HUMAN REVIEW CHECKPOINT: {pause_point}")
        print("=" * 40)
        
        print("📄 Output Data:")
        print("-" * 20)
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        else:
            print(data)
        
        print()
        print("Options:")
        print("1. ✅ Approve - Continue execution")
        print("2. 🔄 Revise - Request revision")
        print("3. ❌ Reject - Stop execution")
        
        while True:
            choice = input("\nEnter your choice (1/2/3): ").strip()
            
            if choice == '1':
                print("✅ Approved! Continuing execution...")
                result = self.crew_client.resume_execution(execution_id)
                return self.monitor_execution(execution_id)
            
            elif choice == '2':
                feedback = input("📝 Enter revision feedback: ").strip()
                if feedback:
                    print("🔄 Requesting revision...")
                    result = self.crew_client.resume_execution(execution_id, feedback)
                    return self.monitor_execution(execution_id)
                else:
                    print("⚠️ Please provide feedback for revision")
            
            elif choice == '3':
                print("❌ Execution rejected by user")
                return False
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3")

def run_enterprise_webhook_hitl_demo():
    """Run Demo 2 with enterprise webhook HITL support."""
    print("🎯 Demo 2: Enterprise Webhook HITL - Full Content Pipeline")
    print("This demo showcases web UI integration with deployed CrewAI AMP crew")
    print()
    
    # Get crew configuration from environment
    crew_url = os.getenv('CREWAI_CREW_URL')
    crew_token = os.getenv('CREWAI_CREW_TOKEN')
    
    if not crew_url or not crew_token:
        print("❌ Missing crew configuration!")
        print("Please set the following environment variables:")
        print("  CREWAI_CREW_URL=https://your-deployed-crew.crewai.com")
        print("  CREWAI_CREW_TOKEN=your-bearer-token")
        print()
        print("💡 Get these values from your CrewAI AMP dashboard:")
        print("  1. Go to your deployed crew")
        print("  2. Copy the API URL from the Status tab")
        print("  3. Copy the Bearer Token from the Status tab")
        return False
    
    # Create crew client
    crew_client = CrewAIAMPClient(crew_url, crew_token)
    
    # Create web UI
    web_ui = Demo2WebUI(crew_client)
    
    # Get topic from user
    print("📝 Enter a topic for the content pipeline:")
    topic = input("Topic: ").strip()
    
    if not topic:
        topic = "AI Business Automation"
        print(f"Using default topic: {topic}")
    
    print()
    
    # Start the pipeline
    success = web_ui.start_content_pipeline(topic)
    
    if success:
        print("\n🎉 Demo 2 completed successfully!")
        print("💡 This demonstrates enterprise webhook HITL with AMP integration")
    else:
        print("\n❌ Demo 2 failed or was cancelled")
    
    return success

def main():
    """Main function for Demo 2."""
    print("🎯 Demo 2: Enterprise Webhook HITL - Full Content Pipeline")
    print("This demo shows web UI integration with deployed CrewAI AMP crew")
    print("featuring multi-agent content pipeline with human gate approvals")
    print()
    
    # Check if crew configuration is available
    crew_url = os.getenv('CREWAI_CREW_URL')
    crew_token = os.getenv('CREWAI_CREW_TOKEN')
    
    if not crew_url or not crew_token:
        print("⚠️ Missing crew configuration!")
        print("Please set the following environment variables:")
        print("  CREWAI_CREW_URL=https://your-deployed-crew.crewai.com")
        print("  CREWAI_CREW_TOKEN=your-bearer-token-from-amp-dashboard")
        print()
        print("💡 Get these values from your CrewAI AMP dashboard:")
        print("  1. Go to your deployed crew")
        print("  2. Copy the API URL from the Status tab")
        print("  3. Copy the Bearer Token from the Status tab")
        print()
        print("🌐 Demo UI will still be available at: http://localhost:5000/demo2")
        print("   (But crew execution will be simulated)")
    else:
        print("✅ Crew configuration found!")
        print(f"🔗 Crew URL: {crew_url}")
        print(f"🔑 Token: {crew_token[:10]}...")
    
    print()
    print("🌐 Launching Demo 2 Web UI...")
    print("📱 Open your browser and go to: http://localhost:5000/demo2")
    print()
    print("🎯 Demo 2 Web UI Features:")
    print("  • Interactive topic input")
    print("  • Real-time execution monitoring")
    print("  • Human review gates with forms")
    print("  • Content download and publishing options")
    print()
    print("Press Ctrl+C to stop the demo")
    
    try:
        # Keep the script running to maintain the webhook server
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()