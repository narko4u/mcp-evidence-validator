# Maintainers

## Project members with access to sensitive resources

| Role | Person / Account | Access |
|------|------------------|--------|
| Maintainer / owner | Empire Labs Pty Ltd (`narko4u`) | Admin: repository settings, branch protection, releases, secrets, GitHub Actions |

Single-maintainer project. No other accounts have write, admin, or secrets
access to this repository.

## Collaborator review policy

Before any collaborator is granted escalated permissions to sensitive
resources (merge approval, branch protection changes, secrets access, or
admin rights), the following review must take place:

1. The proposed collaborator's contribution history is reviewed (quality,
   intent, and consistency with the project's security posture).
2. The identity lineage is established where practicable (association with a
   known trusted organisation, verifiable public identity, or prior
   maintainer relationship).
3. Approval is recorded in the repository (issue or PR comment) before
   access is granted.

This policy is enforced by branch protection: the primary branch requires
review approval and no direct push is permitted. Escalated access is granted
only after the review above completes.

## Roles and responsibilities

- **Maintainer (Empire Labs Pty Ltd / `narko4u`)**
  - Owns the repository, releases, and security response.
  - Reviews and merges pull requests (all merges go through PR review per
    branch protection; as a single-maintainer project there is no
    non-author human reviewer, so OpenSSF criterion QA-07.01 is claimed
    N/A. The collaborator review policy above governs how review is
    enforced should additional maintainers join).
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
