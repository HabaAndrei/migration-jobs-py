import sys, getopt
import uuid


args = sys.argv[1:]
options = "hmo:d:"
long_options = ["help", "description="]

folder_path = "./app_migrations_jobs/"
file_extention = ".py"


JOB_TEMPLATE = '''"""
ID: {id!r}
DESCRIPTION: {description!r}
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone

from database.db_client import AsyncSessionLocal
from database.models.migration_job import MigrationJob

# TODO: replace this with the function you want this job to execute.
# from some.module import the_function_to_run
def the_function_to_run():
    pass


JOB_ID = uuid.UUID({id!r})
DESCRIPTION = {description!r}


async def run():
    async with AsyncSessionLocal() as session:
        job = await session.get(MigrationJob, JOB_ID)

        if job is not None and job.done:
            print(f"Job {{JOB_ID}} already done, skipping.")
            return

        if job is None:
            job = MigrationJob(id=JOB_ID, description=DESCRIPTION)
            session.add(job)
            await session.commit()

        start = time.perf_counter()
        try:
            result = the_function_to_run()
            if asyncio.iscoroutine(result):
                await result
            job.done = True
            job.error_message = None
        except Exception as e:
            job.done = False
            job.error_message = str(e)
        finally:
            job.executed_at = datetime.now(timezone.utc)
            job.execution_time_ms = int((time.perf_counter() - start) * 1000)
            await session.commit()


if __name__ == "__main__":
    asyncio.run(run())
'''


try:
    arguments, values = getopt.getopt(args, options, long_options)

    for currentArg, currentVal in arguments:

        if currentArg in ("-d", "--description"):
            underscore_description = currentVal.replace(" ", "-")
            id = str(uuid.uuid4())
            with open(
                file=f"{folder_path + id + underscore_description + file_extention}",
                mode="w", encoding="utf8"
            ) as f:
                f.write(JOB_TEMPLATE.format(id=id, description=currentVal))

except getopt.error as err:
    print(str(err))
