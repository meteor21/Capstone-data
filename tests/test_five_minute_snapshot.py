import json
from pathlib import Path

from scripts.five_minute_snapshot import parse_first_five


def test_parse_first_five_filters_minutes():
    sample = json.loads((Path("tests/fixtures/sample_summary.json")).read_text())
    rows = parse_first_five(sample)
    assert rows
    assert max(r["minute"] for r in rows) <= 5
    assert "shot_off_target" not in {r["type"] for r in rows}
