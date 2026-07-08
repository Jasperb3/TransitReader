"""
Crew Retry Wrapper

Wraps a crew kickoff with retry/backoff so a single transient failure
(rate limit, provider outage) doesn't kill a 20-30 minute multi-provider
LLM run.
"""

import time
from typing import Any, Callable


def run_crew_with_retry(
    crew_factory: Callable[[], Any],
    inputs: dict,
    name: str,
    retries: int = 2,
    backoff: int = 30,
) -> Any:
    """
    Call crew_factory().kickoff(inputs=inputs), retrying on exception.

    Args:
        crew_factory: Zero-arg callable returning a fresh crew instance
        inputs: Inputs dict passed to kickoff()
        name: Human-readable stage name, used in retry/failure messages
        retries: Number of retry attempts after the first failure
        backoff: Base seconds to wait before retrying (multiplied by attempt number)

    Returns:
        The crew's kickoff() result

    Raises:
        Exception: Names the failed stage if all attempts are exhausted
    """
    last_exception: Exception | None = None

    for attempt in range(1, retries + 2):
        try:
            return crew_factory().kickoff(inputs=inputs)
        except Exception as e:
            last_exception = e
            if attempt <= retries:
                wait_time = backoff * attempt
                print(f"[{name}] attempt {attempt} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

    raise Exception(f"Crew stage '{name}' failed after {retries + 1} attempts") from last_exception
