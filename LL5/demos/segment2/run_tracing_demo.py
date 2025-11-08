"""
Segment 2 demo script: run the CrewAI Studio-exported crew locally with tracing.

This wraps the generated project in `src/crewai_observability_demo` so students can
execute the same crew they saw in CrewAI AMP while capturing traces locally.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from crewai_observability_demo.crew import CrewaiObservabilityDemoCrew  # noqa: E402


def main() -> None:
    crew_factory = CrewaiObservabilityDemoCrew()
    crew = crew_factory.crew()

    # Ensure tracing is enabled even if the env var is unset.
    crew.tracing = True

    result = crew.kickoff()

    print("\n=== Crew Result ===")
    print(result)
    print("\nTracing enabled:", crew.tracing)
    if os.getenv("CREWAI_TRACING_ENABLED"):
        print("CREWAI_TRACING_ENABLED detected; all crews are tracing by default.")
    print("Visit https://app.crewai.com → Traces to inspect this run.")


if __name__ == "__main__":
    main()

