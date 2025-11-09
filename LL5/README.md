# Lightning Lesson 5 — Advanced Observability & Performance

Lightning Lesson 5 focuses on building **production-ready observability** for CrewAI multi-agent systems. The lesson pairs two runnable demos that students can explore locally to understand how tracing and metrics unlock faster debugging and actionable insights.

## Lesson Objectives

- Explain why tracing and metrics are required for diagnosing multi-agent behavior.  
- Show how to enable CrewAI’s native AMP tracing with zero custom code.  
- Demonstrate a self-hosted observability stack (OpenTelemetry Collector → Tempo → Prometheus → Grafana) that captures CrewAI spans and task metrics.  
- Provide reusable code so students can adapt the instrumentation to their own crews.

## Demos in This Lesson

| Segment | Folder | Focus | Highlights |
| --- | --- | --- | --- |
| Segment 2 | `demos/segment2` | CrewAI AMP tracing | Opt-in tracing, ephemeral trace links, AMP dashboard walkthrough |
| Segment 3 | `demos/segment3` | OpenTelemetry metrics + traces | Local OTLP collector, Grafana dashboard, Tempo trace inspection |

Both demos share the same virtual environment (`requirements.txt`) and `.env` configuration. Segment 3 builds on Segment 2 by emitting spans/metrics into a local telemetry pipeline.

## Prerequisites

- Python 3.10–3.13 with the `LL5/venv` virtual environment activated.  
- Dependencies installed from the lesson root:  
  ```bash
  pip install -r requirements.txt
  ```  
- `.env` file in `LL5/` providing at minimum:
  - `OPENAI_API_KEY` (or equivalent provider key)  
  - `CREWAI_TRACING_ENABLED=true`  
  - `OTLP_ENDPOINT=http://localhost:4317` (for Segment 3)  

## How to Run the Demos

1. Clone the repository and open the `LL5/` directory.  
2. Activate the virtual environment (`source venv/bin/activate` or `.\venv\Scripts\activate`).  
3. Load environment variables: `set -a && source .env && set +a`.  
4. Pick a demo:
   - **Segment 2**: `cd demos/segment2 && python run_tracing_demo.py`  
   - **Segment 3**: `cd demos/segment3 && python run_metrics_demo.py` (requires Docker compose stack)  

Refer to each demo’s README for detailed walkthroughs, screenshots, and troubleshooting.

## Troubleshooting & Support

- Verify Docker services (`otel-collector`, `tempo`, `prometheus`, `grafana`) are healthy before starting Segment 3.  
- Increase `DEMO_FLUSH_WAIT_SEC` if spans/metrics appear delayed in Grafana/Tempo.  
- Re-run `docker compose -f demos/segment3/docker-compose.metrics.yml up --build` whenever configuration changes.

## Sources

- `project-context/LL5-demo-plan.md` — lesson planning reference  
- `demos/segment2/README.md` — AMP tracing demo instructions  
- `demos/segment3/README.md` — OpenTelemetry metrics bridge instructions

## Assumptions

- Students can run Docker locally or have access to a shared observability stack.  
- All demos target the CrewAI versions listed in `requirements.txt`.

## Open Questions

- Do we need a lightweight cloud-based collector option for students without Docker?  
- Should future iterations add alerting hooks or keep the focus on dashboards?

## Audit

- timestamp: 2025-11-09T20:07:00Z  
- persona: gpt5-codex  
- action: create-ll5-lesson-readme  
- tools: apply_patch  
- llm: gpt-5-codex (temperature=0.2, max_tokens=2048)

