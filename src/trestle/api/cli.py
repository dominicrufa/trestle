#!/usr/bin/env python3
"""CLI for the NIH RePORTER projects/search client."""

from __future__ import annotations

import argparse
import json
import sys
import time

from .nih_reporter import (
    build_payload,
    call_reporter,
    print_projects,
    print_summary,
    write_csv,
    write_json,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NIH RePORTER API client (projects/search).")
    parser.add_argument(
        "--year",
        type=int,
        action="append",
        help="Fiscal year filter (repeatable). Example: --year 2023",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        action="append",
        help="Keyword filter (repeatable). Example: --keyword cancer",
    )
    parser.add_argument(
        "--activity",
        type=str,
        action="append",
        help="Activity code filter (repeatable). Example: --activity R01",
    )
    parser.add_argument(
        "--org",
        type=str,
        action="append",
        help="Organization name filter (repeatable). Example: --org 'STANFORD UNIVERSITY'",
    )
    parser.add_argument(
        "--pi",
        type=str,
        action="append",
        help="PI name filter (repeatable). Example: --pi Smith",
    )

    parser.add_argument("--limit", type=int, default=10, help="Number of results to return.")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination.")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--include_fields",
        type=str,
        nargs="*",
        default=None,
        help="Override include_fields list. Example: --include_fields ProjectTitle AwardAmount",
    )
    parser.add_argument("--out_json", type=str, default=None, help="Optional output path for full JSON.")
    parser.add_argument("--out_csv", type=str, default=None, help="Optional output path for flattened CSV.")
    parser.add_argument("--print_n", type=int, default=10, help="How many results to print.")
    args = parser.parse_args(argv)
    if args.limit <= 0:
        parser.error("--limit must be greater than 0")
    if args.offset < 0:
        parser.error("--offset must be greater than or equal to 0")
    if args.print_n <= 0:
        parser.error("--print_n must be greater than 0")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(
        fiscal_years=args.year,
        keywords=args.keyword,
        activity_codes=args.activity,
        org_names=args.org,
        pi_names=args.pi,
        include_fields=args.include_fields,
        offset=args.offset,
        limit=args.limit,
    )

    print("Request payload:")
    print(json.dumps(payload, indent=2))
    print()

    start_time = time.time()
    try:
        data = call_reporter(payload, timeout_s=args.timeout)
    except Exception as exc:  # noqa: BLE001
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1
    elapsed = time.time() - start_time

    print_summary(data)
    print(f"Request time: {elapsed:.3f}s")
    print()

    results = data.get("results") or []
    print_projects(results, max_rows=args.print_n)

    if args.out_json:
        write_json(args.out_json, data)
    if args.out_csv:
        write_csv(args.out_csv, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
