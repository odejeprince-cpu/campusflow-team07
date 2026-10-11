# AI Learning Log

## Prince Adams

### Entry 1: Testing AI-written storage code with a damaged JSON file
- **What I asked:** I asked the AI to write my part of CampusFlow (workflow, reports, storage and the main menu), including a `load_tickets` function that handles bad JSON safely.
- **What the AI said:** It wrote `storage.py` so that `load_tickets` returns an empty list for a missing file, raises a `StorageError` for malformed JSON, and checks that the file holds a list of dictionaries. Its tests passed.
- **How I verified it:** The AI's tests only used well-formed tickets, so I tested it myself. I created a ticket, then edited `data/tickets.json` by hand and deleted the `"status"` field. The program started without any error. When I chose option 8 (Reports), it crashed with `KeyError: 'status'` in `reports.py`.
- **Result:** Improved (fix pending). `load_tickets` only checks the overall shape of the file, not that each ticket has all eight fields, and `main.py` does not catch `KeyError`. The fix is to check the required fields when loading and raise a `StorageError` with a clear message, plus a test for it

## <Partner's name: Kayla Ejembi>
(same format)