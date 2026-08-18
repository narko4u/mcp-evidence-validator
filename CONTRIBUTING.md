# Contributing

Thanks for your interest in the MCP Evidence Validator. Contributions are
welcome under the Apache-2.0 licence.

## Ground rules

- **No proprietary data.** This is a public reference implementation. All
  examples must be fictional. Never commit real credentials, tokens, or
  client data — anything that looks like a secret is treated as a leak.
- **Keep it dependency-free.** The project intentionally ships with a
  Python-stdlib-only runtime. New dependencies need a strong justification.
- **Backwards compatibility matters.** The ledger format (`ledger` and
  `version` fields, hash-chain structure) is a stability surface. Changing
  it is a breaking change.

## Getting started

```bash
git clone https://github.com/narko4u/mcp-evidence-validator.git
cd mcp-evidence-validator
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pytest
```

## What to work on

Open issues and the roadmap in the README are the source of truth. Good
first contributions:

- Report renderers (JSON is baseline; HTML/PDF are planned)
- Policy pack support (declaring what "acceptable" means per environment)
- MCP client integration (intercepting tool-call records)
- Documentation and examples

## How tests are run

- **Locally:** `pytest` from the repository root (see Getting started).
  Tests cover the hash-chain construction (genesis, mid-chain tamper,
  foreign-ledger reject), canonical JSON fingerprinting, CLI behaviour, and
  the ledger append/verify flow.
- **In CI:** the `CI` workflow runs on every push and pull request. It runs
  the full pytest suite on Python 3.10, 3.11, and 3.12, lints with Ruff,
  runs Bandit static analysis, and enforces the DCO on pull requests.
- **Interpreting results:** all checks must be green before a PR merges. The
  suite is deterministic — a red run indicates a real regression, not flake.

## Test policy for changes

- **Every change that alters behaviour MUST add or update tests** covering
  the changed functionality in the automated suite.
- A "major change" (new subcommand, ledger-format change, canonical-encoding
  change, new check type) additionally requires tests for the happy path,
  at least one adversarial case (malformed/duplicate/huge input), and a
  tamper case where applicable.
- Test-only or documentation-only changes do not require new tests, but must
  keep the existing suite green.

## Pull request process

1. Fork the repository and create a branch: `feat/<what>` or `fix/<what>`.
2. Add tests for your change (pytest). The suite must stay green on
   Python 3.10, 3.11, and 3.12.
3. Update the README or docs if the CLI surface changes.
4. Open a PR against `main` and describe the change and the test evidence.
5. A maintainer will review; expect at least one round of review.

## Developer certificate of origin

Every commit must carry a `Signed-off-by` trailer asserting that you are
legally authorized to make the contribution (Developer Certificate of
Origin, https://developercertificate.org/). CI enforces this on pull
requests. Add it with `git commit -s` (or `git commit --amend -s` for an
existing commit).

## Code of conduct

All participants must follow the project's
[Code of Conduct](CODE_OF_CONDUCT.md). Be professional, be specific, and
assume good faith.
