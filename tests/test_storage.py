import json
import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets

SAMPLE = [
    {
        "id": "T001",
        "title": "Campus Wi-Fi is down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
    }
]


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "data", "tickets.json")

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_then_load_returns_same_tickets(self):
        save_tickets(SAMPLE, self.path)
        self.assertEqual(load_tickets(self.path), SAMPLE)

    def test_save_creates_missing_folder(self):
        save_tickets(SAMPLE, self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_malformed_json_raises_clear_error_and_keeps_file(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("{ this is not valid json")

        with self.assertRaises(StorageError):
            load_tickets(self.path)

        with open(self.path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), "{ this is not valid json")

    def test_json_that_is_not_a_list_is_rejected(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump({"id": "T001"}, file)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_saving_empty_list_works(self):
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])


if __name__ == "__main__":
    unittest.main()