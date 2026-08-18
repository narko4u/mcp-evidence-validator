#!/usr/bin/env python3
"""Generate the OpenSSF Best Practices Baseline Level 2 automation proposal URL
for project 14122 (mcp-evidence-validator).

Format per ossf/best-practices-badge docs/automation-proposals.md:
  /en/projects/14122/baseline-2/edit?KEY=VALUE&KEY=VALUE...
  KEY = <criterion>_status | <criterion>_justification
  Status values: ?, Unmet, N/A, Met
  OSPS criteria use lowercase underscore form: osps_<cat>_<num>_<sec>
  (e.g. osps_ac_04_01 for OSPS-AC-04.01)

All 19 Level 2 criteria are Met (repo prepared 2026-08-18). Evidence per
docs/OPENSSF-BADGE-LEVEL2.md; justifications match repo state.
"""
from urllib.parse import quote_plus

# (criterion, status, justification) - all 19 Baseline Level 2 criteria
CRITERIA = [
    # --- Access Control ---
    ("osps_ac_04_01", "Met",
     ".github/workflows/ci.yml declares permissions: contents: read at workflow top level; release workflow grants only what it needs (contents: write, id-token: write) for signed publishing"),
    # --- Build and Release ---
    ("osps_br_02_01", "Met",
     "SemVer tags in git (v0.2.0, v0.2.1); version mirrored in pyproject.toml; each official release is a distinct annotated tag"),
    ("osps_br_04_01", "Met",
     "CHANGELOG.md (Keep a Changelog format) documents functional and security changes per release; GitHub Releases generated from merged PRs"),
    ("osps_br_05_01", "Met",
     "Standard Python tooling: pyproject.toml with setuptools backend, pip install in CI; package has zero runtime dependencies (stdlib only)"),
    ("osps_br_06_01", "Met",
     "Release v0.2.1 publishes SHA256SUMS (hashes of every asset) plus sigstore keyless signature (cosign, OIDC identity release.yml@refs/tags/v0.2.1); cosign verify-blob reports Verified OK"),
    # --- Documentation ---
    ("osps_do_06_01", "Met",
     "README Install section and zero-dependency policy describe how dependencies are selected and obtained; dependencies declared exclusively in pyproject.toml"),
    ("osps_do_07_01", "Met",
     "README Install section: git clone, cd, pip install .; CI executes the same path on Python 3.10/3.11/3.12 proving the instructions work"),
    # --- Governance ---
    ("osps_gv_01_01", "Met",
     "MAINTAINERS.md lists the sole maintainer (narko4u, Empire Labs Pty Ltd) with admin access to repository, releases, and CI secrets, plus the security contact"),
    ("osps_gv_01_02", "Met",
     "MAINTAINERS.md documents maintainer duties: triage, review, release process, security response, and the contributor path (fork + PR, DCO sign-off)"),
    ("osps_gv_03_02", "Met",
     "CONTRIBUTING.md covers how to contribute (issues, fork/PR workflow), standards (tests must pass, CI enforced), and the DCO requirement"),
    # --- Legal ---
    ("osps_le_01_01", "Met",
     "DCO enforced two ways: CONTRIBUTING.md DCO section requires Signed-off-by trailer on every commit; CI dco job checks every non-merge commit on PRs and fails the build if missing"),
    # --- Quality ---
    ("osps_qa_03_01", "Met",
     "Branch protection on main requires the test status check (strict: true), blocks force-pushes and deletions, enforce_admins: true; direct pushes rejected (GH006)"),
    ("osps_qa_06_01", "Met",
     ".github/workflows/ci.yml runs the pytest suite (20 tests) on every push and pull_request across Python 3.10/3.11/3.12 plus a CLI entry-point smoke check; failing test blocks merge"),
    # --- Security Assessment ---
    ("osps_sa_01_01", "Met",
     "docs/DESIGN.md documents the system: core model (declarations, contracts, observations, findings), architecture, tamper-evident SHA-256 ledger, security model; actors and actions are described"),
    ("osps_sa_02_01", "Met",
     "README documents all external interfaces: mcp-ev-validate CLI (validate, verify subcommands), module interface, and machine-readable evidence record output; input formats shown in examples/"),
    ("osps_sa_03_01", "Met",
     "docs/THREAT-ASSESSMENT.md identifies assets, enumerates likely/impactful problems with likelihood/impact ratings and mitigations (hash-chain tamper detection, no credential storage); reviewed 2026-08-18"),
    # --- Vulnerability Management ---
    ("osps_vm_01_01", "Met",
     "SECURITY.md defines the CVD policy: private reporting, acknowledgment within 72 hours, and a 90-day coordinated disclosure timeline"),
    ("osps_vm_03_01", "Met",
     "SECURITY.md directs reporters to email contact@empirelabs.com.au privately (do not open a public issue) with subject prefix; GitHub private vulnerability reporting is also enabled on the repository"),
    ("osps_vm_04_01", "Met",
     "GitHub Security Advisories enabled on the repository (secret scanning + push protection on); confirmed vulnerabilities are published as GHSAs with affected and fixed versions, linked from SECURITY.md/CHANGELOG"),
]

BASE = "https://www.bestpractices.dev/en/projects/14122/baseline-2/edit"


def build_url() -> str:
    params = []
    for criterion, status, justification in CRITERIA:
        params.append(f"{criterion}_status={status}")
        params.append(f"{criterion}_justification={quote_plus(justification)}")
    return BASE + "?" + "&".join(params)


if __name__ == "__main__":
    url = build_url()
    print(f"URL length: {len(url)}")
    print(url)
