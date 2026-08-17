"""Core validation logic: declared vs observed MCP server state.

Produces findings for the declared-vs-observed gap and a human-readable
summary. The caller is responsible for ledger bookkeeping.
"""

from typing import Any, Dict, List, Tuple

from .fingerprint import fingerprint


def build_contract(tool: Dict[str, Any]) -> str:
    """Canonical fingerprint of a tool declaration."""
    return fingerprint(
        {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "input_schema": tool.get("input_schema", {}),
            "permissions": tool.get("permissions", []),
        }
    )


def validate_batch(
    declared: Dict[str, Any], observed: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Compare a declared manifest against an observed runtime batch.

    Returns (findings, summary). Findings are dicts with keys:
    observation_index, check, severity, detail, and check-specific extras.
    """
    tools = {t["name"]: t for t in declared.get("tools", [])}
    annotations = declared.get("annotations", [])
    ann_by_tool: Dict[str, List[Dict[str, Any]]] = {}
    for ann in annotations:
        ann_by_tool.setdefault(ann.get("tool"), []).append(ann)

    findings: List[Dict[str, Any]] = []
    obs_list = observed.get("observations", [])

    for obs in obs_list:
        tool_name = obs.get("tool")
        decl = tools.get(tool_name)
        if decl is None:
            findings.append(
                {
                    "observation_index": obs.get("index", 0),
                    "check": "unknown_tool",
                    "severity": "high",
                    "detail": f"tool '{tool_name}' observed but not declared",
                }
            )
            continue

        current = build_contract(decl)
        observed_hash = obs.get("contract_hash")
        anns = ann_by_tool.get(tool_name, [])
        bound = any(a.get("bound_contract") == current for a in anns)

        # Check 1: bound and unmutated (healthy baseline - no finding emitted)
        # Check 2: contract mutated since declaration (stale annotation)
        if observed_hash is not None and observed_hash != current:
            findings.append(
                {
                    "observation_index": obs.get("index", 0),
                    "check": "contract_mutated",
                    "severity": "medium",
                    "detail": (
                        "annotation bound to contract that has changed "
                        "since declaration"
                    ),
                    "declared_contract": current,
                    "observed_contract": observed_hash,
                }
            )
        elif not bound and observed_hash == current:
            findings.append(
                {
                    "observation_index": obs.get("index", 0),
                    "check": "unbound_annotation",
                    "severity": "low",
                    "detail": (
                        f"tool '{tool_name}' observed with no annotation "
                        "bound to the current contract"
                    ),
                }
            )

        # Check 3: observed arguments outside declared input schema
        allowed = set((decl.get("input_schema") or {}).get("properties", {}).keys())
        actual = set((obs.get("args") or {}).keys())
        extra = actual - allowed
        if extra:
            findings.append(
                {
                    "observation_index": obs.get("index", 0),
                    "check": "scope_violation",
                    "severity": "high",
                    "detail": f"arguments outside declared schema: {sorted(extra)}",
                }
            )

    summary = {
        "declared_tools": len(tools),
        "observations": len(obs_list),
        "findings": len(findings),
        "checks": ["bound_unmutated", "contract_mutated", "scope_violation"],
    }
    return findings, summary
