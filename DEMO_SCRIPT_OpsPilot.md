# OpsPilot Hackathon Demo Script

## Demo Title

**OpsPilot: AI Incident War Room**

## Demo Objective

Demonstrate how OpsPilot coordinates specialized agents to investigate operational incidents using grounded log evidence and knowledge-base runbooks.

The demo should prove four things:

1. OpsPilot can investigate a known production-style incident.
2. OpsPilot can retrieve a matching runbook without exposing internal agent payloads.
3. OpsPilot can explain a root cause using both log and KB evidence.
4. OpsPilot refuses to invent evidence for an unknown incident.

## Recommended Demo Duration

Keep the live demonstration focused. Use the primary flow first, then show one targeted capability and one responsible no-match scenario.

## Pre-Demo Checklist

Before presenting:

- [ ] Start from the final tagged or committed OpsPilot build.
- [ ] Activate the project virtual environment.
- [ ] Export environment variables from `.env`.
- [ ] Start Neuro SAN Studio from the repository root.
- [ ] Hard-refresh the browser.
- [ ] Select `basic/opspilot`.
- [ ] Confirm the five agents are visible:
  - IncidentCommander
  - LogInvestigator
  - KnowledgeAgent
  - ResolutionPlanner
  - QualityReviewer
- [ ] Confirm the coded tools are visible:
  - `log_search`
  - `kb_search`
- [ ] Run the focused OpsPilot tests.
- [ ] Keep final screenshots available as a fallback if the cloud model is rate-limited.



### Start Command

```bash
cd /Users/zeroniz/Github/neuro-san-studio
source venv/bin/activate
set -a && source .env && set +a
python -m neuro_san_studio run
```



### Focused Test Command

```bash
python -m pytest -q \
  tests/test_opspilot_log_search.py \
  tests/test_opspilot_kb_search.py \
  tests/test_opspilot_incident_grounding.py \
  tests/test_opspilot_agent_structure.py
```



## Opening Talk Track

> Production support teams often spend critical incident time searching logs, locating runbooks, correlating failures, and deciding what to do next. OpsPilot acts as an AI Incident War Room. It coordinates specialized agents that retrieve operational evidence, locate documented knowledge, explain the likely cause, prepare recovery guidance, and validate whether the investigation is sufficiently grounded.

> The demo uses synthetic production-style incidents, logs, and runbooks. OpsPilot does not execute production changes. It produces evidence-backed findings and plans for operational review.



## Architecture Talk Track

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

> IncidentCommander interprets the request and delegates to the relevant specialists. LogInvestigator retrieves source-referenced operational evidence. KnowledgeAgent retrieves the matching runbook. ResolutionPlanner organizes available guidance into a recovery plan. QualityReviewer checks whether the required grounded artifacts are present.

---



# Demo 1: Full Incident Investigation



## Query

```text
Investigate INC008381005
```



## Presenter Setup

> This is a P1 SAS Grid incident where users cannot launch workspace sessions. OpsPilot should use the complete war-room workflow.



## Expected Agent Flow

```text
IncidentCommander
  -> LogInvestigator
       -> log_search
  -> KnowledgeAgent
       -> kb_search
  -> ResolutionPlanner
  -> QualityReviewer
```



## Expected Grounded Findings



### Operational Evidence

The response should include evidence such as:

- metadata connection-pool utilization increasing from the low 90s to 99%;
- metadata repository request timeouts;
- inability to connect to the metadata server on port 8561;
- authentication token validation failures;
- Object Spawner workspace-session failures; and
- workspace launch timeouts or rejected user sessions.



### Knowledge Match

The response should identify:

```text
KB-1023: Metadata Service Connection Saturation
```



### Root Cause

The response should identify metadata connection-pool exhaustion or saturation as the supported root cause.

### Review Outcome

For a complete grounded response, QualityReviewer should indicate that the evidence, KB match, root cause, plan, and validation steps are present. It should use a non-numeric readiness outcome.

## Presenter Talk Track

> OpsPilot first reconstructs the incident from the operational logs. The evidence shows the metadata connection pool rising to saturation, followed by authentication and workspace-session failures. KnowledgeAgent then correlates the incident with KB-1023. The final response keeps observed log evidence separate from documented KB guidance.



## Pass Criteria

- [ ] `log_search` is invoked.
- [ ] `kb_search` is invoked.
- [ ] `KB-1023` is shown.
- [ ] Root cause is supported by log evidence.
- [ ] No internal `Name`, `Inquiry`, `Mode`, or raw orchestration object is exposed.
- [ ] The response does not claim a production change was executed.



## Screenshot

Save as:

```text
screenshots/01-inc008381005-investigation.png
```

---



# Demo 2: Direct Runbook Retrieval



## Query

```text
Retrieve the runbook for INC008381110
```



## Presenter Setup

> This query demonstrates intent-aware routing. The user wants the runbook, not a full investigation.



## Expected Agent Flow

```text
IncidentCommander
  -> KnowledgeAgent
       -> kb_search
```

The ideal route should not require LogInvestigator, ResolutionPlanner, or QualityReviewer.

## Expected Output

The response should be human-readable Markdown and include:

```text
KB-1101: Jupyter Notebook Kernel Startup Failure
```



### Required Sections

- Root Cause
- Resolution Steps
- Validation Checklist



### Expected Root Cause

The runbook should state that an environment update removed `ipykernel` from the `analytics-prod` image and left the kernel specification pointing to an incompatible interpreter.

### Expected Resolution Guidance

The runbook should include the documented actions:

1. Hold new launches if multiple users are impacted.
2. Add the approved `ipykernel` version and rebuild the immutable image.
3. Rebuild or register the kernelspec against the correct Python interpreter.
4. Publish and deploy the corrected image through the approved change process.
5. Restart the Jupyter kernel deployment and reconnect affected notebooks.



## Presenter Talk Track

> OpsPilot recognizes that this is a runbook-retrieval request and returns KB-1101 directly. The response includes the documented root cause, recovery procedure, and validation checklist without exposing internal agent-to-agent JSON.



## Pass Criteria

- [ ] `KB-1101.md` is returned.
- [ ] The title is Jupyter Notebook Kernel Startup Failure.
- [ ] Root cause, resolution steps, and validation checklist are present.
- [ ] Raw orchestration JSON is not shown.
- [ ] The response does not claim that the incident has been resolved.



## Screenshot

Save as:

```text
screenshots/02-inc008381110-runbook.png
```

---



# Demo 3: Focused Root-Cause Analysis



## Query

```text
What caused INC008381005?
```



## Presenter Setup

> This query asks for the cause rather than the full war-room workflow. OpsPilot should focus on the evidence and matching knowledge.



## Expected Agent Flow

```text
IncidentCommander
  -> LogInvestigator
       -> log_search
  -> KnowledgeAgent
       -> kb_search
```

A recovery plan should not be generated unless requested.

## Expected Output

The response should clearly state:

```text
Metadata connection-pool saturation
```



### Supporting Evidence

Expected evidence includes:

- `connection_saturation_confirmed pool=99%`;
- `authentication_token_validation_failed`;
- `workspace_launch_timeout_exceeded`; and
- `metadata_repository_request_timeout`.



### Knowledge Correlation

The response should reference:

```text
KB-1023: Metadata Service Connection Saturation
```



## Presenter Talk Track

> The root-cause query demonstrates that OpsPilot can provide a concise answer while remaining explainable. It supports the conclusion with specific log patterns and confirms the same failure mode in KB-1023.



## Pass Criteria

- [ ] Root cause is stated directly near the beginning.
- [ ] At least one supporting log pattern is included.
- [ ] KB-1023 is referenced.
- [ ] No unsupported implementation commands are generated.
- [ ] No raw orchestration JSON is exposed.



## Screenshot

Save as:

```text
screenshots/03-inc008381005-root-cause.png
```

---



# Demo 4: Responsible AI / Unknown Incident



## Query

```text
Investigate INC999999999
```



## Presenter Setup

> This incident does not exist in the prepared dataset. The correct behavior is to report missing evidence rather than invent a plausible answer.



## Expected Agent Flow

```text
IncidentCommander
  -> LogInvestigator
       -> log_search
  -> KnowledgeAgent
       -> kb_search
  -> QualityReviewer
```



## Expected Output

The response should state:

```text
No matching log evidence found.
No matching KB found.
REQUIRES FURTHER INVESTIGATION
```

It may recommend verifying the incident ID or gathering additional evidence, but it must not invent an incident title, root cause, runbook, or recovery plan.

## Presenter Talk Track

> This scenario demonstrates responsible no-match behavior. OpsPilot does not hallucinate a root cause or pretend that a runbook exists. It clearly reports the data gap and requires further investigation.



## Pass Criteria

- [ ] No matching log evidence is reported.
- [ ] No matching KB is reported.
- [ ] No root cause is invented.
- [ ] No recovery plan is invented.
- [ ] The result is `REQUIRES FURTHER INVESTIGATION` or equivalent.



## Screenshot

Save as:

```text
screenshots/04-inc999999999-no-match.png
```

---



# Demo 5: Knowledge Discovery



## Query

```text
Is there any knowledge related to SAS issues?
```



## Presenter Setup

> This query demonstrates discovery across the available SAS-related runbooks rather than investigation of one incident.



## Expected Output

The response should identify relevant SAS knowledge available in the local KB dataset. It should distinguish retrieved KB content from general model knowledge.

## Presenter Talk Track

> OpsPilot can also help support engineers discover available operational knowledge. The results are limited to the local synthetic runbook collection used by this demo.



## Pass Criteria

- [ ] At least one SAS-related KB article is returned.
- [ ] Retrieved KB filenames or titles are shown.
- [ ] The response does not claim access to knowledge outside the local dataset.
- [ ] No unsupported incident count or ranking is invented.



## Screenshot

Save as:

```text
screenshots/05-sas-knowledge-discovery.png
```

---

#  Demo Fallback Plan

Cloud-model rate limits may interrupt multi-agent execution. If a live request fails:

1. State that the local coded tools and focused tests are independent of the cloud-model call.
2. Show the stored screenshot for the same scenario.
3. Show the focused OpsPilot test result.
4. Demonstrate either coded tool directly from the terminal.



### Direct Log Search

```bash
python - <<'PY'
import asyncio
from coded_tools.opspilot.log_search import LogSearch

result = asyncio.run(
    LogSearch().async_invoke({"query": "INC008381005"}, {})
)
print(result)
PY
```



### Direct KB Search

```bash
python - <<'PY'
import asyncio
from coded_tools.opspilot.kb_search import KbSearch

result = asyncio.run(
    KbSearch().async_invoke({"query": "INC008381110"}, {})
)
print(result)
PY
```

---



# Closing Talk Track

> OpsPilot demonstrates a practical multi-agent incident-response workflow. It separates evidence collection, knowledge retrieval, planning, and review into specialized responsibilities. The strongest capability is grounded investigation: OpsPilot can show what the logs say, which runbook matches, and when the available data is insufficient. The next production step would be deterministic recovery-plan construction and integration with enterprise incident and observability platforms.



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



# Final Recording Checklist

- [ ] Browser shows `basic/opspilot`.
- [ ] Sample queries are visible.
- [ ] Agent graph is visible before running the first query.
- [ ] Primary investigation completes successfully.
- [ ] Runbook output is human-readable.
- [ ] Root-cause response includes log and KB evidence.
- [ ] Unknown incident demonstrates no hallucination.
- [ ] No API keys, `.env` values, personal paths, or credentials appear in the recording.
- [ ] Screenshots come from the final frozen build.
- [ ] Focused tests are captured.
- [ ] Final Git commit or tag is recorded.