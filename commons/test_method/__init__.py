"""Test Method bounded context."""

from practice.entities import Pipeline


def _create_presenter(workspace_root, repo_root):
    from test_method.presenter import TestMethodPresenter

    return TestMethodPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("test-method", _create_presenter)

PIPELINES: list[Pipeline] = [
    Pipeline(
        name="test-method",
        display_name="Test Method",
        description="Updated.",
        slug_pattern="test-{n}",
    ),
]
