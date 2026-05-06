from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "verification"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    import yaml
    from soccer_capstone.models import ApiConfig

    cfg = yaml.safe_load((ROOT / "config" / "config.yaml").read_text())
    return ApiConfig(**cfg["api"])


def parse_first_five(summary: dict) -> list[dict]:
    timeline = summary.get("timeline", [])
    rows = []
    for ev in timeline:
        minute = ev.get("time") or ev.get("match_time") or 0
        try:
            minute = int(str(minute).split(":")[0])
        except Exception:
            minute = 0
        if minute <= 5:
            rows.append(
                {
                    "id": ev.get("id"),
                    "minute": minute,
                    "type": ev.get("type"),
                    "team": (ev.get("competitor") or {}).get("name"),
                    "x": (ev.get("ball_location") or {}).get("x"),
                    "y": (ev.get("ball_location") or {}).get("y"),
                }
            )
    return rows


def _markdown_table(rows: list[dict], headers: list[str]) -> str:
    if not rows:
        return "No rows"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(out)


def build_report(rows: list[dict], source: str) -> None:
    table_path = REPORT_DIR / "five_min_events.csv"
    md_path = REPORT_DIR / "five_min_report.md"

    with table_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "minute", "type", "team", "x", "y"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r.get("type") for r in rows)
    count_rows = [{"event_type": k, "count": v} for k, v in counts.items()]
    chart_lines = [f"{r['event_type']:<20} {'#' * r['count']} ({r['count']})" for r in count_rows]

    md = [
        "# Five-Minute Snapshot",
        f"Source: {source}",
        "",
        "## Event Table",
        _markdown_table(rows, ["id", "minute", "type", "team", "x", "y"]),
        "",
        "## Event Type Counts",
        _markdown_table(count_rows, ["event_type", "count"]),
        "",
        "## ASCII Bar Chart",
        "```",
        *chart_lines,
        "```",
    ]
    md_path.write_text("\n".join(md))


def main() -> None:
    sample_path = ROOT / "tests" / "fixtures" / "sample_summary.json"
    source = "fixture"

    if os.getenv("SPORTRADAR_API_KEY"):
        try:
            from soccer_capstone.sportradar_client import SportRadarClient
            cfg = load_config()
            client = SportRadarClient(cfg)
            summary = client.get_json("sport_events/sr:sport_event:42255959/summary.json", use_cache=True)
            source = "api_or_cache"
        except Exception:
            summary = json.loads(sample_path.read_text())
            source = "fixture_fallback"
    else:
        summary = json.loads(sample_path.read_text())

    rows = parse_first_five(summary)
    build_report(rows, source)


if __name__ == "__main__":
    main()
