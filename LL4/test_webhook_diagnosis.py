#!/usr/bin/env python3
"""
Diagnostic script to test if CrewAI AMP is sending webhooks
and if the crew is properly configured for HITL
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment
ll4_dir = Path(__file__).parent
load_dotenv(ll4_dir / '.env')

CREW_BASE_URL = os.getenv('CREW_BASE_URL')
CREW_BEARER_TOKEN = os.getenv('CREW_BEARER_TOKEN')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL')

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_configuration():
    """Test if environment is configured correctly."""
    print_section("1. CONFIGURATION CHECK")
    
    issues = []
    
    if not CREW_BASE_URL:
        issues.append("❌ CREW_BASE_URL not set")
    else:
        print(f"✅ CREW_BASE_URL: {CREW_BASE_URL}")
    
    if not CREW_BEARER_TOKEN:
        issues.append("❌ CREW_BEARER_TOKEN not set")
    else:
        print(f"✅ CREW_BEARER_TOKEN: {CREW_BEARER_TOKEN[:8]}...")
    
    if not WEBHOOK_BASE_URL:
        issues.append("❌ WEBHOOK_BASE_URL not set")
    else:
        print(f"✅ WEBHOOK_BASE_URL: {WEBHOOK_BASE_URL}")
    
    if issues:
        print("\n".join(issues))
        return False
    
    return True

def test_webhook_reachability():
    """Test if webhook URL is reachable from internet."""
    print_section("2. WEBHOOK REACHABILITY CHECK")
    
    if not WEBHOOK_BASE_URL:
        print("❌ Cannot test - WEBHOOK_BASE_URL not set")
        return False
    
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Webhook URL is reachable")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Webhook URL returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook URL is NOT reachable: {e}")
        print("\n💡 Possible issues:")
        print("   - ngrok not running")
        print("   - Backend server not running")
        print("   - Firewall blocking")
        return False

def get_crew_inputs():
    """Get crew input schema."""
    print_section("3. CREW INPUT SCHEMA")
    
    try:
        response = requests.get(
            f"{CREW_BASE_URL}/inputs",
            headers={'Authorization': f'Bearer {CREW_BEARER_TOKEN}'},
            timeout=10
        )
        response.raise_for_status()
        
        inputs = response.json()
        print("✅ Successfully retrieved input schema")
        print(f"\nInputs: {json.dumps(inputs, indent=2)}")
        return inputs
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get inputs: {e}")
        return None

def test_kickoff_with_webhook():
    """Test kickoff with webhook URLs."""
    print_section("4. TEST KICKOFF WITH WEBHOOKS")
    
    print("🚀 Attempting kickoff with webhook URLs...")
    print(f"   Task webhook: {WEBHOOK_BASE_URL}/api/webhooks/task")
    print(f"   Step webhook: {WEBHOOK_BASE_URL}/api/webhooks/step")
    print(f"   Crew webhook: {WEBHOOK_BASE_URL}/api/webhooks/crew")
    
    try:
        payload = {
            "inputs": {
                "topic": "HITL Diagnostic Test"
            },
            "taskWebhookUrl": f"{WEBHOOK_BASE_URL}/api/webhooks/task",
            "stepWebhookUrl": f"{WEBHOOK_BASE_URL}/api/webhooks/step",
            "crewWebhookUrl": f"{WEBHOOK_BASE_URL}/api/webhooks/crew"
        }
        
        print(f"\n📤 Sending kickoff request...")
        response = requests.post(
            f"{CREW_BASE_URL}/kickoff",
            headers={
                'Authorization': f'Bearer {CREW_BEARER_TOKEN}',
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        kickoff_id = result.get('kickoff_id')
        
        print(f"✅ Kickoff successful!")
        print(f"   Execution ID: {kickoff_id}")
        
        return kickoff_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Kickoff failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None

def monitor_execution(kickoff_id, duration=60):
    """Monitor execution status and check for webhooks."""
    print_section("5. MONITORING EXECUTION")
    
    print(f"⏱️  Monitoring for {duration} seconds...")
    print(f"   Watch your BACKEND LOGS for webhook notifications!")
    print(f"   You should see: 📋 TASK WEBHOOK RECEIVED")
    print()
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < duration:
        try:
            response = requests.get(
                f"{CREW_BASE_URL}/status/{kickoff_id}",
                headers={'Authorization': f'Bearer {CREW_BEARER_TOKEN}'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status != last_status:
                    print(f"[{int(time.time() - start_time)}s] Status: {status}")
                    last_status = status
                
                if status in ['completed', 'failed', 'error']:
                    print(f"\n✅ Execution {status}")
                    print(f"\n📊 Final result:")
                    print(json.dumps(data, indent=2))
                    
                    # Check if it completed too fast (indication HITL didn't work)
                    if status == 'completed' and time.time() - start_time < 30:
                        print(f"\n⚠️  WARNING: Completed in {int(time.time() - start_time)}s")
                        print("   This is too fast for HITL workflow!")
                        print("   Expected: Should pause for human input")
                    
                    return data
            
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Status check failed: {e}")
            time.sleep(3)
    
    print(f"\n⏱️  Monitoring timeout reached")
    return None

def main():
    """Run diagnostic tests."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           CrewAI HITL Webhook Diagnostic Tool                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Configuration
    if not test_configuration():
        print("\n❌ Configuration errors found. Fix .env file first.")
        return 1
    
    # Test 2: Webhook reachability
    if not test_webhook_reachability():
        print("\n⚠️  Webhook URL not reachable. Continuing anyway...")
    
    # Test 3: Get inputs
    get_crew_inputs()
    
    # Test 4: Kickoff
    print("\n" + "="*70)
    user_input = input("\n🤔 Do you want to test a crew kickoff? (y/n): ")
    if user_input.lower() != 'y':
        print("\nSkipping kickoff test. Exiting.")
        return 0
    
    kickoff_id = test_kickoff_with_webhook()
    if not kickoff_id:
        print("\n❌ Kickoff failed. Cannot continue.")
        return 1
    
    # Test 5: Monitor
    print("\n" + "="*70)
    print("🎯 KEY DIAGNOSTIC:")
    print("   1. Watch your BACKEND logs (demo2-backend terminal)")
    print("   2. You should see: 📋 TASK WEBHOOK RECEIVED")
    print("   3. If you DON'T see webhooks, AMP is not sending them")
    print("="*70)
    
    monitor_execution(kickoff_id, duration=120)
    
    print_section("DIAGNOSTIC COMPLETE")
    
    print("🔍 KEY QUESTIONS:")
    print()
    print("1. Did you see '📋 TASK WEBHOOK RECEIVED' in backend logs?")
    print("   ✅ YES → Webhooks work, issue is elsewhere")
    print("   ❌ NO  → AMP is NOT sending webhooks (root cause)")
    print()
    print("2. Did the crew complete in < 30 seconds?")
    print("   ✅ YES → HITL is NOT working (tasks not pausing)")
    print("   ❌ NO  → Good, but check if it actually paused")
    print()
    print("3. Did backend show '👤 HUMAN INPUT REQUIRED'?")
    print("   ✅ YES → Backend detected HITL task correctly")
    print("   ❌ NO  → Backend didn't detect HITL (check logic)")
    
    print("\n📝 Next Steps:")
    print("   If webhooks NOT received:")
    print("   → Problem: AMP not configured to send webhooks")
    print("   → Check: AMP deployment settings, not just kickoff request")
    print("   → Solution: Find correct webhook config in AMP platform")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


