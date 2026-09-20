#!/usr/bin/env python3
"""Verify the Sigstore attestation PyPI serves for the wheel this record cites.

This is the step that lets `appraisal.provenance_depth_verified` honestly say
`builder` instead of `surface`. It is not a formality - it either verifies or it
does not, and the value in the record has to follow the result.

What is checked:

  * the DSSE envelope signature, against the Fulcio certificate chain anchored
    in Sigstore's published trust root (fetched over TUF, not taken from the
    bundle itself)
  * the Rekor transparency-log inclusion proof for the entry
  * the signing certificate's OIDC claims, against the specific builder we
    claim: the workflow, the tag ref, the repository, the runner environment
  * that the statement's subject digest is the wheel digest the TRACE record
    carries in build_provenance.digest

If any of that fails, the record's provenance_depth_verified must stay at
surface and this script says so.
"""

import base64
import json
import sys

from sigstore.models import Bundle
from sigstore.verify import Verifier
from sigstore.verify import policy as pol

BUNDLE = "/tmp/pypi-bundle.json"
WHEEL = "mcp_evidence_validator-0.5.0-py3-none-any.whl"
WHEEL_DIGEST = "sha256:a9c34e8b4040e9e7a370953430eed09e7790bb3c15c0a0f6beb74d311d203053"

SIGNER_URI = (
    "https://github.com/narko4u/mcp-evidence-validator/.github/workflows/"
    "release.yml@refs/tags/v0.5.0"
)
REPO = "narko4u/mcp-evidence-validator"
ISSUER = "https://token.actions.githubusercontent.com"
RUNNER = "github-hosted"


def s(value):
    """Sigstore's bundle model wants these as strings."""
    return None if value is None else str(value)


def to_sigstore_bundle(pypi: dict) -> dict:
    """Map a PyPI integrity attestation onto a Sigstore bundle.

    PyPI serves the same material with snake_case keys; the field set is
    otherwise the one a bundle carries, so this is a rename rather than a
    reconstruction. Nothing is added that PyPI did not serve.
    """
    att = pypi["attestation_bundles"][0]["attestations"][0]
    env = att["envelope"]
    vm = att["verification_material"]
    entries = []
    for e in vm["transparency_entries"]:
        proof = e.get("inclusionProof") or {}
        entries.append(
            {
                "logIndex": s(e.get("logIndex")),
                "logId": {"keyId": (e.get("logId") or {}).get("keyId")},
                "kindVersion": e.get("kindVersion"),
                "integratedTime": s(e.get("integratedTime")),
                "inclusionPromise": {
                    "signedEntryTimestamp": (
                        (e.get("inclusionPromise") or {}).get("signedEntryTimestamp")
                    )
                },
                "inclusionProof": {
                    "logIndex": s(proof.get("logIndex")),
                    "rootHash": proof.get("rootHash"),
                    "treeSize": s(proof.get("treeSize")),
                    "hashes": proof.get("hashes"),
                    "checkpoint": {"envelope": (proof.get("checkpoint") or {}).get("envelope")},
                },
                "canonicalizedBody": e.get("canonicalizedBody"),
            }
        )
    return {
        "mediaType": "application/vnd.dev.sigstore.bundle.v0.3+json",
        "verificationMaterial": {
            "certificate": {"rawBytes": vm["certificate"]},
            "tlogEntries": entries,
        },
        "dsseEnvelope": {
            "payload": env["statement"],
            "payloadType": "application/vnd.in-toto+json",
            "signatures": [{"sig": env["signature"]}],
        },
    }


def main() -> int:
    raw = json.load(open(BUNDLE))
    builder = raw["attestation_bundles"][0]["publisher"]
    print("=== what PyPI says about the publisher ===")
    print(f"  {json.dumps(builder)}")

    bundle = Bundle.from_json(json.dumps(to_sigstore_bundle(raw)))
    print("\n=== bundle parsed under Sigstore's model ===")
    print(f"  parsed: {type(bundle).__name__}")

    checks = {
        "issuer": pol.OIDCIssuer(ISSUER),
        "signer (workflow@ref)": pol.OIDCBuildSignerURI(SIGNER_URI),
        "repository": pol.GitHubWorkflowRepository(REPO),
        "runner environment": pol.OIDCRunnerEnvironment(RUNNER),
    }

    print("\n=== verifying signature, cert chain and Rekor inclusion ===")
    verifier = Verifier.production()
    failed = []
    for label, one in checks.items():
        try:
            result = verifier.verify_dsse(bundle, one)
            print(f"  PASS  {label}")
        except Exception as ex:  # noqa: BLE001
            failed.append(label)
            print(f"  FAIL  {label}: {type(ex).__name__}: {ex}")

    if failed:
        print("\n  VERDICT: NOT VERIFIED - provenance_depth_verified must stay 'surface'")
        return 1

    print("\n  VERDICT: VERIFIED")
    print("  The DSSE signature, the Fulcio chain and the Rekor inclusion proof all")
    print("  check out, and the signing certificate's OIDC claims are the builder we")
    print("  claim. provenance_depth_verified may be recorded as 'builder'.")

    # verify_dsse hands back (payload_type, payload_bytes)
    payload = result
    if isinstance(result, tuple):
        payload = next((x for x in result if isinstance(x, bytes)), None)
        if payload is None:
            print(f"\n  unexpected verify_dsse return: {[type(x).__name__ for x in result]}")
            return 1
    statement = json.loads(payload.decode())
    subject = statement["subject"][0]
    print("\n=== the statement binds this exact wheel ===")
    print(f"  subject name   : {subject['name']}")
    print(f"  subject sha256 : sha256:{subject['digest']['sha256']}")
    print(f"  record claims  : {WHEEL_DIGEST}")
    match = f"sha256:{subject['digest']['sha256']}" == WHEEL_DIGEST
    print(f"  match          : {match}")
    print(f"  predicateType  : {statement['predicateType']}")
    print(f"  predicate      : {statement['predicate']}")
    if not match:
        print("\n  the statement is for a different artifact than the record cites")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
