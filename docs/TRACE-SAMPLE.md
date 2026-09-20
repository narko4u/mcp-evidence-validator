# TRACE sample: one recorded MCP tool call, both contract outcomes

This is the sample requested on
[awesome-ai-governance#68](https://github.com/agentrust-io/awesome-ai-governance/pull/68),
with the proposed mapping and the exact package versions. Every value below is
read off a committed artifact. Nothing here is asserted without a file behind it.

## 1. The pair

Both cases run against the **same server**,
`@modelcontextprotocol/server-filesystem`, so the two outcomes differ because of
the contract and not because of the server. That is the comparison you asked for.

| | Unchanged contract | Changed contract |
|---|---|---|
| declared capture | 2026.8.31 | 2026.1.14 |
| observed capture | 2026.8.31 | 2026.8.31 |
| declared tools | 14 | 14 |
| observations | 1 | 3 |
| **findings** | **0** | **3** |
| check that fired | none | `contract_mutated` (medium), 3 times |
| ledger head | `sha256:816a1051…24baec` | `sha256:597c86a8…21077a` |
| pair files | `examples/agent-directed-declared.json`<br>`examples/agent-directed-observed.json` | `examples/filesystem-server-declared.json`<br>`examples/filesystem-server-observed.json` |

### What actually changed between the two versions

All 14 tools differ between 2026.1.14 and 2026.8.31. The change is not cosmetic
drift in descriptions; it is the annotation surface:

- **`openWorldHint` was added to all 14 tools.** None carried it in 2026.1.14.
- **`move_file` changed `destructiveHint` from `false` to `true`.** This is the
  only `destructiveHint` or `readOnlyHint` change across the two versions, and it
  is the reason the changed case is worth showing. A caller reading the
  2026.1.14 declaration would have been told this tool was not destructive. It is.

That is a declaration that was true when it was made and is no longer true, which
is exactly the condition a declared-versus-observed check exists to catch.

### The call that was recorded

The unchanged case is a single call, chosen by the agent from the served menu:

| | |
|---|---|
| tool | `read_text_file` |
| arguments | `{"path": "<allowed-root>/sample.txt"}` |
| outcome | text content returned, `isError: false` |
| declared contract | `sha256:9994016fe5e423a4de4616674c01daaf10f84ea6a2bb8d57595bb8f9ac06fd8c` |
| observed contract | `sha256:5b0dc61658af6e987fb841f8998537c209903a0918ab08e6b083d23f6fa01fe1` |

`read_text_file` over the deprecated `read_file`, and a read-only tool over every
mutating alternative, so a recorded call does not leave the reader reasoning
about side effects it caused.

## 2. Proposed mapping onto TRACE v0.2

The TRACE v0.2 record is the claim. The ledger is the evidence for the checks
that were actually performed. These are two artifacts and the mapping keeps them
apart, for the reason you gave: verifying the record establishes the signature
and the checks performed, and the validator compares the declaration against the
observations supplied to it.

| Our artifact | TRACE v0.2 destination | Fidelity |
|---|---|---|
| evidence ledger head | `references[rel=evidence].digest`, and `tool_transcript.hash` | **exact.** The digest binds the ledger. |
| declared contract hash | `references[rel=declared-contract].digest` | **exact** |
| observed runtime contract hash | `references[rel=observed-runtime].digest` | **exact** |
| recorded call count | `tool_transcript.call_count` | **exact** |
| validator package | `origin.producer` | informal string |
| validator version | `origin.producer` | informal string |
| self vs independent appraisal | `appraisal.verifier` | **exact**, and `appraisal.status` records the outcome |
| findings count and severity | `appraisal.status` only (`affirming` / `warning`) | **lossy.** "0 findings" and "3 findings, all medium" collapse to two values. |
| check names (`bound_unmutated`, `contract_mutated`, `scope_violation`, `recipe_mismatch`) | none | **no destination** |
| contract recipe id | none | **no destination** |
| observation count | none | **no destination** |
| the arguments of the call | none. Only the transcript hash is carried. | **no destination** |
| exact package versions of the validator and its dependencies | `build_provenance.*` describes the released wheel only | **partial** |

### The three rows that do not map

These are the gaps, and we would rather name them than fill them with something
that looks like a mapping and is not:

1. **Findings have no field.** TRACE v0.2 carries an appraisal status, which is a
   verdict, and no structured finding list. The record can say the appraisal
   affirmed; it cannot say what was checked or what severity came back.
2. **The check vocabulary has no field.** Which checks ran is not representable.
   A reader cannot tell from the record whether a clean result came from a strong
   check set or a weak one.
3. **The observation count has no field.** This one matters more than it looks:
   without it, "one recorded call, zero findings" and "three recorded calls,
   zero findings" are the same record.

The recommended handling is the one this sample uses: keep the finding detail in
the ledger, bind the ledger by digest from `references`, and let the record stay
a claim about a ledger rather than a substitute for it. That keeps the two
artifacts separate and checkable independently, which is the property your
comment asks for.

## 3. Exact package versions

Every run in this sample:

```
mcp-evidence-validator    0.5.0
agentrust-trace           0.10.0
agentrust-trace-tests     0.5.1
cmcp-runtime              0.5.0
agent-manifest            0.12.0
sigstore                  4.5.0
Python                    3.13.13
```

The validator is released on PyPI as `mcp-evidence-validator` 0.5.0, Apache-2.0.

## 4. What the TRACE record claims, and what it does not

The signed record accompanying this sample clears the conformance suite at
**Level 0 and only Level 0**.

```
TRACE Conformance Report -- Level 0 — Software-only
  Level 0  PASS
  Level 1  FAIL
  Level 2  FAIL
```

- **Level 1** requires a hardware TEE. This run has no hardware root of trust, so
  `runtime.platform` is `software-only`. That is infrastructure, not code.
- **Level 2** requires a transparency receipt. None exists for this record.
- The record is **self-signed, and the signing key is not retained.** Verification
  therefore requires `allow_embedded_key`, which establishes that the record is
  internally consistent and not that it came from a trusted issuer.

## 5. What none of this establishes

Stated separately, because it is the limit most easily read past:

**Neither artifact establishes that the observations captured everything.**

Verifying the record establishes its signature and the checks actually performed.
The validator compares the declaration against the observations supplied to it.
A call that was never recorded cannot be found by comparing a declaration against
a transcript. The ledger binds what was observed; it says nothing about what was
not. A clean result means the observations supplied are consistent with the
declaration, and not that the observations are complete.
