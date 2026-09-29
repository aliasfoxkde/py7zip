"""Deterministic acquisition tests using a real local file transport."""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

import pytest

import py7zip.acquisition as acquisition_module
from py7zip.acquisition import (
    ArtifactAcquisitionError,
    ArtifactIntegrityError,
    ArtifactLockTimeoutError,
    ArtifactManager,
)
from py7zip.platforms import ArtifactCatalog, ArtifactSpec, PlatformInfo


def _local_spec(tmp_path: Path, payload: bytes) -> ArtifactSpec:
    source = tmp_path / "source" / "artifact"
    source.parent.mkdir()
    source.write_bytes(payload)
    return ArtifactSpec(
        "artifact", "7za", hashlib.sha256(payload).hexdigest(), len(payload)
    )


def test_manager_downloads_verifies_and_reuses_cache(tmp_path, monkeypatch):
    payload = b"verified artifact bytes"
    spec = _local_spec(tmp_path, payload)
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    monkeypatch.setattr(
        "py7zip.acquisition.ArtifactCatalog.resolve", lambda _info: spec
    )

    manager = ArtifactManager(
        tmp_path / "cache", base_url=(tmp_path / "source").as_uri()
    )
    first = manager.ensure(info)
    second = manager.ensure(info)

    assert first == second
    assert first.read_bytes() == payload
    assert first.stat().st_mode & 0o111


def test_manager_rejects_corrupt_cached_artifact(tmp_path, monkeypatch):
    payload = b"verified artifact bytes"
    spec = _local_spec(tmp_path, payload)
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "7za").write_bytes(b"corrupt")
    monkeypatch.setattr(
        "py7zip.acquisition.ArtifactCatalog.resolve", lambda _info: spec
    )

    with pytest.raises(ArtifactIntegrityError, match="integrity mismatch"):
        ArtifactManager(cache, base_url=(tmp_path / "source").as_uri()).ensure(info)


def test_manager_rejects_oversized_download(tmp_path, monkeypatch):
    payload = b"too large"
    source = tmp_path / "source"
    source.mkdir()
    (source / "artifact").write_bytes(payload)
    spec = ArtifactSpec(
        "artifact", "7za", hashlib.sha256(payload[:-1]).hexdigest(), len(payload) - 1
    )
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    monkeypatch.setattr(
        "py7zip.acquisition.ArtifactCatalog.resolve", lambda _info: spec
    )

    with pytest.raises(ArtifactIntegrityError, match="exceeds catalog size"):
        ArtifactManager(
            tmp_path / "cache", base_url=(tmp_path / "source").as_uri()
        ).ensure(info)


@pytest.mark.parametrize(
    "spec", ArtifactCatalog.specs(), ids=lambda spec: spec.relative_path
)
def test_catalog_digests_match_checked_in_artifacts(spec):
    artifact = Path(__file__).parents[1] / spec.relative_path

    assert artifact.stat().st_size == spec.size_bytes
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == spec.sha256


def test_lock_recovery_removes_lock_owned_by_dead_process(tmp_path):
    manager = ArtifactManager(tmp_path, lock_stale_after=0.01)
    lock = tmp_path / ".7za.lock"
    lock.write_text("pid=999999999\ntime=0\n", encoding="ascii")
    old = time.time() - 10
    os.utime(lock, (old, old))

    with manager._lock(lock):
        assert lock.exists()
        assert f"pid={os.getpid()}" in lock.read_text(encoding="ascii")
    assert not lock.exists()


def test_lock_owned_by_current_process_times_out(tmp_path):
    manager = ArtifactManager(tmp_path, lock_timeout=0.01, lock_stale_after=0.01)
    lock = tmp_path / ".7za.lock"
    lock.write_text(f"pid={os.getpid()}\ntime=0\n", encoding="ascii")
    old = time.time() - 10
    os.utime(lock, (old, old))

    with pytest.raises(ArtifactLockTimeoutError), manager._lock(lock):
        pass
    lock.unlink()


def test_manager_rejects_non_positive_timeouts(tmp_path):
    with pytest.raises(ValueError, match="timeouts must be positive"):
        ArtifactManager(tmp_path, timeout=0)
    with pytest.raises(ValueError, match="timeouts must be positive"):
        ArtifactManager(tmp_path, lock_timeout=-1.0)
    with pytest.raises(ValueError, match="timeouts must be positive"):
        ArtifactManager(tmp_path, lock_stale_after=0.0)


def test_manager_refuses_destination_escaping_the_cache(tmp_path, monkeypatch):
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    escaping = ArtifactSpec("bin/lin/pc/x64/7za", "../escaped", "0" * 64, 1)
    monkeypatch.setattr(
        "py7zip.acquisition.ArtifactCatalog.resolve", lambda _info: escaping
    )

    with pytest.raises(ArtifactAcquisitionError, match="escapes cache"):
        ArtifactManager(tmp_path / "cache").ensure(info)


def test_download_transport_failure_becomes_typed_error(tmp_path, monkeypatch):
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")

    def failing_urlopen(_url, **_kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr("py7zip.acquisition.urlopen", failing_urlopen)

    with pytest.raises(ArtifactAcquisitionError, match="failed to acquire"):
        ArtifactManager(tmp_path / "cache").ensure(info)


def test_recent_foreign_lock_blocks_until_timeout(tmp_path, monkeypatch):
    """A lock with a live PID and fresh mtime is never stolen."""
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    cache = tmp_path / "cache"
    cache.mkdir()
    lock = cache / ".7za.lock"
    lock.write_text(f"pid={os.getpid()}\n", encoding="ascii")

    manager = ArtifactManager(cache, lock_timeout=0.1, lock_stale_after=999.0)
    start = time.monotonic()
    with pytest.raises(ArtifactLockTimeoutError, match="timed out"):
        manager.ensure(info)
    assert time.monotonic() - start >= 0.1
    assert lock.exists()  # the live lock is intact


def test_malformed_stale_lock_is_left_alone(tmp_path, monkeypatch):
    """Unparseable stale locks are refused, not stolen blind."""
    payload = b"verified artifact bytes"
    spec = _local_spec(tmp_path, payload)
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    cache = tmp_path / "cache"
    cache.mkdir()
    lock = cache / ".7za.lock"
    lock.write_text("not-a-valid-lock\n", encoding="ascii")
    past = time.time() - 999.0
    os.utime(lock, (past, past))
    monkeypatch.setattr(
        "py7zip.acquisition.ArtifactCatalog.resolve", lambda _info: spec
    )

    manager = ArtifactManager(
        cache, base_url=(tmp_path / "source").as_uri(), lock_timeout=0.1
    )
    with pytest.raises(ArtifactLockTimeoutError):
        manager.ensure(info)
    assert lock.read_text(encoding="ascii") == "not-a-valid-lock\n"


def test_stale_lock_of_live_owner_is_not_stolen(tmp_path, monkeypatch):
    """``os.kill`` PermissionError means the owner exists: keep waiting."""
    payload = b"verified artifact bytes"
    spec = _local_spec(tmp_path, payload)
    info = PlatformInfo("linux", "x86_64", 64, "pc", "x64")
    cache = tmp_path / "cache"
    cache.mkdir()
    lock = cache / ".7za.lock"
    lock.write_text("pid=999999\n", encoding="ascii")
    past = time.time() - 999.0
    os.utime(lock, (past, past))

    def permission_denied(_pid, _signal):
        raise PermissionError("owned by another user")

    monkeypatch.setattr(acquisition_module.os, "kill", permission_denied)
    monkeypatch.setattr(
        "py7zip.acquisition.ArtifactCatalog.resolve", lambda _info: spec
    )

    manager = ArtifactManager(
        cache, base_url=(tmp_path / "source").as_uri(), lock_timeout=0.1
    )
    with pytest.raises(ArtifactLockTimeoutError):
        manager.ensure(info)
    assert lock.exists()
