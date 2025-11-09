"""
Segment 3 demo: wire CrewAI task execution into OpenTelemetry.
"""

from __future__ import annotations

import os
import time
from textwrap import dedent

from crewai import Agent, Crew, Process, Task

# Importing telemetry registers the event listeners and exporters.
from telemetry import CREW_TELEMETRY_BRIDGE  # noqa: F401  # pylint: disable=unused-import


def build_agents() -> tuple[Agent, Agent]:
    researcher = Agent(
        role="Research Analyst",
        goal="Surface the newest CrewAI observability tips",
        backstory=dedent(
            """\
            Focused on identifying upgrades to tracing and metrics.
            Comfortable digesting docs and changelogs."""
        ),
        verbose=True,
    )

    writer = Agent(
        role="Content Synthesizer",
        goal="Summarize the observability upgrades for leadership",
        backstory=dedent(
            """\
            Turns raw findings into actionable internal memos.
            Highlights impact on performance and reliability."""
        ),
        verbose=True,
    )

    return researcher, writer


def build_tasks(researcher: Agent, writer: Agent) -> tuple[Task, Task]:
    analysis = Task(
        description=dedent(
            """\
            Investigate the latest CrewAI observability documentation.
            List any tracing or metrics improvements announced this quarter."""
        ),
        expected_output="Bullet list covering features, benefits, and links to docs.",
        agent=researcher,
    )

    draft = Task(
        description=dedent(
            """\
            Using the research summary, draft an internal update for the platform team.
            Include one recommendation for enabling tracing in current multi-agent flows."""
        ),
        expected_output="Executive summary with two insights and one call to action.",
        agent=writer,
    )

    return analysis, draft


def main() -> None:
    iterations = max(int(os.getenv("DEMO_RUN_ITERATIONS", "3")), 1)
    delay_between_runs = max(float(os.getenv("DEMO_RUN_DELAY_SEC", "2.0")), 0.0)
    flush_wait_seconds = max(float(os.getenv("DEMO_FLUSH_WAIT_SEC", "3.0")), 0.0)

    results: list[str] = []

    for iteration in range(1, iterations + 1):
        researcher, writer = build_agents()
        analysis, draft = build_tasks(researcher, writer)

        crew = Crew(
            agents=[researcher, writer],
            tasks=[analysis, draft],
            process=Process.sequential,
            tracing=True,
            verbose=True,
        )

        print(f"\n=== Crew Iteration {iteration}/{iterations} ===")
        result = crew.kickoff()
        results.append(str(result))

        if delay_between_runs and iteration < iterations:
            print(f"\nSleeping {delay_between_runs:.1f}s before next run to keep metrics streaming...")
            time.sleep(delay_between_runs)

    print("\n=== Crew Results (most recent last) ===")
    for idx, output in enumerate(results, start=1):
        print(f"\n--- Result {idx} ---\n{output}")

    if os.getenv("OTLP_ENDPOINT"):
        print(f"\nOTLP exports sent to: {os.getenv('OTLP_ENDPOINT')}")
    else:
        print("\nOTLP_ENDPOINT not set. Defaulting to http://localhost:4317.")
    print("Check your Grafana/Prometheus dashboards for latency + success metrics.")

    if flush_wait_seconds:
        print(f"\nWaiting {flush_wait_seconds:.1f}s to allow OpenTelemetry exporters to flush...")
        time.sleep(flush_wait_seconds)


if __name__ == "__main__":
    main()


