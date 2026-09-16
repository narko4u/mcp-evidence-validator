"""The filesystem-server example: a real capture, and the drift inside it.

`examples/capture_mcp_server.py` starts a published MCP server over stdio, so
every contract hash in the pair tested here came out of the server itself. These
tests recompute those hashes from the raw captures in `examples/captures/`, then
run the validator over the pair.

The pair is static, so the tests need neither Node.js nor network access.
"""

import json
import os
import sys
from pathlib import Path

from mcp_evidence_validator.cli import load_json, main
from mcp_evidence_validator.fingerprint import fingerprint
from mcp_evidence_validator.validator import (
    CONTRACT_RECIPE_CURRENT,
    CONTRACT_RECIPE_FIELDS,
    build_contract,
    contract_payload,
    validate_batch,
)

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "examples"
CAPTURES = EXAMPLES / "captures"
sys.path.insert(0, str(EXAMPLES))

from capture_mcp_server import build_pair  # noqa: E402

LABEL = "filesystem-server"
PACKAGE = "@modelcontextprotocol/server-filesystem"
DECLARED_VERSION = "2026.1.14"
OBSERVED_VERSION = "2026.8.31"


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def to_declared(tool, recipe=CONTRACT_RECIPE_CURRENT):
    """The mapping the capture script applies to a served tool object."""
    declared = {
        "name": tool["name"],
        "description": tool.get("description", ""),
        "input_schema": tool.get("inputSchema", {}),
        "permissions": tool.get("permissions", []),
    }
    if recipe in ("2", "3"):
        declared["output_schema"] = tool.get("outputSchema", {})
        declared["annotations"] = tool.get("annotations", {})
    if recipe == "3":
        declared["title"] = tool.get("title", "")
        declared["execution"] = tool.get("execution", {})
    declared["contract_recipe"] = recipe
    return declared


def served_tools(raw, recipe=CONTRACT_RECIPE_CURRENT):
    return {tool["name"]: to_declared(tool, recipe) for tool in raw["tools"]}


def captures():
    declared = load(CAPTURES / f"{LABEL}-{DECLARED_VERSION}.tools-list.json")
    observed = load(CAPTURES / f"{LABEL}-{OBSERVED_VERSION}.tools-list.json")
    calls = load(CAPTURES / f"{LABEL}-{OBSERVED_VERSION}.calls.json")
    return declared, observed, calls


def example_pair():
    return (
        load(EXAMPLES / f"{LABEL}-declared.json"),
        load(EXAMPLES / f"{LABEL}-observed.json"),
    )


def test_the_pair_carries_the_captured_manifests():
    declared_raw, observed_raw, calls_raw = captures()
    declared, observed = example_pair()

    assert declared["server"] == declared_raw["server_info"]["name"]
    assert observed["server"] == calls_raw["server_info"]["name"]
    assert {tool["name"]: tool for tool in declared["tools"]} == served_tools(declared_raw)

    # The observed side derives from the manifest the *call* session served, so
    # the capture must carry it: a separate tools/list session is provenance,
    # not the declaration those calls ran under.
    call_session = served_tools(calls_raw)
    for observation, raw_call in zip(
        observed["observations"], calls_raw["calls"], strict=True
    ):
        assert observation["tool"] == raw_call["tool"]
        assert observation["observed_at"] == raw_call["observed_at"]
        assert observation["contract_hash"] == build_contract(
            call_session[raw_call["tool"]]
        )
        # Arguments are recorded relative to the server's allowed root; the raw
        # capture holds the byte-exact ones.
        assert observation["args"] == {
            key: os.path.relpath(value, calls_raw["root"])
            if isinstance(value, str) and value.startswith(calls_raw["root"])
            else value
            for key, value in raw_call["args"].items()
        }


def test_the_call_session_manifest_agrees_with_the_tools_list_session():
    """Both sessions are recorded, and this capture shows them agreeing.

    The calls were made against one session and a separate tools/list session
    listed the same version. The pair claims the call session's declaration, so
    if the two ever disagreed for a called tool, the evidence for that would
    live here rather than being averaged away.
    """
    _, observed_raw, calls_raw = captures()
    flat = {tool["name"]: to_declared(tool) for tool in observed_raw["tools"]}
    call_session = {tool["name"]: to_declared(tool) for tool in calls_raw["tools"]}

    for call in calls_raw["calls"]:
        name = call["tool"]
        assert name in flat, f"{name} was called but the tools/list session lacked it"
        assert build_contract(call_session[name]) == build_contract(flat[name])
        # The call-time hash the session recorded is the same value, so the
        # stored evidence and the derivation cannot disagree silently.
        assert call["contract_hash"] == build_contract(call_session[name])


def test_a_capture_without_its_call_session_manifest_is_refused():
    """A capture that cannot supply its own session's manifest stops the build.

    Previously the per-call manifest was taken from the tools/list session
    whatever the call session had served. A server may vary its declaration per
    session, so that could assert a contract the call never ran under; the
    fallback is now a refusal to derive, not a guess.
    """
    import pytest

    declared_raw, observed_raw, calls_raw = captures()
    stripped = {key: value for key, value in calls_raw.items() if key != "tools"}
    with pytest.raises(SystemExit, match="call-session manifests"):
        build_pair(declared_raw, observed_raw, stripped, PACKAGE, DECLARED_VERSION)


def test_the_pair_is_exactly_what_the_captures_derive():
    """The pair is a view of the captures, not a hand-maintained document.

    Both sides are regenerated here by the same function the capture script and
    `examples/rebuild_pair.py` use, so an edit made directly to a pair file
    fails this test rather than quietly becoming evidence.
    """
    declared_raw, observed_raw, calls_raw = captures()
    declared, observed = example_pair()
    assert (declared, observed) == build_pair(
        declared_raw, observed_raw, calls_raw, PACKAGE, DECLARED_VERSION
    )


def test_the_capture_is_self_describing_about_its_recipe():
    """The recipe travels next to the hashes it produced, in every artifact."""
    declared_raw, observed_raw, calls_raw = captures()
    declared, observed = example_pair()

    assert calls_raw["contract_recipe"] == CONTRACT_RECIPE_CURRENT
    assert declared["contract_recipe"] == CONTRACT_RECIPE_CURRENT
    assert observed["contract_recipe"] == CONTRACT_RECIPE_CURRENT
    for call in calls_raw["calls"]:
        assert call["contract_recipe"] == CONTRACT_RECIPE_CURRENT
    for observation in observed["observations"]:
        assert observation["contract_recipe"] == CONTRACT_RECIPE_CURRENT
    for tool in declared["tools"]:
        assert tool["contract_recipe"] == CONTRACT_RECIPE_CURRENT


def test_the_example_finds_the_real_contract_mutation():
    declared, observed = example_pair()
    findings, summary = validate_batch(declared, observed)

    assert summary["declared_tools"] == 14
    assert summary["observations"] == 3
    assert summary["findings"] == 3
    assert summary["contract_recipes"] == [CONTRACT_RECIPE_CURRENT]

    assert {f["check"] for f in findings} == {"contract_mutated"}
    assert {f["severity"] for f in findings} == {"medium"}
    assert {f["contract_recipe"] for f in findings} == {CONTRACT_RECIPE_CURRENT}
    assert [
        observed["observations"][f["observation_index"] - 1]["tool"] for f in findings
    ] == ["read_text_file", "read_media_file", "get_file_info"]

    declared_raw, observed_raw, _ = captures()
    read_media = next(
        f for f in findings
        if observed["observations"][f["observation_index"] - 1]["tool"]
        == "read_media_file"
    )
    assert read_media["declared_contract"] == build_contract(
        served_tools(declared_raw)["read_media_file"]
    )
    assert read_media["observed_contract"] == build_contract(
        served_tools(observed_raw)["read_media_file"]
    )
    assert read_media["declared_contract"] != read_media["observed_contract"]


def test_recipe_2_was_required_to_see_two_of_the_three_mutations():
    """Two of the three findings are changes recipe 1 signed off as healthy.

    The 2026.8.31 release added an ``openWorldHint`` annotation to every tool.
    That leaves ``read_text_file`` and ``get_file_info`` byte-identical under
    recipe 1 while their contracts genuinely moved - which is the argument for
    the wider recipe, made by the example rather than by description.
    """
    declared_raw, observed_raw, _ = captures()
    for name in ("read_text_file", "get_file_info"):
        old = served_tools(declared_raw)[name]
        new = served_tools(observed_raw)[name]

        assert build_contract(old, "1") == build_contract(new, "1")
        assert build_contract(old, "2") != build_contract(new, "2")
        assert old["annotations"] != new["annotations"]

    # The third changed its description and output schema too, so recipe 1 saw
    # that one - it just could not say anything about what the tool returns.
    old = served_tools(declared_raw)["read_media_file"]
    new = served_tools(observed_raw)["read_media_file"]
    assert build_contract(old, "1") != build_contract(new, "1")


def test_only_the_observed_tools_are_annotated():
    """Unannotated calls report unbound_annotation, so the pair binds all three."""
    declared, observed = example_pair()
    annotated = {annotation["tool"] for annotation in declared["annotations"]}
    assert annotated == {observation["tool"] for observation in observed["observations"]}


def test_what_moved_between_the_two_versions():
    """The input schema is identical either side; the description and the
    declared output schema both moved."""
    declared_raw, observed_raw, _ = captures()
    old = served_tools(declared_raw)["read_media_file"]
    new = served_tools(observed_raw)["read_media_file"]
    raw_old = {tool["name"]: tool for tool in declared_raw["tools"]}["read_media_file"]
    raw_new = {tool["name"]: tool for tool in observed_raw["tools"]}["read_media_file"]

    assert old["input_schema"] == new["input_schema"]
    assert old["description"] != new["description"]
    assert old["output_schema"] == raw_old["outputSchema"]
    assert new["output_schema"] == raw_new["outputSchema"]
    assert old["output_schema"] != new["output_schema"]


def test_recipe_1_was_blind_to_an_output_schema_only_change():
    """The hole issue #23 described, pinned deliberately.

    Recipe 1 folds four fields, so a server that changes only what it returns
    keeps the same contract hash and the tool reports healthy. This is the
    reason recipe 2 exists, and it stays asserted so the gap cannot quietly
    reappear as a "fix" that weakens the contract again.
    """
    declared_raw, _, _ = captures()
    old = served_tools(declared_raw)["read_media_file"]
    changed_output = dict(old, output_schema={"type": "object", "changed": True})

    assert build_contract(changed_output, "1") == build_contract(old, "1")
    assert build_contract(changed_output, "2") != build_contract(old, "2")


def test_recipe_2_hashes_the_declared_output_schema():
    declared_raw, _, _ = captures()
    old = served_tools(declared_raw)["read_media_file"]

    payload = contract_payload(old, "2")
    assert list(payload) == [
        "name",
        "description",
        "input_schema",
        "permissions",
        "output_schema",
        "annotations",
    ]
    assert payload["output_schema"] == old["output_schema"]
    assert build_contract(old, "2") == fingerprint(payload)


def test_recipe_2_hashes_the_annotation_hints():
    """A tool's annotation hints are part of its contract, not a footnote."""
    declared_raw, _, _ = captures()
    old = served_tools(declared_raw)["create_directory"]
    assert old["annotations"], "the capture should carry annotation hints"

    hinted = dict(old, annotations=dict(old["annotations"], destructiveHint=True))
    assert build_contract(hinted, "2") != build_contract(old, "2")
    assert build_contract(hinted, "1") == build_contract(old, "1")


def test_recipe_2_was_blind_to_title_and_execution():
    """The hole issue #26 described, pinned deliberately.

    Recipe 2 folds the output schema and the annotation hints, but every served
    tool also carries a ``title`` and an ``execution`` block and neither was in
    the hash: a server could retitle a tool, or change what its execution
    permits, and report healthy.

    The captures show both fields served and *unchanged* between the two
    versions, so this gap is pinned with a constructed mutation rather than one
    the example exhibits. The capture proves the fields ride on the wire; it
    does not prove they ever moved, and saying otherwise would be inventing
    evidence the pair does not hold.
    """
    declared_raw, _, _ = captures()
    old = served_tools(declared_raw)["read_text_file"]
    assert old["title"], "the capture should carry a served title"
    assert old["execution"], "the capture should carry an execution block"

    retitled = dict(old, title="Something Else Entirely")
    retasked = dict(old, execution={"taskSupport": "required"})
    assert retitled["title"] != old["title"]
    assert retasked["execution"] != old["execution"]

    for mutated in (retitled, retasked):
        assert build_contract(mutated, "2") == build_contract(old, "2")
        assert build_contract(mutated, "3") != build_contract(old, "3")


def test_recipe_3_still_excludes_the_fields_no_capture_carries():
    """``_meta`` and ``icons`` are deliberately outside every recipe.

    No capture has carried either, and folding a field into the contract that
    the declaration does not carry would hash the fallback default as though a
    server had served it. The exclusion is a measurement, not an oversight, so
    it is asserted against the captures rather than asserted in a comment.
    """
    for capture in captures():
        for tool in capture["tools"]:
            assert "_meta" not in tool
            assert "icons" not in tool


def test_every_field_a_recipe_hashes_is_carried_by_the_capture_mapping():
    """A recipe must not hash a field the declaration mapping drops.

    If the mapping omits a field the recipe covers, the hash covers the
    fallback default and reports a contract nobody captured. Running this over
    every known recipe means adding one without carrying its fields fails here,
    instead of quietly widening what "unchanged" is taken to mean.
    """
    declared_raw, _, _ = captures()
    raw = {tool["name"]: tool for tool in declared_raw["tools"]}["read_text_file"]

    for recipe in sorted(CONTRACT_RECIPE_FIELDS):
        declared = to_declared(raw, recipe)
        for field in CONTRACT_RECIPE_FIELDS[recipe]:
            assert field in declared, (
                f"recipe {recipe} hashes {field!r} but the capture mapping "
                f"drops it, so the hash would cover a default"
            )

    # And the fields recipe 3 was introduced for carry what was served.
    declared = to_declared(raw, "3")
    assert declared["title"] == raw["title"]
    assert declared["execution"] == raw["execution"]


def test_recipe_3_hashes_exactly_the_declared_title_and_execution():
    """Recipe 3 is recipe 2 plus two fields, and no fewer.

    This pins the field set in both directions: a field silently dropped would
    weaken the contract back to a gap this release exists to close, and a field
    silently added would change what every recipe-3 hash means without a recipe
    of its own.
    """
    declared_raw, _, _ = captures()
    old = served_tools(declared_raw)["read_text_file"]

    payload = contract_payload(old, "3")
    assert list(payload) == [
        "name",
        "description",
        "input_schema",
        "permissions",
        "output_schema",
        "annotations",
        "title",
        "execution",
    ]
    assert payload["title"] == old["title"]
    assert payload["execution"] == old["execution"]
    assert build_contract(old, "3") == fingerprint(payload)

    # The recipe-2 field set is untouched: widening is a new recipe, never a
    # redefinition of an existing one.
    assert list(contract_payload(old, "2")) == [
        "name",
        "description",
        "input_schema",
        "permissions",
        "output_schema",
        "annotations",
    ]


def test_a_single_tool_can_opt_out_of_the_manifest_recipe():
    declared_raw, _, _ = captures()
    tool = served_tools(declared_raw)["read_text_file"]
    legacy = dict(tool, contract_recipe="1")
    assert build_contract(legacy) == build_contract(tool, "1")
    assert build_contract(legacy) != build_contract(tool, "2")


def test_the_pair_runs_through_the_cli(tmp_path, capsys):
    declared, observed = example_pair()
    declared_path = tmp_path / "declared.json"
    observed_path = tmp_path / "observed.json"
    out = tmp_path / "evidence.json"
    declared_path.write_text(json.dumps(declared), encoding="utf-8")
    observed_path.write_text(json.dumps(observed), encoding="utf-8")

    rc = main(
        [
            "validate",
            "--declared",
            str(declared_path),
            "--observed",
            str(observed_path),
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert "contract_recipe" not in capsys.readouterr().err

    ledger = load_json(str(out))
    assert ledger["version"] == "0.3"
    report = ledger["blocks"][2]["record"]
    assert report["summary"]["findings"] == 3
    assert report["summary"]["contract_recipes"] == [CONTRACT_RECIPE_CURRENT]
    assert {f["check"] for f in report["findings"]} == {"contract_mutated"}

    head = ledger["blocks"][-1]["hash"]
    assert main(["verify", "--ledger", str(out), "--expected-head", head]) == 0
    assert f"contract recipes: {CONTRACT_RECIPE_CURRENT}" in capsys.readouterr().out
