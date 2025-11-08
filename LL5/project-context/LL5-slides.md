# LL5 Slide Deck Content — Advanced Observability & Performance

Use this content verbatim (or with light trimming) when building the Slidev deck under `projects/maven/presentations/LL5`. Image filenames assume you will capture fresh screenshots and place them in `projects/maven/presentations/LL5/assets/`.

## Slide 1 — Title & Hook (0:00–0:30)
- **Title**: Predictive Observability for CrewAI Multiagent Systems
- **Subtitle**: Lightning Lesson 5 · Advanced Observability & Performance
- **Slide Copy**: “When your agents slow down, do you know before the users do?”
- **Visuals**: Full-bleed gradient or hero image; overlay small stat “82% of outages are caught first by users without proactive monitoring — Gartner 2024” (feel free to verify/update stat if needed).
- **Speaker Cue**: Open with the question aloud, then introduce the session focus on preventing surprises through tracing, metrics, and predictive alerts.

## Slide 2 — Learning Outcomes (0:30–1:30)
- **Headline**: Today you will…
- **Body Copy** (three bullets):
  - “Instrument CrewAI crews with enterprise-grade tracing beyond plain logs.”
  - “Detect degradation patterns before they escalate with lightweight predictive alerts.”
  - “Track tokens and costs so optimizations are data-driven, not guesswork.”
- **Visuals**: Use lesson-branded icons or a simple checklist graphic (e.g., `LL5/assets/outcomes-icons.png` once created).
- **Speaker Cue**: Tie each outcome to the lesson projects and mention students will leave with runnable reference code.

## Slide 3 — 30-Minute Agenda (1:30–2:30)
- **Headline**: Agenda & Flow
- **Body Copy**: Create a horizontal timeline with five segments:
  1. “0:00–05:00 · Why observability + architecture overview”
  2. “05:00–12:00 · AMP tracing live demo”
  3. “12:00–20:00 · OpenTelemetry metrics bridge”
  4. “20:00–26:00 · Langtrace predictive alert”
  5. “26:00–30:00 · Wrap + student challenge”
- **Visuals**: Timeline graphic or stacked boxes; highlight key transitions in the deck theme colors.
- **Speaker Cue**: Emphasize that each segment builds toward preventing failures before users notice.

## Slide 4 — Why Observability Beyond Logs (2:30–4:00)
- **Headline**: Logs Aren’t Enough for Agentic Systems
- **Body Copy**:
  - “Agent runs span multiple tools, retries, and prompts—logs alone miss the full path.”
  - “Traces surface task timelines and root causes; metrics quantify latency, cost, and quality.”
  - “Alerting turns insights into timely action so users aren’t first responders.”
- **Visuals**: Compare “Log Stream” vs “Trace + Metrics + Alerts” using a split graphic (`LL5/assets/observability-layers.png`).
- **Speaker Cue**: Reference recent incidents or anecdotes where missing observability caused customer pain.

## Slide 5 — Target Observability Architecture (4:00–5:00)
- **Headline**: Reference Architecture for LL5 Demo
- **Body Copy** (left column):
  - “CrewAI Agents & Tasks”
  - “Built-in AMP Tracing”
  - “OpenTelemetry Collector → Grafana dashboards”
  - “Langtrace (self-hosted) for deep trace analytics”
- **Callout**: “100% achievable with free tiers / OSS — no licenses required.”
- **Visuals**: Diagram showing data flow (e.g., `LL5/assets/ll5-architecture.png`). Include arrows and labels for metrics, traces, and alerts.
- **Speaker Cue**: Highlight modularity—students can swap Grafana for Prometheus or another OSS tool.

## Slide 6 — AMP Tracing Setup (5:00–12:00 demo anchor)
- **Headline**: Enable CrewAI AMP Tracing in < 60 Seconds
- **Body Copy**: Short checklist:
  1. “Authenticate once: `crewai login`”
  2. “Flip the switch: add `tracing=True` or set `CREWAI_TRACING_ENABLED=true`”
  3. “Kick off the crew and open the AMP dashboard”
- **Code Block** (for the slide; keep monospace formatting):
  ```python
  crew = Crew(
      agents=[researcher, writer],
      tasks=[analysis, draft],
      process=Process.sequential,
      tracing=True,
      verbose=True,
  )
  result = crew.kickoff()
  ```
- **Visuals**: Include a small screenshot thumbnail of the AMP login CLI prompt if helpful (`LL5/assets/amp-login.png`).
- **Speaker Cue**: Point out that this is the base layer every production crew should adopt.

## Slide 7 — AMP Trace Walkthrough (live demo reminder)
- **Headline**: Reading the Trace like a Flight Recorder
- **Body Copy**:
  - “Timeline: identify slow agents in seconds.”
  - “LLM & tool calls: audit every prompt/response.”
  - “Cost view: watch token spend per run.”
- **Visuals**: Capture three screenshots from AMP:
  - `LL5/assets/amp-timeline.png` (task timeline)
  - `LL5/assets/amp-tool-logs.png` (tool usage panel)
  - `LL5/assets/amp-costs.png` (token/cost metrics)
- **Speaker Cue**: While demoing live, call attention to where predictive signals first emerge (longer bars, repeated retries).

## Slide 8 — OpenTelemetry Metrics Bridge (12:00–20:00 demo anchor)
- **Headline**: Export Crew Metrics with OpenTelemetry
- **Body Copy**:
  - “One-time setup bridges CrewAI runs into Grafana/Prometheus.”
  - “Track `crew_tasks_latency_ms` and `crew_tasks_success_total` every execution.”
  - “Dashboard highlights spike detection and throughput trends.”
- **Code Snippet** (trimmed for slide readability):
  ```python
  latency_histogram = metrics.get_meter("ll5").create_histogram(
      "crew_tasks_latency_ms"
  )
  @contextmanager
  def track_task(name: str):
      start = time.perf_counter()
      yield
      duration = (time.perf_counter() - start) * 1_000
      latency_histogram.record(duration, {"task": name})
  ```
- **Visuals**: Screenshot of Grafana panel (`LL5/assets/grafana-latency.png`) showing latency histogram and success counter.
- **Speaker Cue**: Reinforce that OpenTelemetry is vendor-neutral and lightweight to self-host.

## Slide 9 — Langtrace Streaming & Predictive Alert (20:00–26:00 demo anchor)
- **Headline**: Catch Slowdowns Before Users Notice
- **Body Copy**:
  - “Stream CrewAI runs into Langtrace (Docker-friendly).”
  - “Maintain a rolling window of execution times.”
  - “Fire a warning when latest run > 1.35× moving average.”
- **Code Snippet**:
  ```python
  if latest > moving_avg * 1.35:
      langtrace.log_alert(
          run_id=run_id,
          level="warning",
          message=f"Execution spike {latest:.0f} ms vs {moving_avg:.0f} ms",
      )
  ```
- **Visuals**: Langtrace run screenshot with alert banner (`LL5/assets/langtrace-alert.png`).
- **Speaker Cue**: Explain how this alert can push to Slack, PagerDuty, or email in production workflows.

## Slide 10 — Wrap-Up & Student Challenge (26:00–30:00)
- **Headline**: Your Turn to Operationalize Observability
- **Body Copy**:
  - “Layered stack = AMP tracing + OTEL dashboards + Langtrace alerts.”
  - “Predictive hooks stop regressions before users feel them.”
  - “Challenge: extend alerts to watch token spikes and error bursts.”
- **CTA Box**: “Clone the LL5 demo repo · Run the dashboards · Share learnings in the course forum.”
- **Visuals**: Use a consolidated architecture thumbnail or success metrics chart (`LL5/assets/observability-summary.png`).
- **Speaker Cue**: Invite questions and set expectations for the follow-up assignment.

## Optional Appendix Slides
- **A1 — Environment Variables Cheat Sheet**: Present a table with `CREWAI_TRACING_ENABLED`, `OTLP_ENDPOINT`, `LANGTRACE_BASE_URL`, `LANGTRACE_API_KEY`.
- **A2 — Docker Compose Snapshot**: Show sanitized snippet orchestrating OpenTelemetry Collector, Grafana, and Langtrace.
- **A3 — Troubleshooting Checklist**: Bullet “AMP trace not showing?”, “Collector not reachable?”, “Langtrace auth errors?” with quick fixes.
- Store appendix assets under `LL5/assets/appendix/`.

## MCP Canva Integration Notes
- No official Canva MCP connector exists yet. To automate slide updates from Cursor, you would need to implement a custom MCP server that wraps Canva’s REST APIs or design exports.
- Until then, build slides in Slidev (or another Markdown-friendly tool), export HTML/PDF, and manually port key visuals into Canva if you prefer that design system.

## Sources
- [CrewAI Observability Overview](https://docs.crewai.com/en/observability/overview)
- [CrewAI Tracing Guide](https://docs.crewai.com/en/observability/tracing)
- Internal context: `LL5/project-context/LL5-goal.md`, `LL5/project-context/observability.md`, `LL5/project-context/performance.md`, `LL5/project-context/LL5-demo-plan.md`

## Assumptions
- You will capture fresh screenshots from your own AMP, Grafana, and Langtrace environments to ensure visual authenticity.
- The Slidev deck will live in `projects/maven/presentations/LL5`, reusing shared assets/components configured in the presentations workspace.
- Live demo segments follow the timings and flow described in `LL5-demo-plan.md`.

## Open Questions
- Do we want to pre-bake fallback screenshot slides in case live tools are unavailable?
- Should student-facing PDFs include appendix slides or remain in the instructor version only?
- Is there value in packaging the predictive alert hook as an installable module for students?

## Audit
- timestamp: 2025-11-07T01:05:00Z
- persona: product-mgr
- action: enrich-ll5-slides-content
- tools: none
- llm: gpt-5-codex (temperature=0.2, max_tokens=2048)

