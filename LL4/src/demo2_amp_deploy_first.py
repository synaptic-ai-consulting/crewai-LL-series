#!/usr/bin/env python3
"""
Demo 2: TechCorp Content Creation Pipeline with HITL
Configuration checker and instructions provider
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Main function - checks configuration and provides instructions."""
    print("🎯 Demo 2: TechCorp Content Creation Pipeline with HITL")
    print("=" * 70)
    print()
    
    # Get the LL4 directory (parent of src)
    ll4_dir = Path(__file__).parent.parent
    os.chdir(ll4_dir)
    
    # Load environment variables from LL4/.env
    env_path = ll4_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
    else:
        print(f"⚠️  .env file not found at: {env_path}")
        return 1
    
    print()
    
    # Check for AMP configuration
    if not check_configuration():
        return 1
    
    print()
    print("=" * 70)
    print("✅ Configuration OK!")
    print()
    print("📋 To run Demo 2, please start the following services manually:")
    print()
    print("1️⃣  Start ngrok (in a separate terminal):")
    print("   ngrok http 5000")
    print()
    print("2️⃣  Start the backend (in a separate terminal):")
    print("   cd demo2-backend")
    print("   npm start")
    print()
    print("3️⃣  Start the frontend (in a separate terminal):")
    print("   cd demo2-frontend")
    print("   npm start")
    print()
    print("🌐 Once all services are running:")
    print("   Frontend: http://localhost:3000")
    print("   Backend:  http://localhost:5000")
    print()
    print("=" * 70)
    
    return 0

def check_configuration():
    """Check if required configuration is present."""
    print("🔍 Checking configuration...")
    print()
    
    # Check for CREW_BASE_URL and CREW_BEARER_TOKEN from .env
    crew_url = os.getenv('CREW_BASE_URL')
    crew_token = os.getenv('CREW_BEARER_TOKEN')
    webhook_url = os.getenv('WEBHOOK_BASE_URL')
    
    missing = []
    warnings = []
    
    if not crew_url:
        missing.append('CREW_BASE_URL')
    else:
        print(f"✅ CREW_BASE_URL: {crew_url}")
    
    if not crew_token:
        missing.append('CREW_BEARER_TOKEN')
    else:
        masked_token = '*' * (len(crew_token) - 4) + crew_token[-4:] if len(crew_token) > 4 else '***'
        print(f"✅ CREW_BEARER_TOKEN: {masked_token}")
    
    if not webhook_url:
        missing.append('WEBHOOK_BASE_URL')
        print("❌ WEBHOOK_BASE_URL: Not set")
    elif not webhook_url.startswith('https://'):
        warnings.append('WEBHOOK_BASE_URL should be HTTPS (use ngrok)')
        print(f"⚠️  WEBHOOK_BASE_URL: {webhook_url} (should be HTTPS)")
    elif 'localhost' in webhook_url or '127.0.0.1' in webhook_url:
        warnings.append('WEBHOOK_BASE_URL cannot be localhost for CrewAI AMP')
        print(f"⚠️  WEBHOOK_BASE_URL: {webhook_url} (cannot use localhost)")
    else:
        print(f"✅ WEBHOOK_BASE_URL: {webhook_url}")
    
    print()
    
    if missing:
        print("❌ CONFIGURATION ERROR:")
        print("   Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print()
        print("📖 Setup Instructions:")
        print("   1. See docs/ENV_CONFIGURATION_GUIDE.md for detailed setup")
        print("   2. Create LL4/.env file with required variables")
        print("   3. Start ngrok: ngrok http 5000")
        print("   4. Copy ngrok HTTPS URL to WEBHOOK_BASE_URL in .env")
        print()
        return False
    
    if warnings:
        print("⚠️  CONFIGURATION WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
        print("🔧 For HITL to work properly:")
        print("   1. WEBHOOK_BASE_URL must be a public HTTPS URL")
        print("   2. Start ngrok: ngrok http 5000")
        print("   3. Update WEBHOOK_BASE_URL in .env with ngrok URL")
        print("   4. Configure webhooks in CrewAI AMP platform")
        print()
    
    # Check if AMP webhooks are configured
    print("⚠️  CRITICAL: Ensure webhooks are configured in CrewAI AMP:")
    print("   1. Go to https://app.crewai.com")
    print("   2. Navigate to your crew deployment")
    print("   3. Go to Settings → Webhooks")
    print("   4. Add webhook URLs:")
    print(f"      - Task: {webhook_url}/api/webhooks/task" if webhook_url else "      - Task: <ngrok-url>/api/webhooks/task")
    print(f"      - Step: {webhook_url}/api/webhooks/step" if webhook_url else "      - Step: <ngrok-url>/api/webhooks/step")
    print(f"      - Crew: {webhook_url}/api/webhooks/crew" if webhook_url else "      - Crew: <ngrok-url>/api/webhooks/crew")
    print("   5. Save and redeploy if required")
    print()
    
    return True

if __name__ == "__main__":
    sys.exit(main())
