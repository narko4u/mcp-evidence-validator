# MCP Evidence Validator

Validate what an MCP server *declares* against what it *actually does*, and produce a tamper-evident evidence record you can hand to an auditor.

**Status:** Prototype (draft v0.1)  
**License:** Apache-2.0  
**Language:** Python 3.10+ (stdlib only)

---

## Why

Model Context Protocol (MCP) is the industry standard for connecting AI agents to tools and data. It is now governed by the Agentic AI Foundation (AAIF) under the Linux Foundation, with 97M+ monthly SDK downloads and 10,000+ active public servers.

But the protocol leaves the *evidence* problem open:

- A server declares tool schemas and permissions, but nothing verifies those declarations against observed runtime behaviour.
- An annotation can be accurate at declaration time and silently stale minutes later, when the contract it was bound to mutates underneath it.
- MCP has already seen the first malicious server (Sept 2025), CVE-2025-6514 (CVSS 9.6, RCE), and a hosting-platform breach affecting 3,000+ downstream applications.

The **declared-vs-observed gap** is the measurement finding that matters. This validator is a reference implementation for closing it.

## What it does

1. **Captures declarations** - the tool schemas, permissions, and annotations an MCP server publishes.
2. **Observes reality** - the tool invocations, argument shapes, and contract hashes seen at runtime.
3. **Checks the gap** - declared annotation still bound? Contract mutated since declaration? Privilege use inside declared scope?
4. **Produces a tamper-evident ledger** - every check result is committed to a SHA-256 hash chain. Changing any earlier record invalidates every record after it.

## Quick start

```bash
cd prototype
python3 validate.py --declared ../examples/fictional-server-declared.json \
                    --observed ../examples/fictional-server-observed.json \
                    --out /tmp/evidence.json
cat /tmp/evidence.json
```

Output is a machine-readable evidence record with a `chain` of hash-linked entries plus a human-readable `findings` summary.

## Concepts

| Term | Meaning |
|------|---------|
| Declaration | What a server publishes: tool name, description, input schema, permission scope |
| Contract | A canonical, hashable form of a declaration (canonical JSON → SHA-256) |
| Annotation | A statement binding a declaration to a contract (e.g. "this tool is scoped to read-only") |
| Observation | A runtime fact: invocation record, argument values, contract hash at call time |
| Finding | A measurable gap between declaration and observation |
| Ledger | An append-only SHA-256 hash chain over every captured record |

## Check types (prototype)

- **Bound, contract unmutated** - healthy baseline: annotation still matches the contract it was declared against.
- **Bound, contract since mutated** - finding: the annotation was accurate at declaration time but is stale because the contract moved underneath it. Pairs with a review-scheduling gate.
- **Observed outside declared scope** - finding: runtime behaviour exceeds what the declaration permits (arguments, tools, or permissions not present in the declaration).

## Roadmap

- [ ] MCP client integration (intercept tool-call records via a lightweight proxy)
- [ ] Automated review-scheduling gate (re-validate annotations on contract change)
- [ ] Report renderers (JSON, HTML, PDF)
- [ ] Policy pack support (declare what "acceptable" means per environment)

## Project status

This is the public face of an evidence-engineering programme. The core ideas are exercised in production-grade systems elsewhere in the organisation; this repository is the open, reference implementation. It contains no proprietary code and no real client data. All examples are fictional.

## Feedback

Open an issue or start a discussion. Contributions welcome under the Apache-2.0 licence.
