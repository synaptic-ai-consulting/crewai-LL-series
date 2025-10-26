"""
Flask webhook server for CrewAI HITL (Human-in-the-Loop) demos.
Handles webhook notifications and provides web UI for human feedback.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Set template folder explicitly - run from LL4 root directory
app = Flask(__name__, template_folder='../templates')

# In-memory storage for demo purposes (use database in production)
pending_reviews: Dict[str, Dict[str, Any]] = {}
crew_executions: Dict[str, Any] = {}

def verify_bearer_token(request) -> bool:
    """Verify Bearer token authentication for webhook endpoints."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    expected_token = os.getenv('WEBHOOK_SECRET_TOKEN', 'demo-secret-token')
    return token == expected_token

def store_pending_review(execution_id: str, task_id: str, task_output: str, agent_role: str = "Unknown"):
    """Store pending review for UI display."""
    pending_reviews[execution_id] = {
        'execution_id': execution_id,
        'task_id': task_id,
        'task_output': task_output,
        'agent_role': agent_role,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending_review'
    }

@app.route('/')
def index():
    """Main demo selection page."""
    return render_template('index.html')

@app.route('/demo1')
def demo1_ui():
    """Demo 1: Open Source HITL UI."""
    return render_template('demo1_ui.html', demo_title="Open Source HITL", demo_description="Basic human_input=True functionality")

@app.route('/demo2')
def demo2_ui():
    """Demo 2: Enterprise Webhook HITL UI."""
    return render_template('demo1_ui.html', demo_title="Enterprise Webhook HITL", demo_description="Advanced webhook-based HITL with UI integration")

@app.route('/demo3')
def demo3_ui():
    """Demo 3: Multi-Agent Workflow UI."""
    return render_template('demo3_ui.html')

@app.route('/hitl', methods=['GET', 'POST'])
def hitl_webhook():
    """Receive HITL webhook notifications from CrewAI."""
    if request.method == 'GET':
        # Handle GET requests (CrewAI might send GET requests)
        print("📥 HITL Webhook GET request received")
        return jsonify({"status": "webhook_endpoint_active", "message": "HITL webhook endpoint is ready"})
    
    # Handle POST requests
    if not verify_bearer_token(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.json
        execution_id = data.get('execution_id')
        task_id = data.get('task_id')
        task_output = data.get('task_output', '')
        agent_role = data.get('agent_role', 'Unknown')
        
        if not execution_id or not task_id:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Store for UI review
        store_pending_review(execution_id, task_id, task_output, agent_role)
        
        print(f"📥 HITL Webhook received: {execution_id} - {task_id}")
        print(f"📝 Task output length: {len(task_output)} characters")
        
        return jsonify({"status": "received", "execution_id": execution_id})
    
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/hitl/iteration/<int:iteration>', methods=['POST'])
def hitl_webhook_iteration(iteration):
    """Receive HITL webhook for iterative refinement demos."""
    if not verify_bearer_token(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.json
        execution_id = data.get('execution_id')
        task_id = data.get('task_id')
        task_output = data.get('task_output', '')
        agent_role = data.get('agent_role', 'Unknown')
        
        # Store with iteration context
        store_pending_review(execution_id, task_id, task_output, agent_role)
        
        print(f"📥 HITL Iteration {iteration} Webhook: {execution_id} - {task_id}")
        
        return jsonify({"status": "received", "execution_id": execution_id, "iteration": iteration})
    
    except Exception as e:
        print(f"❌ Iteration webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/hitl/multi-agent', methods=['POST'])
def hitl_webhook_multi_agent():
    """Receive HITL webhook for multi-agent workflow demos."""
    if not verify_bearer_token(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.json
        execution_id = data.get('execution_id')
        task_id = data.get('task_id')
        task_output = data.get('task_output', '')
        agent_role = data.get('agent_role', 'Unknown')
        
        # Store for multi-agent workflow
        store_pending_review(execution_id, task_id, task_output, agent_role)
        
        print(f"📥 HITL Multi-Agent Webhook: {execution_id} - {task_id} ({agent_role})")
        
        return jsonify({"status": "received", "execution_id": execution_id})
    
    except Exception as e:
        print(f"❌ Multi-agent webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/resume', methods=['POST'])
def resume_execution():
    """Resume crew execution with human feedback."""
    try:
        data = request.json
        execution_id = data.get('execution_id')
        task_id = data.get('task_id')
        human_feedback = data.get('human_feedback', '')
        is_approve = data.get('is_approve', False)
        
        if not execution_id or not task_id:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Update pending review status
        if execution_id in pending_reviews:
            pending_reviews[execution_id]['status'] = 'resumed'
            pending_reviews[execution_id]['human_feedback'] = human_feedback
            pending_reviews[execution_id]['is_approve'] = is_approve
        
        print(f"🔄 Resume execution: {execution_id} - {task_id}")
        print(f"💬 Feedback: {human_feedback[:100]}...")
        print(f"✅ Approved: {is_approve}")
        
        return jsonify({
            "status": "resumed", 
            "execution_id": execution_id,
            "feedback_received": True
        })
    
    except Exception as e:
        print(f"❌ Resume error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/pending-reviews')
def get_pending_reviews():
    """Get all pending reviews for UI display."""
    return jsonify(list(pending_reviews.values()))

@app.route('/api/pending-reviews/<execution_id>')
def get_pending_review(execution_id):
    """Get specific pending review."""
    if execution_id in pending_reviews:
        return jsonify(pending_reviews[execution_id])
    return jsonify({"error": "Review not found"}), 404

@app.route('/webhooks/task', methods=['POST'])
def task_webhook():
    """Task completion webhook."""
    print("📋 Task webhook received")
    return jsonify({"status": "received"})

@app.route('/webhooks/step', methods=['POST'])
def step_webhook():
    """Step completion webhook."""
    print("👣 Step webhook received")
    return jsonify({"status": "received"})

@app.route('/webhooks/crew', methods=['POST'])
def crew_webhook():
    """Crew completion webhook."""
    print("🚀 Crew webhook received")
    return jsonify({"status": "received"})

@app.errorhandler(404)
def webhook_not_found(error):
    return jsonify({"error": "Webhook endpoint not found"}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Invalid authentication token"}), 401

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    print(f"🚀 Starting HITL Webhook Server on port {port}")
    print(f"🔑 Using token: {os.getenv('WEBHOOK_SECRET_TOKEN', 'demo-secret-token')}")
    app.run(host='0.0.0.0', port=port, debug=True)

