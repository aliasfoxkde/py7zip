"""Deterministic acquisition tests using a real local file transport."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from py7zip.acquisition import ArtifactIntegrityError, ArtifactManager
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

    manager = ArtifactManager(tmp_path / "cache", base_url=(tmp_path / "source").as_uri())
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
        ArtifactManager(tmp_path / "cache", base_url=(tmp_path / "source").as_uri()).ensure(info)


@pytest.mark.parametrize(
    "spec", ArtifactCatalog.specs(), ids=lambda spec: spec.relative_path
)
def test_catalog_digests_match_checked_in_artifacts(spec):
    artifact = Path(__file__).parents[1] / spec.relative_path

    assert artifact.stat().st_size == spec.size_bytes
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == spec.sha256
