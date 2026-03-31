from pathlib import Path
import sys
import importlib

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

gmd_module = importlib.import_module("global_macro_data.gmd")


class _LocalResponse:
    def __init__(self, content: bytes):
        self.content = content
        self.text = content.decode("utf-8", errors="replace")

    def raise_for_status(self) -> None:
        return None


def _clear_all_caches():
    for cache_fn in (
        gmd_module._versions_df,
        gmd_module._varlist_df,
        gmd_module._source_list_df,
        gmd_module._bib_df,
        gmd_module._country_df,
    ):
        if hasattr(cache_fn, "cache_clear"):
            cache_fn.cache_clear()


@pytest.fixture(autouse=True)
def local_data_backend(monkeypatch):
    """Route all GMD fetches to local Stata repo files for deterministic tests."""
    local_root = REPO_ROOT
    stata_root_candidates = [
        REPO_ROOT.parent / "Global-Macro-Database-Stata-main",
        REPO_ROOT.parent / "Global-Macro-Database-Stata",
    ]

    if (local_root / "data" / "final").exists() and (local_root / "data" / "clean").exists():
        data_root = local_root
    else:
        data_root = None
        for candidate in stata_root_candidates:
            if candidate.exists():
                data_root = candidate
                break
        if data_root is None:
            pytest.skip("Global-Macro-Database-Stata repo not found next to Python repo")

    def _map_path(relative_path: str) -> Path:
        rel = relative_path.replace("\\", "/")
        if rel.startswith("helpers/"):
            return data_root / "data" / rel
        if rel.startswith("distribute/"):
            filename = rel.split("/", 1)[1]
            return data_root / "data" / "final" / filename
        if rel.startswith("clean/combined/"):
            filename = rel.split("/", 2)[2]
            return data_root / "data" / "clean" / filename
        raise RuntimeError(f"Unhandled resource path in test backend: {relative_path}")

    def _fetch_local(relative_path: str):
        target = _map_path(relative_path)
        if not target.exists():
            raise RuntimeError(f"Local test resource not found: {target}")
        return _LocalResponse(target.read_bytes())

    monkeypatch.setattr(gmd_module, "_fetch_first", _fetch_local)
    monkeypatch.setattr(gmd_module, "_fetch_primary", _fetch_local)
    monkeypatch.setattr(gmd_module, "_fetch_secondary", _fetch_local)

    _clear_all_caches()
    yield
    _clear_all_caches()
