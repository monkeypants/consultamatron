---
source_hash: sha256:c4c335136cd43b1a15cf50358641e0cbdaff430c3fb76d5d7b1479ca564c01d1
---
Partnerships: private Git repos sharing proprietary skillsets with specific collaborators without publishing to commons. Stored under `partnerships/{slug}/` (gitignored).

Structure identical to commons sources: `partnerships/acme-corp/skillsets/acme-strategy/__init__.py + skills/ + docs/`. Partners clone Consultamatron, then `git clone <private-repo> partnerships/acme-corp`. CLI auto-discovers partnership skillsets alongside commons and personal.

Setup: host creates private repo with `skillsets/` structure and invites collaborators. Collaborator clones into `partnerships/{slug}/`. No CLI distinction between sources.

T-shaped capability: commons = horizontal bar (broad shared methodology), partnerships = vertical bar (deep proprietary expertise). Engagements can draw from both simultaneously (e.g. commons `wardley-mapping` + partnership industry knowledge packs).

Feedback routing: partner raises issue/PR in partnership repo → host reviews and merges → partners `git pull`. Commons never sees proprietary content.

Access revocation: remove from GitHub repo; local clone persists but can't pull updates. Full revocation: rotate repo URL or regenerate deploy keys.
