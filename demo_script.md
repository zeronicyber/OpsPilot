# OpsPilot Judge Demo Script

## Architecture Workflow

Use this workflow explicitly in every investigation:

```text
IncidentCommander
	-> LogInvestigator
		-> log_search

IncidentCommander
	-> KnowledgeAgent
		-> kb_search
```

IncidentCommander coordinates the specialists. LogInvestigator retrieves observed operational evidence. KnowledgeAgent retrieves documented runbook guidance. The final response must keep those two evidence types separate.

## Demo 1 - Critical P1 Incident

### Prompt

> Investigate INC008381005.
>
> Use LogInvestigator to collect operational evidence.
> Use KnowledgeAgent to retrieve the matching runbook.
>
> Provide:
>
> 1. Incident Summary
> 2. Observed Log Evidence
> 3. Documented KB Root Cause
> 4. Documented Resolution Steps
> 5. Validation Checklist
> 6. Confidence Level
>
> Only use evidence returned by `log_search` and `kb_search`.
> Do not add unsupported conclusions.

### Expected Outcome

- Metadata service saturation is identified from the operational logs.
- `KB-1023` is returned by `kb_search`.
- Documented resolution and validation steps are displayed.

## Demo 2 - Python Analytics Incident

### Prompt

> Investigate INC008381110.
>
> Use LogInvestigator to collect operational evidence.
> Use KnowledgeAgent to retrieve the matching runbook.
>
> Provide:
>
> 1. Incident Summary
> 2. Observed Log Evidence
> 3. Documented KB Root Cause
> 4. Documented Resolution Steps
> 5. Validation Checklist
> 6. Confidence Level
>
> Only use grounded evidence.

### Expected Outcome

- The missing `ipykernel` dependency is identified.
- `KB-1101` is returned by `kb_search`.
- The documented recovery procedure is displayed.

## Demo 3 - Responsible AI / No Match Scenario

### Prompt

> Investigate INC999999999.
>
> Use LogInvestigator and KnowledgeAgent.
>
> Provide:
>
> 1. Any matching log evidence
> 2. Any matching KB entries
> 3. Data gaps identified
> 4. Recommended next investigative steps
>
> Do not invent incident details, root causes, or runbook content.

### Expected Outcome

- No matching incident is found.
- No hallucinated answer is produced.
- Missing evidence is explained clearly.

## Optional Demo 4 - Backup Scenario

Run this only if a judge asks for another scenario or a primary demo encounters a model rate limit.

### Prompt

> Investigate INC008380901.
>
> Use LogInvestigator to collect operational evidence.
> Use KnowledgeAgent to retrieve the matching runbook.
>
> Clearly separate observed HTTP 503 log evidence from documented KB guidance.
> Do not add unsupported conclusions.

### Expected Outcome

- SAS Web backend capacity exhaustion is supported by the logs.
- `KB-0901` is returned by `kb_search`.
- Documented load-balancer recovery and validation guidance is displayed.

## Presentation Notes

During the demo, emphasize:

1. **Multi-Agent Architecture** - IncidentCommander delegates instead of investigating directly.
2. **Grounded Log Retrieval** - LogInvestigator uses `log_search` for observed events.
3. **Grounded KB Retrieval** - KnowledgeAgent uses `kb_search` for documented guidance.
4. **Root Cause Analysis** - Root causes are stated only when supported by the sources.
5. **Responsible AI Behavior** - The no-match scenario reports data gaps instead of guessing.
6. **No Unsupported Conclusions** - Evidence and recommendations remain visibly separate.
