#!/usr/bin/env python3
"""Capture an MCP server session in which the *agent* chose the call.

Why this exists, next to `capture_mcp_server.py`:

`capture_mcp_server.py` walks a fixed list of tools (``--call read_text_file
...``) and derives each call's arguments from a hardcoded table. The recorded
calls are therefore the ones the script was told to make. No model is in the
loop, and nothing in the resulting artifact says which model, if any, directed
them. A TRACE record built from such a run cannot truthfully populate
``model`` - there was no model in the execution being attested.

This script splits the run in two so the model's decision becomes a real,
inspectable artifact:

  phase 1  --menu OUT
           start the server, ask ``tools/list``, write the menu the model will
           choose from. No calls are made.

           (the model reads that menu and writes a directive: a tool name, the
           exact arguments, and the reasoning behind the choice)

  phase 2  --directive IN
           read the directive, start the server, execute exactly that one call,
           and record the directive's digest beside the observed call.

The directive is authored between the phases, from the menu alone. Both files
land in the capture, so a reader can check the choice against the menu the
model was actually shown, and the call against the directive the model
actually wrote. Nothing here invents a call, and the script never picks a tool
on the model's behalf.

The two phases are separate processes on purpose: phase 2 never sees the menu
phase's memory, only the menu file, so the directive has to stand on its own.

Usage:

  python3 examples/agent_directed_capture.py menu \\
      --package @modelcontextprotocol/server-filesystem --version 2026.8.31 \\
      --root /tmp/agent-directed-root --out /tmp/menu.json

  # ... model authors the directive from /tmp/menu.json ...

  python3 examples/agent_directed_capture.py execute \\
      --package @modelcontextprotocol/server-filesystem --version 2026.8.31 \\
      --root /tmp/agent-directed-root --directive /tmp/directive.json \\
      --label agent-directed --examples-dir examples

Writes, under the examples dir:

  <label>-declared.json              the declared side of the pair
  <label>-observed.json              the observed side of the pair
  captures/<label>-<version>.declared.tools-list.json
  captures/<label>-<version>.calls.json   calls, carrying the directive digest
  captures/<label>-directive.json         the model's directive, verbatim
"""

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from capture_mcp_server import (  # noqa: E402
    CONTRACT_RECIPE_CURRENT,
    CONTRACT_RECIPE_FIELDS,
    Session,
    build_contract,
    build_pair,
    sha256_file,
    to_declared,
    write_json,
)

DIRECTIVE_VERSION = "agent-directive/1"


def capture_menu(package, version, root):
    """Phase 1: the menu the model chooses from, and nothing else."""
    session = Session(package, version, root).start()
    try:
        tools = session.tools()
        return {
            "directive_version": DIRECTIVE_VERSION,
            "package": package,
            "version": version,
            "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "protocol_version": session.negotiated,
            "server_info": session.server_info,
            # The menu is the server's own tools/list reply, verbatim: no
            # field is renamed or dropped. `build_pair`/`to_declared` read the
            # served camelCase shape, and a menu that had been reshaped for
            # readability would hash to a different contract than the server
            # actually served - which reads as contract drift that never
            # happened.
            "tools": tools,
        }
    finally:
        session.close()


def validate_directive(directive, menu):
    """Refuse a directive that does not name a real tool with schema-valid args.

    The point of the directive is that the model's choice is recorded, not that
    it is unfalsifiable. These checks make the recorded choice checkable against
    the menu the model was shown: a tool that was not served, or an argument the
    served schema does not declare, is rejected here rather than quietly
    landing in a transcript that reads as if the model asked for it.
    """
    problems = []
    served = {t["name"]: t for t in menu["tools"]}
    tool = directive.get("tool")
    if tool not in served:
        problems.append(f"tool {tool!r} was not served in the menu")
        return problems
    if not directive.get("director", {}).get("model_id"):
        problems.append("directive carries no director.model_id")
    if not directive.get("rationale"):
        problems.append("directive carries no rationale")

    schema = served[tool].get("inputSchema") or {}
    props = schema.get("properties", {})
    args = directive.get("arguments", {})
    for name in args:
        if name not in props:
            problems.append(f"argument {name!r} is not declared by {tool!r}'s schema")
    for name in schema.get("required", []):
        if name not in args:
            problems.append(f"required argument {name!r} is missing from the directive")
    return problems


def capture_directed(package, version, root, directive, recipe=CONTRACT_RECIPE_CURRENT):
    """Phase 2: execute exactly the directed call, in its own session.

    The manifest the call runs under is captured in this same session, because
    the contract a call was made under is the one that session served. Deriving
    it from the menu session would assert a contract that was never in force
    when the call was made.
    """
    session = Session(package, version, root).start()
    try:
        manifest = session.tools()
        served = {t["name"]: t for t in manifest}
        name = directive["tool"]
        if name not in served:
            raise SystemExit(f"{package}@{version} does not serve a tool named {name!r}")
        arguments = directive["arguments"]
        outcome = session.call(101, name, arguments)
        return {
            "directive_version": DIRECTIVE_VERSION,
            "package": package,
            "version": version,
            "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "protocol_version": session.negotiated,
            "server_info": session.server_info,
            "root": str(root),
            "contract_recipe": recipe,
            "directed_by": directive.get("director", {}),
            "directive": directive,
            "tools": manifest,
            "calls": [
                {
                    "index": 1,
                    "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "tool": name,
                    "args": arguments,
                    "rel_args": {
                        key: str(Path(value).relative_to(root))
                        if isinstance(value, str)
                        and str(value).startswith(str(root) + "/")
                        else value
                        for key, value in arguments.items()
                    },
                    "contract_hash": build_contract(to_declared(served[name], recipe)),
                    "contract_recipe": recipe,
                    "outcome": outcome,
                }
            ],
        }
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="phase", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--package", required=True)
    common.add_argument("--version", required=True)
    common.add_argument("--root", required=True)

    p_menu = sub.add_parser("menu", parents=[common], help="phase 1: write the tool menu")
    p_menu.add_argument("--out", required=True)

    p_exec = sub.add_parser("execute", parents=[common], help="phase 2: run the directive")
    p_exec.add_argument("--directive", required=True)
    p_exec.add_argument("--label", default="agent-directed")
    p_exec.add_argument("--examples-dir", default=str(HERE))
    p_exec.add_argument(
        "--recipe", default=CONTRACT_RECIPE_CURRENT, choices=sorted(CONTRACT_RECIPE_FIELDS)
    )

    args = parser.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)

    if args.phase == "menu":
        menu = capture_menu(args.package, args.version, root)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(menu, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"menu: {len(menu['tools'])} tools from "
              f"{menu['server_info'].get('name')}@{args.version}")
        print(f"      {out}  {sha256_file(out)}")
        print("      the model chooses from this file alone; no calls were made.")
        return 0

    examples = Path(args.examples_dir)
    captures = examples / "captures"
    directive_path = Path(args.directive)
    directive = json.loads(directive_path.read_text(encoding="utf-8"))

    # The menu the model was shown is re-derived from the server, and the
    # directive is checked against it, so a directive cannot name a tool or an
    # argument that was never on the menu.
    menu = capture_menu(args.package, args.version, root)
    problems = validate_directive(directive, menu)
    if problems:
        for problem in problems:
            print(f"directive rejected: {problem}", file=sys.stderr)
        return 2

    calls_raw = capture_directed(
        args.package, args.version, root, directive, args.recipe
    )
    calls_raw["directive_hash"] = sha256_file(directive_path)

    # Same version on both sides: this is a clean run, so the pair is expected
    # to show no contract drift. The mutated pair lives in the other example.
    declared, observed = build_pair(
        menu, menu, calls_raw, args.package, args.version, args.recipe
    )

    declared_path = examples / f"{args.label}-declared.json"
    observed_path = examples / f"{args.label}-observed.json"
    declared_hash = write_json(declared_path, declared)
    observed_hash = write_json(observed_path, observed)

    raw_declared = captures / f"{args.label}-{args.version}.declared.tools-list.json"
    raw_calls = captures / f"{args.label}-{args.version}.calls.json"
    raw_directive = captures / f"{args.label}-directive.json"
    raw_declared_hash = write_json(raw_declared, menu)
    raw_calls_hash = write_json(raw_calls, calls_raw)
    raw_directive_hash = write_json(raw_directive, directive)

    record = calls_raw["calls"][0]
    print(f"directed by : {calls_raw['directed_by']}")
    print(f"tool        : {record['tool']}")
    print(f"arguments   : {record['args']}")
    print(f"isError     : {record['outcome']['isError']}")
    print(f"content     : {record['outcome']['content_types']}")
    print()
    print(f"declared  {declared_path}  {declared_hash}")
    print(f"observed  {observed_path}  {observed_hash}")
    print(f"directive {raw_directive}  {raw_directive_hash}")
    print(f"raw       {raw_declared_hash} {raw_calls_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
