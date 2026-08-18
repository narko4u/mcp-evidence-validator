# Maintainers

## Project members with access to sensitive resources

| Role | Person / Account | Access |
|------|------------------|--------|
| Maintainer / owner | Empire Labs Pty Ltd (`narko4u`) | Admin: repository settings, branch protection, releases, secrets, GitHub Actions |

Single-maintainer project. No other accounts have write, admin, or secrets
access to this repository.

## Roles and responsibilities

- **Maintainer (Empire Labs Pty Ltd / `narko4u`)**
  - Owns the repository, releases, and security response.
  - Reviews and merges pull requests (all merges go through PR review per
    branch protection; the maintainer cannot approve their own PR, so a
    second reviewer is required for each merge).
  - Triages security reports per `SECURITY.md` (72h acknowledgement, 90-day
    coordinated disclosure).
  - Decides on dependency additions (project intentionally ships with a
    zero-runtime-dependency standard-library-only implementation).
- **Contributors**
  - Anyone contributing via fork and pull request per `CONTRIBUTING.md`.
  - Must pass CI (tests on Python 3.10-3.12) and carry `Signed-off-by` on
    every commit (DCO).
  - Do not have write access to the repository; access is granted only
    through reviewed pull requests.

## Contact

Security matters: see `SECURITY.md`. General questions: GitHub issues.
