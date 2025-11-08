# Segment 2 · AMP Tracing Demo

This folder contains the live demo used in Segment 2 of the lesson. It mirrors the crew you built inside CrewAI Studio and shows how to enable built-in AMP tracing locally.

## What’s Included

- `src/crewai_observability_demo/`: the Studio-exported project (agents, tasks, crew wiring).  
- `run_tracing_demo.py`: thin wrapper that imports the exported crew, forces `tracing=True`, and kicks off the run.  
- `knowledge/`: any optional knowledge files you attached in Studio.

## Prerequisites

- Python 3.10 – 3.13 (use the LL5 virtualenv).  
- Dependencies installed from the lesson root: `pip install -r ../requirements.txt`.  
- LLM credentials in `LL5/.env` (e.g., `OPENAI_API_KEY`).  
- Optional: `CREWAI_TRACING_ENABLED=true` in `.env` so tracing stays on by default.

## Run the Demo

```bash
cd LL5/demos/segment2
python run_tracing_demo.py
```

During the run, CrewAI will ask if you’d like to view execution traces. If you answer “y”:

- An ephemeral trace link opens immediately in your browser (no AMP login required) and stays active for 24 hours.  
- You’ll also be prompted to add an email to create a CrewAI AMP account if you want to persist traces past the 24-hour window.

## Expected Output

- Console logs showing both agents completing their tasks (analysis + memo).  
- Confirmation that tracing is enabled and a link to the generated trace.  
- If `CREWAI_TRACING_ENABLED` was not set, the CLI sets it in `.env` after you opt in.

## Next Steps for Students

- Explore the AMP trace: review agent reasoning, task timelines, tool usage, and token/cost metrics.  
- Update `agents.yaml` / `tasks.yaml` to experiment with different prompts, then rerun.  
- Capture screenshots for the slides or lesson recap before the ephemeral link expires.  
- (Optional) Set up an AMP account to retain and compare multiple runs over time.

## Troubleshooting

- **Missing API key**: ensure `.env` contains `OPENAI_API_KEY` (or another provider token).  
- **No trace link shown**: rerun the script and answer “y” when prompted, or set `CREWAI_TRACING_ENABLED=true` beforehand.  
- **Need a fresh crew**: re-export from Studio and replace the `src/crewai_observability_demo` folder.
