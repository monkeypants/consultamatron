"""Pantheon aggregation tests — progressive story in three layers.

**TestPantheonFormat** — teaches how pantheon markdown becomes data.
**TestPantheonAggregation** — teaches how skillsets contribute luminaries.
**TestPantheonList** — CLI boundary using a stub usecase double.

Two fictional skillsets exercise multi-skillset aggregation:

- **peace** contributes the philosophers pantheon
- **war** contributes the jedi-order pantheon
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from bin.cli.di import Container
from bin.cli.dtos import ListPantheonRequest, ListPantheonResponse, LuminarySummary
from bin.cli.main import cli
from bin.cli.usecases import ListPantheonUseCase, _parse_pantheon

# ---------------------------------------------------------------------------
# Test data — raw markdown in the real format
# ---------------------------------------------------------------------------

PHILOSOPHERS_MD = """\
---
type: pantheon
---
# Philosophers

Ancient thinkers whose ideas remain structurally relevant to
analytical consulting.

---

## Aristotle

Systematic classification, formal logic, causality.
Invoke when categorising or building taxonomies.

## Socrates

Dialectic questioning, exposing hidden assumptions.
Invoke when premises need challenging.

## Marcus Aurelius

Stoic judgement under uncertainty, duty, resilience.
Invoke when facing difficult trade-offs.

## Plato

Ideal forms, abstraction, definition of essences.
Invoke when defining interfaces or abstract models.

## Epicurus

Simplicity, necessity, avoiding unnecessary pain.
Invoke when evaluating whether complexity is justified.

## Heraclitus

Change, flux, impermanence, unity of opposites.
Invoke when designing for evolution.
"""

JEDI_MD = """\
---
type: pantheon
---
# Jedi Order

Strategic archetypes from the Jedi Council, each representing
a distinct decision-making posture.

---

## Yoda

Deep patience, long-term thinking, training discipline.
Invoke when short-term pressure distorts judgement.

## Obi-Wan Kenobi

Pragmatic mentorship, adapting principles to context.
Invoke when ideals conflict with operational reality.

## Mace Windu

Decisive authority, controlled aggression, risk assessment.
Invoke when a situation demands firm action over deliberation.

## Ahsoka Tano

Independent judgement, questioning institutional orthodoxy.
Invoke when the established approach may be the problem.

## Qui-Gon Jinn

Intuition, living in the moment, defying protocol for cause.
Invoke when rules obstruct the right thing to do.

## Luke Skywalker

Redemptive optimism, seeing potential others have written off.
Invoke when a situation appears beyond recovery.
"""


# ---------------------------------------------------------------------------
# Stub SkillsetKnowledge (dict-backed test double)
# ---------------------------------------------------------------------------


class StubSkillsetKnowledge:
    """Dict-backed double for the SkillsetKnowledge port."""

    def __init__(self, items: dict[tuple[str, str], str]) -> None:
        self._items = items

    def read_item(self, skillset_name: str, item_type: str) -> str | None:
        return self._items.get((skillset_name, item_type))


# ---------------------------------------------------------------------------
# Precomputed luminary lists for CLI-level tests
# ---------------------------------------------------------------------------

PHILOSOPHERS = [
    LuminarySummary(
        name="Aristotle",
        skillset="peace",
        summary=(
            "Systematic classification, formal logic, causality.\n"
            "Invoke when categorising or building taxonomies."
        ),
    ),
    LuminarySummary(
        name="Socrates",
        skillset="peace",
        summary=(
            "Dialectic questioning, exposing hidden assumptions.\n"
            "Invoke when premises need challenging."
        ),
    ),
    LuminarySummary(
        name="Marcus Aurelius",
        skillset="peace",
        summary=(
            "Stoic judgement under uncertainty, duty, resilience.\n"
            "Invoke when facing difficult trade-offs."
        ),
    ),
    LuminarySummary(
        name="Plato",
        skillset="peace",
        summary=(
            "Ideal forms, abstraction, definition of essences.\n"
            "Invoke when defining interfaces or abstract models."
        ),
    ),
    LuminarySummary(
        name="Epicurus",
        skillset="peace",
        summary=(
            "Simplicity, necessity, avoiding unnecessary pain.\n"
            "Invoke when evaluating whether complexity is justified."
        ),
    ),
    LuminarySummary(
        name="Heraclitus",
        skillset="peace",
        summary=(
            "Change, flux, impermanence, unity of opposites.\n"
            "Invoke when designing for evolution."
        ),
    ),
]

JEDI = [
    LuminarySummary(
        name="Yoda",
        skillset="war",
        summary=(
            "Deep patience, long-term thinking, training discipline.\n"
            "Invoke when short-term pressure distorts judgement."
        ),
    ),
    LuminarySummary(
        name="Obi-Wan Kenobi",
        skillset="war",
        summary=(
            "Pragmatic mentorship, adapting principles to context.\n"
            "Invoke when ideals conflict with operational reality."
        ),
    ),
    LuminarySummary(
        name="Mace Windu",
        skillset="war",
        summary=(
            "Decisive authority, controlled aggression, risk assessment.\n"
            "Invoke when a situation demands firm action over deliberation."
        ),
    ),
    LuminarySummary(
        name="Ahsoka Tano",
        skillset="war",
        summary=(
            "Independent judgement, questioning institutional orthodoxy.\n"
            "Invoke when the established approach may be the problem."
        ),
    ),
    LuminarySummary(
        name="Qui-Gon Jinn",
        skillset="war",
        summary=(
            "Intuition, living in the moment, defying protocol for cause.\n"
            "Invoke when rules obstruct the right thing to do."
        ),
    ),
    LuminarySummary(
        name="Luke Skywalker",
        skillset="war",
        summary=(
            "Redemptive optimism, seeing potential others have written off.\n"
            "Invoke when a situation appears beyond recovery."
        ),
    ),
]


# ===========================================================================
# TestPantheonFormat — how pantheon markdown becomes data
# ===========================================================================


class TestPantheonFormat:
    """The parser extracts (name, summary) pairs from ## headings."""

    def test_headings_become_luminary_names(self):
        results = _parse_pantheon("## Alice\n\nWise.\n\n## Bob\n\nBrave.\n")
        assert [name for name, _ in results] == ["Alice", "Bob"]

    def test_body_becomes_summary(self):
        results = _parse_pantheon("## Alice\n\nWise and kind.\nVery wise.\n")
        assert results[0][1] == "Wise and kind.\nVery wise."

    def test_intro_before_first_heading_is_skipped(self):
        content = "# Title\n\nIntro paragraph.\n\n## Alice\n\nWise.\n"
        results = _parse_pantheon(content)
        assert len(results) == 1
        assert results[0][0] == "Alice"

    def test_empty_sections_are_skipped(self):
        content = "## Alice\n\nWise.\n\n## Empty\n\n## Bob\n\nBrave.\n"
        results = _parse_pantheon(content)
        names = [name for name, _ in results]
        assert "Empty" not in names
        assert names == ["Alice", "Bob"]

    def test_frontmatter_stripped_content(self):
        """Parser works on body after frontmatter has been stripped."""
        from practice.frontmatter import split_frontmatter

        _, body = split_frontmatter(PHILOSOPHERS_MD)
        results = _parse_pantheon(body)
        assert len(results) == 6
        assert results[0][0] == "Aristotle"
        assert results[5][0] == "Heraclitus"


# ===========================================================================
# TestPantheonAggregation — how skillsets contribute luminaries
# ===========================================================================


class TestPantheonAggregation:
    """The usecase aggregates luminaries across skillsets via the port."""

    @pytest.fixture()
    def knowledge(self):
        from practice.frontmatter import split_frontmatter

        _, peace_body = split_frontmatter(PHILOSOPHERS_MD)
        _, war_body = split_frontmatter(JEDI_MD)
        return StubSkillsetKnowledge(
            {
                ("peace", "pantheon"): peace_body,
                ("war", "pantheon"): war_body,
            }
        )

    @pytest.fixture()
    def usecase(self, knowledge):
        return ListPantheonUseCase(knowledge=knowledge)

    def test_single_skillset_returns_its_luminaries(self, usecase):
        resp = usecase.execute(ListPantheonRequest(skillset_names=["peace"]))
        names = [lum.name for lum in resp.luminaries]
        assert "Aristotle" in names
        assert "Socrates" in names
        assert "Yoda" not in names

    def test_multiple_skillsets_aggregate(self, usecase):
        resp = usecase.execute(ListPantheonRequest(skillset_names=["peace", "war"]))
        names = [lum.name for lum in resp.luminaries]
        assert "Aristotle" in names
        assert "Yoda" in names

    def test_luminaries_attributed_to_skillset(self, usecase):
        resp = usecase.execute(ListPantheonRequest(skillset_names=["peace", "war"]))
        by_skillset = {lum.name: lum.skillset for lum in resp.luminaries}
        assert by_skillset["Aristotle"] == "peace"
        assert by_skillset["Yoda"] == "war"

    def test_skillset_with_no_pantheon_contributes_nothing(self, usecase):
        resp = usecase.execute(ListPantheonRequest(skillset_names=["peace", "silence"]))
        names = [lum.name for lum in resp.luminaries]
        assert "Aristotle" in names
        assert len(names) == 6  # only peace luminaries

    def test_unknown_skillset_silently_skipped(self, usecase):
        resp = usecase.execute(ListPantheonRequest(skillset_names=["chaos"]))
        assert resp.luminaries == []

    def test_empty_request_returns_empty(self, usecase):
        resp = usecase.execute(ListPantheonRequest(skillset_names=[]))
        assert resp.luminaries == []


# ===========================================================================
# TestPantheonList — CLI boundary (uses stub usecase double)
# ===========================================================================


class StubListPantheonUseCase:
    """In-memory double that returns canned luminary data.

    peace -> philosophers, war -> jedi, unknown -> empty.
    """

    def execute(self, request: ListPantheonRequest) -> ListPantheonResponse:
        luminaries: list[LuminarySummary] = []
        packs: list[str] = []
        if "peace" in request.skillset_names:
            luminaries.extend(PHILOSOPHERS)
            packs.append("peace/docs/pantheon")
        if "war" in request.skillset_names:
            luminaries.extend(JEDI)
            packs.append("war/docs/pantheon")
        return ListPantheonResponse(luminaries=luminaries, source_packs=packs)


@pytest.fixture()
def run(tmp_config, monkeypatch):
    """CLI runner with a stub pantheon usecase injected into the container."""
    monkeypatch.setattr(
        "bin.cli.main.Config",
        type(
            "Config",
            (),
            {"from_repo_root": staticmethod(lambda _: tmp_config)},
        ),
    )

    _original_init = Container.__init__

    def _patched_init(self, config):
        _original_init(self, config)
        self.list_pantheon_usecase = StubListPantheonUseCase()

    monkeypatch.setattr(Container, "__init__", _patched_init)

    runner = CliRunner()
    return lambda *args: runner.invoke(cli, list(args))


class TestPantheonList:
    """practice pantheon list --skillsets <names>"""

    def test_peace_returns_philosophers_not_jedi(self, run):
        result = run("pantheon", "list", "--skillsets", "peace")
        assert result.exit_code == 0
        assert "Aristotle" in result.output
        assert "Socrates" in result.output
        assert "Yoda" not in result.output

    def test_war_returns_jedi_not_philosophers(self, run):
        result = run("pantheon", "list", "--skillsets", "war")
        assert result.exit_code == 0
        assert "Yoda" in result.output
        assert "Obi-Wan Kenobi" in result.output
        assert "Aristotle" not in result.output

    def test_both_returns_all_with_attribution(self, run):
        result = run("pantheon", "list", "--skillsets", "peace,war")
        assert result.exit_code == 0
        assert "Aristotle" in result.output
        assert "Yoda" in result.output
        assert "peace" in result.output
        assert "war" in result.output
        assert "12" in result.output

    def test_unknown_returns_no_luminaries_found(self, run):
        result = run("pantheon", "list", "--skillsets", "chaos")
        assert result.exit_code == 0
        assert "No luminaries found" in result.output

    def test_missing_skillsets_is_rejected(self, run):
        result = run("pantheon", "list")
        assert result.exit_code != 0

    def test_luminary_summary_in_output(self, run):
        """Summaries appear so agents can parse invocation triggers."""
        result = run("pantheon", "list", "--skillsets", "peace")
        assert result.exit_code == 0
        assert "categorising" in result.output
