"""CampusFlow command-line menu. Handles input and output only; the rules live in campusflow/."""

import sys

from campusflow.reports import format_report, generate_report
from campusflow.storage import DEFAULT_PATH, StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket  # written by your partner
from campusflow.workflow import (
    assign_ticket,
    change_status,
    find_ticket,
    get_work_queue,
    reopen_ticket,
)

MENU = """
=== CampusFlow Helpdesk ===
1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change status (in_progress / resolved)
6. Reopen resolved ticket
7. Work queue
8. Reports
9. Exit
"""


def print_ticket(ticket):
    print(f"  ID:             {ticket['id']}")
    print(f"  Title:          {ticket['title']}")
    print(f"  Category:       {ticket['category']}")
    print(f"  Urgency:        {ticket['urgency']}")
    print(f"  Affected users: {ticket['affected_users']}")
    print(f"  Priority:       {ticket['priority']}")
    print(f"  Status:         {ticket['status']}")
    print(f"  Assigned to:    {ticket['assigned_to'] or 'unassigned'}")


def print_ticket_rows(tickets):
    if not tickets:
        print("No tickets to show.")
        return
    for ticket in tickets:
        print(
            f"{ticket['id']} | {ticket['priority']:<8} | {ticket['status']:<11} | "
            f"{ticket['assigned_to'] or 'unassigned':<12} | {ticket['title']}"
        )


def handle_choice(choice, tickets):
    """Run one menu action. Returns True if tickets changed and need saving."""
    if choice == "1":
        title = input("Title: ")
        category = input("Category (Network/Hardware/Software/Other): ")
        urgency = input("Urgency (low/medium/high): ")
        affected_users = input("Affected users: ")
        ticket = create_ticket(tickets, title, category, urgency, affected_users)
        print(f"Created ticket {ticket['id']} with priority {ticket['priority']}.")
        return True

    if choice == "2":
        print_ticket_rows(tickets)
        return False

    if choice == "3":
        print_ticket(find_ticket(tickets, input("Ticket ID: ")))
        return False

    if choice == "4":
        ticket_id = input("Ticket ID: ")
        staff_name = input("Assign to (staff name): ")
        ticket = assign_ticket(tickets, ticket_id, staff_name)
        print(f"Ticket {ticket['id']} assigned to {ticket['assigned_to']}.")
        return True

    if choice == "5":
        ticket_id = input("Ticket ID: ")
        new_status = input("New status (in_progress/resolved): ")
        ticket = change_status(tickets, ticket_id, new_status)
        print(f"Ticket {ticket['id']} is now {ticket['status']}.")
        return True

    if choice == "6":
        ticket = reopen_ticket(tickets, input("Ticket ID: "))
        print(f"Ticket {ticket['id']} reopened.")
        return True

    if choice == "7":
        print_ticket_rows(get_work_queue(tickets))
        return False

    if choice == "8":
        print(format_report(generate_report(tickets)))
        return False

    print("Invalid choice. Please enter a number from 1 to 9.")
    return False


def main():
    try:
        tickets = load_tickets(DEFAULT_PATH)
    except StorageError as error:
        print(f"Error: {error}")
        sys.exit(1)

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "9":
            print("Goodbye!")
            break

        try:
            changed = handle_choice(choice, tickets)
            if changed:
                save_tickets(tickets, DEFAULT_PATH)
        except (ValueError, StorageError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()