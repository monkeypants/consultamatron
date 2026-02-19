The deliverable pipeline separates what to present from how to render it. `ProjectPresenter` (per-skillset) assembles workspace artifacts into `ProjectContribution` entities. `SiteRenderer` (single implementation) consumes contributions to produce static HTML.

Domain model: `ProjectContribution` contains `ProjectSection` entries, each holding `ContentPage` lists and `PageGroup` collections. Generic content entities in `bin/cli/content.py`; skillset-specific types behind presenter boundaries.

Adding a skillset: declare SKILLSETS, implement presenter, register in DI. No renderer or protocol changes required (OCP). Current implementations: wardley-mapping (Presentations, Atlas, Analysis sections) and business-model-canvas (Analysis section).

Limitations: client-level content still read directly by renderer (invariant doctrine, not skill-specific). PARA model partially represented (Projects and Resources only).
