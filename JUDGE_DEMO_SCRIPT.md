# OpsPilot Judge Demo Script

## Project

**OpsPilot: AI Incident War Room**

## One-Line Pitch

OpsPilot is an AI Operations Copilot that coordinates specialist agents to investigate incidents using grounded operational logs and knowledge-base runbooks, explain the root cause, prepare recovery guidance, and avoid unsupported conclusions when evidence is missing.

## Problem

During production incidents, support teams spend critical time:

- searching multiple operational logs;
- locating the correct runbook;
- correlating symptoms with known failure patterns;
- identifying a supported root cause; and
- deciding whether available evidence is sufficient to act.

This process is slow, manual, and dependent on individual experience.

## Solution

OpsPilot creates an AI-assisted incident war room using Neuro SAN Studio.

```text
User
  -> IncidentCommander
       -> LogInvestigator
            -> log_search
       -> KnowledgeAgent
            -> kb_search
       -> ResolutionPlanner
       -> QualityReviewer
```

### Agent Responsibilities

- **IncidentCommander** interprets the request, selects the relevant specialists, and presents a consolidated response.
- **LogInvestigator** retrieves incident-specific evidence through `log_search`.
- **KnowledgeAgent** retrieves documented runbooks through `kb_search`.
- **ResolutionPlanner** organizes available runbook guidance into a recovery plan for review.
- **QualityReviewer** checks whether the required grounded artifacts are present and reports missing information.

### Grounding Sources

- Synthetic production-style operational logs
- Markdown knowledge-base runbooks
- Local coded tools with source-referenced results

OpsPilot does not execute production changes. Recovery guidance remains subject to operational review and approval.

---

# Live Demo Flow

## Demo 1: Full Incident Investigation

### Query

```text
Investigate INC008381005
```

### What This Demonstrates

- Complete multi-agent orchestration
- Operational log retrieval
- KB correlation
- Root-cause analysis
- Recovery guidance
- Investigation-quality validation

### Expected Evidence

- Metadata connection-pool utilization increases toward 99%.
- Metadata repository requests time out.
- Authentication token validation fails.
- Workspace sessions cannot be created or time out.
- `KB-1023: Metadata Service Connection Saturation` is matched.

### Expected Conclusion

```text
Root cause: Metadata Server connection-pool saturation
```

### Judge Talk Track

> OpsPilot reconstructs the incident using operational evidence, then correlates the failure pattern with KB-1023. The response separates observed log evidence from documented runbook guidance, making the conclusion explainable and reviewable.

### Success Check

- `log_search` invoked
- `kb_search` invoked
- `KB-1023` returned
- Root cause supported by evidence
- No internal agent JSON exposed
- No claim that production changes were executed

---

## Demo 2: Direct Runbook Retrieval

### Query

```text
Retrieve the runbook for INC008381110
```

### What This Demonstrates

- Intent-aware routing
- Direct knowledge retrieval
- Human-readable runbook presentation
- Documented resolution and validation guidance

### Expected Result

```text
KB-1101: Jupyter Notebook Kernel Startup Failure
```

The response should include:

- documented root cause;
- resolution steps; and
- validation checklist.

### Expected Root Cause

An environment update removed `ipykernel` from the `analytics-prod` image and left the kernelspec pointing to an incompatible interpreter.

### Judge Talk Track

> This request does not require a complete investigation. OpsPilot routes directly to KnowledgeAgent and returns the matching KB article in a user-friendly format without exposing internal orchestration payloads.

### Success Check

- `KB-1101.md` returned
- Correct title shown
- Root cause present
- Resolution steps present
- Validation checklist present
- No raw `Name`, `Inquiry`, `Mode`, or `Response` object shown

---

## Demo 3: Responsible AI and No-Match Handling

### Query

```text
Investigate INC999999999
```

### What This Demonstrates

- Safe handling of unknown incidents
- No unsupported root cause
- No fabricated runbook
- Clear evidence-gap reporting

### Expected Result

```text
No matching log evidence found.
No matching KB found.
REQUIRES FURTHER INVESTIGATION
```

### Judge Talk Track

> The incident is absent from the prepared dataset. OpsPilot does not fabricate a plausible technical explanation. It reports that evidence and knowledge are missing and requires further investigation.

### Success Check

- No matching logs reported
- No matching KB reported
- No incident title invented
- No root cause invented
- No recovery plan invented
- Outcome requires further investigation

---

# Optional Supporting Queries

Use only if the primary three demos complete successfully.

## Focused Root-Cause Analysis

```text
What caused INC008381005?
```

Expected result:

- Direct answer near the beginning
- Metadata connection-pool saturation
- Supporting log patterns
- KB-1023 correlation

## Knowledge Discovery

```text
Is there any knowledge related to SAS issues?
```

Expected result:

- Relevant SAS runbook names or filenames
- Results limited to the local KB dataset
- No unsupported counts or rankings

---

# Key Innovation

OpsPilot separates four operational concerns:

```text
Observed evidence
  -> Documented knowledge
  -> Recovery guidance
  -> Grounding validation
```

This separation makes the workflow easier to explain, test, and audit than a single-agent response.

## Responsible AI Positioning

OpsPilot is designed to:

- distinguish log evidence from KB guidance;
- avoid subjective confidence percentages;
- avoid claiming successful recovery without operational validation;
- return a no-match result when evidence is unavailable; and
- treat recovery guidance as a plan for review, not an executed production change.

## Business Value

- Faster initial incident triage
- Consistent use of documented runbooks
- Reduced manual log and KB searching
- Explainable root-cause analysis
- Clear identification of missing evidence
- Safer incident-response recommendations

---

# Technical Proof

The project includes focused tests for:

- log searching;
- KB searching;
- incident-to-log and incident-to-KB grounding; and
- agent and tool structure.

Run only the OpsPilot tests:

```bash
python -m pytest -q \
  tests/test_opspilot_log_search.py \
  tests/test_opspilot_kb_search.py \
  tests/test_opspilot_incident_grounding.py \
  tests/test_opspilot_agent_structure.py
```

The full Neuro SAN Studio repository test suite is not required for the demo because it includes unrelated tests with optional dependencies.

---

# Demo Fallback

Cloud-model rate limits may interrupt a live multi-agent run.

If that happens:

1. Show the saved screenshot for the selected scenario.
2. Show the focused OpsPilot test result.
3. Demonstrate the local coded tool directly.

## Direct Log Search

```bash
python - <<'PY'
import asyncio
from coded_tools.opspilot.log_search import LogSearch

print(asyncio.run(
    LogSearch().async_invoke({"query": "INC008381005"}, {})
))
PY
```

## Direct KB Search

```bash
python - <<'PY'
import asyncio
from coded_tools.opspilot.kb_search import KbSearch

print(asyncio.run(
    KbSearch().async_invoke({"query": "INC008381110"}, {})
))
PY
```

---

# Closing Statement

> OpsPilot demonstrates a practical multi-agent approach to incident investigation. It retrieves operational evidence, correlates documented knowledge, explains supported root causes, and identifies when the available data is insufficient. The next production step is deterministic recovery-plan construction and integration with enterprise incident-management and observability platforms.

## Final Message

```text
Evidence found
  -> Knowledge matched
  -> Root cause explained
  -> Recovery guidance reviewed
```

For an unknown incident:

```text
No evidence
  -> No KB
  -> No invented conclusion
  -> Further investigation required
```

---

# Judge Demo Checklist

- [ ] Show project name and one-line pitch.
- [ ] Show the five-agent architecture.
- [ ] Run `Investigate INC008381005`.
- [ ] Run `Retrieve the runbook for INC008381110`.
- [ ] Run `Investigate INC999999999`.
- [ ] Keep technical narration focused on grounding and orchestration.
- [ ] Avoid showing API keys, `.env`, personal paths, or credentials.
- [ ] Use screenshots if the cloud model is rate-limited.
- [ ] Close with the business value and responsible AI behavior.
