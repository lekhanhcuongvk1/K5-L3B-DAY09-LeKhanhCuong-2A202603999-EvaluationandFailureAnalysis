"""Eval-set identity must survive Git Windows/Linux checkout conversion."""
import hashlib

import pytest

from lab9.evalset import sha12

pytestmark = pytest.mark.student


def test_lab9_evalset_sha_matches_across_windows_and_linux(tmp_path):
    content = '{"item_id":"E-001","note":"hoàn tiền"}\n{"item_id":"E-002"}\n'.encode("utf-8")
    windows, linux = tmp_path / "windows.jsonl", tmp_path / "linux.jsonl"
    windows.write_bytes(content.replace(b"\n", b"\r\n"))
    linux.write_bytes(content)
    assert sha12(windows) == sha12(linux) == hashlib.sha256(content).hexdigest()[:12]


def test_lab9_evalset_sha_still_detects_item_changes(tmp_path):
    path = tmp_path / "items.jsonl"
    path.write_bytes(b'{"failure_modes":["FM-03"]}\n')
    original = sha12(path)
    path.write_bytes(b'{"failure_modes":["FM-08"]}\n')
    assert sha12(path) != original
