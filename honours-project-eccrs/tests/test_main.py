"""Tests for the CLI (__main__.py), which had none: they run it end to end, so the
manual check before submission is now automatic and repeatable.
"""

from __future__ import annotations

import pytest

from eccrs_workbench.__main__ import main


def test_cli_runs_end_to_end_on_cancer_lp(capsys):
    exit_code = main(["datasets/cancer/rules.txt", "datasets/cancer/data-cancer.lp"])
    out = capsys.readouterr().out
    assert exit_code == 0  # cancer satisfies all three assumptions
    assert "all three assumptions hold" in out
    assert "Phase 4: agreement analysis" in out
    assert "100.0%" in out  # 699 instances + 64 patterns, both 100% agreement
    assert "| dataset instances | 699 |" in out
    assert "ground-truth class taken from a(10)" in out


def test_cli_runs_end_to_end_on_cancer_csv(capsys):
    exit_code = main(
        ["datasets/cancer/rules.txt", "--instances-csv", "datasets/cancer/instances.csv"]
    )
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "175 instances; ground truth from the CSV y column" in out
    assert "100.0%" in out


@pytest.mark.parametrize("name", ["mushroom", "bank"])
def test_cli_runs_end_to_end_on_the_other_two_lp_datasets(capsys, name):
    exit_code = main([f"datasets/{name}/rules.txt", f"datasets/{name}/data-{name}.lp"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "all three assumptions hold" in out
    assert "100.0%" in out


def test_cli_reports_violations_and_continues_on_scholarship(capsys):
    exit_code = main(["tests/fixtures/scholarship.rules.txt"])
    out = capsys.readouterr().out
    assert exit_code == 1  # violations present -> non-zero, per __main__.py's contract
    assert "VIOLATION [strict closure]" in out
    assert "continuing anyway" in out
    assert "Phase 4: agreement analysis" in out  # did not halt


def test_cli_rejects_both_a_data_file_and_instances_csv():
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "datasets/cancer/rules.txt",
                "datasets/cancer/data-cancer.lp",
                "--instances-csv",
                "datasets/cancer/instances.csv",
            ]
        )
    assert excinfo.value.code == 2  # argparse's usage-error exit code


def test_cli_respects_an_explicit_class_atom_override(capsys):
    exit_code = main(
        [
            "datasets/cancer/rules.txt",
            "datasets/cancer/data-cancer.lp",
            "--class-atom",
            "10",
        ]
    )
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "ground-truth class taken from a(10)" in out
