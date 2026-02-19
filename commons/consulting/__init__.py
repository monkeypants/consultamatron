"""Consulting bounded context — presenter and standalone skills."""

from __future__ import annotations


def _create_presenter(workspace_root, repo_root):
    from consulting.presenter import ConsultingProjectPresenter

    return ConsultingProjectPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("consulting", _create_presenter)

SKILLSETS: list = []
