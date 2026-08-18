# Security Assessment

Status: assessment performed for the v0.2.0 release (2026-08-17). This
document records the most likely and impactful potential security problems
for this software and the mitigations in place. It is reviewed before each
release.

## What this software is

A command-line validator that compares *declared* MCP server metadata against
*observed* runtime records and appends results to a tamper-evident SHA-256
hash chain. It has no network listeners, no server component, no runtime
dependencies, and stores no credentials.

## Assets

1. **Ledger integrity** — the ability to prove that a recorded evidence
   record has not been altered.
2. **Confidentiality of observed records** — observations may contain
   argument shapes and metadata; the design supports redaction flags.

## Likely and impactful problems

| # | Problem | Likelihood | Impact | Mitigation |
|---|---------|------------|--------|------------|
| 1 | Tampering with ledger records (alter, delete, reorder) | Medium | High (breaks the core promise) | SHA-256 hash chain: any change to a prior record invalidates all later blocks; `verify` replays the full chain; tests cover genesis, mid-chain tamper, foreign-ledger reject |
| 2 | Non-canonical JSON encoding producing ambiguous hashes | Medium | High (hash mismatch / bypass) | Canonical JSON (sorted keys, stable serialization); fingerprint tests cover key ordering and whitespace |
| 3 | Maliciously crafted input files (huge, deeply nested, or malformed JSON) | Medium | Low-Medium (DoS of the validator) | Standard library JSON parsing with bounded input expectations; CLI is local and user-invoked; no network exposure |
| 4 | Secret/credential leakage into records | Low | High | Design stores hashes and metadata only, never credentials or payload contents; CONTRIBUTING forbids committing secrets; examples are fictional |
| 5 | Dependency supply-chain risk | Low | Low | Zero runtime dependencies (stdlib only); CI installs from source |
| 6 | Weak hash algorithm over time | Low (long-term) | High | SHA-256 with documented construction; any weakness is treated as the highest-priority finding per SECURITY.md |

## Threat model scope

- **In scope:** CLI input handling, canonical fingerprinting, ledger append
  and verify logic, hash-chain construction.
- **Explicitly out of scope:** the MCP servers being validated (the validator
  does not run them), transport security of observations (handled by the
  observer/client wrapper), identity and delegated authorization (AAIF
  Identity & Trust WG domain).

## Attack surface analysis

Critical code paths, functions, and interactions, with the threats
considered for each:

| Surface | Critical path / functions | Threat scenarios considered |
|---------|---------------------------|------------------------------|
| CLI entry (`cli.py`) | argument parsing, file reads, subcommand dispatch | crafted arguments, symlink/file confusion, path traversal, unexpected encodings |
| Fingerprint engine (`validator.py`) | canonical-JSON serialization, hash computation | key-ordering confusion, whitespace/unicode ambiguity, duplicate keys, oversized payloads, algorithm confusion |
| Ledger append/verify (`ledger.py`) | hash-chain linking, genesis handling, re-verification | reorder, delete, replay, partial-write, foreign-ledger substitution, nonce/counter forgery |
| Evidence records | redaction flags, metadata fields | credential leakage into records, spoofed metadata, type confusion |

Threat-model update policy: this analysis is re-run and updated before each
release and whenever a new feature or breaking change touches any of the
surfaces above (per the OSPS SA-03.02 control).

## Security review policy

- Review before each release; findings filed privately per `SECURITY.md`.
- Automated: CI runs the test suite (including tamper tests) on every
  commit/PR.
- Manual: maintainer reviews the ledger construction and canonical-JSON
  fingerprinting before release tags.
