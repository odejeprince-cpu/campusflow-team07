import copy
import unittest

from campusflow.reports import generate_report
from campusflow.workflow import (
    assign_ticket,
    change_status,
    get_work_queue,
    reopen_ticket,
)


def make_ticket(ticket_id, priority="low", status="open", assigned_to=None):
    return {
        "id": ticket_id,
        "title": f"Problem {ticket_id}",
        "category": "Network",
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestAssign(unittest.TestCase):
    def test_assign_sets_staff_name(self):
        tickets = [make_ticket("T001")]
        ticket = assign_ticket(tickets, "T001", "  Amaka ")
        self.assertEqual(ticket["assigned_to"], "Amaka")

    def test_assign_accepts_lowercase_id(self):
        tickets = [make_ticket("T001")]
        assign_ticket(tickets, "t001", "Amaka")
        self.assertEqual(tickets[0]["assigned_to"], "Amaka")

    def test_assign_unknown_id_is_rejected(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T999", "Amaka")

    def test_assign_blank_name_is_rejected_and_ticket_unchanged(self):
        tickets = [make_ticket("T001")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "   ")
        self.assertEqual(tickets, before)

    def test_resolved_ticket_cannot_be_assigned(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Amaka")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Chidi")
        self.assertEqual(tickets[0]["assigned_to"], "Amaka")


class TestStatusWorkflow(unittest.TestCase):
    def test_full_lifecycle(self):
        tickets = [make_ticket("T001", assigned_to="Amaka")]
        change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "in_progress")
        change_status(tickets, "T001", "RESOLVED")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_unassigned_ticket_cannot_be_in_progress(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "open")

    def test_cannot_skip_from_open_to_resolved(self):
        tickets = [make_ticket("T001", assigned_to="Amaka")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "open")

    def test_invalid_status_is_rejected(self):
        tickets = [make_ticket("T001", assigned_to="Amaka")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "banana")

    def test_resolved_ticket_cannot_change_status_without_reopen(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Amaka")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_reopen_sets_resolved_ticket_to_open(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Amaka")]
        reopen_ticket(tickets, "T001")
        self.assertEqual(tickets[0]["status"], "open")

    def test_reopen_rejects_ticket_that_is_not_resolved(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            reopen_ticket(tickets, "T001")

    def test_reopened_ticket_can_be_assigned_again(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Amaka")]
        reopen_ticket(tickets, "T001")
        assign_ticket(tickets, "T001", "Chidi")
        self.assertEqual(tickets[0]["assigned_to"], "Chidi")


class TestWorkQueue(unittest.TestCase):
    def test_queue_orders_by_priority(self):
        tickets = [
            make_ticket("T001", "low"),
            make_ticket("T002", "critical"),
            make_ticket("T003", "medium"),
            make_ticket("T004", "high"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T002", "T004", "T003", "T001"])

    def test_queue_breaks_ties_by_numeric_id(self):
        # As text "T10" < "T2", so this checks the numeric comparison.
        tickets = [make_ticket("T10", "high"), make_ticket("T2", "high")]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T2", "T10"])

    def test_queue_only_includes_open_tickets(self):
        tickets = [
            make_ticket("T001", "critical", status="resolved"),
            make_ticket("T002", "critical", status="in_progress", assigned_to="A"),
            make_ticket("T003", "low", status="open"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T003"])

    def test_queue_of_no_tickets_is_empty(self):
        self.assertEqual(get_work_queue([]), [])


class TestReports(unittest.TestCase):
    def test_report_with_zero_tickets(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertTrue(all(count == 0 for count in report["by_status"].values()))
        self.assertTrue(all(count == 0 for count in report["by_priority"].values()))

    def test_report_counts_status_and_priority(self):
        tickets = [
            make_ticket("T001", "critical", "open"),
            make_ticket("T002", "critical", "resolved"),
            make_ticket("T003", "low", "open"),
        ]
        report = generate_report(tickets)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_status"]["open"], 2)
        self.assertEqual(report["by_status"]["resolved"], 1)
        self.assertEqual(report["by_status"]["in_progress"], 0)
        self.assertEqual(report["by_priority"]["critical"], 2)
        self.assertEqual(report["by_priority"]["low"], 1)


if __name__ == "__main__":
    unittest.main()