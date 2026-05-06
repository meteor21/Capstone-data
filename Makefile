.PHONY: five-min-snapshot five-min-aggregate five-min-all test

five-min-snapshot:
	python scripts/five_minute_snapshot.py

five-min-aggregate:
	python scripts/five_minute_aggregate.py

five-min-all: five-min-snapshot five-min-aggregate

test:
	python -m pytest -q
