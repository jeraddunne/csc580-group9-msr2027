"""Tests for the local labelling page and label import (offline)."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pandas as pd

from msr_pipeline import label_ui
from msr_pipeline import validation as v

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = re.compile(r"const DATA = (.*?);\nconst storeKey", re.S)


def _kit():
    spec = importlib.util.spec_from_file_location(
        "annotation_kit", ROOT / "scripts" / "annotation_kit.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(page: str) -> dict:
    match = PAYLOAD.search(page)
    assert match, "DATA payload not found"
    return json.loads(match.group(1))


def test_packet_key_signals_and_pairs():
    assert label_ui.packet_key("signals", "# x\n- file_sha: `abc1234def`\n") == "abc1234def"
    pair = "- file_sha_a: `aaaaaaa1`\n- file_sha_b: `bbbbbbb2`\n"
    assert label_ui.packet_key("lineage", pair) == "aaaaaaa1|bbbbbbb2"
    assert label_ui.packet_key("drift", "no keys here") is None
    assert label_ui.packet_key("signals", "- file_sha: `sha-A`\n") == "sha-A"


def test_read_packets_skips_index_and_unkeyed(tmp_path: Path):
    (tmp_path / "INDEX.md").write_text("- file_sha: `ffffffff`\n", encoding="utf-8")
    (tmp_path / "001_a.md").write_text("- file_sha: `aaaaaaaa`\n", encoding="utf-8")
    (tmp_path / "002_b.md").write_text("no key\n", encoding="utf-8")
    assert [k for k, _ in label_ui.read_packets(tmp_path, "signals")] == ["aaaaaaaa"]
    assert label_ui.read_packets(tmp_path / "missing", "signals") == []


def test_build_items_covers_every_signal_row():
    labels = pd.DataFrame(
        {
            "file_sha": ["s1", "s1", "s2"],
            "rule_id": ["R-A", "R-B", "NONE"],
            "label": ["RISKY", "", ""],
            "missed_category": ["", "", ""],
            "notes": ["", "", ""],
        }
    )
    items = label_ui.build_items("signals", labels, [("s1", "packet one")])
    assert [i["key"] for i in items] == ["s1", "s2"]
    assert [r["rule_id"] for r in items[0]["rows"]] == ["R-A", "R-B"]
    assert items[0]["rows"][0]["label"] == "RISKY"
    assert "not found" in items[1]["packet"]
    assert sum(len(i["rows"]) for i in items) == len(labels)


def test_build_items_pairs_follow_packet_order():
    labels = pd.DataFrame(
        {
            "file_sha_a": ["a1", "a2"],
            "file_sha_b": ["b1", "b2"],
            "same_lineage": ["YES", ""],
            "notes": ["", ""],
        }
    )
    items = label_ui.build_items("lineage", labels, [("a2|b2", "p2"), ("a1|b1", "p1")])
    assert [i["key"] for i in items] == ["a2|b2", "a1|b1"]
    assert items[1]["rows"][0]["label"] == "YES"


def test_build_html_embeds_packet_text_inertly():
    hostile = "</script><script>alert(1)</script><!-- <script>"
    items = [
        {
            "key": "s1",
            "packet": hostile,
            "rows": [{"rule_id": "R-A", "label": "", "missed_category": "", "notes": ""}],
        }
    ]
    page = label_ui.build_html("signals", "jd", 1, items, ["REMOTE_CODE"])
    assert page.count("<script") == 1 and page.count("</script>") == 1
    assert "<!-- <script>" not in page
    data = _payload(page)
    assert data["items"][0]["packet"] == hostile
    assert data["filename"] == "signals_jd_r1.csv"
    assert data["choices"]["none"] == list(v.NO_SIGNAL_LABELS)
    assert data["columns"] == v.KIND_COLUMNS["signals"]
    assert "https://" not in page.split("<script>")[1]  # no network requests in the page script


def test_import_labels_validates_and_protects_existing(tmp_path: Path):
    ann = tmp_path / "annotations"
    ann.mkdir()
    blank = pd.DataFrame(
        {
            "file_sha": ["s1", "s2"],
            "rule_id": ["R-A", "NONE"],
            "label": ["", ""],
            "missed_category": ["", ""],
            "notes": ["", ""],
        }
    )
    blank.to_csv(ann / "signals_jd_r1.csv", index=False)
    download = tmp_path / "signals_jd_r1 (2).csv"  # browsers add a counter on repeat downloads
    good = blank.copy()
    good["label"] = ["RISKY", "NONE_PRESENT"]
    good.to_csv(download, index=False)

    target, problems, n = label_ui.import_labels(download, ann, ["R-A"], ["REMOTE_CODE"])
    assert problems == [] and n == 2 and target.name == "signals_jd_r1.csv"

    changed = good.copy()
    changed.loc[0, "label"] = "NOT_PRESENT"
    changed.to_csv(download, index=False)
    target, problems, _ = label_ui.import_labels(download, ann, ["R-A"], ["REMOTE_CODE"])
    assert target is None and "differ" in problems[0]
    target, problems, _ = label_ui.import_labels(
        download, ann, ["R-A"], ["REMOTE_CODE"], replace=True
    )
    assert problems == []
    assert v.read_label_csv(ann / "signals_jd_r1.csv").loc[0, "label"] == "NOT_PRESENT"

    bad = good.copy()
    bad.loc[1, "label"] = "RISKY"  # not allowed for a NONE row
    bad.to_csv(download, index=False)
    target, problems, _ = label_ui.import_labels(download, ann, ["R-A"], ["REMOTE_CODE"])
    assert target is None and problems

    extra = pd.concat([good, good.iloc[[0]].assign(file_sha="s3")], ignore_index=True)
    extra.to_csv(download, index=False)
    _, problems, _ = label_ui.import_labels(download, ann, ["R-A"], ["REMOTE_CODE"])
    assert "do not match" in problems[0]

    wrong_name = tmp_path / "labels.csv"
    good.to_csv(wrong_name, index=False)
    assert label_ui.import_labels(wrong_name, ann, ["R-A"], [])[1]


def test_kit_ui_and_import_end_to_end(data_root: Path, tmp_path: Path):
    kit = _kit()
    ann = data_root / "data" / "annotations"
    assert kit.main(["ui", "--rater", "jd", "--round", "1"]) == 1  # no sheets yet
    assert kit.main(["sample", "--negatives", "5"]) == 0
    assert kit.main(["sheet", "--rater", "jd", "--round", "1"]) == 0
    assert kit.main(["ui", "--rater", "jd", "--round", "1"]) == 0

    page = ann / "work" / "label_signals_jd_r1.html"
    assert page.exists()
    data = _payload(page.read_text(encoding="utf-8"))
    labels = v.read_label_csv(ann / "signals_jd_r1.csv")
    assert sum(len(i["rows"]) for i in data["items"]) == len(labels)
    assert not any(i["packet"].startswith("Reading packet not found") for i in data["items"])

    download = tmp_path / "signals_jd_r1.csv"
    labels["label"] = "NONE_PRESENT"
    labels.to_csv(download, index=False)
    assert kit.main(["import", str(download)]) == 0
    assert (v.read_label_csv(ann / "signals_jd_r1.csv")["label"] == "NONE_PRESENT").all()

    labels.loc[0, "label"] = "RISKY"
    labels.to_csv(download, index=False)
    assert kit.main(["import", str(download)]) == 1
    assert kit.main(["import", str(tmp_path / "missing.csv")]) == 1
