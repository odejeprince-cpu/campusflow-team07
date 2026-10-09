"""JSON storage. This is the ONLY module that reads or writes the tickets file."""

import json
import os

DEFAULT_PATH = os.path.join("data", "tickets.json")


class StorageError(Exception):
    """Raised when the tickets file cannot be read or written safely."""


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