#!/usr/bin/env python3
"""
Reset CrewAI memory storage for LL3 demos.
Usage:
  python src/reset_memories.py                # Reset Crew memories, then clean legacy top-level files
  python src/reset_memories.py --dry-run      # Show what would be deleted
"""

import os
import argparse
import shutil
from pathlib import Path

from crewai import Crew, Agent, Task, Process, LLM


def delete_legacy_top_level_files(storage_dir: Path, dry_run: bool = False) -> None:
    """Delete top-level storage files and folders that are not demo-specific.

    Preserves: demo1/ and demo2/ directories. Removes any other top-level
    directories and known DB/lock files at the root of `storage_dir`.
    """
    preserve_dirs = {"demo1", "demo2"}
    removable_file_prefixes = (
        "chroma.sqlite3",
        "latest_kickoff_task_outputs.db",
        "long_term_memory_storage.db",
        "chromadb-",  # lock files like chromadb-<hash>.lock
    )

    if not storage_dir.exists():
        print(" - (storage directory not found)")
        return

    print("\n🧹 Cleaning legacy top-level items (preserving demo1/ and demo2/)...")
    for entry in storage_dir.iterdir():
        try:
            if entry.is_dir():
                if entry.name in preserve_dirs:
                    continue
                print(f"   🗑️  remove directory: {entry}")
                if not dry_run:
                    shutil.rmtree(entry, ignore_errors=True)
            else:
                if entry.name == ".crewai_user.json":
                    # Keep user config file
                    continue
                if any(entry.name.startswith(p) for p in removable_file_prefixes):
                    print(f"   🗑️  remove file:      {entry}")
                    if not dry_run:
                        try:
                            entry.unlink(missing_ok=True)
                        except TypeError:
                            if entry.exists():
                                entry.unlink()
        except Exception as e:  # pragma: no cover
            print(f"   ⚠️  could not remove {entry}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset and clean LL3 memory storage")
    parser.add_argument("--dry-run", action="store_true", help="Only print actions without deleting")
    args = parser.parse_args()
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

    # Clean legacy top-level items (non-demo)
    delete_legacy_top_level_files(storage_dir, dry_run=args.dry_run)

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


