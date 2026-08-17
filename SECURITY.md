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
