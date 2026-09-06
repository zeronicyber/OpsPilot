import asyncio

from coded_tools.opspilot.resolution_plan_builder import ResolutionPlanBuilder


KB_ARGS = {
    "incident_id": "INC008381110",
    "kb_file": "KB-1101.md",
    "kb_title": "Jupyter Notebook Kernel Startup Failure",
    "resolution_steps": "1. Install ipykernel.\n2. Rebuild the kernelspec.\n",
    "validation_checklist": "- [ ] Kernel starts successfully.\n- [ ] Test cell executes.\n",
}


def test_builds_only_numbered_kb_actions():
    result = asyncio.run(ResolutionPlanBuilder().async_invoke(KB_ARGS, {}))

    assert result["status"] == "READY_FOR_REVIEW"
    assert result["recovery_actions"] == [
        {
            "action_number": 1,
            "action": "Install ipykernel.",
            "source": "KB-1101.md Resolution Step #1",
        },
        {
            "action_number": 2,
            "action": "Rebuild the kernelspec.",
            "source": "KB-1101.md Resolution Step #2",
        },
    ]
    assert result["validation_actions"] == [
        {
            "validation_number": 1,
            "action": "Kernel starts successfully.",
            "source": "KB-1101.md Validation Checklist #1",
        },
        {
            "validation_number": 2,
            "action": "Test cell executes.",
            "source": "KB-1101.md Validation Checklist #2",
        },
    ]
    assert result["missing_information"] == []


def test_missing_resolution_steps_is_insufficient_evidence():
    arguments = {**KB_ARGS, "resolution_steps": ""}

    result = ResolutionPlanBuilder().invoke(arguments, {})

    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["missing_information"] == ["KB resolution steps"]
    assert "recovery_actions" not in result


def test_missing_validation_checklist_is_insufficient_evidence():
    arguments = {**KB_ARGS, "validation_checklist": ""}

    result = ResolutionPlanBuilder().invoke(arguments, {})

    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["missing_information"] == ["KB validation checklist"]
    assert "validation_actions" not in result


def test_multiline_items_are_normalized_without_rewriting_content():
    arguments = {
        **KB_ARGS,
        "resolution_steps": "1. Clear stale connections\n   before restart.\n",
        "validation_checklist": "1. Login succeeds.\n2) Workspace launches.\n",
    }

    result = ResolutionPlanBuilder().invoke(arguments, {})

    assert result["recovery_actions"][0]["action"] == "Clear stale connections before restart."
    assert result["validation_actions"][1]["action"] == "Workspace launches."
