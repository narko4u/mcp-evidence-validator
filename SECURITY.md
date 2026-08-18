# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x: (prototype)    |

## Reporting a Vulnerability

Security issues are handled privately. **Do not open a public issue for a
security vulnerability.**

- **Preferred:** email **contact@empirelabs.com.au** with the subject
  `[mcp-evidence-validator] security report`
- Include: affected version, a minimal reproduction, impact, and (if known)
  a suggested fix.
- You will receive an acknowledgment within **72 hours** and a target fix
  timeline within **5 business days**.

If the issue is critical (remote code execution, credential exposure, or
tamper-evidence bypass), mention `CRITICAL` in the subject line so it is
triaged first.

## Disclosure

We follow a 90-day coordinated disclosure window from confirmation. Public
advisories are posted as GitHub Security Advisories for this repository.

## Tamper-evidence note

The ledger's integrity depends on SHA-256. If you believe you have found a
weakness in the hash-chain construction, the canonical-JSON encoding, or the
verification logic, report it under this policy — that class of bug is the
highest-priority finding for this project.

## Secrets and credentials policy

- This project does **not** store, read, or transmit secrets, API keys,
  tokens, or credentials at runtime. The validator takes observations as
  input and writes evidence records; it has no network listeners and no
  credential store.
- Repository secrets are stored only in GitHub Actions encrypted secrets
  (`Settings > Secrets and variables > Actions`). Access is limited to
  maintainers with admin rights, and secret values are never written into
  workflow logs, artifacts, or documentation.
- If a secret is accidentally committed or exposed, rotate it immediately,
  remove the value from history, and report it under this policy.

## Dependency (SCA) policy

- The shipped package has **zero runtime dependencies** (standard-library
  only), which minimises the software composition attack surface.
- Development/CI dependencies are pinned and reviewed. Software composition
  analysis runs on every pull request (see `.github/workflows/ci.yml`) and
  must pass before merge.
- **Remediation threshold:** any known vulnerability with a CVSS score of
  4.0 or higher in a dependency used at build, test, or release time must be
  remediated (upgrade, remove, or documented non-exploitable suppression)
  before that dependency can ship in a release. Lower-severity findings are
  triaged within 30 days.
- SCA violations block release: no release is cut while a high-severity
  dependency finding is unresolved.

## Static analysis (SAST) policy

- Static analysis (Ruff + Bandit) runs on every pull request and must pass
  before merge.
- **Remediation threshold:** Bandit findings rated High or Medium must be
  fixed before merge (no suppression except a documented, reviewed
  false-positive note). Low-severity findings are triaged within 30 days.
- SAST violations block release: no release is cut while a High or Medium
  finding is unresolved.

## Vulnerability Exploitability eXchange (VEX)

- The project publishes a VEX document at `docs/VEX.md` stating the
  exploitability status of known vulnerabilities in project components.
- Current status: the shipped artifact has zero runtime dependencies and
  exposes no network surface; see `docs/VEX.md` for per-component
  statements.

## End-of-support statement

- **0.2.x** receives security updates for the life of the 0.2 series and for
  90 days after the next minor release ships.
- **< 0.2** (prototype) receives no security updates; users must upgrade to
  the current 0.2.x release.
- End-of-support for each release is announced in the release notes when a
  newer series ships.
