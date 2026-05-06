from scripts.five_minute_aggregate import aggregate


def test_aggregate_counts_by_team_and_type():
    rows = [
        {"team": "A", "type": "shot_on_target"},
        {"team": "A", "type": "shot_on_target"},
        {"team": "A", "type": "foul"},
        {"team": "B", "type": "foul"},
    ]
    out = aggregate(rows)
    assert { (r["team"], r["event_type"], r["count"]) for r in out } == {
        ("A", "foul", 1),
        ("A", "shot_on_target", 2),
        ("B", "foul", 1),
    }
