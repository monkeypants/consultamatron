# Deliverable Architecture

How the site rendering pipeline works, and how to extend it.

## Domain model

A consulting deliverable is not a web site. It is a structured
projection of a PARA-organised knowledge base. The site is one
rendering of that projection. The invariant shape — client engagement,
projects with pipelines, shared research, engagement history — hasn't
changed in a thousand years of consulting. Only the skills brought to
bear change.

The domain entities model **what gets delivered**, independent of
rendering format:

```
ProjectContribution
├── hero_figure: Figure | None
├── overview_md: str
└── sections: list[ProjectSection]
    ├── pages: list[ContentPage]        # flat pages (e.g. Analysis)
    ├── groups: list[PageGroup]         # categorised index (e.g. Atlas)
    └── tours: list[TourPageContent]    # curated presentations
```

Every project produces sections. A project with just a brief gets
`sections=[ProjectSection(label="Analysis", pages=[brief_page])]`. A
project with everything gets three sections (Presentations, Atlas,
Analysis). There is no flat vs three-tier mode detection — just "show
what exists."

### Key entities

| Entity | Purpose |
|--------|---------|
| `Figure` | SVG content with optional caption |
| `ContentPage` | A single page of prose + optional figures |
| `PageGroup` | A labelled collection of pages (atlas category) |
| `TourStopContent` | One assembled tour stop with figures and analysis |
| `TourGroupContent` | Related stops plus transition prose |
| `TourPageContent` | Complete tour: opening, groups, metadata |
| `ProjectSection` | A major section within a project |
| `ProjectContribution` | Everything a project contributes to the deliverable |

All entities are defined in `bin/cli/entities.py`.

## Protocol boundary

The architecture separates **what to present** from **how to render
it** via two protocols:

### ProjectPresenter

Assembles a project's workspace artifacts into a
`ProjectContribution`. Reads markdown files, SVGs, and manifests from
the workspace filesystem. One presenter per skillset.

```python
class ProjectPresenter(Protocol):
    def present(
        self,
        project: Project,
        tours: list[TourManifest],
    ) -> ProjectContribution: ...
```

### SiteRenderer

Receives pre-assembled `ProjectContribution` entities and produces
output. Handles content transformation (markdown to HTML, SVG
embedding, templates) and file I/O. Does not decide what to present —
that decision belongs to presenters.

```python
class SiteRenderer(Protocol):
    def render(
        self,
        client: str,
        contributions: list[ProjectContribution],
        research_topics: list[ResearchTopic],
    ) -> Path: ...
```

### Pipeline

```
Workspace files
    ↓
ProjectPresenter.present()      ← one per skillset
    ↓
ProjectContribution entities    ← skillset-agnostic
    ↓
SiteRenderer.render()           ← one implementation (Jinja2)
    ↓
Static HTML site
```

The `RenderSiteUseCase` orchestrates this: it loads projects, looks up
the correct presenter per skillset, calls `present()`, collects
contributions, and passes them to the renderer.

## Adding a new skillset

1. **Define the skillset manifest** in `skillsets/`.

2. **Implement a presenter** in `bin/cli/infrastructure/`:

```python
class NewSkillsetPresenter:
    def __init__(self, workspace_root: Path) -> None:
        self._ws_root = workspace_root

    def present(
        self,
        project: Project,
        tours: list[TourManifest],
    ) -> ProjectContribution:
        proj_dir = self._ws_root / project.client / "projects" / project.slug
        # Read workspace files, assemble sections
        return ProjectContribution(
            slug=project.slug,
            title=project.slug,
            skillset=project.skillset,
            status=project.status.value,
            overview_md="...",
            sections=[...],
        )
```

3. **Register in DI** (`bin/cli/di.py`):

```python
self.presenters["new-skillset"] = NewSkillsetPresenter(
    workspace_root=config.workspace_root,
)
```

4. **Add tests** in `tests/test_newskillset_presenter.py`.

No changes to the renderer, usecase, or protocol are required. This is
the Open/Closed principle at work: the consulting engagement model
(invariant) is decoupled from specific skill implementations
(variable).

## Current implementations

| Skillset | Presenter | Sections |
|----------|-----------|----------|
| `wardley-mapping` | `WardleyProjectPresenter` | Presentations, Atlas, Analysis |
| `business-model-canvas` | `BmcProjectPresenter` | Analysis |

## Limitations

- **Client-level content** (engagement log, research files) is still
  read directly by the renderer. This is invariant consulting doctrine,
  not skill-specific, so it doesn't violate Open/Closed. Extracting it
  is future work if a non-HTML renderer is needed.

- **PARA model** is partially represented. Projects and Resources are
  modelled. Areas (ongoing responsibilities) and Archives (completed
  work) are not yet part of the deliverable structure.
