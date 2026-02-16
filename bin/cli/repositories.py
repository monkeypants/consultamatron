"""Re-export shim — repositories have moved to consulting.repositories."""

from consulting.repositories import (
    DecisionRepository,
    EngagementRepository,
    ProjectRepository,
    ResearchTopicRepository,
    SkillsetRepository,
)

__all__ = [
    "DecisionRepository",
    "EngagementRepository",
    "ProjectRepository",
    "ResearchTopicRepository",
    "SkillsetRepository",
]
