#!/usr/bin/env python3
"""MCP Evidence Validator CLI.

Compares declared MCP server state against observed runtime state and
emits a tamper-evident evidence ledger.

Usage:
  python3 validate.py --declared manifest.json --observed observed.json --out evidence.json
"""

import argparse
import json
import sys

from fingerprint import fingerprint
from ledger import Ledger


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_contract(tool: dict) -> str:
    """Canonical fingerprint of a tool declaration."""
    return fingerprint({
        "name": tool["name"],
        "description": tool.get("description", ""),
        "input_schema": tool.get("input_schema", {}),
        "permissions": tool.get("permissions", []),
    })


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Evidence Validator")
    parser.add_argument("--declared", required=True, help="declared manifest JSON")
    parser.add_argument("--observed", required=True, help="observed runtime JSON")
    parser.add_argument("--out", required=True, help="output evidence ledger JSON")
    args = parser.parse_args()

    declared = load_json(args.declared)
    observed = load_json(args.observed)

    led = Ledger()
    led.append("declaration", declared)
    led.append("observation_batch", observed)

    tools = {t["name"]: t for t in declared.get("tools", [])}
    annotations = declared.get("annotations", [])
    ann_by_tool = {}
    for ann in annotations:
        ann_by_tool.setdefault(ann.get("tool"), []).append(ann)

    findings = []
    obs_list = observed.get("observations", [])

    for obs in obs_list:
        tool_name = obs.get("tool")
        decl = tools.get(tool_name)
        if decl is None:
            findings.append({
                "observation_index": obs.get("index", 0),
                "check": "unknown_tool",
                "severity": "high",
                "detail": f"tool '{tool_name}' observed but not declared",
            })
            led.append("observation", obs)
            continue

        current = build_contract(decl)
        observed_hash = obs.get("contract_hash")
        anns = ann_by_tool.get(tool_name, [])
        bound = any(a.get("bound_contract") == current for a in anns)

        # Check 1: bound and unmutated (healthy baseline)
        # Check 2: contract mutated since declaration (stale annotation)
        if observed_hash is not None and observed_hash != current:
            findings.append({
                "observation_index": obs.get("index", 0),
                "check": "contract_mutated",
                "severity": "medium",
                "detail": f"annotation bound to contract that has changed since declaration",
                "declared_contract": current,
                "observed_contract": observed_hash,
            })
        elif not bound and observed_hash == current:
            findings.append({
                "observation_index": obs.get("index", 0),
                "check": "unbound_annotation",
                "severity": "low",
                "detail": f"tool '{tool_name}' observed with no annotation bound to the current contract",
            })

        # Check 3: observed arguments outside declared input schema
        allowed = set((decl.get("input_schema") or {}).get("properties", {}).keys())
        actual = set((obs.get("args") or {}).keys())
        extra = actual - allowed
        if extra:
            findings.append({
                "observation_index": obs.get("index", 0),
                "check": "scope_violation",
                "severity": "high",
                "detail": f"arguments outside declared schema: {sorted(extra)}",
            })

        led.append("observation", obs)

    report = {
        "summary": {
            "declared_tools": len(tools),
            "observations": len(obs_list),
            "findings": len(findings),
            "checks": ["bound_unmutated", "contract_mutated", "scope_violation"],
        },
        "findings": findings,
    }
    led.append("report", report)

    problems = led.verify()
    if problems:
        print("LEDGER CORRUPT:", problems, file=sys.stderr)
        return 1

    led.dump(args.out)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
