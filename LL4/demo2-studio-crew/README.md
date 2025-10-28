# TechCorp Content Creation Pipeline Crew

This CrewAI crew is part of **Demo 2: Enterprise AMP Deployment with HITL** in the LL4 Lightning Lesson series.

## Overview

A production-ready, multi-agent content creation pipeline with **Human-in-the-Loop (HITL)** approval gates, deployed on **CrewAI AMP Enterprise Platform**.

### Pipeline Flow

```
1. Content Researcher
   ↓ Research topic
   🛑 HUMAN REVIEW (approve/provide feedback)
   
2. Blog Writer
   ↓ Create blog post (using approved research)
   ✓ Automatic (no review)
   
3. Editor
   ↓ Refine content
   🛑 HUMAN REVIEW (final approval)
   
Final Output: Publication-ready blog post
```

## Crew Structure

### Agents (`config/agents.yaml`)

1. **Content Researcher** - Gathers comprehensive information and insights
2. **Blog Writer** - Creates engaging blog posts from research
3. **Editor** - Polishes content for publication

### Tasks (`config/tasks.yaml`)

1. **research_topic_analysis** - `human_input: true` ✅
2. **blog_post_creation** - `human_input: false` 
3. **editorial_review_and_refinement** - `human_input: true` ✅

### Configuration (`crew.py`)

- Uses `@CrewBase` decorator pattern
- Sequential process
- HITL enabled on 2 of 3 tasks
- Webhook-based communication with Demo 2 backend

## Deployment Status

This crew is **currently deployed** on CrewAI AMP Enterprise Platform.

**Deployment URL**: (from your `.env`)
```
CREW_BASE_URL=https://techcorp-content-creation-pipeline-v1-xxxxx.crewai.com
```

## How to Use This Crew

**You don't run this crew directly from this folder.** It's deployed on AMP and accessed through the Demo 2 system.

### To Use the Deployed Crew:

See the main **[LL4/README.md](../README.md)** for complete Demo 2 setup instructions.

**Quick summary:**
1. Configure `.env` in `LL4/` directory
2. Start ngrok tunnel
3. Start Node.js backend (`demo2-backend/`)
4. Start React frontend (`demo2-frontend/`)
5. Access UI at http://localhost:3000

## Local Testing (Optional)

To test the crew logic locally **without HITL**:

```bash
cd LL4/demo2-studio-crew

# Install dependencies
crewai install

# Set environment variables
export OPENAI_API_KEY=your_key_here
export SERPER_API_KEY=your_key_here  # for SerperDevTool

# Run locally
crewai run
```

**Note**: Local execution won't trigger HITL webhooks. For full HITL testing, use the deployed version through Demo 2.

## Deploying/Redeploying

If you need to deploy or update the crew on AMP:

```bash
cd LL4/demo2-studio-crew

# Login to CrewAI (first time only)
crewai login

# Deploy the crew
crewai deploy

# Follow prompts and note:
# - Deployment URL → Update CREW_BASE_URL in LL4/.env
# - Bearer token → Update CREW_BEARER_TOKEN in LL4/.env
```

After deployment:
1. Update `LL4/.env` with new URLs/tokens
2. Configure webhooks in AMP platform (see LL4/README.md)
3. Restart Demo 2 services

## File Structure

```
demo2-studio-crew/
├── src/techcorp_content_creation_pipeline/
│   ├── crew.py              # Crew definition with human_input=True
│   ├── main.py              # Entry point for local testing
│   ├── config/
│   │   ├── agents.yaml      # Agent definitions
│   │   └── tasks.yaml       # Task definitions with HITL flags
│   └── tools/
│       └── custom_tool.py   # Custom tools (if any)
├── pyproject.toml           # Dependencies and metadata
└── README.md                # This file
```

## Requirements

- Python >=3.10 <3.14
- CrewAI CLI (`pip install crewai`)
- OpenAI API key
- SerperDev API key (for research tool)
- CrewAI AMP account (for deployment)

## HITL Configuration

Tasks with `human_input=True` will:
1. Complete execution
2. Send webhook to Demo 2 backend
3. Pause execution waiting for human feedback
4. Resume after approval/feedback received

**Critical**: Webhooks must be configured in the AMP platform for HITL to work. See [LL4/README.md](../README.md) for webhook setup instructions.

## Troubleshooting

### Crew doesn't pause for HITL
- Verify webhooks are configured in AMP platform
- Check that `human_input=True` in `config/tasks.yaml`
- Ensure crew was deployed recently (after HITL settings added)

### Local run fails
- Check API keys are set
- Verify dependencies: `crewai install`
- Try: `pip install crewai[tools]`

### Deployment fails
- Ensure logged in: `crewai login`
- Check network connection
- Verify pyproject.toml is valid

## Related Documentation

- **[LL4/README.md](../README.md)** - Complete Demo 2 setup guide
- **[LL4/docs/WEBHOOK-SERVER-USAGE.md](../docs/WEBHOOK-SERVER-USAGE.md)** - Backend webhook details
- **[CrewAI Documentation](https://docs.crewai.com)** - Official CrewAI docs
- **[CrewAI HITL Guide](https://docs.crewai.com/en/enterprise/guides/human-in-the-loop)** - Enterprise HITL documentation

## Support

For Demo 2 specific issues:
- Check troubleshooting in [LL4/README.md](../README.md)
- Review diagnostic logs
- Run `python LL4/test_webhook_diagnosis.py`

For CrewAI platform issues:
- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewai)

---

**Part of**: LL4 Lightning Lesson Series - Demo 2: Enterprise AMP Deployment with HITL
