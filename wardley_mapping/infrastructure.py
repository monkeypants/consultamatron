"""Wardley Mapping infrastructure implementations."""

from __future__ import annotations

from pathlib import Path

from wardley_mapping.types import TourManifest
from bin.cli.infrastructure.json_store import read_json_object, write_json_object


class JsonTourManifestRepository:
    """Tour manifest repository. One manifest.json per tour directory."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def _file(
        self, client: str, engagement: str, project_slug: str, tour_name: str
    ) -> Path:
        return (
            self._root
            / client
            / "engagements"
            / engagement
            / project_slug
            / "presentations"
            / tour_name
            / "manifest.json"
        )

    def get(
        self,
        client: str,
        engagement: str,
        project_slug: str,
        tour_name: str,
    ) -> TourManifest | None:
        data = read_json_object(self._file(client, engagement, project_slug, tour_name))
        if data is None:
            return None
        return TourManifest.model_validate(data)

    def list_all(
        self, client: str, engagement: str, project_slug: str
    ) -> list[TourManifest]:
        """List all tour manifests for a project."""
        pres_dir = (
            self._root
            / client
            / "engagements"
            / engagement
            / project_slug
            / "presentations"
        )
        if not pres_dir.is_dir():
            return []
        manifests = []
        for tour_dir in sorted(pres_dir.iterdir()):
            if not tour_dir.is_dir():
                continue
            data = read_json_object(tour_dir / "manifest.json")
            if data is not None:
                manifests.append(TourManifest.model_validate(data))
        return manifests

    def save(self, manifest: TourManifest) -> None:
        write_json_object(
            self._file(
                manifest.client,
                manifest.engagement,
                manifest.project_slug,
                manifest.name,
            ),
            manifest.model_dump(mode="json"),
        )
