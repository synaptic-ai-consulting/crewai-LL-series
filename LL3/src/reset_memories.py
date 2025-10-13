#!/usr/bin/env python3
"""
Reset CrewAI memory storage for LL3 demos.
Usage: python src/reset_memories.py
"""

import os
from pathlib import Path

from crewai import Crew, Agent, Task, Process, LLM


def main() -> None:
    # Ensure we run from LL3 root
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)

    # Point storage to LL3/storage
    storage_dir = project_root / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)

    print(f"🔧 CREWAI_STORAGE_DIR: {os.environ['CREWAI_STORAGE_DIR']}")

    # Minimal valid crew (no execution needed) to access reset API
    llm = LLM(model="gpt-4o-mini")
    agent = Agent(
        role="Temp Reset Agent",
        goal="Reset memories",
        backstory="Utility agent",
        llm=llm,
        memory=True,
        allow_delegation=False,
        verbose=False,
    )
    task = Task(description="noop", expected_output="noop", agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, memory=True, verbose=False)

    for t in ("short", "long", "entity", "knowledge"):
        try:
            crew.reset_memories(command_type=t)
            print(f"✅ Reset {t} memory")
        except Exception as e:  # pragma: no cover
            print(f"⚠️  Could not reset {t} memory: {e}")

    # Show remaining storage contents
    print("\n📁 Storage contents after reset:")
    if storage_dir.exists():
        names = sorted(p.name for p in storage_dir.iterdir())
        if names:
            for n in names:
                print(" -", n)
        else:
            print(" - (empty)")
    else:
        print(" - (directory not found)")


if __name__ == "__main__":
    main()


