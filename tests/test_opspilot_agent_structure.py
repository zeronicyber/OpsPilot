from pathlib import Path

from pyhocon import ConfigFactory


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPOSITORY_ROOT / "registries" / "basic" / "opspilot.hocon"
EXPECTED_AGENTS = {
    "IncidentCommander",
    "LogInvestigator",
    "KnowledgeAgent",
    "ResolutionPlanner",
    "QualityReviewer",
    "ExecutiveReporter",
}
EXPECTED_CODED_TOOLS = {"incident_validator", "log_search", "kb_search", "resolution_plan_builder"}
EXPECTED_LLM_CONFIG = {
    "class": "langchain_mistralai.chat_models.ChatMistralAI",
    "model_name": "mistral-small-latest",
    "temperature": 0.1,
}


def load_registry():
    """Load the registry with includes resolved from the repository root."""
    content = REGISTRY_PATH.read_text(encoding="utf-8")
    return ConfigFactory.parse_string(content, basedir=str(REPOSITORY_ROOT))


def registry_entries():
    return load_registry().get("tools")


def entries_by_name():
    entries = registry_entries()
    return {entry["name"]: entry for entry in entries}


def test_expected_agents_and_coded_tools_exist_exactly_once():
    entries = registry_entries()
    names = [entry["name"] for entry in entries]

    assert set(names) == EXPECTED_AGENTS | EXPECTED_CODED_TOOLS
    for name in EXPECTED_AGENTS | EXPECTED_CODED_TOOLS:
        assert names.count(name) == 1, f"Registry entry {name!r} must exist exactly once"


def test_incident_commander_delegates_to_all_specialists():
    entries = entries_by_name()

    assert entries["IncidentCommander"]["tools"] == [
        "incident_validator",
        "LogInvestigator",
        "KnowledgeAgent",
        "ResolutionPlanner",
        "QualityReviewer",
        "ExecutiveReporter",
    ]


def test_incident_commander_renders_runbook_retrieval_as_user_markdown():
    instructions = entries_by_name()["IncidentCommander"]["instructions"]

    required_phrases = (
        "Runbook Found",
        "KB filename",
        "KB title",
        "## Root Cause",
        "## Resolution Steps",
        "## Validation Checklist",
        "user-friendly Markdown",
        "Return only the user-facing Markdown report",
    )
    for phrase in required_phrases:
        assert phrase in instructions, f"IncidentCommander is missing {phrase!r}"

    forbidden_phrases = (
        "internal orchestration JSON",
        "tool payloads",
        "agent payloads",
        "fields Name, Inquiry, or Mode",
    )
    for phrase in forbidden_phrases:
        assert phrase in instructions, f"IncidentCommander must forbid {phrase!r}"


def test_incident_commander_routes_executive_summary_command():
    instructions = " ".join(entries_by_name()["IncidentCommander"]["instructions"].casefold().split())

    assert 'generate executive summary for inc...' in instructions
    assert 'invoke executivereporter directly' in instructions
    assert 'only its executive markdown summary' in instructions


def test_incident_commander_routes_demo_investigation_as_ordered_story():
    instructions = " ".join(entries_by_name()["IncidentCommander"]["instructions"].split()).casefold()

    required_phrases = (
        'input matching exactly "demo investigate inc..."',
        "enter demo mode",
        "same investigation and quality-review workflow",
        "must never change evidence selection",
        "## demo mode: <incident_id>",
        "### step 1: registered agents",
        "### step 2: investigation workflow",
        "### step 3: agent execution trace",
        "### step 4: investigation report",
        "### step 5: root cause confidence",
        "### step 6: recovery plan",
        "### step 7: executive summary",
        "### step 8: grounding evidence",
        "actual execution trace",
        "do not claim an agent responded if it did not",
        "do not duplicate or invent evidence",
    )
    for phrase in required_phrases:
        assert phrase in instructions, f"Demo Mode contract is missing {phrase!r}"

    section_positions = [
        instructions.index("### step 1: registered agents"),
        instructions.index("### step 2: investigation workflow"),
        instructions.index("### step 3: agent execution trace"),
        instructions.index("### step 4: investigation report"),
        instructions.index("### step 5: root cause confidence"),
        instructions.index("### step 6: recovery plan"),
        instructions.index("### step 7: executive summary"),
        instructions.index("### step 8: grounding evidence"),
    ]
    assert section_positions == sorted(section_positions)


def test_executive_reporter_has_grounded_compact_summary_contract():
    instructions = " ".join(entries_by_name()["ExecutiveReporter"]["instructions"].split()).casefold()

    for phrase in (
        "## executive incident summary",
        "business impact",
        "affected users",
        "root cause",
        "mitigation",
        "status",
        "risk level",
        "confidence",
        "grounding sources",
        "maximum of 10 content lines",
        "not available rather than guessing",
        "independently callable",
        "status must be copied verbatim from the incident record",
        "never state that a service was restored, an incident was resolved, or a fix",
        "recommended mitigation",
        "recovery actions are recommendations awaiting human execution",
    ):
        assert phrase in instructions, phrase


def test_investigation_reports_require_deterministic_root_cause_confidence():
    entries = entries_by_name()
    commander = " ".join(entries["IncidentCommander"]["instructions"].split()).casefold()

    for phrase in (
        "## root cause confidence",
        "exactly three candidates",
        "deterministic evidence rubric",
        "whole-number percentages",
        "sum to 100",
        "selected cause",
        "immediately before the resolution plan",
        "do not use model opinion",
        "unsupported causes",
    ):
        assert phrase in commander, f"Missing root-cause confidence rule: {phrase!r}"


def test_all_agents_normalize_end_user_responses():
    entries = entries_by_name()
    agent_names = (
        "IncidentCommander",
        "KnowledgeAgent",
        "LogInvestigator",
        "ResolutionPlanner",
        "QualityReviewer",
        "ExecutiveReporter",
    )
    required_phrases = (
        "for direct end-user responses",
        "always render markdown",
        "headings",
        "bullet lists",
        "numbered steps",
        "never expose name, inquiry, mode",
        "response",
        "internal json payloads",
        "agent orchestration objects",
        "internal json is allowed only for agent-to-agent communication",
        "must never be shown to an end user",
    )
    for agent_name in agent_names:
        instructions = " ".join(entries[agent_name]["instructions"].casefold().split())
        for phrase in required_phrases:
            assert phrase in instructions, f"{agent_name} is missing {phrase!r}"


def test_retrieval_specialists_have_their_coded_tools():
    entries = entries_by_name()

    assert entries["LogInvestigator"]["tools"] == ["log_search"]
    assert entries["KnowledgeAgent"]["tools"] == ["kb_search"]
    assert entries["ResolutionPlanner"]["tools"] == ["resolution_plan_builder"]


def test_resolution_planner_requires_grounded_recovery_fields():
    instructions = entries_by_name()["ResolutionPlanner"]["instructions"].casefold()

    required_phrases = (
        "observed log evidence",
        "grounded kb content",
        "immediate actions",
        "validation actions",
        "expected outcome",
        "recovery confidence",
        "never create unsupported recommendations",
        "every action must trace directly",
        "kb resolution step #",
        "kb validation checklist item #",
        "do not infer actions from root cause",
        "do not generate commands",
        "unless that exact action explicitly exists",
        "verbatim kb resolution step text",
        "verbatim kb validation checklist text",
    )
    for phrase in required_phrases:
        assert phrase in instructions, f"ResolutionPlanner is missing {phrase!r}"


def test_quality_reviewer_requires_grounded_quality_checks():
    instructions = " ".join(entries_by_name()["QualityReviewer"]["instructions"].split()).casefold()

    required_phrases = (
        "validation gate between resolutionplanner and executivereporter",
        "verify that the referenced kb file or article id is present",
        "root cause is explicitly supported by the supplied log events",
        "every recovery and validation action is present in the supplied kb guidance",
        "grounding score: x%",
        "evidence completeness: x%",
        "kb coverage: x%",
        "recovery plan quality: x%",
        "overall score: x/100",
        "status:",
        "approved only when every required artifact is present",
        "needs review",
        "arithmetic mean of the four displayed percentages",
        "knowledge base article:",
        "not found",
        "manual investigation required",
        "never invent evidence",
        "never create new root causes",
        "never create new actions",
        "never return \"i'm not relevant.\"",
    )
    for phrase in required_phrases:
        assert phrase in instructions, f"QualityReviewer is missing {phrase!r}"

    forbidden_phrases = (
        "no numeric scoring",
        "no percentages",
        "never output an investigation quality score",
    )
    for phrase in forbidden_phrases:
        assert phrase not in instructions, f"QualityReviewer still forbids requested scoring: {phrase!r}"


def test_investigation_responses_require_grounding_evidence_footer():
    required_phrases = (
        "at the end of every incident investigation response",
        "grounding evidence",
        "incident record",
        "log events (<count>)",
        "knowledge base article (<kb_id>)",
        "resolution runbook",
        "evidence quality:",
        "grounded",
        "assumptions:",
        "use the actual count of log events",
        "never claim an evidence source that was not used",
        "knowledge base article: not found",
        "manual investigation required",
    )
    for agent_name in ("IncidentCommander", "ExecutiveReporter"):
        instructions = " ".join(entries_by_name()[agent_name]["instructions"].split()).casefold()
        for phrase in required_phrases:
            assert phrase in instructions, f"{agent_name} is missing {phrase!r}"


def test_all_agent_and_tool_references_resolve():
    entries = entries_by_name()
    declared_names = set(entries)

    references = {
        reference
        for entry in entries.values()
        for reference in entry.get("tools", [])
    }
    assert references <= declared_names

    coded_tool_entries = {
        name: entry for name, entry in entries.items() if "class" in entry
    }
    assert set(coded_tool_entries) == EXPECTED_CODED_TOOLS
    assert all(entry["class"] for entry in coded_tool_entries.values())


def test_mistral_cloud_configuration_is_unchanged():
    llm_config = load_registry().get("llm_config")

    assert dict(llm_config) == EXPECTED_LLM_CONFIG
