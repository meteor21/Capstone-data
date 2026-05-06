from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "verification"
INPUT_CSV = REPORT_DIR / "five_min_events.csv"
OUTPUT_CSV = REPORT_DIR / "five_min_team_event_counts.csv"
OUTPUT_MD = REPORT_DIR / "five_min_aggregate_report.md"


def load_rows() -> list[dict[str, str]]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV}")
    with INPUT_CSV.open() as f:
        return list(csv.DictReader(f))


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, str | int]]:
    counts: defaultdict[str, Counter] = defaultdict(Counter)
    for row in rows:
        counts[row.get("team", "Unknown")][row.get("type", "unknown")] += 1

    out: list[dict[str, str | int]] = []
    for team, counter in sorted(counts.items()):
        for event_type, count in sorted(counter.items()):
            out.append({"team": team, "event_type": event_type, "count": count})
    return out


def write_outputs(agg_rows: list[dict[str, str | int]]) -> None:
    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["team", "event_type", "count"])
        writer.writeheader()
        writer.writerows(agg_rows)

    md_lines = [
        "# Five-Minute Aggregate Report",
        "",
        "| team | event_type | count |",
        "|---|---|---|",
    ]
    for row in agg_rows:
        md_lines.append(f"| {row['team']} | {row['event_type']} | {row['count']} |")

    OUTPUT_MD.write_text("\n".join(md_lines) + "\n")


def main() -> None:
    rows = load_rows()
    agg_rows = aggregate(rows)
    write_outputs(agg_rows)


if __name__ == "__main__":
    main()
