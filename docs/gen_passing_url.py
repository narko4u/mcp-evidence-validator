#!/usr/bin/env python3
"""Generate the OpenSSF Best Practices Passing-badge automation proposal URL
for project 14122 (mcp-evidence-validator).

Format per ossf/best-practices-badge docs/automation-proposals.md:
  /en/projects/14122/passing/edit?KEY=VALUE&KEY=VALUE...
  KEY = <criterion>_status | <criterion>_justification
  Status values: ?, Unmet, N/A, Met
"""
from urllib.parse import quote_plus

# (criterion, status, justification) - all 67 Passing criteria
CRITERIA = [
    # --- Basics (13) ---
    ("description_good", "Met", "README.md succinctly describes what the software does in plain language"),
    ("interact", "Met", "README.md covers how to obtain, give feedback (GitHub Issues) and contribute"),
    ("contribution", "Met", "CONTRIBUTING.md explains the pull-request contribution process (URL in repo)"),
    ("contribution_requirements", "Met", "CONTRIBUTING.md documents DCO sign-off, tests, and coding standards"),
    ("floss_license", "Met", "Released under Apache-2.0 (OSI-approved FLOSS license)"),
    ("floss_license_osi", "Met", "Apache-2.0 is approved by the Open Source Initiative"),
    ("license_location", "Met", "LICENSE file at repository root: github.com/narko4u/mcp-evidence-validator"),
    ("documentation_basics", "Met", "README.md: pip install, CLI usage with examples, security notes"),
    ("documentation_interface", "Met", "README.md documents CLI commands, module API, and JSON output format"),
    ("sites_https", "Met", "Repository and release URLs are served over HTTPS (github.com)"),
    ("discussion", "Met", "GitHub Issues and pull-request discussions, searchable and URL-addressable"),
    ("english", "Met", "All documentation, code comments and issue handling are in English"),
    ("maintained", "Met", "Actively maintained; badge submission, CI, and releases are current (2026-08)"),
    # --- Change Control (9) ---
    ("repo_public", "Met", "Public version-controlled repository with URL: github.com/narko4u/mcp-evidence-validator"),
    ("repo_track", "Met", "All changes tracked in git with full history"),
    ("repo_interim", "Met", "Feature branches with interim commits before merge to main"),
    ("repo_distributed", "Met", "git is a distributed version control system"),
    ("version_unique", "Met", "SemVer versions v0.2.0 and v0.2.1 in pyproject.toml and release tags"),
    ("version_semver", "Met", "Releases use Semantic Versioning (v0.2.0, v0.2.1)"),
    ("version_tags", "Met", "Git tags v0.2.0 and v0.2.1 mark releases"),
    ("release_notes", "Met", "CHANGELOG.md plus GitHub Releases with human-readable summaries"),
    ("release_notes_vulns", "Met", "No vulnerabilities released; CHANGELOG and release notes document security changes"),
    # --- Reporting (8) ---
    ("report_process", "Met", "Bug reports via GitHub Issues (URL in repo): github.com/narko4u/mcp-evidence-validator/issues"),
    ("report_tracker", "Met", "GitHub Issues tracks individual issues"),
    ("report_responses", "Met", "All submitted bug reports acknowledged"),
    ("enhancement_responses", "Met", "Enhancement requests acknowledged and tracked in GitHub Issues"),
    ("report_archive", "Met", "GitHub Issues are archived and searchable"),
    ("vulnerability_report_process", "Met", "SECURITY.md publishes the vulnerability reporting process (URL in repo)"),
    ("vulnerability_report_private", "Met", "GitHub private vulnerability reporting enabled"),
    ("vulnerability_report_response", "Met", "SECURITY.md commits to responding within 90 days"),
    # --- Quality (13) ---
    ("build", "Met", "setuptools build from pyproject.toml; CI builds the package from source"),
    ("build_common_tools", "Met", "Standard Python tooling (setuptools, pip)"),
    ("build_floss_tools", "Met", "Build tools are FLOSS (setuptools, pip)"),
    ("test", "Met", "pytest suite (20 tests) runs in CI and is documented in CONTRIBUTING.md"),
    ("test_invocation", "Met", "CI runs pytest; how to run tests documented in CONTRIBUTING.md"),
    ("test_most", "Met", "Tests cover the core modules (validator, ledger, fingerprint)"),
    ("test_policy", "Met", "CONTRIBUTING.md requires tests for major new functionality"),
    ("tests_are_added", "Met", "New functionality lands with tests in the same PR"),
    ("tests_documented_added", "Met", "Test requirements and additions documented in CONTRIBUTING.md"),
    ("warnings", "Met", "ruff linter runs in CI on every PR and push (fails on any finding)"),
    ("warnings_fixed", "Met", "CI blocks merge on any lint finding; current tree is clean"),
    ("warnings_strict", "Met", "ruff enforces a broad rule set and fails the build on any violation"),
    ("know_secure_design", "Met", "docs/DESIGN.md and docs/THREAT-ASSESSMENT.md document secure design approach"),
    # --- Security (16) ---
    ("know_common_errors", "Met", "docs/THREAT-ASSESSMENT.md covers common security pitfalls and mitigations"),
    ("crypto_published", "N/A", "Project implements no encryption; uses only SHA-256 for integrity hashing"),
    ("crypto_call", "N/A", "No cryptographic primitives are implemented or called directly"),
    ("crypto_floss", "N/A", "No encryption functionality to implement"),
    ("crypto_keylength", "N/A", "No encryption keys used"),
    ("crypto_working", "N/A", "No encryption mechanisms"),
    ("crypto_pfs", "N/A", "No encrypted communication channels"),
    ("crypto_password_storage", "N/A", "No password storage"),
    ("crypto_random", "N/A", "No cryptographic randomness requirements"),
    ("delivery_mitm", "Met", "HTTPS-only delivery via GitHub Releases"),
    ("delivery_unsigned", "Met", "Every release ships sigstore keyless-signed SHA256SUMS (v0.2.1 verified)"),
    ("vulnerabilities_fixed_60_days", "Met", "No known unpatched vulnerabilities"),
    ("vulnerabilities_critical_fixed", "Met", "No known critical vulnerabilities; SECURITY.md 90-day policy"),
    ("no_leaked_credentials", "Met", "Credential leak audit passed; secret scanning and push protection enabled"),
    ("installation_common", "Met", "Standard installation via pip (python -m pip install mcp-evidence-validator)"),
    ("test_continuous_integration", "Met", "GitHub Actions runs the full test suite on every PR and push"),
    # --- Analysis (8) ---
    ("static_analysis", "Met", "bandit security scanner runs in CI on every PR and push"),
    ("static_analysis_common_vulnerabilities", "Met", "bandit checks common vulnerability patterns"),
    ("static_analysis_fixed", "Met", "CI fails on any bandit finding; current tree has zero findings"),
    ("static_analysis_often", "Met", "Static analysis runs on every pull request and push"),
    ("dynamic_analysis", "Unmet", "No dynamic analysis tool applied yet"),
    ("dynamic_analysis_unsafe", "Unmet", "No dynamic analysis tool applied yet"),
    ("dynamic_analysis_enable_assertions", "N/A", "Pure Python project; no memory-unsafe language to guard"),
    ("dynamic_analysis_fixed", "Unmet", "No dynamic analysis in place yet"),
]

BASE = "https://www.bestpractices.dev/en/projects/14122/passing/edit"

params = []
for name, status, just in CRITERIA:
    params.append(f"{name}_status={status}")
    params.append(f"{name}_justification={quote_plus(just)}")

url = BASE + "?" + "&".join(params)
print(f"Criteria count: {len(CRITERIA)}")
print(f"URL length: {len(url)}")
print()
print(url)
