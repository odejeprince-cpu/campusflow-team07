"""JSON storage. This is the ONLY module that reads or writes the tickets file."""

import json
import os

DEFAULT_PATH = os.path.join("data", "tickets.json")

REQUIRED_KEYS = (
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
)
VALID_STATUSES = ("open", "in_progress", "resolved")
VALID_PRIORITIES = ("critical", "high", "medium", "low")


class StorageError(Exception):
    """Raised when the tickets file cannot be read or written safely."""


def _check_ticket(ticket, position, path):
    """Raise StorageError if a loaded ticket is missing fields or has unusable values.

    Catching this at load time gives a clear message, instead of a crash later
    (for example a KeyError in the reports) when a function reads the bad field.
    """
    label = f"ticket #{position} in {path}"

    missing = [key for key in REQUIRED_KEYS if key not in ticket]
    if missing:
        raise StorageError(
            f"{label} is missing required field(s): {', '.join(missing)}. "
            "Fix or move the file; it has not been changed."
        )

    ticket_id = ticket["id"]
    if not (
        isinstance(ticket_id, str)
        and ticket_id.startswith("T")
        and ticket_id[1:].isascii()
        and ticket_id[1:].isdigit()
    ):
        raise StorageError(
            f"{label} has an invalid id {ticket_id!r} (expected something like 'T001'). "
            "It has not been changed."
        )

    if ticket["status"] not in VALID_STATUSES:
        raise StorageError(
            f"{label} has an invalid status {ticket['status']!r}. "
            f"Expected one of: {', '.join(VALID_STATUSES)}. It has not been changed."
        )

    if ticket["priority"] not in VALID_PRIORITIES:
        raise StorageError(
            f"{label} has an invalid priority {ticket['priority']!r}. "
            f"Expected one of: {', '.join(VALID_PRIORITIES)}. It has not been changed."
        )


def load_tickets(path=DEFAULT_PATH):
    """Load tickets from a JSON file.

    - Missing file: return an empty list (a fresh start).
    - Malformed or wrong-shaped file: raise StorageError. The file is never
      overwritten here, so existing data is not silently erased.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise StorageError(
            f"{path} contains invalid JSON ({error}). "
            "Fix or move the file; it has not been changed."
        ) from error
    except OSError as error:
        raise StorageError(f"Could not read {path}: {error}") from error

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise StorageError(
            f"{path} must contain a list of tickets. It has not been changed."
        )

    for position, ticket in enumerate(data, start=1):
        _check_ticket(ticket, position, path)

    return data


def save_tickets(tickets, path=DEFAULT_PATH):
    """Save tickets to a JSON file.

    Writes to a temporary file first and then swaps it in, so a crash while
    saving cannot leave a half-written tickets file behind.
    """
    temp_path = path + ".tmp"
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=2)
        os.replace(temp_path, path)
    except OSError as error:
        raise StorageError(f"Could not save to {path}: {error}") from error