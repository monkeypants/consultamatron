"""Test Method bounded context."""

from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from test_method.presenter import TestMethodPresenter

    return TestMethodPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("test-method", _create_presenter)

SKILLSETS: list[Skillset] = [
    Skillset(
        name="test-method",
        display_name="Test Method",
        description="Updated.",
        slug_pattern="test-{n}",
        problem_domain="Testing",
    ),
]
