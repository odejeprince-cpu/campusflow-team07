import copy
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

    def write_raw(self, text):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(text)

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_then_load_returns_same_tickets(self):
        save_tickets(SAMPLE, self.path)
        self.assertEqual(load_tickets(self.path), SAMPLE)

    def test_save_creates_missing_folder(self):
        save_tickets(SAMPLE, self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_malformed_json_raises_clear_error_and_keeps_file(self):
        self.write_raw("{ this is not valid json")

        with self.assertRaises(StorageError):
            load_tickets(self.path)

        with open(self.path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), "{ this is not valid json")

    def test_json_that_is_not_a_list_is_rejected(self):
        self.write_raw(json.dumps({"id": "T001"}))
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_saving_empty_list_works(self):
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])


class TestLoadRejectsDamagedTickets(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "tickets.json")

    def write_tickets(self, tickets):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(tickets, file)

    def assert_rejected_and_file_unchanged(self, tickets, expected_text):
        self.write_tickets(tickets)
        with open(self.path, "r", encoding="utf-8") as file:
            before = file.read()

        with self.assertRaises(StorageError) as context:
            load_tickets(self.path)
        self.assertIn(expected_text, str(context.exception))

        with open(self.path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), before)

    def test_ticket_missing_status_is_rejected(self):
        ticket = copy.deepcopy(SAMPLE[0])
        del ticket["status"]
        self.assert_rejected_and_file_unchanged([ticket], "status")

    def test_error_names_every_missing_field(self):
        ticket = copy.deepcopy(SAMPLE[0])
        del ticket["status"]
        del ticket["priority"]
        self.write_tickets([ticket])
        with self.assertRaises(StorageError) as context:
            load_tickets(self.path)
        self.assertIn("status", str(context.exception))
        self.assertIn("priority", str(context.exception))

    def test_invalid_status_value_is_rejected(self):
        ticket = copy.deepcopy(SAMPLE[0])
        ticket["status"] = "banana"
        self.assert_rejected_and_file_unchanged([ticket], "invalid status")

    def test_invalid_priority_value_is_rejected(self):
        ticket = copy.deepcopy(SAMPLE[0])
        ticket["priority"] = "urgent"
        self.assert_rejected_and_file_unchanged([ticket], "invalid priority")

    def test_invalid_id_is_rejected(self):
        ticket = copy.deepcopy(SAMPLE[0])
        ticket["id"] = "001"
        self.assert_rejected_and_file_unchanged([ticket], "invalid id")

    def test_error_points_to_the_bad_ticket(self):
        good = copy.deepcopy(SAMPLE[0])
        bad = copy.deepcopy(SAMPLE[0])
        bad["id"] = "T002"
        del bad["title"]
        self.write_tickets([good, bad])
        with self.assertRaises(StorageError) as context:
            load_tickets(self.path)
        self.assertIn("ticket #2", str(context.exception))


if __name__ == "__main__":
    unittest.main()