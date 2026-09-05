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
EXPECTED_CODED_TOOLS = {"log_search", "kb_search"}
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


def test_retrieval_specialists_have_their_coded_tools():
    entries = entries_by_name()

    assert entries["LogInvestigator"]["tools"] == ["log_search"]
    assert entries["KnowledgeAgent"]["tools"] == ["kb_search"]


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
        "investigation quality score",
        "missing information",
        "ready for execution",
        "execute with caution",
        "partial evidence",
        "requires further investigation",
        "never invent evidence",
        "never create new root causes",
        "never create new recommendations",
        "never create new actions",
        "no partial scoring",
        "never use ai confidence",
        "never output a confidence percentage",
        "maximum score = 100",
        "can never exceed 100",
        "clamp the investigation quality score to 100",
        "award each of the six components at most once",
        "explain scoring using the rubric",
        "score breakdown",
    )
    for phrase in required_phrases:
        assert phrase in instructions, f"QualityReviewer is missing {phrase!r}"

    for weight in (
        "incident found: 15 points",
        "log evidence found: 20 points",
        "kb match found: 20 points",
        "root cause identified: 15 points",
        "resolution plan present: 15 points",
        "validation steps present: 15 points",
    ):
        assert weight in instructions, f"QualityReviewer is missing score weight {weight!r}"


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
