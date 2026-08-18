"""Command-line interface for the MCP Evidence Validator.

Subcommands:
    validate  --declared manifest.json --observed observed.json --out evidence.json
    verify    --ledger evidence.json          (integrity check of a hash chain)
"""

import argparse
import json
import sys
from typing import Any

from . import __version__
from .ledger import Ledger
from .validator import validate_batch


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_validate(args: argparse.Namespace) -> int:
    declared = load_json(args.declared)
    observed = load_json(args.observed)

    led = Ledger()
    led.append("declaration", declared)
    led.append("observation_batch", observed)

    findings, summary = validate_batch(declared, observed)
    report = {"summary": summary, "findings": findings}
    led.append("report", report)

    problems = led.verify()
    if problems:
        print("LEDGER CORRUPT:", problems, file=sys.stderr)
        return 1

    led.dump(args.out)
    print(json.dumps(report, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        led = Ledger.load(args.ledger)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"verify failed: {exc}", file=sys.stderr)
        return 2

    problems = led.verify()
    if problems:
        print(f"LEDGER CORRUPT ({len(led)} blocks):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    types = {}
    for block in led:
        types[block["type"]] = types.get(block["type"], 0) + 1
    print(f"ledger intact: {len(led)} blocks, chain verified")
    print("block types:", json.dumps(types, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-ev-validate",
        description="MCP Evidence Validator - declared-vs-observed checks with "
        "a tamper-evident SHA-256 evidence ledger.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="compare declarations to observations")
    p_validate.add_argument("--declared", required=True, help="declared manifest JSON")
    p_validate.add_argument("--observed", required=True, help="observed runtime JSON")
    p_validate.add_argument("--out", required=True, help="output evidence ledger JSON")
    p_validate.set_defaults(func=cmd_validate)

    p_verify = sub.add_parser("verify", help="verify a ledger's hash chain integrity")
    p_verify.add_argument("--ledger", required=True, help="evidence ledger JSON")
    p_verify.set_defaults(func=cmd_verify)

    return parser


def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
