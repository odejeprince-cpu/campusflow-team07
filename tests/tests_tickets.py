import copy
import os
import tempfile
import unittest

from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import calculate_priority, create_ticket


class TestPriority(unittest.TestCase):
    def test_rule_1_high_urgency_and_10_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("high", 15), "critical")

    def test_rule_2_high_urgency_alone_is_high(self):
        self.assertEqual(calculate_priority("high", 1), "high")
        self.assertEqual(calculate_priority("high", 9), "high")

    def test_rule_2_ten_users_alone_is_high(self):
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("medium", 50), "high")

    def test_rule_3_medium_urgency_is_medium(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")

    def test_rule_3_three_users_is_medium(self):
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("low", 9), "medium")

    def test_rule_4_everything_else_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")
        self.assertEqual(calculate_priority("low", 2), "low")


class TestCreateTicket(unittest.TestCase):
    def test_create_builds_complete_ticket(self):
        tickets = []
        ticket = create_ticket(tickets, "Campus Wi-Fi is down", "Network", "high", "15")
        self.assertEqual(
            ticket,
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
        )
        self.assertEqual(tickets, [ticket])

    def test_case_variations_are_normalized(self):
        tickets = []
        ticket = create_ticket(tickets, "  Laptop broken ", "hArDwArE", " MEDIUM ", " 2 ")
        self.assertEqual(ticket["title"], "Laptop broken")
        self.assertEqual(ticket["category"], "Hardware")
        self.assertEqual(ticket["urgency"], "medium")
        self.assertEqual(ticket["affected_users"], 2)

    def test_ids_are_sequential(self):
        tickets = []
        for _ in range(3):
            create_ticket(tickets, "Issue", "Other", "low", "1")
        self.assertEqual([t["id"] for t in tickets], ["T001", "T002", "T003"])

    def test_blank_title_is_rejected(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "   ", "Network", "low", "1")
        self.assertEqual(tickets, [])

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket([], "Issue", "Plumbing", "low", "1")

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket([], "Issue", "Network", "urgent", "1")

    def test_invalid_affected_users_are_rejected(self):
        for bad in ["0", "-3", "2.5", "abc", "", "  ", 0, -1, 2.5, True, None]:
            with self.subTest(affected_users=bad):
                with self.assertRaises(ValueError):
                    create_ticket([], "Issue", "Network", "low", bad)

    def test_failed_create_does_not_change_existing_tickets(self):
        tickets = []
        create_ticket(tickets, "Good ticket", "Network", "low", "1")
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Bad ticket", "Network", "low", "zero")
        self.assertEqual(tickets, before)

    def test_ids_stay_unique_after_save_and_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tickets.json")
            tickets = []
            create_ticket(tickets, "First", "Network", "low", "1")
            create_ticket(tickets, "Second", "Network", "low", "1")
            save_tickets(tickets, path)

            reloaded = load_tickets(path)
            new_ticket = create_ticket(reloaded, "Third", "Network", "low", "1")

            ids = [t["id"] for t in reloaded]
            self.assertEqual(new_ticket["id"], "T003")
            self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()