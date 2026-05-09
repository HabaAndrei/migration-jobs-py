"""
Run all app migration jobs (sequentially), then verify status in the DB.

Usage:
    uv run run_job_migrations.py            # run all pending jobs, then print verification
    uv run run_job_migrations.py --verify   # only print verification (no execution)
"""

import asyncio
import importlib.util
import sys
from pathlib import Path

from sqlalchemy import select

from database.db_client import AsyncSessionLocal
from database.models.migration_job import MigrationJob


JOBS_DIR = Path(__file__).parent / "app_migrations_jobs"


def _load_job_module(path: Path):
    """Dynamically import a job file as a module so we can call its run() coroutine."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def run_all_jobs():
    """Execute every job file in app_migrations_jobs/ one by one (alphabetical order)."""
    files = sorted(p for p in JOBS_DIR.glob("*.py") if not p.name.startswith("_"))
    if not files:
        print("No migration job files found.")
        return

    print(f"Found {len(files)} job file(s). Running step by step...\n")
    for path in files:
        print(f"--- {path.name} ---")
        try:
            module = _load_job_module(path)
        except Exception as e:
            print(f"  load failed: {e}")
            continue

        if not hasattr(module, "run"):
            print("  skipped: no run() coroutine in this file.")
            continue

        try:
            await module.run()
            print("  ok")
        except Exception as e:
            print(f"  run() raised: {e}")


async def verify_jobs():
    """Print every MigrationJob row with its status (done / error / timing)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MigrationJob).order_by(MigrationJob.created_at)
        )
        jobs = list(result.scalars().all())

        total = len(jobs)
        done_count = sum(1 for j in jobs if j.done)
        error_count = sum(1 for j in jobs if j.error_message)
        pending_count = total - done_count

    print(f"\nMigrationJob rows: {total}  (done: {done_count}, pending: {pending_count}, with error: {error_count})")
    if total == 0:
        return

    print(f"\n{'id':<38} {'done':<5} {'ms':<8} description / error")
    print("-" * 100)
    for j in jobs:
        ms = j.execution_time_ms if j.execution_time_ms is not None else "-"
        line = f"{str(j.id):<38} {str(j.done):<5} {str(ms):<8} {j.description}"
        if j.error_message:
            line += f"  | error: {j.error_message}"
        print(line)


async def main():
    if "--verify" in sys.argv:
        await verify_jobs()
        return

    await run_all_jobs()
    print("\n=== verification (DB state) ===")
    await verify_jobs()


if __name__ == "__main__":
    asyncio.run(main())
