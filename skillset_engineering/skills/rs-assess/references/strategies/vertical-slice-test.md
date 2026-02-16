# Strategy: Vertical Slice Test

Test whether the target pipeline can handle a single finding
from identification through to resolution without disproportionate
overhead.

## When to Load

Target pipeline feels too heavyweight for the changes it
typically needs, or the operator reports that small improvements
require traversing the entire pipeline.

## Method

### 1. Select a representative finding

Choose a finding from the current assessment that:
- Is clearly scoped (not a systemic redesign)
- Represents a typical improvement the target would process
- Can be evaluated without external dependencies

### 2. Trace the resolution path

Walk the finding through the target's pipeline:
- Which stages does it touch?
- What artifacts must be created or updated?
- Which gates must it pass through?
- How many human approval points does it encounter?

Record each step with the artifact or action required.

### 3. Measure ceremony overhead

For the traced path, estimate:
- Number of artifacts created or modified
- Number of human approval gates
- Proportion of work that is process (creating artifacts,
  recording decisions) vs substance (making the actual change)

### 4. Proportionality assessment

Compare ceremony to the change's risk profile:
- Is the overhead proportional to the risk of getting it wrong?
- Would a simpler path produce the same quality outcome?
- Are there stages that add no information for this class of change?

### 5. Generalise

Repeat the trace for 2-3 different finding types:
- A structural fix (mechanical, low risk)
- A methodological improvement (medium risk)
- A pipeline redesign (high risk, high reversibility cost)

Check whether ceremony scales appropriately with risk.

## Output

`assessment/strategies.md` section containing:
- Resolution path trace per finding type
- Ceremony overhead measurements
- Proportionality assessment (ceremony vs risk)
- Recommendations for streamlining low-risk change paths
