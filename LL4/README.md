# LL4: CrewAI Human-in-the-Loop (HITL) Demos

This folder contains two demonstrations of Human-in-the-Loop workflows with CrewAI, showcasing different implementation approaches from basic open-source to enterprise deployment.

## 📋 Table of Contents

- [Overview](#overview)
- [Demo 1: Open Source HITL](#demo-1-open-source-hitl)
- [Demo 2: Enterprise AMP Deployment with HITL](#demo-2-enterprise-amp-deployment-with-hitl)
- [Architecture Comparison](#architecture-comparison)
- [Quick Start](#quick-start)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Human-in-the-Loop (HITL)** workflows allow AI agents to pause execution and request human feedback before proceeding. These demos showcase two different approaches:

| Feature | Demo 1 | Demo 2 |
|---------|--------|--------|
| **Type** | Open-source, local execution | Enterprise AMP deployment |
| **Deployment** | Local Python | CrewAI AMP (cloud) |
| **Backend** | Python Flask (`webhook_server.py`) | Node.js Express (`demo2-backend/`) |
| **Frontend** | HTML templates | React app (`demo2-frontend/`) |
| **Webhook Method** | Basic `human_input=True` | Enterprise webhook integration |
| **Tunneling** | Not required | ngrok (for public webhooks) |
| **Use Case** | Development, testing | Production-ready content pipeline |

---

## Demo 1: Open Source HITL

### Description

Demo 1 demonstrates basic HITL functionality using CrewAI's built-in `human_input=True` parameter. The crew runs **locally** and pauses for human feedback through a simple web interface.

### Features

- ✅ Local crew execution
- ✅ Basic `human_input=True` support
- ✅ Python Flask webhook server
- ✅ Simple web UI for feedback
- ✅ No cloud deployment required
- ✅ Perfect for development and testing

### Architecture

```
User Browser
    ↓
Flask Server (webhook_server.py)
    ↓
Local CrewAI Crew
    ↓ (pauses on human_input=True)
Flask Server receives notification
    ↓
Web UI shows review interface
    ↓
User provides feedback
    ↓
Crew resumes execution
```

### Setup & Run

#### 1. Install Dependencies

```bash
cd LL4
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configure Environment

```bash
cp env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY
```

#### 3. Run Demo 1

**Option A: Using the launcher script**
```bash
python run_demo.py --demo demo1
```

**Option B: Manual start**
```bash
# Start webhook server
python src/webhook_server.py

# In another terminal, run the demo
python src/demo1_opensource_hitl.py
```

#### 4. Access the UI

Open your browser to:
- **Main UI**: http://localhost:5000/demo1
- **Webhook endpoint**: http://localhost:5000/hitl

### Code Structure

```
LL4/
├── src/
│   ├── webhook_server.py       # Flask server for webhooks
│   └── demo1_opensource_hitl.py  # Demo 1 crew implementation
├── templates/
│   └── demo1_ui.html           # Web UI for Demo 1
└── config/
    ├── agents.yaml             # Agent definitions
    └── tasks.yaml              # Task definitions
```

---

## Demo 2: Enterprise AMP Deployment with HITL

### Description

Demo 2 demonstrates a **production-ready HITL workflow** with a CrewAI crew deployed to the **AMP Enterprise Platform**. It features a multi-agent content creation pipeline with human approval gates at key stages.

### Features

- ✅ Deployed on CrewAI AMP Enterprise Platform
- ✅ Multi-agent content pipeline (Researcher → Writer → Editor)
- ✅ Webhook-based HITL integration
- ✅ Node.js backend with Express
- ✅ React frontend with real-time updates
- ✅ ngrok tunnel for public webhook access
- ✅ Production-grade error handling

### Content Pipeline

```
1. Content Researcher
   ↓ (researches topic)
   🛑 HUMAN REVIEW REQUIRED
   ↓ (user approves/provides feedback)

2. Blog Writer  
   ↓ (creates blog post)
   ✓ (automatic, no review)

3. Editor
   ↓ (refines content)
   🛑 HUMAN REVIEW REQUIRED
   ↓ (user approves/provides feedback)

Final Output
```

### Architecture

```
User (Frontend - localhost:3000)
    ↓ 1. Kickoff request
Backend (Node.js - localhost:5000)
    ↓ 2. POST /kickoff + webhook URLs
ngrok (public HTTPS tunnel)
    ↓ 3. Forward to AMP
CrewAI AMP Platform (cloud)
    ↓ 4. Execute crew
    ↓ 5. Task completes, needs human input
    ↓ 6. Send webhook notification
ngrok ← AMP
    ↓ 7. Forward webhook
Backend
    ↓ 8. Store pending task
Frontend (polls for updates)
    ↓ 9. Display review UI
User provides feedback
    ↓ 10. POST /feedback
Backend
    ↓ 11. POST /resume to AMP
AMP continues execution
```

### Setup & Run

> **⚠️ Important**: Demo 2 cannot be run with `python run_demo.py --demo 2`. That command only checks your configuration. See the steps below for the actual setup.

#### Prerequisites

- ✅ Node.js 16+ and npm
- ✅ ngrok ([download](https://ngrok.com/download))
- ✅ CrewAI AMP account with deployed crew
- ✅ Python 3.10+ (for deployment if needed)

#### 0. Check Configuration (Optional)

Before starting services, verify your setup:

```bash
cd LL4
python run_demo.py --demo 2
```

This will validate your `.env` file and show any configuration issues. **This does not run the demo** - it's just a pre-flight check.

#### 1. Configure Environment

```bash
cd LL4
cp env.example .env
nano .env  # or use your editor
```

**Required variables:**
```bash
# CrewAI AMP Configuration
CREW_BASE_URL=https://your-crew-name.crewai.com
CREW_BEARER_TOKEN=your_bearer_token

# Webhook Configuration (get from step 2)
WEBHOOK_PORT=5000
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

#### 2. Start ngrok (Terminal 1)

```bash
cd LL4
./ngrok http 5000
# Or if ngrok is in PATH:
ngrok http 5000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`) and update `WEBHOOK_BASE_URL` in your `.env` file.

#### 3. Configure Webhooks in AMP Platform 🚨

**This step is critical for HITL to work!**

1. Go to https://app.crewai.com
2. Navigate to your crew deployment
3. Find webhook configuration (may be in Settings or Scheduler)
4. Add your webhook URLs:
   ```
   Task Webhook: https://your-ngrok-url.ngrok.io/api/webhooks/task
   Step Webhook: https://your-ngrok-url.ngrok.io/api/webhooks/step
   Crew Webhook: https://your-ngrok-url.ngrok.io/api/webhooks/crew
   ```
5. Save and redeploy if prompted

#### 4. Start Backend (Terminal 2)

```bash
cd LL4/demo2-backend
npm install  # First time only
npm start
```

**Verify output shows:**
```
✅ CREW_BASE_URL: https://...
✅ CREW_BEARER_TOKEN: ce07...
✅ WEBHOOK_BASE_URL: https://...ngrok.io
🚀 Server running on: http://localhost:5000
```

#### 5. Start Frontend (Terminal 3)

```bash
cd LL4/demo2-frontend
npm install  # First time only
npm start
```

Browser opens at http://localhost:3000

#### 6. Run the Demo

1. **Enter a topic** (e.g., "AI Agent Development Best Practices")
2. Click **"Generate Blog Post"**
3. **Wait for first review** - Research analysis appears
4. **Review and approve** or provide feedback
5. **Wait for second review** - Editorial review appears
6. **Final approval** - Complete blog post is generated

### Code Structure

```
LL4/
├── demo2-studio-crew/              # CrewAI crew (deployed to AMP)
│   ├── src/
│   │   └── techcorp_content_creation_pipeline/
│   │       ├── crew.py            # Crew with human_input=True
│   │       ├── main.py            # Entry point
│   │       └── config/            # YAML configurations
│   │           ├── agents.yaml
│   │           └── tasks.yaml
│   └── pyproject.toml
│
├── demo2-backend/                  # Node.js webhook server
│   ├── server.js                  # Express server
│   └── package.json
│
├── demo2-frontend/                 # React application
│   ├── src/
│   │   ├── TechCorpCrewApp.js    # Main UI component
│   │   └── TechCorpCrewApp.css
│   ├── public/
│   └── package.json
│
└── src/
    └── demo2_amp_deploy_first.py  # Configuration checker
```

### Deploying the Crew to AMP

If you need to deploy or redeploy the crew:

```bash
cd LL4/demo2-studio-crew

# Make sure you're logged in to CrewAI
crewai login

# Deploy the crew
crewai deploy

# Follow the prompts and note:
# - Deployment URL
# - Bearer token
# Update these in LL4/.env
```

---

## Architecture Comparison

### Demo 1: Local Execution

**Pros:**
- ✅ Simple setup
- ✅ No cloud dependencies
- ✅ Fast development iteration
- ✅ Works offline
- ✅ No external costs

**Cons:**
- ❌ Not production-ready
- ❌ Limited scalability
- ❌ Single-machine execution
- ❌ Basic UI

**Best for:** Development, testing, learning HITL concepts

### Demo 2: AMP Enterprise

**Pros:**
- ✅ Production-ready
- ✅ Scalable cloud execution
- ✅ Professional UI
- ✅ Enterprise features
- ✅ Team collaboration ready

**Cons:**
- ❌ More complex setup
- ❌ Requires cloud account
- ❌ ngrok or public URL needed
- ❌ Potential costs (AMP platform)

**Best for:** Production deployments, team workflows, enterprise use cases

---

## Quick Start

### Just want to see HITL in action?

**Demo 1 (5 minutes) - Can use `run_demo.py`:**
```bash
cd LL4
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Add your OPENAI_API_KEY to .env
python run_demo.py --demo 1
# Open http://localhost:5000/demo1
```

**Demo 2 (15 minutes) - Manual service startup required:**

> **⚠️ Note**: `python run_demo.py --demo 2` only checks configuration. To run Demo 2, follow these steps:

```bash
# Prerequisites: CrewAI AMP account, deployed crew, ngrok installed

# 1. Setup environment
cd LL4
cp env.example .env
# Edit .env with: CREW_BASE_URL, CREW_BEARER_TOKEN, WEBHOOK_BASE_URL

# 2. (Optional) Check configuration
python run_demo.py --demo 2  # Pre-flight check only

# 3. Start ngrok (Terminal 1)
./ngrok http 5000
# Copy the HTTPS URL and update WEBHOOK_BASE_URL in .env

# 4. Configure webhooks in AMP platform (see Demo 2 section)

# 5. Start backend (Terminal 2)
cd demo2-backend && npm start

# 6. Start frontend (Terminal 3)
cd demo2-frontend && npm start

# 7. Open http://localhost:3000 in your browser
```

---

## Troubleshooting

### Demo 1 Issues

**Problem: "Module not found" errors**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem: Crew doesn't pause**
```bash
# Solution: Check that tasks have human_input=True in config/tasks.yaml
# Verify webhook server is running on port 5000
```

**Problem: Can't access web UI**
```bash
# Solution: Ensure Flask server is running
python src/webhook_server.py
# Then visit http://localhost:5000/demo1
```

### Demo 2 Issues

**Problem: Pipeline completes without pausing**

This is the most common issue. See detailed troubleshooting:

1. **Check backend logs** - do you see `📋 TASK WEBHOOK RECEIVED`?
   - ❌ NO → AMP is not sending webhooks
   - ✅ YES → Check if `👤 HUMAN INPUT REQUIRED` appears

2. **Verify webhook configuration in AMP platform**
   - Go to app.crewai.com
   - Find your crew → Settings/Webhooks
   - Ensure webhook URLs are configured

3. **Check ngrok is running**
   - Visit http://localhost:4040 (ngrok inspector)
   - Look for incoming requests from AMP

4. **Run diagnostic script**
   ```bash
   cd LL4
   python test_webhook_diagnosis.py
   ```

**Problem: Backend fails to start**
```bash
# Check .env file
cat .env  # Should have CREW_BASE_URL, CREW_BEARER_TOKEN, WEBHOOK_BASE_URL

# Verify variable names match (not CREWAI_CREW_URL, etc.)
```

**Problem: ngrok URL keeps changing**
```bash
# Free ngrok gives new URL each restart
# Solution:
# 1. Note new ngrok URL
# 2. Update WEBHOOK_BASE_URL in .env
# 3. Update webhooks in AMP platform
# 4. Restart backend

# Or: Get static URL with ngrok paid plan
```

---

## Documentation

### Demo 2 Detailed Guides

- **[WEBHOOK-SERVER-USAGE.md](docs/WEBHOOK-SERVER-USAGE.md)** - Backend webhook server details
- **[test_webhook_diagnosis.py](test_webhook_diagnosis.py)** - Diagnostic tool for troubleshooting

### Additional Resources

- **CrewAI Documentation**: https://docs.crewai.com
- **CrewAI HITL Guide**: https://docs.crewai.com/en/enterprise/guides/human-in-the-loop
- **ngrok Documentation**: https://ngrok.com/docs

---

## Project Structure

```
LL4/
├── README.md                       # This file
├── env.example                     # Environment template
├── requirements.txt                # Python dependencies
├── run_demo.py                     # Demo launcher script
│
├── src/                           # Demo 1 source
│   ├── webhook_server.py          # Flask webhook server
│   ├── demo1_opensource_hitl.py   # Demo 1 implementation
│   └── demo2_amp_deploy_first.py  # Demo 2 config checker
│
├── config/                        # Demo 1 configuration
│   ├── agents.yaml
│   └── tasks.yaml
│
├── templates/                     # Demo 1 HTML templates
│   ├── demo1_ui.html
│   └── index.html
│
├── demo2-studio-crew/            # Demo 2 crew (AMP deployment)
│   ├── src/
│   ├── config/
│   └── pyproject.toml
│
├── demo2-backend/                # Demo 2 Node.js backend
│   ├── server.js
│   └── package.json
│
├── demo2-frontend/               # Demo 2 React frontend
│   ├── src/
│   └── package.json
│
├── docs/                         # Documentation
│   └── WEBHOOK-SERVER-USAGE.md
│
└── test/                         # Tests
```

---

## Using `run_demo.py`

The `run_demo.py` script provides different functionality for each demo:

### Demo 1: Full Execution
```bash
python run_demo.py --demo 1
# Starts Flask webhook server and runs the demo
# Access UI at http://localhost:5000/demo1
```

### Demo 2: Configuration Check Only
```bash
python run_demo.py --demo 2
# ✅ Checks your .env configuration
# ✅ Validates CREW_BASE_URL, CREW_BEARER_TOKEN, WEBHOOK_BASE_URL
# ✅ Shows setup instructions
# ❌ Does NOT start ngrok, backend, or frontend
# ❌ Does NOT run the actual demo
```

**Why the difference?**
- Demo 1 is a single Python process (easy to launch)
- Demo 2 requires three separate services: ngrok (Go binary), Node.js backend, and React frontend
- Demo 2 services must be started manually (see Demo 2 Setup section)

### Other Commands
```bash
python run_demo.py --list-demos  # Show available demos
python run_demo.py --validate    # Validate environment setup
python run_demo.py --setup       # Install Python dependencies
```

## Contributing

These demos are part of the CrewAI Lightning Lesson series. For questions or issues:

1. Check the troubleshooting section above
2. Review the detailed documentation in `docs/`
3. Run diagnostic tools for Demo 2

---

## License

See the main project LICENSE file.

---

## Summary

**Choose Demo 1** if you want:
- Quick local testing
- Simple HITL learning
- Development environment
- No cloud setup
- ✅ **Can use `run_demo.py --demo 1`**

**Choose Demo 2** if you want:
- Production deployment
- Enterprise features
- Multi-agent content pipeline
- Scalable architecture
- ⚠️ **Requires manual service startup** (not via `run_demo.py`)

Both demos showcase the power of Human-in-the-Loop workflows with CrewAI, just at different scales and complexity levels. Start with Demo 1 to learn the concepts, then move to Demo 2 for production implementation.

### Quick Reference

| Aspect | Demo 1 | Demo 2 |
|--------|--------|--------|
| **Launcher** | `python run_demo.py --demo 1` | Manual (3 terminals) |
| **Setup Time** | 5 minutes | 15 minutes |
| **Services** | 1 (Flask) | 3 (ngrok + Node.js + React) |
| **Deployment** | Local only | CrewAI AMP (cloud) |
| **Best For** | Learning, testing | Production |

Happy building! 🚀

