# OpenSSF Baseline Level 2 — Answer Sheet

**Project:** mcp-evidence-validator
**Project ID:** 14122 (bestpractices.dev)
**Criteria version:** OSPS Baseline v2026.02.19
**Date:** 2026-08-18
**Status:** Level 1 (24/24) earned; Level 2 mapping below

How to use: open https://www.bestpractices.dev/projects/14122, click "Edit", switch the
criteria view to Level 2 (the form shows all levels; answer the Level 2 rows). For each
criterion below, paste the "Answer" into the box and the "Evidence" into the comment/
justification field. Answers are honest and match what the repository actually does.

---

## OSPS-AC-04.01 — CI/CD task default permissions
**Answer:** Met
**Evidence:** `.github/workflows/ci.yml` declares `permissions: contents: read` at the
workflow top level; the release workflow declares the minimum it needs
(`contents: write, id-token: write`) only for publishing signed artifacts. Jobs run with
least privilege by default.

## OSPS-BR-02.01 — Unique version identifier per release
**Answer:** Met
**Evidence:** SemVer tags in git: `v0.2.0`, `v0.2.1`. Version mirrored in
`pyproject.toml` (`version = "0.2.1"`). Each official release is a distinct annotated tag
with a matching package version.

## OSPS-BR-04.01 — Descriptive log of functional/security modifications
**Answer:** Met
**Evidence:** `CHANGELOG.md` (Keep a Changelog format) documents functional and security
changes per release (Added/Security sections). GitHub Releases additionally generate
release notes from merged PRs (compare `v0.2.0...v0.2.1`).

## OSPS-BR-05.01 — Standardized dependency ingestion tooling
**Answer:** Met
**Evidence:** Build uses standard Python tooling: `pyproject.toml` with the setuptools
backend, `pip install .` in CI. The package has **zero runtime dependencies** (stdlib
only), so the dependency surface is minimal; when dependencies are added they will be
declared in `pyproject.toml` and resolved via pip/PyPI.

## OSPS-BR-06.01 — Release signed or signed manifest with hashes
**Answer:** Met
**Evidence:** Release `v0.2.1` publishes `SHA256SUMS` (cryptographic hashes of every
asset) plus a sigstore keyless signature (`SHA256SUMS.sig`, `SHA256SUMS.pem`). Signing is
done by `.github/workflows/release.yml` using cosign with OIDC identity
`release.yml@refs/tags/v0.2.1`, issuer `token.actions.githubusercontent.com`.
Verification: `cosign verify-blob` reports "Verified OK"; `sha256sum` matches for both
artifacts (wheel and sdist).

## OSPS-DO-06.01 — Dependency selection/obtaining/tracking documented
**Answer:** Met
**Evidence:** README "Install" and "Zero dependencies — Python 3.10+ standard library
only" sections describe the dependency posture. Dependencies are declared exclusively in
`pyproject.toml`; the project tracks a zero-runtime-dependency policy, and CI installs
from source via pip. Any future dependency must be declared there and will be locked by
the normal release process.

## OSPS-DO-07.01 — Build instructions documented
**Answer:** Met
**Evidence:** README "Install" section: `git clone`, `cd`, `pip install .`. CI executes
the same path (`pip install . && pytest`) on Python 3.10/3.11/3.12, proving the documented
instructions work. Requires Python 3.10+; no other libraries, frameworks, or SDKs.

## OSPS-GV-01.01 — Members with access to sensitive resources
**Answer:** Met
**Evidence:** `MAINTAINERS.md` lists the sole maintainer (narko4u, Empire Labs Pty Ltd)
with admin access to the repository, releases, and CI secrets, plus the security contact.
Sensitive resources (CI secrets) are scoped to repository-level secrets accessible only
to the listed admin.

## OSPS-GV-01.02 — Roles and responsibilities documented
**Answer:** Met
**Evidence:** `MAINTAINERS.md` documents maintainer duties: triage, review, release
process, security response, and the contributor path (fork + PR, DCO sign-off).

## OSPS-GV-03.02 — Contributor guide with acceptable contribution requirements
**Answer:** Met
**Evidence:** `CONTRIBUTING.md` covers how to contribute (issues, fork/PR workflow),
standards (tests must pass, CI enforced, changelog entry for user-visible changes), and
the DCO requirement (every commit Signed-off-by).

## OSPS-LE-01.01 — Every commit asserts legal authorization (DCO)
**Answer:** Met
**Evidence:** Enforced two ways: (1) `CONTRIBUTING.md` DCO section requires a
`Signed-off-by:` trailer on every commit; (2) the CI `dco` job checks every
non-merge commit on PRs and fails the build if a trailer is missing
(`git rev-list --no-merges <base>..HEAD`, greps for `^Signed-off-by:`).

## OSPS-QA-03.01 — Status checks must pass before primary-branch commits
**Answer:** Met
**Evidence:** Branch protection on `main` requires the `test` status check (strict: true),
blocks force-pushes and deletions, and `enforce_admins: true` (admins are also bound).
Direct pushes to `main` are rejected (GH006: protected branch).

## OSPS-QA-06.01 — CI runs automated test suite before accepting commits
**Answer:** Met
**Evidence:** `.github/workflows/ci.yml` runs the pytest suite (20 tests) on every push
and pull_request across Python 3.10, 3.11, 3.12, plus a CLI entry-point smoke check
(`mcp-ev-validate --version`). PRs cannot merge while `test` is failing (required status
check).

## OSPS-SA-01.01 — Design documentation with actions and actors
**Answer:** Met
**Evidence:** `docs/DESIGN.md` documents the system: core model (declarations, contracts,
observations, findings), architecture, ledger (tamper-evident SHA-256 chain), security
model, and scope. Actors (validator CLI user, MCP server, ledger consumer/auditor) and
actions (capture, compare, chain, verify) are described.

## OSPS-SA-02.01 — External software interfaces documented
**Answer:** Met
**Evidence:** README documents all external interfaces: the `mcp-ev-validate` CLI
(`validate`, `verify` subcommands with their flags), the module interface
(`python -m mcp_evidence_validator`), and the machine-readable evidence record output
(hash-linked `chain` + `findings`). Input formats are shown in `examples/` (fictional).

## OSPS-SA-03.01 — Security assessment performed
**Answer:** Met
**Evidence:** `docs/THREAT-ASSESSMENT.md` identifies assets (ledger integrity,
confidentiality of observed records), enumerates likely/impactful problems with
likelihood/impact ratings and mitigations (e.g. tamper detection via hash chain, no
credential storage, redaction flag). Reviewed 2026-08-18.

## OSPS-VM-01.01 — Coordinated vulnerability disclosure policy with timeframe
**Answer:** Met
**Evidence:** `SECURITY.md` defines the CVD policy: private reporting via GitHub
private vulnerability reporting, response commitment and 90-day coordinated disclosure
timeline.

## OSPS-VM-03.01 — Private vulnerability reporting channel
**Answer:** Met
**Evidence:** `SECURITY.md` directs reporters to GitHub's private vulnerability reporting
form (repository security tab enabled, `security_events`), which goes directly to the
security contact listed in MAINTAINERS.md.

## OSPS-VM-04.01 — Publicly publish data about discovered vulnerabilities
**Answer:** Met
**Evidence:** GitHub Security Advisories are enabled on the repository
(secret scanning + push protection on); any confirmed vulnerability is published as a
GHSA with affected versions and fixed version, and linked from SECURITY.md/CHANGELOG.

---

## Summary

| Criterion | Answer | Primary evidence |
|---|---|---|
| AC-04.01 | Met | ci.yml `permissions: contents: read` |
| BR-02.01 | Met | SemVer tags v0.2.0/v0.2.1 |
| BR-04.01 | Met | CHANGELOG.md (Keep a Changelog) |
| BR-05.01 | Met | pyproject.toml + setuptools, zero runtime deps |
| BR-06.01 | Met | SHA256SUMS + cosign sigstore, "Verified OK" |
| DO-06.01 | Met | README deps posture + pyproject.toml |
| DO-07.01 | Met | README Install (proven by CI) |
| GV-01.01 | Met | MAINTAINERS.md |
| GV-01.02 | Met | MAINTAINERS.md roles |
| GV-03.02 | Met | CONTRIBUTING.md |
| LE-01.01 | Met | DCO CI job + CONTRIBUTING |
| QA-03.01 | Met | Branch protection (test check, strict) |
| QA-06.01 | Met | ci.yml pytest 3 Python versions |
| SA-01.01 | Met | docs/DESIGN.md |
| SA-02.01 | Met | README CLI/module/output docs |
| SA-03.01 | Met | docs/THREAT-ASSESSMENT.md |
| VM-01.01 | Met | SECURITY.md CVD + 90-day |
| VM-03.01 | Met | Private reporting form |
| VM-04.01 | Met | Security advisories enabled |

All 19 Level 2 criteria are **Met**. The repository was prepared specifically for this
level on 2026-08-18 (CHANGELOG, MAINTAINERS, threat assessment, DCO enforcement,
least-privilege CI, signed release v0.2.1).
