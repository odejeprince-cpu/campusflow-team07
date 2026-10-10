"""Ticket workflow: assignment, status changes, reopening and the work queue.

Every function takes the ticket list as its first argument, checks the input
BEFORE changing anything, and raises ValueError with a clear message when the
input or the requested transition is invalid. A failed call never changes a ticket.
"""

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
VALID_STATUSES = ("open", "in_progress", "resolved")

# Each status may only move forward to this one status.
NEXT_STATUS = {
    "open": "in_progress",
    "in_progress": "resolved",
}


def find_ticket(tickets, ticket_id):
    """Return the ticket with this ID, or raise ValueError if it does not exist."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID must not be blank.")
    wanted = ticket_id.strip().upper()
    for ticket in tickets:
        if ticket["id"] == wanted:
            return ticket
    raise ValueError(f"Ticket {wanted} not found.")


def _reject_if_resolved(ticket):
    if ticket["status"] == "resolved":
        raise ValueError(
            f"Ticket {ticket['id']} is resolved. Reopen it before making changes."
        )


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket to a staff member and return the updated ticket."""
    ticket = find_ticket(tickets, ticket_id)
    _reject_if_resolved(ticket)

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff member name must not be blank.")

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    """Move a ticket open -> in_progress -> resolved and return the updated ticket."""
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str) or new_status.strip().lower() not in VALID_STATUSES:
        raise ValueError(
            "Invalid status. Choose one of: " + ", ".join(VALID_STATUSES) + "."
        )
    new_status = new_status.strip().lower()
    current = ticket["status"]

    if current == "resolved":
        raise ValueError(
            f"Ticket {ticket['id']} is resolved. Use reopen to set it back to open."
        )
    if new_status == current:
        raise ValueError(f"Ticket {ticket['id']} is already {current}.")
    if NEXT_STATUS.get(current) != new_status:
        raise ValueError(f"Cannot move a ticket from {current} to {new_status}.")
    if new_status == "in_progress" and not ticket["assigned_to"]:
        raise ValueError(
            f"Ticket {ticket['id']} must be assigned before it can be in_progress."
        )

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Set a resolved ticket back to open and return it."""
    ticket = find_ticket(tickets, ticket_id)
    if ticket["status"] != "resolved":
        raise ValueError(
            f"Only resolved tickets can be reopened (ticket {ticket['id']} is {ticket['status']})."
        )
    ticket["status"] = "open"
    return ticket


def _id_number(ticket_id):
    """'T012' -> 12, so T2 sorts before T10 (text sorting would get this wrong)."""
    return int(ticket_id[1:])


def get_work_queue(tickets):
    """Return open tickets: critical -> high -> medium -> low, then lowest ID first."""
    open_tickets = [t for t in tickets if t["status"] == "open"]
    return sorted(
        open_tickets,
        key=lambda t: (PRIORITY_ORDER[t["priority"]], _id_number(t["id"])),
    )