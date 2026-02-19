"""Shared domain entities referenced by practice-layer protocols.

Entities that appear in protocol signatures in this package are shared
vocabulary across all bounded contexts. They live here — not in any
single BC — so that dependency direction flows downward.

Lifecycle-only entities (DecisionEntry, EngagementEntry) belong in
their bounded context, not here.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from practice.discovery import PipelineStage


# ---------------------------------------------------------------------------
# Skillset (discovery vocabulary — every BC declares these)
# ---------------------------------------------------------------------------


class Skillset(BaseModel):
    """A consulting product line declared in bounded context modules.

    A Skillset with a populated pipeline is implemented — projects can
    be created and driven through the pipeline. A Skillset with an empty
    pipeline is a prospectus — it describes a methodology that is not yet
    operational.
    """

    name: str
    display_name: str
    description: str
    pipeline: list[PipelineStage] = []
    slug_pattern: str
    problem_domain: str = ""
    deliverables: list[str] = []
    value_proposition: str = ""
    classification: list[str] = []
    evidence: list[str] = []

    @property
    def is_implemented(self) -> bool:
        """True when the pipeline has at least one stage."""
        return len(self.pipeline) > 0


# ---------------------------------------------------------------------------
# Project (shared — appears in ProjectPresenter.present() signature)
# ---------------------------------------------------------------------------


class ProjectStatus(str, Enum):
    """Lifecycle phase of a consulting project.

    The lifecycle is linear:
    planning → elaboration → implementation → review → closed.
    Each label describes the project's phase, not the operator's activity.
    """

    PLANNING = "planning"
    ELABORATION = "elaboration"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    CLOSED = "closed"

    def next(self) -> ProjectStatus | None:
        """Return the next lifecycle phase, or None if terminal."""
        members = list(ProjectStatus)
        idx = members.index(self)
        return members[idx + 1] if idx + 1 < len(members) else None


class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM_HIGH = "Medium-High"
    MEDIUM = "Medium"
    LOW = "Low"


class Project(BaseModel):
    """A single consulting project within a client engagement."""

    slug: str
    client: str
    engagement: str
    skillset: str
    status: ProjectStatus
    created: date
    notes: str = ""


# ---------------------------------------------------------------------------
# ResearchTopic (shared — appears in SiteRenderer.render() signature)
# ---------------------------------------------------------------------------


class ResearchTopic(BaseModel):
    """A completed research topic in the client's research manifest."""

    filename: str
    client: str
    topic: str
    date: date
    confidence: Confidence


# ---------------------------------------------------------------------------
# Engagement (unit of contracted work with a client)
# ---------------------------------------------------------------------------


class EngagementStatus(str, Enum):
    """Lifecycle phase of a consulting engagement.

    The lifecycle is linear:
    planning → active → review → closed.
    """

    PLANNING = "planning"
    ACTIVE = "active"
    REVIEW = "review"
    CLOSED = "closed"

    def next(self) -> EngagementStatus | None:
        """Return the next lifecycle phase, or None if terminal."""
        members = list(EngagementStatus)
        idx = members.index(self)
        return members[idx + 1] if idx + 1 < len(members) else None


class Engagement(BaseModel):
    """A unit of contracted work with a client.

    Engagements scope which skillset sources are permitted and
    contain projects. Research stays client-scoped.
    """

    slug: str
    client: str
    status: EngagementStatus
    allowed_sources: list[str] = Field(default_factory=lambda: ["commons", "personal"])
    created: date
    notes: str = ""


# ---------------------------------------------------------------------------
# SkillsetSource (provenance of skillset definitions)
# ---------------------------------------------------------------------------


class SourceType(str, Enum):
    """Where a skillset comes from."""

    COMMONS = "commons"
    PERSONAL = "personal"
    PARTNERSHIP = "partnership"


class SkillsetSource(BaseModel):
    """A source of skillset definitions."""

    slug: str
    source_type: SourceType
    skillset_names: list[str]


# ---------------------------------------------------------------------------
# Profile (named collection of skillsets for an activity type)
# ---------------------------------------------------------------------------


class Profile(BaseModel):
    """A named collection of skillsets for a type of activity."""

    name: str
    display_name: str
    description: str
    skillsets: list[str]


# ---------------------------------------------------------------------------
# Engagement protocol value objects (computed, no identity, no persistence)
# ---------------------------------------------------------------------------


class ProjectPipelinePosition(BaseModel):
    """Derived position of one project within its skillset pipeline."""

    project_slug: str
    skillset: str
    current_stage: int
    total_stages: int
    completed_gates: list[str]
    next_gate: str | None


class EngagementDashboard(BaseModel):
    """Aggregate engagement state derived from gate artifacts."""

    engagement_slug: str
    status: str
    projects: list[ProjectPipelinePosition]


class NextAction(BaseModel):
    """Recommended next skill execution within an engagement."""

    skill: str
    project_slug: str
    reason: str
    prerequisite_exists: bool


# ---------------------------------------------------------------------------
# Skillset Capability (integration protocol — the practice/skillset boundary)
# ---------------------------------------------------------------------------


class CapabilityDirection(str, Enum):
    """Whether the practice layer drives or is driven by the skillset.

    All current capabilities are driven: the practice layer reaches into
    the skillset for domain-specific material. The dyad drives the practice
    layer (driver direction); the practice layer drives skillsets (driven).
    """

    DRIVER = "driver"
    DRIVEN = "driven"


class CapabilityMechanism(str, Enum):
    """How the port/adapter contract is expressed.

    Code ports use Python Protocols enforced by @runtime_checkable and
    conformance tests. Language ports use filesystem conventions enforced
    by token-burning verification during skillset engineering.
    """

    CODE_PORT = "code_port"
    LANGUAGE_PORT = "language_port"
    BOTH = "both"
    UNDEFINED = "undefined"


class CapabilityMaturity(str, Enum):
    """How established the capability's contract and enforcement are.

    nascent: concept exists in documentation, no enforcement mechanism.
    established: convention documented, shape tests in CI.
    mature: code port with Protocol + DI + conformance tests, or
            language port with shape tests + contract verification.
    """

    NASCENT = "nascent"
    ESTABLISHED = "established"
    MATURE = "mature"


class CapabilityDiscovery(str, Enum):
    """How the practice layer discovers a skillset's adapter."""

    DI_SCAN = "di_scan"
    FILESYSTEM_CONVENTION = "filesystem_convention"
    PACK_MANIFEST = "pack_manifest"
    NOT_DEFINED = "not_defined"


class SemanticVerification(BaseModel):
    """Specification for token-burning verification of a language port.

    Contract verification is token-conservative (shallow scan for
    structural violations). Fitness verification is token-generous
    (deep evaluation of adapter quality in context of the skillset).
    """

    reference_problem: str = ""
    sample_size: int = 3
    max_tokens_per_evaluation: int = 2000
    evaluation_criteria: list[str] = []
    trigger: str = "content change in adapter files"


class Capability(BaseModel):
    """A facet of the Consultamatron Integration Protocol.

    Each Capability describes one port at the practice/skillset boundary:
    the practice layer defines a capability (what it provides), and the
    skillset supplies an adapter (domain-specific material that facilitates
    the capability in a particular domain).

    The Capability entity is the metamodel. It drives: the contributor
    catalogue (what must my skillset provide?), rs-assess evaluation
    (is this skillset well-integrated?), and conformance testing (does
    this adapter satisfy the contract?).

    Properties capture both the structural contract (how to use) and the
    architectural rationale (how to understand — Parnas's hidden decision,
    Larman's information expert assignment).
    """

    name: str
    description: str
    direction: CapabilityDirection
    mechanism: CapabilityMechanism
    adapter_contract: str
    discovery: CapabilityDiscovery
    maturity: CapabilityMaturity
    hidden_decision: str
    information_expert: str
    structural_tests: list[str] = []
    semantic_verification: SemanticVerification | None = None


# ---------------------------------------------------------------------------
# Knowledge Pack (semantic pack convention — dual-fidelity knowledge storage)
# ---------------------------------------------------------------------------


class CompilationState(str, Enum):
    """Freshness of a knowledge pack's compiled _bytecode/ mirror.

    CLEAN: bytecode exists and content hashes match all source items.
    DIRTY: bytecode exists but at least one hash mismatches.
    ABSENT: no _bytecode/ directory.
    CORRUPT: bytecode has orphan mirrors — summaries with no
        corresponding source item.
    """

    CLEAN = "clean"
    DIRTY = "dirty"
    ABSENT = "absent"
    CORRUPT = "corrupt"


@runtime_checkable
class PackItem(Protocol):
    """Any item in a knowledge pack.

    The narrow interface between the convention layer (storage,
    compression) and the use case layer (domain-specific consumption).
    Name is derived from the filename; item_type from the frontmatter
    ``type:`` field.
    """

    name: str
    item_type: str


class ActorGoal(BaseModel):
    """Who benefits from a knowledge pack and what they get."""

    actor: str
    goal: str


class KnowledgePack(BaseModel):
    """Identity and freshness metadata for a semantic pack.

    Represents the manifest in ``index.md`` frontmatter plus the
    compilation state of the ``_bytecode/`` mirror.
    """

    name: str
    purpose: str
    actor_goals: list[ActorGoal] = []
    triggers: list[str] = []
    compilation_state: CompilationState = CompilationState.ABSENT


# ---------------------------------------------------------------------------
# Skill Manifest (SKILL.md frontmatter — agentskills.io spec)
# ---------------------------------------------------------------------------


class FreedomLevel(str, Enum):
    """How much latitude the agent has during skill execution."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SkillMetadata(BaseModel):
    """Metadata block nested inside SKILL.md frontmatter."""

    author: str
    version: str
    freedom: FreedomLevel
    skillset: str | None = None
    stage: str | None = None


class SkillManifest(BaseModel):
    """Parsed identity of a SKILL.md file.

    Validated from YAML frontmatter. The ``name`` field must be
    kebab-case and at most 64 characters. The ``description`` must
    be non-empty and at most 1024 characters.
    """

    name: str = Field(max_length=64, pattern=r"^[a-z][a-z0-9]*(-[a-z][a-z0-9]*)*$")
    description: str = Field(min_length=1, max_length=1024)
    metadata: SkillMetadata


# ---------------------------------------------------------------------------
# Freshness assessment (computed from filesystem state)
# ---------------------------------------------------------------------------


class ItemFreshness(BaseModel):
    """Per-item compilation status within a pack."""

    name: str
    is_composite: bool
    state: str  # "clean" | "dirty" | "orphan" | "absent"


class PackFreshness(BaseModel):
    """Complete freshness assessment of a knowledge pack.

    compilation_state is the rollup for this level only (shallow).
    Use deep_state to include descendant pack states.
    """

    pack_root: str  # string, not Path (for serialisation)
    compilation_state: CompilationState
    items: list[ItemFreshness]
    children: list["PackFreshness"] = []

    @property
    def deep_state(self) -> CompilationState:
        """Worst state across self and all descendants.

        Precedence: CORRUPT > DIRTY > ABSENT > CLEAN.
        """
        states = [self.compilation_state] + [c.deep_state for c in self.children]
        for s in (
            CompilationState.CORRUPT,
            CompilationState.DIRTY,
            CompilationState.ABSENT,
        ):
            if s in states:
                return s
        return CompilationState.CLEAN
