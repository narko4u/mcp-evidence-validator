"""Generates the fictional demo manifests for the MCP Evidence Validator.

Run:  python3 make_examples.py
Writes:
  examples/fictional-server-declared.json
  examples/fictional-server-observed.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "prototype"))
from fingerprint import fingerprint

HERE = os.path.dirname(os.path.abspath(__file__))

get_forecast_contract = fingerprint({
    "name": "get_forecast",
    "description": "Return forecast for a city",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "days": {"type": "integer", "minimum": 1, "maximum": 7},
        },
        "required": ["city"],
    },
    "permissions": ["read:weather"],
})

declared = {
    "server": "fictional-weather",
    "declared_at": "2026-08-01T00:00:00Z",
    "tools": [
        {
            "name": "get_forecast",
            "description": "Return forecast for a city",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "days": {"type": "integer", "minimum": 1, "maximum": 7},
                },
                "required": ["city"],
            },
            "permissions": ["read:weather"],
        },
        {
            "name": "submit_weather_report",
            "description": "Submit a community weather report",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "condition": {"type": "string"},
                },
                "required": ["city", "condition"],
            },
            "permissions": ["write:weather"],
        },
    ],
    "annotations": [
        {
            "id": "ann-001",
            "tool": "get_forecast",
            "statement": "read-only access to public weather data",
            "bound_contract": get_forecast_contract,
        }
    ],
}

observed = {
    "server": "fictional-weather",
    "observations": [
        {
            "index": 1,
            "observed_at": "2026-08-02T12:00:00Z",
            "tool": "get_forecast",
            "args": {"city": "Townsville", "days": 3},
            "contract_hash": get_forecast_contract,
        },
        {
            "index": 2,
            "observed_at": "2026-08-02T12:05:00Z",
            "tool": "get_forecast",
            "args": {"city": "Townsville", "days": 3, "admin_token": "redacted"},
            "contract_hash": get_forecast_contract,
        },
        {
            "index": 3,
            "observed_at": "2026-08-02T12:10:00Z",
            "tool": "get_forecast",
            "args": {"city": "Townsville", "days": 3},
            "contract_hash": "sha256:deadbeef" * 0 + "sha256:" + "f" * 64,
        },
    ],
}

os.makedirs(HERE, exist_ok=True)
with open(os.path.join(HERE, "fictional-server-declared.json"), "w") as fh:
    json.dump(declared, fh, indent=2)
with open(os.path.join(HERE, "fictional-server-observed.json"), "w") as fh:
    json.dump(observed, fh, indent=2)
print("wrote fictional demo manifests")
