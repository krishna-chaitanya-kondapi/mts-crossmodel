# Generate mock assessment — independent product workflow

Status: partially implemented; not production ready. Never invoke weekly generation or its curriculum allocation. Read specs/generate_mock_assessment/definition-of-done.md and acceptance-criteria.json. Use dedicated product entry point scripts/generate_mock_assessment.py.

1. Recover approved source and historical output, freeze assessment-specific RunSpec and source/item manifest; obtain scope approval.
2. Select or extract source items, preserve passage clusters, math assets and provenance; independently review every answer and scoring rule.
3. Render student/key from canonical manifest using independent assessment presentation policy. Verify structure, scaling, page constraints and every page visually.
4. Record revision-bound evidence and run verification gate. Repair and reverify; checkpoint on blockers. Do not declare complete until mandatory criteria pass.
5. Human acceptance and explicit artifact-specific release approval precede publishing. Golden regressions never publish.

Current CLI implements the evidence gate, fixed-source Math student profiles, Math teacher keys, ELA teacher reflow, and a generic ELA source-region renderer. Complete RunSpec-driven orchestration and source-verified ELA student composition remain open.
