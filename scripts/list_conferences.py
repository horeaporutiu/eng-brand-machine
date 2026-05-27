#!/usr/bin/env python3
"""List conferences from data/conferences.json without re-running the full pipeline.

This is a tiny CLI for non-Python folks and CI jobs that just need the catalog
data — useful for cross-posting upcoming events to Slack, generating sponsorship
spreadsheets, or sanity-checking that data/conferences.json parses cleanly.

Examples
--------
    # All upcoming local events for the configured city
    python3 scripts/list_conferences.py

    # Just the major AI conferences scanned by the Pulse panel
    python3 scripts/list_conferences.py --type global

    # JSON output for piping into jq, Slack, etc.
    python3 scripts/list_conferences.py --format json

    # Override the city used for the local schedule
    python3 scripts/list_conferences.py --location "Berlin, Germany"
"""

import argparse
import json
import os
import sys


def _ensure_repo_on_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)


_ensure_repo_on_path()

import eng_brand_machine as ebm  # noqa: E402


def _local_rows(location):
    schedule = ebm.build_ai_conference_schedule(location=location)
    return [
        {
            "name": item["name"],
            "date": item["date_label"],
            "venue": item["venue"],
            "format": item["format"],
            "tags": item.get("tags", []),
            "location": item["location"],
            "focus": item.get("focus", ""),
            "miro_angle": item.get("miro_angle", ""),
        }
        for item in schedule
    ]


def _global_rows():
    return [
        {
            "name": conf["name"],
            "long_name": conf.get("long_name", ""),
            "cadence": conf.get("cadence", ""),
            "audience": conf.get("audience", ""),
            "signal_topics": conf.get("signal_topics", []),
            "keyword_count": len(conf.get("keywords", [])),
        }
        for conf in ebm.MAJOR_AI_CONFERENCES
    ]


def _render_table(rows):
    if not rows:
        print("(no rows)")
        return
    columns = list(rows[0].keys())
    widths = {c: len(c) for c in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row[col])))
    header = "  ".join(col.upper().ljust(widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    for row in rows:
        print("  ".join(str(row[col]).ljust(widths[col]) for col in columns))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="List conferences from data/conferences.json"
    )
    parser.add_argument(
        "--type",
        choices=("local", "global", "all"),
        default="local",
        help="Which catalog section to print (default: local)",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--location",
        default=ebm.EVENT_TRACKER_LOCATION,
        help=f"City to scope the local schedule (default: {ebm.EVENT_TRACKER_LOCATION!r})",
    )
    args = parser.parse_args(argv)

    payload = {}
    if args.type in ("local", "all"):
        payload["local"] = _local_rows(args.location)
    if args.type in ("global", "all"):
        payload["global"] = _global_rows()

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if "local" in payload:
        print(f"\n📍 Upcoming events in {args.location}\n")
        _render_table([
            {k: ", ".join(v) if isinstance(v, list) else v for k, v in row.items()}
            for row in payload["local"]
        ])
    if "global" in payload:
        print("\n🧠 Major AI conferences tracked by the Pulse panel\n")
        _render_table([
            {k: ", ".join(v) if isinstance(v, list) else v for k, v in row.items()}
            for row in payload["global"]
        ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
