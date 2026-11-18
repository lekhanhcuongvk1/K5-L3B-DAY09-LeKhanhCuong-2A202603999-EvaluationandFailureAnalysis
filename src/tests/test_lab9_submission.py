"""Windows subprocess encoding and safe resume without rerunning agent evaluations."""
import subprocess

import pytest

from lab9 import submission

pytestmark = pytest.mark.student


def test_lab9_submission_forces_child_utf8(monkeypatch, capsys):
    observed = {}

    def run(argv, **kwargs):
        observed.update(argv=argv, **kwargs)
        return subprocess.CompletedProcess(argv, 0, stdout="PASS — đánh giá đúng\n", stderr="")

    monkeypatch.setattr(submission.subprocess, "run", run)
    assert submission.command("lab9.ci_check") == "PASS — đánh giá đúng\n"
    assert observed["argv"][1:3] == ["-X", "utf8"]
    assert observed["env"]["PYTHONUTF8"] == "1"
    assert observed["env"]["PYTHONIOENCODING"] == "utf-8"
    assert observed["encoding"] == "utf-8"


def test_lab9_submission_real_child_unicode():
    # Small real child process; no agent evaluations or network.
    assert "lab9.submission" in submission.command("lab9.submission", "--help")


def test_lab9_submission_preserves_failure_status(monkeypatch):
    monkeypatch.setattr(submission.subprocess, "run", lambda *a, **k:
                        subprocess.CompletedProcess(a, 2, stdout="failed", stderr="details"))
    with pytest.raises(RuntimeError, match="returned 2, expected 0"):
        submission.command("lab9.ci_check")
