# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[SemVer](https://semver.org/).

## [0.2.0] - 2026-08-17

### Added
- Installable package (`pyproject.toml`, src/ layout, `mcp-ev-validate` console script)
- `validate` subcommand: compare a declared manifest against observed runtime records
- `verify` subcommand: replay the SHA-256 hash chain and report any corruption
- Test suite (pytest, 20 tests) covering fingerprinting, ledger chaining, tamper detection, and CLI entry points
- GitHub Actions CI (Python 3.10, 3.11, 3.12)
- Security policy (SECURITY.md) with private reporting and 90-day coordinated disclosure
- Contributing guide and Code of Conduct

### Security
- Ledger integrity depends on SHA-256 over canonical JSON; tampering with any
  prior record invalidates all subsequent records (verified by the test suite).
- No runtime dependencies; no secrets or credentials are stored in the ledger.

## [0.1.0] - 2026-08-01

### Added
- Prototype: declared-vs-observed evidence model (declarations, contracts, observations, findings)
- Prototype hash-chain ledger (`prototype/ledger.py`, `prototype/fingerprint.py`)
- Design document (docs/DESIGN.md)
