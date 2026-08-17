"""Allow `python -m mcp_evidence_validator` to work like the CLI."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
