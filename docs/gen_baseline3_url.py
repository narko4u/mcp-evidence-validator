#!/usr/bin/env python3
"""Generate the OpenSSF Best Practices Baseline Level 3 automation proposal URL
for project 14122 (mcp-evidence-validator).

Format per ossf/best-practices-badge docs/automation-proposals.md:
  /en/projects/14122/baseline-3/edit?KEY=VALUE&KEY=VALUE...
  KEY = <criterion>_status | <criterion>_justification
  Status values: ?, Unmet, N/A, Met
  OSPS criteria use lowercase underscore form: osps_<cat>_<num>_<sec>
  (e.g. osps_ac_04_02 for OSPS-AC-04.02)

All 21 Level 3 criteria addressed 2026-08-18: 19 Met, 2 N/A (QA-04.02
single-repository project, QA-07.01 single-maintainer project). Evidence
landed via PRs #12 (docs), #13 (CI), #14 (QA-07.01 N/A claim); justifications
match repo state at main 046e968+e35538e.
"""
from urllib.parse import quote_plus

# (criterion, status, justification) - all 21 Baseline Level 3 criteria
CRITERIA = [
    # --- Access Control ---
    ("osps_ac_04_02", "Met",
     ".github/workflows/ci.yml declares permissions: contents: read at workflow top level; release.yml grants only what it needs (contents: write, id-token: write) for signed publishing"),
    # --- Build and Release ---
    ("osps_br_01_04", "Met",
     "release.yml validates workflow_dispatch tag input against ^v[0-9]+\\.[0-9]+\\.[0-9]+$ and exits 1 on mismatch, so manual collaborator input cannot reach the pipeline unsanitized"),
    ("osps_br_02_02", "Met",
     "Each release is an annotated SemVer tag (v0.2.0, v0.2.1) and every asset (wheel, sdist, SBOM, SHA256SUMS, sig, pem) is named with or hashed into the release identifier; SHA256SUMS binds all assets to the tag"),
    ("osps_br_07_02", "Met",
     "SECURITY.md 'Secrets and credentials policy': no runtime secrets are stored in the repo, CI secrets live in GitHub Actions encrypted secrets, rotation is required if a secret is exposed"),
    # --- Documentation ---
    ("osps_do_03_01", "Met",
     "README 'Verifying releases' section documents sha256sum -c SHA256SUMS plus cosign verify-blob with the exact commands and expected output for release v0.2.1"),
    ("osps_do_03_02", "Met",
     "README 'Verifying releases' documents the expected sigstore identity (certificate-identity .../release.yml@refs/tags/v0.2.1, OIDC issuer https://token.actions.githubusercontent.com) and the cosign command to verify it"),
    ("osps_do_04_01", "Met",
     "SECURITY.md 'Supported Versions' table states the scope and duration of support for each release line (current minor gets updates; older lines listed with their status)"),
    ("osps_do_05_01", "Met",
     "SECURITY.md 'End-of-support statement' describes when releases stop receiving security updates (0.2.x receives updates until 90 days after the next minor; <0.2 receives none)"),
    # --- Governance ---
    ("osps_gv_04_01", "Met",
     "MAINTAINERS.md 'Collaborator review policy': contribution history review, identity lineage, and recorded approval (issue/PR comment) are required before any collaborator is granted escalated permissions to sensitive resources"),
    # --- Quality ---
    ("osps_qa_02_02", "Met",
     "release.yml generates a CycloneDX SBOM (anchore/sbom-action@v0, cyclonedx-json) on every release; SBOM.cdx.json is attached to release v0.2.1 alongside the other assets"),
    ("osps_qa_04_02", "N/A",
     "Single-repository project: the release is built entirely from this one repository, so there are no subprojects to which stricter-or-equal requirements would apply"),
    ("osps_qa_06_02", "Met",
     "CONTRIBUTING.md 'How tests are run' documents local execution (pytest) and CI execution (pytest on Python 3.10-3.12 plus ruff, bandit, DCO checks) and what the suite covers"),
    ("osps_qa_06_03", "Met",
     "CONTRIBUTING.md 'Test policy for changes': behavior changes MUST add or update automated tests, major changes require happy-path, adversarial, and tamper cases; docs-only changes are exempt"),
    ("osps_qa_07_01", "N/A",
     "Single-maintainer project: no non-author human reviewer exists, so a non-author approval requirement cannot be satisfied. Branch protection still requires all status checks (test, lint, sca) and enforce_admins: true prevents even the admin from bypassing them; MAINTAINERS.md documents the N/A claim and the review policy that applies if collaborators join"),
    # --- Security Assessment ---
    ("osps_sa_03_02", "Met",
     "docs/THREAT-ASSESSMENT.md contains an attack surface analysis (CLI entry, fingerprint engine, ledger, evidence records) with threat scenarios per surface, and a policy to re-run it before each release or when new features touch those surfaces"),
    # --- Vulnerability Management ---
    ("osps_vm_04_02", "Met",
     "docs/VEX.md is a CycloneDX-style VEX document listing every shipped component (the package itself, stdlib, build/test-only tooling) with exploitability status: all known vulnerabilities assessed 'Not affected' given no network listener and no runtime dependencies; reviewed before each release"),
    ("osps_vm_05_01", "Met",
     "SECURITY.md 'Dependency (SCA) policy' defines the remediation threshold (CVSS >= 4.0 must be remediated before merge) and the process for identifying, prioritizing, and remediating findings"),
    ("osps_vm_05_02", "Met",
     "SECURITY.md 'Dependency (SCA) policy' states SCA violations must be addressed before any release, and the sca status check (pip-audit on runtime and dev dependencies) verifies compliance on every pull request"),
    ("osps_vm_05_03", "Met",
     "The sca job (pip-audit) runs automatically on every change to the codebase and is a required status check in branch protection, so SCA violations block the merge; no suppression mechanism exists"),
    ("osps_vm_06_01", "Met",
     "SECURITY.md 'Static analysis (SAST) policy' defines the remediation threshold (High and Medium findings must be fixed before merge) and the process for identifying, prioritizing, and remediating findings"),
    ("osps_vm_06_02", "Met",
     "The lint job (ruff + bandit) runs automatically on every change to the codebase and is a required status check in branch protection, so security weaknesses block the merge; no suppression mechanism exists"),
]

BASE = "https://www.bestpractices.dev/en/projects/14122/baseline-3/edit"


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
