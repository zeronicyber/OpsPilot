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
}
EXPECTED_CODED_TOOLS = {"log_search", "kb_search", "resolution_plan_builder"}
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
        "LogInvestigator",
        "KnowledgeAgent",
        "ResolutionPlanner",
        "QualityReviewer",
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


def test_all_agents_normalize_end_user_responses():
    entries = entries_by_name()
    agent_names = (
        "IncidentCommander",
        "KnowledgeAgent",
        "LogInvestigator",
        "ResolutionPlanner",
        "QualityReviewer",
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
    instructions = entries_by_name()["QualityReviewer"]["instructions"].casefold()

    required_phrases = (
        "incident found",
        "log evidence found",
        "kb match found",
        "root cause identified",
        "resolution plan present",
        "validation steps present",
        "missing information",
        "ready for execution",
        "execute with caution",
        "requires further investigation",
        "never invent evidence",
        "never create new root causes",
        "never create new recommendations",
        "never create new actions",
        "never use ai confidence",
        "never output a confidence percentage",
        "no numeric scoring",
        "no percentages",
        "no confidence scores",
        "never output an investigation quality score",
        "never return \"i'm not relevant.\"",
        "validation gate",
    )
    for phrase in required_phrases:
        assert phrase in instructions, f"QualityReviewer is missing {phrase!r}"

    forbidden_phrases = (
        "investigation quality score:",
        "maximum score = 100",
        "15 points",
        "20 points",
        "xx/100",
        "score breakdown",
        "partial evidence",
    )
    for phrase in forbidden_phrases:
        assert phrase not in instructions, f"QualityReviewer still contains {phrase!r}"


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
