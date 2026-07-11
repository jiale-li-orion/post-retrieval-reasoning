import hashlib
import json
from pathlib import Path

import pytest

from adapters.atm import ATMAdapter, DatasetIntegrityError


ATM_ROOT = (
    Path(__file__).resolve().parents[3] / "other_repo_references" / "ATM-Bench"
)


@pytest.mark.skipif(not ATM_ROOT.exists(), reason="pinned ATM-Bench checkout absent")
def test_full_and_hard_counts_and_hashes() -> None:
    adapter = ATMAdapter(ATM_ROOT)

    full = adapter.load_split("full")
    hard = adapter.load_split("hard")

    assert len(full) == 1013
    assert len(hard) == 31
    assert adapter.split_sha256("full") == (
        "ab6eaa9df62fb4162e0f5eecd98768a7e3ae721e32d2db2cf227ff41e3295762"
    )
    assert adapter.split_sha256("hard") == (
        "acd35f2a172a9741d970d2cf21184ff0af8d79a8bf59967fc8aa33d619f6af4a"
    )


@pytest.mark.skipif(not ATM_ROOT.exists(), reason="pinned ATM-Bench checkout absent")
@pytest.mark.parametrize("k", [25, 50, 100, 200])
def test_niah_pool_contains_all_gold_evidence(k: int) -> None:
    adapter = ATMAdapter(ATM_ROOT)

    for item in adapter.load_niah(k):
        assert set(item.evidence_ids).issubset(item.niah_evidence_ids)
        assert len(item.niah_evidence_ids) >= len(item.evidence_ids)


@pytest.mark.skipif(not ATM_ROOT.exists(), reason="pinned ATM-Bench checkout absent")
def test_sgm_chunks_preserve_official_bytes_and_order() -> None:
    adapter = ATMAdapter(ATM_ROOT)
    item = adapter.load_split("hard")[0]

    chunks = adapter.collect_sgm_chunks(item.evidence_ids)

    assert len(chunks) == len(item.evidence_ids)
    assert [chunk.splitlines()[0] for chunk in chunks] == [
        f"ID: {evidence_id}" for evidence_id in item.evidence_ids
    ]
    assert chunks == adapter.collect_official_sgm_chunks(item.evidence_ids)


def test_split_hash_mismatch_is_fatal(tmp_path: Path) -> None:
    root = tmp_path / "ATM-Bench"
    qa_dir = root / "data" / "atm-bench"
    qa_dir.mkdir(parents=True)
    (qa_dir / "atm-bench-hard.json").write_text("[]", encoding="utf-8")
    digest = hashlib.sha256(b"[]").hexdigest()
    assert digest != ATMAdapter.EXPECTED_HASHES["hard"]

    with pytest.raises(DatasetIntegrityError, match="SHA256 mismatch"):
        ATMAdapter(root).load_split("hard")
