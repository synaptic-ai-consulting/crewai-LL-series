# LL5 Demo Plan — Advanced Observability & Performance

## Session Objective
- Reinforce the lesson goal from `LL5-goal.md` by demonstrating enterprise-ready observability and predictive performance monitoring for CrewAI multiagent systems.
- Ship reusable reference code that students can extend on their own projects to enable tracing, metrics export, and proactive alerting without paid licenses.

## 30-Minute Agenda
- 00:00–05:00 — Context and success criteria for observability & performance.
- 05:00–12:00 — Enable CrewAI AMP tracing and inspect a baseline run.
- 12:00–20:00 — Wire CrewAI metrics into OpenTelemetry for local dashboards.
- 20:00–26:00 — Add Langtrace streaming plus a predictive slowdown alert hook.
- 26:00–30:00 — Recap, student challenge, and Q&A call-to-action.

## Demo Environment Setup
- Python 3.10+ project with `crewai`, `crewai-tools`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, and `langtrace` installed.
- `.env` file storing `CREWAI_TRACING_ENABLED=true`, `OTLP_ENDPOINT=http://localhost:4317`, and (optional) `LANGTRACE_API_KEY` for hosted use; no key needed when running the open-source Langtrace server locally.
- Local OpenTelemetry Collector running with the default OTLP receiver; provide a prebuilt `docker-compose` snippet in lesson materials.
- Optional: Langtrace open-source server via Docker (`docker run -p 3100:3100 langtrace/langtrace:latest`).

## Segment Details

### Segment 1 — Kickoff & Baseline Observability (0:00–5:00)
- Align the room on why observability is more than logging: link to lesson goals about predictive performance monitoring and failure prevention.
- Show the target architecture diagram (CrewAI agents ⟶ AMP tracing ⟶ OpenTelemetry ⟶ Langtrace dashboards).
- Call out key metrics students should watch (execution time, token usage, success rate, cost) referencing the observability and performance briefs.

### Segment 2 — Enable CrewAI AMP Tracing (5:00–12:00)
1. Walk through authentication `crewai login` (already completed) and point to the AMP dashboard tabs students will explore.
2. Demo enabling tracing inline, highlighting both parameter and env-var options:

```python
from crewai import Agent, Crew, Process, Task

researcher = Agent(
    role="Research Analyst",
    goal="Gather timely insights",
    backstory="Efficient fact-finder tuned for short briefs",
    verbose=True,
)

writer = Agent(
    role="Content Synthesizer",
    goal="Produce executive-ready output",
    backstory="Transforms findings into concise memos",
    verbose=True,
)

analysis = Task(
    description="Summarize the latest CrewAI observability updates",
    expected_output="Three bullet executive summary",
    agent=researcher,
)

draft = Task(
    description="Draft a stakeholder memo using the research findings",
    expected_output="One-page memo",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[analysis, draft],
    process=Process.sequential,
    tracing=True,
    verbose=True,
)

result = crew.kickoff()
print(result)
```

3. Run once, then pivot to the AMP dashboard to highlight agent decisions, task timelines, token/cost metrics, and error tracing features.
4. Note the global `CREWAI_TRACING_ENABLED=true` toggle for teams who prefer zero-code config.

### Segment 3 — OpenTelemetry Metrics Export (12:00–20:00)
- Position OpenTelemetry as a free, vendor-neutral option students can self-host to build dashboards (e.g., Grafana, Prometheus) without license fees.
- Introduce a lightweight metrics bridge that listens to CrewAI task completions and emits spans/metrics:

```python
import os
import time
from contextlib import contextmanager

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")

resource = Resource.create({"service.name": "ll5-demo-crew"})

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT))
)
trace.set_tracer_provider(tracer_provider)

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[
        PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=OTLP_ENDPOINT),
            export_interval_millis=5000,
        )
    ],
)
metrics.set_meter_provider(meter_provider)

success_counter = metrics.get_meter("ll5-demo").create_counter(
    "crew_tasks_success_total",
    description="Number of successful CrewAI tasks",
)

latency_histogram = metrics.get_meter("ll5-demo").create_histogram(
    "crew_tasks_latency_ms",
    description="CrewAI task latency in milliseconds",
)

@contextmanager
def track_task(task_name: str):
    tracer = trace.get_tracer("ll5-demo")
    start = time.perf_counter()
    with tracer.start_as_current_span(task_name) as span:
        yield
        duration_ms = (time.perf_counter() - start) * 1_000
        span.set_attribute("crew.task.duration_ms", duration_ms)
        latency_histogram.record(duration_ms, {"crew.task": task_name})
        success_counter.add(1, {"crew.task": task_name})
```

- Wrap each `Task.execute()` call (show how to decorate or patch in the demo repo) and preview Grafana dashboard with latency histogram and success counter widgets.

### Segment 4 — Langtrace Streaming & Predictive Alerts (20:00–26:00)
- Highlight Langtrace as an open-source tracing UI (Docker deployable) that augments AMP with conversational drill-downs.
- Show how to forward CrewAI events through Langtrace while adding a simple predictive slowdown detector that compares the last five runs to a moving baseline:

```python
import statistics
from collections import deque

from langtrace import Langtrace

langtrace = Langtrace(
    api_key=os.getenv("LANGTRACE_API_KEY", "demo"),
    project_name="ll5-demo",
    base_url=os.getenv("LANGTRACE_BASE_URL", "http://localhost:3100"),
)

latency_history = deque(maxlen=5)

def record_run(run_id: str, task_latencies_ms: dict[str, float]):
    langtrace.log_run(
        run_id=run_id,
        metrics={f"task.{name}.latency_ms": value for name, value in task_latencies_ms.items()},
    )

    total_latency = sum(task_latencies_ms.values())
    latency_history.append(total_latency)

    if len(latency_history) == latency_history.maxlen:
        moving_avg = statistics.fmean(list(latency_history)[:-1])
        latest = latency_history[-1]
        if latest > moving_avg * 1.35:
            langtrace.log_alert(
                run_id=run_id,
                level="warning",
                message=f"Execution time spike: {latest:.0f} ms vs baseline {moving_avg:.0f} ms",
            )
```

- During the demo, run the crew twice with a simulated slow tool to trigger the alert and show the Langtrace UI highlighting the warning.
- Tie back to the “prevent failures before they occur” insight by explaining how this early-warning hook can fan out to Slack or PagerDuty in real deployments.

### Segment 5 — Wrap-Up & Student Challenge (26:00–30:00)
- Recap the layered observability stack and what each tool surfaces.
- Challenge students to extend the predictive alert to watch token spikes or error-rate increases.
- Share the GitHub branch containing the demo code and configuration snippets for self-paced exploration.

## Key Metrics & Talking Points
- Execution time distribution (latency histogram) to illustrate workload hotspots.
- Token usage per task from the AMP trace to motivate cost optimization discussions.
- Success vs. failure counts and how alert thresholds can be tuned to reduce noise.
- Impact of tracing on developer velocity—faster debugging, reproducible insights, and audit trails.

## Student Follow-Up Assets
- Demo repository folder with ready-to-run scripts (`crew_run.py`, `telemetry.py`, `langtrace_hooks.py`).
- `docker-compose.yml` templates for OpenTelemetry Collector, Grafana, and Langtrace.
- Screenshot walkthrough of AMP trace views annotated with the metrics discussed in class.
- Cheat sheet summarizing environment variables, key commands, and troubleshooting steps.

## Sources
- [CrewAI Observability Overview](https://docs.crewai.com/en/observability/overview)
- [CrewAI Tracing Guide](https://docs.crewai.com/en/observability/tracing)
- Internal context: `LL5/project-context/LL5-goal.md`

## Assumptions
- Students can run Docker locally or have access to a shared collector/observability stack provided by the instructor.
- No paid SaaS tiers are required; all integrations rely on open-source deployments or free community editions.
- CrewAI version used in class matches the repository baseline to avoid API drift during the live demo.
- Hosted Langtrace usage remains optional; the open-source container meets lesson goals.

## Open Questions
- Should we pre-record fallback trace screenshots in case network access to AMP or Langtrace fails during the live session?
- Do we need to provide a lightweight alternative for students who cannot run Docker (e.g., Cloud-based collector sandbox)?
- What success metrics will we collect from students to measure adoption of the observability stack after the lesson?

## Audit
- timestamp: 2025-11-07T00:00:00Z
- persona: product-mgr
- action: create-ll5-demo-plan
- tools: none
- llm: gpt-5-codex (temperature=0.2, max_tokens=2048)

