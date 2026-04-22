import time

from qiskit.providers.jobstatus import JobStatus


TERMINAL_STATES = {JobStatus.DONE, JobStatus.ERROR, JobStatus.CANCELLED}


def wait_for_job(job, backend=None, poll_interval: float = 5.0, verbose: bool = True):
    """Block until *job* reaches a terminal state and return its result object.

    Raises RuntimeError if the job ends in ERROR or CANCELLED.
    """
    last_status = None

    while True:
        status = job.status()

        if status != last_status:
            if verbose:
                print(f"Job status: {status}")
                if backend is not None:
                    try:
                        print(f"Number of pending jobs: {backend.num_pending_jobs}")
                    except Exception:
                        pass
            last_status = status

        if status in TERMINAL_STATES:
            break

        time.sleep(poll_interval)

    if status != JobStatus.DONE:
        raise RuntimeError(f"Job finished with status: {status}")

    return job.result()