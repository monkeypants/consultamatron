---
source_hash: sha256:20ac144efd29b45a330d533a6df1dcc8d748db58ebc73fe2d4c30e46021710e5
---
The engagement lifecycle is not a skillset pipeline — it is the host of pipelines. Three nested protocols: engagement protocol (outer, orchestrates cross-project progress), skillset protocol (middle, drives individual projects through pipeline stages), skills engineering protocol (inner, propose-negotiate-agree loop).

The engagement protocol operates as a use case layer with two commands: `engagement status` (derive pipeline position for all projects via gate inspection) and `engagement next` (apply sequencing rules, recommend next action). State is derived from gate artifact existence, not stored separately. Value objects (EngagementDashboard, ProjectPipelinePosition) are computed on demand and discarded.

Architecture: Clean Architecture (dependency rule, use cases as central concept, LLM as outermost-ring framework detail), Hexagonal Architecture (operator as driver port, GateInspector as driven port), GRASP (Protected Variations, Low Coupling, Information Expert), SOLID (ISP, DIP, OCP).

Consumer-driven contracts: each PipelineStage declares `consumes` entries specifying what it reads from prerequisite gates. Skillsets plug in as plugins: declare SKILLSETS, produce gate artifacts, follow propose-negotiate-agree. The core guarantees discovery, status tracking, next-action recommendation, and conformance verification.
