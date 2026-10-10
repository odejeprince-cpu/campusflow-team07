# CampusFlow

A command-line helpdesk ticket manager for Learn2Earn campus staff.
Built in Python with the standard library only.

## Run

```bash
python3 main.py
```

Tickets are saved to `data/tickets.json` (not committed to Git).

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Project layout

- `main.py` - CLI menu (input/output only)
- `campusflow/tickets.py` - ticket creation, validation, priority
- `campusflow/workflow.py` - assignment, status changes, work queue
- `campusflow/reports.py` - totals and breakdowns
- `campusflow/storage.py` - JSON load/save
- `tests/` - automated tests
- `docs/` - design decisions and AI learning logs