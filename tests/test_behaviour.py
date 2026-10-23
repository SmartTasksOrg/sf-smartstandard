"""Behaviour of core.standard and core.conformance."""
import hashlib
from sf_smartstandard import core


def test_the_standard_hash_is_sha256_of_the_rule_ids():
    s = core.standard()
    ids = ",".join(r.id for r in s.rules)
    assert s.id == "iaiso-baseline" and len(s.rules) == 4
    assert s.hash == "sha256:" + hashlib.sha256(ids.encode()).hexdigest()[:12]
    assert core.standard() == s


def test_an_empty_folder_conforms_to_nothing(tmp_path):
    c = core.conformance(str(tmp_path))
    assert c.score == 0 and c.drift == ["STD-README", "STD-SMARTJSON", "STD-LICENSE", "STD-TESTS"]


def test_a_complete_folder_conforms_fully(tmp_path):
    for f in ("README.md", ".smart.json", "LICENSE"):
        (tmp_path / f).write_text("x")
    (tmp_path / "tests").mkdir()
    c = core.conformance(str(tmp_path))
    assert c.score == 100 and c.drift == []


def test_score_is_the_share_of_rules_met(tmp_path):
    (tmp_path / "README.md").write_text("x")
    (tmp_path / "LICENSE").write_text("x")
    c = core.conformance(str(tmp_path))
    assert c.score == 50 and c.drift == ["STD-SMARTJSON", "STD-TESTS"]


def test_a_tests_file_is_not_a_tests_folder(tmp_path):
    (tmp_path / "tests").write_text("x")
    assert "STD-TESTS" in core.conformance(str(tmp_path)).drift
