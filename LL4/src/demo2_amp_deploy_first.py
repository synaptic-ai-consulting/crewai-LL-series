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
    
    # Check for CREW_BASE_URL and CREW_BEARER_TOKEN from .env
    crew_url = os.getenv('CREW_BASE_URL')
    crew_token = os.getenv('CREW_BEARER_TOKEN')
    webhook_url = os.getenv('WEBHOOK_BASE_URL')
    
    missing = []
    if not crew_url:
        missing.append('CREW_BASE_URL')
    if not crew_token:
        missing.append('CREW_BEARER_TOKEN')
    if not webhook_url:
        missing.append('WEBHOOK_BASE_URL')
    
    if missing:
        print("⚠️  Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print()
        print("Please ensure these are set in your .env file")
        return False
    
    print(f"✅ CREW_BASE_URL: {crew_url}")
    print(f"✅ CREW_BEARER_TOKEN: {'*' * (len(crew_token) - 4) + crew_token[-4:]}")
    print(f"✅ WEBHOOK_BASE_URL: {webhook_url}")
    
    return True

if __name__ == "__main__":
    sys.exit(main())
