Deliverable presentation is the output pipeline. Skillsets implement a `ProjectPresenter` whose `present()` method returns a `ProjectContribution` containing ContentPage groups, NarrativeGroup tours, and Figure elements. The presenter is the Anti-Corruption Layer translating skillset-specific workspace artifacts into the generic content model.

Registration: `PRESENTER_FACTORY` tuple in `__init__.py` mapping skillset name to factory function. Discovery via DI scan. The `SiteRenderer` protocol consumes `ProjectContribution` entities to produce static HTML.

Adding a new skillset requires declaring SKILLSETS, implementing a presenter, and registering via PRESENTER_FACTORY. No changes to renderer or use case. OCP applied to the deliverable pipeline.

An emerging sibling capability (presentation preparation) would add pedagogic metadata to content. When it stabilises, this capability splits into deliverable assembly (code port) and presentation preparation (language port). Maturity: mature.
