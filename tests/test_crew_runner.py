import pytest

from transit_reader.utils.crew_runner import run_crew_with_retry


class _FlakyCrew:
    call_count = 0

    def kickoff(self, inputs):
        _FlakyCrew.call_count += 1
        if _FlakyCrew.call_count == 1:
            raise RuntimeError("transient failure")
        return "success"


class _AlwaysFailsCrew:
    def kickoff(self, inputs):
        raise RuntimeError("permanent failure")


def test_run_crew_with_retry_succeeds_after_one_failure(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    _FlakyCrew.call_count = 0

    result = run_crew_with_retry(lambda: _FlakyCrew(), {}, "test_stage")

    assert result == "success"
    assert _FlakyCrew.call_count == 2


def test_run_crew_with_retry_raises_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda seconds: None)

    with pytest.raises(Exception, match="test_stage"):
        run_crew_with_retry(lambda: _AlwaysFailsCrew(), {}, "test_stage", retries=1)
