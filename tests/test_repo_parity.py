from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_stata_parity import check_parity  # noqa: E402
from setup_helpers import build_helpers  # noqa: E402


def test_stata_repository_is_mirrored_when_available():
    stata_root = REPO_ROOT.parent / "Global-Macro-Database-Stata-main"
    if not stata_root.exists():
        pytest.skip("Stata repository not available next to Python repository.")

    code = check_parity(
        python_root=REPO_ROOT,
        stata_root=stata_root,
        allowed_hash_mismatch=[],
    )
    assert code == 0


def test_setup_helpers_is_idempotent_on_current_repo():
    targets = [
        REPO_ROOT / "data" / "helpers" / "source_list.csv",
        REPO_ROOT / "data" / "helpers" / "bib_dataframe.csv",
        REPO_ROOT / "data" / "helpers" / "varlist.csv",
    ]
    original_bytes = {p: p.read_bytes() for p in targets}
    try:
        before = {p: pd.read_csv(p) for p in targets}
        build_helpers(REPO_ROOT)
        after = {p: pd.read_csv(p) for p in targets}

        for path in targets:
            left = before[path]
            right = after[path]
            assert list(left.columns) == list(right.columns)
            if path.name == "bib_dataframe.csv":
                left = left.sort_values("source_name").reset_index(drop=True)
                right = right.sort_values("source_name").reset_index(drop=True)
            assert left.equals(right)
    finally:
        for path, content in original_bytes.items():
            path.write_bytes(content)
