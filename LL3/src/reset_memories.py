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
    parser.add_argument("--dry-run", action="store_true", help="Only print actions without deleting (for root clean)")
    parser.add_argument("--demo", choices=["1", "2", "demo1", "demo2", "all"], help="Reset memories for a specific demo (demo1/demo2) or both")
    parser.add_argument("--clean-root", action="store_true", help="Also clean legacy files in LL3/storage root (ignored when --demo is set)")
    parser.add_argument("--purge", action="store_true", help="Dangerous: fully delete demo storage files (Chroma/SQLite) for selected demo(s)")
    args = parser.parse_args()
    # Ensure we run from LL3 root
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)

    def purge_path(path: Path) -> None:
        if not path.exists():
            return
        print(f"\n🗑️  Purging storage files at: {path}")
        for entry in list(path.iterdir()):
            try:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    entry.unlink(missing_ok=True)
            except Exception as e:
                print(f"   ⚠️  Could not delete {entry}: {e}")

    def reset_at(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        os.environ["CREWAI_STORAGE_DIR"] = str(path)
        print(f"\n🔧 CREWAI_STORAGE_DIR: {os.environ['CREWAI_STORAGE_DIR']}")

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

        # Show remaining storage contents for this path
        print("\n📁 Storage contents after reset:")
        if path.exists():
            names = sorted(p.name for p in path.iterdir())
            if names:
                for n in names:
                    print(" -", n)
            else:
                print(" - (empty)")
        else:
            print(" - (directory not found)")

    storage_root = project_root / "storage"

    if args.demo in ("1", "demo1"):
        demo_path = storage_root / "demo1"
        if args.purge:
            purge_path(demo_path)
        reset_at(demo_path)
        return
    if args.demo in ("2", "demo2"):
        demo_path = storage_root / "demo2"
        if args.purge:
            purge_path(demo_path)
        reset_at(demo_path)
        return
    if args.demo == "all":
        for d in ("demo1", "demo2"):
            demo_path = storage_root / d
            if args.purge:
                purge_path(demo_path)
            reset_at(demo_path)
        return

    # Default behavior: reset root and optionally clean legacy top-level files
    reset_at(storage_root)
    if args.clean_root:
        delete_legacy_top_level_files(storage_root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()


