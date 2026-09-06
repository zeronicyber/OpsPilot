# OpsPilot Evidence Audit

Audit date: 2026-09-06

## Source of Truth

Factual claims were checked against:

- `registries/basic/opspilot.hocon`
- `coded_tools/opspilot/`
- `opspilot_data/incidents.json`
- `opspilot_data/logs/*.log`
- `opspilot_data/kb/*.md`
- `tests/test_opspilot_*.py`

The local catalog records `INC008381005` as **Open / P1**. `INC999999999` is absent from the catalog and has no matching local log or KB evidence. A valid no-match response is `REQUIRES FURTHER INVESTIGATION`.

## Trusted Judge-Facing Evidence

These files are suitable for demonstrating structure, workflow, or locally verifiable test output, subject to the qualifications below:

- `screenshots/01_agent_introduction.png` - active network overview.
- `screenshots/01_agent_registry.png` - six-agent registry view.
- `screenshots/10_Focused OpsPilot Tests.png` - focused test capture showing the local test result.
- `screenshots/11_executive-summary.html` - curated judge-facing summary. Its incident status for `INC008381005` agrees with the catalog.
- `screenshots/11_opspilot-proof.html` - curated proof page showing the three coded tools, recovery-plan stage, quality-review stage, executive-report stage, and focused test result.
- `screenshots/04-resolution-plan-agent.png` - illustrative recovery-planning workflow evidence; the plan remains model output grounded in supplied KB content and is not proof of executed remediation.
- `screenshots/05-quality-score.png` - illustrative QualityReviewer output; the score is model-generated under registry instructions, not an independent deterministic scorer.
- `screenshots/06-knowledge-agent.png` and `screenshots/07-executive-reporter-agent.png` - illustrative specialist workflow evidence, not independent source data.

The source files and focused tests remain authoritative over captured chat text or model-rendered claims.

## Contradictory or Unsafe Evidence

### `screenshots/Demo mode.txt`

Exclude or regenerate this file before submission because it contains multiple unsupported claims:

- `Investigate INC999999999` is shown with `Log Events (12)` even though the incident is absent from the catalog and has no matching local logs.
- It associates the unknown incident with `KB-2024-05-19-001`, which is not supported by the local KB directory.
- It marks the unknown incident `Resolved`, reports `Confidence: 95%`, and says `Evidence Quality: Grounded` with `Assumptions: None`.
- Its `INC008381005` sections also mark the catalog incident `Resolved`, while the local catalog says `Open / P1`.
- It repeats unsupported `Log Events (12)` and `Confidence: 95%` claims for the valid incident without establishing those values from the deterministic local tools.

### `screenshots/DEMO_INVESTIGATION_INC008381005.md`

Exclude or regenerate this file because it marks `INC008381005` as `Resolved`, while the local catalog says `Open / P1`. It also reports `Log Events (12)` and `Confidence: 95%` as if they were authoritative, although those exact values are not established by the local source-of-truth contract.

### Other PNG Captures

The remaining PNGs are useful UI or workflow illustrations, but model-generated incident statuses, confidence values, event counts, KB identifiers, and remediation outcomes must not be treated as source evidence. In particular, do not use any capture to claim that `INC008381005` was resolved or that remediation was executed. Reconcile such claims with the catalog, logs, KB files, and registry before presentation.

## Submission Handling

- Keep the trusted structural and test evidence listed above.
- Exclude or regenerate both contradictory text captures before presenting the evidence package.
- Do not claim that a screenshot proves an incident status, event count, KB identifier, root cause, confidence score, or service recovery unless the claim is also supported by the local source files and coded-tool output.
- For `INC999999999`, present only the validator no-match result and `REQUIRES FURTHER INVESTIGATION`; do not show a fabricated full investigation.
