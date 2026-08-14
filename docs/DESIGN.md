# Design: MCP Evidence Validator (draft v0.1)

## 1. Goal

Provide a repeatable, machine-checkable way to answer the question an auditor asks:

> "How do I know this MCP server is still doing what it said it would do?"

The answer is an **evidence record**: a hash-chained ledger of declarations, observations, and the checks between them, produced automatically and verifiable by anyone with the ledger.

## 2. Core model

### 2.1 Declarations

A declaration is what a server publishes about itself. Minimum viable shape:

```json
{
  "server": "fictional-weather",
  "declared_at": "2026-08-01T00:00:00Z",
  "tools": [
    {
      "name": "get_forecast",
      "description": "Return forecast for a city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string"},
          "days": {"type": "integer", "minimum": 1, "maximum": 7}
        },
        "required": ["city"]
      },
      "permissions": ["read:weather"]
    }
  ],
  "annotations": [
    {
      "id": "ann-001",
      "tool": "get_forecast",
      "statement": "read-only access to public weather data",
      "bound_contract": "sha256:abc123..."
    }
  ]
}
```

### 2.2 Contracts

A contract is the canonical, hashable form of a declaration. We fingerprint the canonical JSON (sorted keys, stable serialization) with SHA-256. The contract hash is what annotations bind to, and what we re-derive on every observation.

If the re-derived hash differs from the bound hash, **the contract has mutated**.

### 2.3 Observations

An observation is a runtime fact captured at or around a tool call:

```json
{
  "observed_at": "2026-08-02T12:00:00Z",
  "server": "fictional-weather",
  "tool": "get_forecast",
  "args": {"city": "Townsville", "days": 3},
  "contract_hash": "sha256:abc123...",
  "result": {"status": "ok"}
}
```

The observer (proxy, gateway, or client wrapper) records the contract hash *at call time*, capturing whether the declaration the agent believed it was calling still holds.

### 2.4 Findings

A finding is a measured gap. Three prototype checks:

| Check | Condition | Verdict |
|-------|-----------|---------|
| Bound and unmutated | annotation exists AND observed contract hash == bound hash | **healthy baseline** |
| Bound, contract mutated | annotation exists BUT observed contract hash != bound hash | **finding: stale annotation** |
| Observed outside declared scope | tool call uses tools/args/permissions not in the declaration | **finding: scope violation** |

A finding is never an accusation. It is a signal to schedule review: if an annotation is stale, re-verify it; if a scope is violated, decide whether the declaration or the runtime is wrong.

### 2.5 Ledger (tamper-evident chain)

Every record (declaration, observation, finding) is appended to a SHA-256 hash chain:

```
block_n = sha256(prev_hash + canonical_json(record_n))
```

Properties:

- Any mutation to a past record changes its hash and therefore every later block.
- Verification is O(n) and requires only the ledger file.
- The ledger can be anchored externally (published hash, timestamped) for non-repudiation.

## 3. Architecture

```
+----------------+      +----------------+      +----------------+
|  Declarations  |      |  Observations  |      |  Findings      |
|  (manifest)    |      |  (runtime)     |      |  (checks)      |
+----------------+      +----------------+      +----------------+
        |                       |                       |
        +-----------+-----------+-----------------------+
                    |
                    v
          +------------------+
          | Evidence Ledger  |
          | (hash chain)     |
          +------------------+
                    |
                    v
          +------------------+
          | Report (JSON/UI) |
          +------------------+
```

Components in the prototype:

- `prototype/validate.py` - CLI entry point; runs checks and emits the ledger.
- `prototype/ledger.py` - hash-chain append and verify.
- `prototype/fingerprint.py` - canonical JSON fingerprinting.
- (Roadmap) `prototype/observer.py` - lightweight MCP client wrapper that records observations.

## 4. Security model

- The validator does **not** trust server self-reports. Observations come from the call path (client/gateway side), not from the server.
- The ledger is append-only; verification is independent of the validator binary (documented algorithm).
- Contract fingerprinting is deterministic: same declaration always yields the same hash.
- No secrets are stored. The ledger contains hashes and metadata, never credentials or payload contents (observation records store argument *shape* optionally, with a redaction flag).

## 5. Scope (explicit non-goals)

- Identity and delegated authorization (SPIFFE/SVID, RFC 8693, UCAN capability tokens) are handled by the AAIF Identity & Trust WG, not here.
- This is not a runtime sandbox or an enforcement engine. It measures and records; policy engines can consume the ledger.
- It does not replace threat modeling; it operationalizes one part of it (evidence of ongoing compliance).

## 6. Compatibility

- Language: Python 3.10+, standard library only (prototype).
- Output: JSON (machine) and console (human).
- Works with any MCP server whose tool calls can be observed; protocol version agnostic at the ledger level.

## 7. Reference context

- AAIF Security & Privacy WG Best Practices Guide (draft v0.1): post-incident forensics domain.
- OWASP MCP Governance and Risk Framework: automated evidence collection and enforcement appendix (PR in review).
- Observed industry data: 90% of deployed agents hold ~10x more privilege than a single task requires (Obsidian Security 2025); first malicious MCP server Sept 2025; CVE-2025-6514 (CVSS 9.6).
