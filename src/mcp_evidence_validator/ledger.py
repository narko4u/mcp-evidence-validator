"""Tamper-evident ledger: append-only SHA-256 hash chain.

block_n = sha256(prev_hash + canonical_json(record_n))

Any mutation to a past record changes its hash and therefore every
later block, so a forged or edited ledger is detectable in one pass.
"""

import hashlib
import json
from typing import Any, Dict, List

from .fingerprint import canonical_json

GENESIS = "sha256:" + ("0" * 64)

LEDGER_NAME = "mcp-evidence-validator"
LEDGER_VERSION = "0.2"


class Ledger:
    def __init__(self) -> None:
        self._blocks: List[Dict[str, Any]] = []

    @classmethod
    def load(cls, path: str) -> "Ledger":
        led = cls()
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("ledger") != LEDGER_NAME:
            raise ValueError(
                f"not a {LEDGER_NAME} ledger (ledger field = {data.get('ledger')!r})"
            )
        led._blocks = data.get("blocks", [])
        return led

    def append(self, record_type: str, record: Dict[str, Any]) -> Dict[str, Any]:
        prev_hash = self._blocks[-1]["hash"] if self._blocks else GENESIS
        body = canonical_json({"type": record_type, "record": record})
        block_hash = "sha256:" + hashlib.sha256(
            (prev_hash + body).encode("utf-8")
        ).hexdigest()
        block = {
            "index": len(self._blocks),
            "prev_hash": prev_hash,
            "type": record_type,
            "record": record,
            "hash": block_hash,
        }
        self._blocks.append(block)
        return block

    def verify(self) -> List[str]:
        """Return a list of corruption messages (empty when intact)."""
        problems = []
        prev_hash = GENESIS
        for block in self._blocks:
            body = canonical_json({"type": block["type"], "record": block["record"]})
            expected = "sha256:" + hashlib.sha256(
                (prev_hash + body).encode("utf-8")
            ).hexdigest()
            if block["hash"] != expected:
                problems.append(f"block {block['index']}: hash mismatch")
                return problems
            prev_hash = block["hash"]
        return problems

    def dump(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(
                {"ledger": LEDGER_NAME, "version": LEDGER_VERSION, "blocks": self._blocks},
                fh,
                indent=2,
            )

    def __len__(self) -> int:
        return len(self._blocks)

    def __iter__(self):
        return iter(self._blocks)
