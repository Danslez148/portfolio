"""The live-demo front end (`python -m eccrs_workbench.demo`).

It is a thin layer over baseline/report/explanation, so these tests pin the things a
presenter would be embarrassed by: the numbers on screen disagreeing with the committed
evaluation (`tests/fixtures/evaluation.json`), the two modes disagreeing with each
other, escape codes leaking into a pipe, or a self-contained HTML file phoning home.

Cancer and the scholarship fixture only -- both run in well under a second. Mushroom and
bank are exercised by actually running the command (see the commit that added it).
"""

from __future__ import annotations

import json

import pytest

from eccrs_workbench import demo
from tests.examples import FIXTURES, REPO, pattern

EVALUATION = json.loads((FIXTURES / "evaluation.json").read_text())
CANCER_EVAL = next(d for d in EVALUATION["datasets"] if d["name"] == "cancer")
CANCER_SAT = EVALUATION["sat"]["cancer"]

STAT_KEYS = ("n", "agree", "disagree", "both_abstain")


def _figures(stats: dict) -> dict:
    return {k: stats[k] for k in STAT_KEYS}


@pytest.fixture(scope="module")
def cancer():
    return demo.analyse(demo.resolve_target("cancer"), mode="both")


# discovery


def test_discovery_finds_the_three_shipped_datasets():
    names = [path.name for path in demo.discover_datasets()]
    assert {"cancer", "mushroom", "bank"} <= set(names)


def test_folder_without_rules_txt_is_rejected(tmp_path):
    with pytest.raises(demo.DemoError, match="rules.txt"):
        demo.resolve_target(str(tmp_path))


def test_discovery_skips_folders_without_rules_txt(tmp_path):
    (tmp_path / "good").mkdir()
    (tmp_path / "good" / "rules.txt").write_text("r1: IF a(1)=1 THEN y=1\n")
    (tmp_path / "empty").mkdir()
    assert [p.name for p in demo.discover_datasets(tmp_path)] == ["good"]


def test_bare_name_and_explicit_path_resolve_to_the_same_dataset():
    by_name = demo.resolve_target("cancer")
    by_path = demo.resolve_target(str(REPO / "datasets" / "cancer"))
    assert by_name.rules_path == by_path.rules_path
    assert by_name.csv_path == by_path.csv_path
    assert by_name.csv_path is not None and by_name.csv_path.name == "instances.csv"


# the numbers match what the committed evaluation reports


def test_cancer_sat_calls_match_the_committed_evaluation(cancer):
    assert cancer.runs["naive"].pattern_calls == CANCER_SAT["naive_total_calls"]
    assert cancer.runs["optimised"].pattern_calls == CANCER_SAT["collapsed_total_calls"]


def test_cancer_agreement_matches_the_committed_evaluation(cancer):
    for run in cancer.runs.values():
        assert _figures(run.pattern_space) == _figures(CANCER_EVAL["pattern_space"])
        assert _figures(run.realisable) == _figures(
            CANCER_EVAL["pattern_space_realisable"]
        )
        assert _figures(run.instances) == _figures(CANCER_EVAL["csv_holdout"])


def test_cancer_header_matches_the_committed_evaluation(cancer):
    assert cancer.rules == CANCER_EVAL["rules"]
    assert cancer.rule_atoms == CANCER_EVAL["rule_atoms"]
    assert cancer.violations == {
        "sanity": [],
        "strict closure": [],
        "no total override": [],
    }
    assert cancer.base_rank_calls == CANCER_SAT["base_rank_calls"]
    assert len(cancer.rank_levels) == CANCER_EVAL["distinct_ranks"]


def test_optimised_evaluates_classes_naive_evaluates_patterns(cancer):
    assert cancer.runs["naive"].pattern_units == CANCER_EVAL["patterns_total"]
    assert (
        cancer.runs["optimised"].pattern_units
        == CANCER_EVAL["applicable_rule_set_classes"]
    )


def test_naive_and_optimised_give_identical_statistics(cancer):
    naive, optimised = cancer.runs["naive"], cancer.runs["optimised"]
    assert _figures(naive.pattern_space) == _figures(optimised.pattern_space)
    assert _figures(naive.realisable) == _figures(optimised.realisable)
    assert _figures(naive.instances) == _figures(optimised.instances)


def test_naive_and_optimised_agree_on_the_scholarship_divergence():
    result = demo.analyse(
        demo.resolve_target(str(FIXTURES / "scholarship.rules.txt")), mode="both"
    )
    assert _figures(result.runs["naive"].pattern_space) == _figures(
        result.runs["optimised"].pattern_space
    )


# modes


@pytest.mark.parametrize("mode", ["naive", "optimised"])
def test_single_mode_runs_only_that_path(mode, capsys):
    result = demo.analyse(demo.resolve_target("cancer"), mode=mode)
    assert list(result.runs) == [mode]

    assert demo.main(["cancer", "--mode", mode, "--no-color"]) == 0
    out = capsys.readouterr().out
    other = "optimised" if mode == "naive" else "naive"
    assert mode in out
    assert other not in out
    assert "speed-up" not in out.lower()


def test_both_mode_finishes_with_a_speedup_line(capsys):
    assert demo.main(["cancer", "--no-color"]) == 0
    out = capsys.readouterr().out
    speedup = [line for line in out.splitlines() if "speed-up" in line.lower()]
    assert len(speedup) == 1
    assert f"{CANCER_SAT['naive_total_calls']}" in speedup[0]
    assert f"{CANCER_SAT['collapsed_total_calls']}" in speedup[0]


def test_abstentions_are_their_own_column(capsys):
    demo.main(["cancer", "--no-color"])
    assert "both-abstain" in capsys.readouterr().out


# colour


def test_no_ansi_escape_codes_with_no_color_flag(capsys):
    demo.main(["cancer", "--no-color"])
    assert "\x1b" not in capsys.readouterr().out


def test_no_ansi_escape_codes_when_stdout_is_not_a_tty(capsys):
    # capsys replaces stdout with a non-tty stream, exactly like a pipe.
    demo.main(["cancer"])
    assert "\x1b" not in capsys.readouterr().out


def test_colour_is_emitted_when_asked_for(cancer):
    assert "\x1b[" in demo.render_text(cancer, color=True)
    assert "\x1b" not in demo.render_text(cancer, color=False)


# the header and the traces


def test_header_names_dataset_conditions_and_rank_levels(cancer):
    text = demo.render_text(cancer, color=False)
    assert "cancer" in text
    for condition in ("sanity", "strict closure", "no total override"):
        assert condition in text
    for label, rule_ids in cancer.rank_levels:
        assert f"rank {label}: {', '.join(rule_ids)}" in text


def test_rule_ids_within_a_rank_are_in_natural_order(cancer):
    ids = [rule_id for _label, rule_ids in cancer.rank_levels for rule_id in rule_ids]
    assert ids[:5] == ["0", "1", "6", "10", "11"]  # not the lexical "0, 1, 10, 11, 6"


def test_default_is_two_traces_and_traces_flag_changes_it(capsys):
    demo.main(["cancer", "--no-color"])
    assert capsys.readouterr().out.count("--- pattern") == 2
    demo.main(["cancer", "--no-color", "--traces", "1"])
    assert capsys.readouterr().out.count("--- pattern") == 1
    demo.main(["cancer", "--no-color", "--traces", "0"])
    assert capsys.readouterr().out.count("--- pattern") == 0


def test_cancer_traces_show_an_override_case_when_nothing_diverges(cancer):
    assert cancer.divergences == []
    assert any("overridden by" in trace for trace in cancer.traces)


# the scholarship fixture, via a path argument


def test_scholarship_shows_the_one_known_divergence(capsys):
    path = str(FIXTURES / "scholarship.rules.txt")
    result = demo.analyse(demo.resolve_target(path), mode="both")

    assert result.runs["naive"].instances is None  # a bare rules file has no CSV
    assert result.runs["naive"].pattern_space["disagree"] == 1
    assert [p for _key, p in result.divergences] == [pattern(1, 1, 1, 1, 1)]
    assert "DIVERGE (MSW=None, RC=1)" in result.traces[0]

    assert demo.main([path, "--no-color"]) == 0
    assert "DIVERGE" in capsys.readouterr().out


# html


def test_html_is_self_contained_and_names_the_dataset(tmp_path, capsys):
    target = tmp_path / "out" / "cancer.html"
    assert demo.main(["cancer", "--html", str(target), "--no-color"]) == 0

    html = target.read_text(encoding="utf-8")
    assert "cancer" in html
    assert "http" not in html.lower()
    assert "<script" not in html.lower()
    assert "<pre>" in html
    assert str(target) in capsys.readouterr().out


def test_html_default_path_is_demo_output_dataset_html(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert demo.main(["cancer", "--mode", "optimised", "--html", "--no-color"]) == 0
    assert (tmp_path / "demo-output" / "cancer.html").is_file()


def test_html_escapes_trace_text(cancer):
    html = demo.render_html(cancer)
    assert "=>" not in html  # ">" must be entity-escaped inside <pre>
    assert "=&gt;" in html


# CLI edges


def test_list_prints_the_datasets_and_runs_nothing(capsys):
    assert demo.main(["--list"]) == 0
    out = capsys.readouterr().out
    for name in ("cancer", "mushroom", "bank"):
        assert name in out
    assert "SAT calls" not in out


def test_missing_rules_txt_is_a_clear_error_not_a_traceback(tmp_path, capsys):
    assert demo.main([str(tmp_path)]) != 0
    assert "rules.txt" in capsys.readouterr().err


def test_no_argument_prompts_for_a_numbered_choice(tmp_path, monkeypatch, capsys):
    # A private datasets/ holding only cancer, so choice "1" is cheap and unambiguous.
    package = tmp_path / "cancer"
    package.mkdir()
    for name in ("rules.txt", "instances.csv"):
        (package / name).write_bytes((REPO / "datasets" / "cancer" / name).read_bytes())
    monkeypatch.setattr(demo, "DATASETS_DIR", tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")

    assert demo.main(["--mode", "optimised", "--no-color", "--traces", "0"]) == 0
    out = capsys.readouterr().out
    assert "1) cancer" in out
    assert "SAT calls" in out


def test_prompt_rejects_a_choice_outside_the_list(tmp_path, monkeypatch, capsys):
    (tmp_path / "cancer").mkdir()
    (tmp_path / "cancer" / "rules.txt").write_text("r1: IF a(1)=1 THEN y=1\n")
    monkeypatch.setattr(demo, "DATASETS_DIR", tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "7")
    assert demo.main([]) != 0
    assert "7" in capsys.readouterr().err


def test_html_flag_before_the_dataset_does_not_swallow_it(tmp_path, monkeypatch, capsys):
    # `--html cancer` would naively read "cancer" as the output path.
    monkeypatch.chdir(tmp_path)
    assert demo.main(["--html", "cancer", "--mode", "optimised", "--no-color"]) == 0
    assert (tmp_path / "demo-output" / "cancer.html").is_file()
