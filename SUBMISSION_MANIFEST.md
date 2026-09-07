# OpsPilot — Submission Manifest

OpsPilot is built on **Neuro SAN Studio** (Cognizant AI Lab). The full project is included so it runs as-is, but most files belong to the upstream framework.

The files listed below are the OpsPilot contribution. Everything else in this archive is upstream Neuro SAN Studio code.

---

## Agent network

```
registries/basic/opspilot.hocon
```

Declarative six-agent network: IncidentCommander, LogInvestigator, KnowledgeAgent, ResolutionPlanner, QualityReviewer, ExecutiveReporter.

---

## Coded tools

```
coded_tools/opspilot/__init__.py
coded_tools/opspilot/incident_validator.py
coded_tools/opspilot/log_search.py
coded_tools/opspilot/kb_search.py
coded_tools/opspilot/resolution_plan_builder.py
```

Deterministic local Python. No external API calls.

---

## Synthetic data

```
opspilot_data/incidents.json     Incident catalog
opspilot_data/logs/              Operational log fixtures
opspilot_data/kb/                Markdown knowledge base articles
```

All records are synthetic fixtures created for this demonstration. No production or customer data is represented.

---

## Tests

```
tests/test_opspilot_agent_structure.py
tests/test_opspilot_incident_validator.py
tests/test_opspilot_incident_validation_integration.py
tests/test_opspilot_incident_grounding.py
tests/test_opspilot_log_search.py
tests/test_opspilot_kb_search.py
tests/test_opspilot_resolution_plan_builder.py
```

Run with:

```bash
pytest tests/test_opspilot*.py -q
```

---

## Documentation and evidence

```
README.md                Project landing page
README_OpsPilot.md       Full project documentation
EVIDENCE_AUDIT.md        Evidence integrity audit
screenshots/             Captured workflow evidence
```

---

## How to run

See the setup and execution sections in `README_OpsPilot.md`.

In short: create the virtual environment, set a valid model API key in `.env` (see `.env.example`), start Neuro SAN Studio, and select the `basic/opspilot` agent network.

The coded tools and tests run locally without a model key. The complete agent workflow requires model access.

---

## Scope

OpsPilot is a demonstration of an incident-investigation workflow. It is not connected to production observability or incident-management systems, does not execute remediation, and does not verify service recovery.
