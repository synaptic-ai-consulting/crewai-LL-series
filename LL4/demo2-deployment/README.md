# Demo 2: Enterprise Webhook HITL

This is the deployment package for Demo 2, showcasing enterprise webhook-based Human-in-the-Loop (HITL) workflows with CrewAI AMP.

## Features

- Multi-agent content pipeline (Researcher → Writer → Editor)
- Human gate approvals at each stage
- Webhook-based HITL integration
- Enterprise AMP deployment

## Deployment

This package is designed to be deployed to CrewAI AMP using:

```bash
crewai deploy create
```

## Configuration

Ensure your `.env` file contains:
- `OPENAI_API_KEY`: Your OpenAI API key
- `CREWAI_API_KEY`: Your CrewAI AMP API key (for enterprise features)

## Usage

After deployment, this crew can be invoked via webhooks for HITL workflows.


