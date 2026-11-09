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


import json

import pytest


def _complete_repo(root):
    (root / "README.md").write_text("# Tool\n\n```bash\npip install tool\n```\n")
    (root / ".smart.json").write_text(json.dumps({"family": "Smart*", "iaiso_section": "§7"}))
    (root / "LICENSE").write_text("Apache License, Version 2.0")
    (root / "tests").mkdir()
    (root / "tests" / "test_x.py").write_text("def test(): pass\n")


def test_strict_checks_content_not_just_presence(tmp_path):
    """Version 3.0 passed empty placeholder files."""
    for f in ("README.md", ".smart.json", "LICENSE"):
        (tmp_path / f).write_text("x")
    (tmp_path / "tests").mkdir()
    assert core.conformance(str(tmp_path)).score == 100                  # baseline: presence
    strict = core.conformance(str(tmp_path), "iaiso-strict")
    assert strict.score == 0 and strict.drift == ["STD-README", "STD-SMARTJSON", "STD-LICENSE", "STD-TESTS"]


def test_a_real_repo_passes_strict(tmp_path):
    _complete_repo(tmp_path)
    assert core.conformance(str(tmp_path), "iaiso-strict").drift == []


def test_strict_smart_json_needs_both_keys(tmp_path):
    _complete_repo(tmp_path)
    (tmp_path / ".smart.json").write_text(json.dumps({"family": "Smart*"}))
    assert core.conformance(str(tmp_path), "iaiso-strict").drift == ["STD-SMARTJSON"]


def test_custom_standards(tmp_path):
    _complete_repo(tmp_path)
    std_file = tmp_path / "team.json"
    std_file.write_text(json.dumps({"id": "team", "rules": [
        {"id": "T-SECURITY", "desc": "SECURITY.md", "check": "nonempty", "path": "SECURITY.md"},
        {"id": "T-APACHE", "check": "contains", "path": "LICENSE", "arg": "Apache"},
        {"id": "T-CI", "check": "glob", "path": ".github", "arg": "**/*.yml"}]}))
    std = core.load_standard(str(std_file))
    assert std.id == "team" and std.hash.startswith("sha256:")
    c = core.conformance(str(tmp_path), std)
    assert c.drift == ["T-SECURITY", "T-CI"] and c.score == 33


@pytest.mark.parametrize("rule", [
    {"id": "x", "check": "teleport", "path": "a"},
    {"id": "x", "check": "contains", "path": "a"},
    {"id": "x", "check": "exists", "path": "../outside"},
    {"id": "x", "check": "exists", "path": "/etc/passwd"},
    {"id": "x", "check": "exists", "path": "\\Windows\\win.ini"},
    {"id": "x", "check": "exists", "path": "C:x"},
    {"id": "x", "check": "exists", "path": "C:/Windows/win.ini"},
    {"id": "x", "check": "exists", "path": "//server/share/x"},
    {"id": "x", "check": "exists", "path": "docs\\..\\..\\outside"},
])
def test_custom_rules_are_validated(tmp_path, rule):
    f = tmp_path / "s.json"
    f.write_text(json.dumps({"rules": [rule]}))
    with pytest.raises(ValueError):
        core.load_standard(str(f))


def test_cli_sets_the_exit_code(tmp_path, capsys):
    from sf_smartstandard import cli
    _complete_repo(tmp_path)
    assert cli.main([str(tmp_path), "--standard", "iaiso-strict"]) == 0
    (tmp_path / "LICENSE").write_text("")
    assert cli.main([str(tmp_path), "--standard", "iaiso-strict", "--json"]) == 1
    assert '"STD-LICENSE"' in capsys.readouterr().out


def test_an_html_heading_counts_as_a_heading(tmp_path):
    _complete_repo(tmp_path)
    (tmp_path / "README.md").write_text('<h1 align="center">Tool</h1>\n\n```bash\npip install tool\n```\n')
    assert core.conformance(str(tmp_path), "iaiso-strict").drift == []
