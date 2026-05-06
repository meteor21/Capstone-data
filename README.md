# Soccer Betting Capstone — Data Layer

## Where to see code and tables
- **In GitHub code tab**: all source/config/scripts/tests in this repository.
- **In GitHub PR diff**: file-by-file changes from each commit/PR.
- **In Codex (here)**: I can print file contents or summaries at any time.

Generated verification outputs live at:
- `reports/verification/five_min_events.csv`
- `reports/verification/five_min_report.md`
- `reports/verification/five_min_team_event_counts.csv`
- `reports/verification/five_min_aggregate_report.md`

## Quick commands
Run from repo root:

```bash
make five-min-snapshot   # pull/parse first 5 minutes and create table + chart report
make five-min-aggregate  # aggregate by team/event-type from snapshot CSV
make five-min-all        # run both steps
```

## Notes
- If `SPORTRADAR_API_KEY` is set, snapshot script attempts SportRadar summary pull.
- If not set or pull fails, script falls back to fixture data for deterministic output.
