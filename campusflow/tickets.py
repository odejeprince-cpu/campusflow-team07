"""Ticket creation: input validation, priority calculation and unique IDs.

Functions raise ValueError with a clear message on invalid input. Input is
checked BEFORE anything is added to the ticket list, so a failed call never
leaves a half-built ticket behind.
"""

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCY_LEVELS = ("low", "medium", "high")


def validate_title(title):
    """Return the title without surrounding spaces, or raise ValueError if blank."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title must not be blank.")
    return title.strip()


def validate_category(category):
    """Return the category in its standard spelling (e.g. 'network' -> 'Network')."""
    if isinstance(category, str):
        for allowed in CATEGORIES:
            if category.strip().lower() == allowed.lower():
                return allowed
    raise ValueError("Invalid category. Choose one of: " + ", ".join(CATEGORIES) + ".")


def validate_urgency(urgency):
    """Return the urgency in lowercase, or raise ValueError if not allowed."""
    if isinstance(urgency, str) and urgency.strip().lower() in URGENCY_LEVELS:
        return urgency.strip().lower()
    raise ValueError("Invalid urgency. Choose one of: " + ", ".join(URGENCY_LEVELS) + ".")


def validate_affected_users(affected_users):
    """Return affected_users as a positive int.

    Accepts an int or a string of digits. Rejects zero, negatives, decimals,
    booleans and text.
    """
    message = "Affected users must be a positive whole number (1 or more)."

    if isinstance(affected_users, bool):  # True/False are ints in Python, so block them
        raise ValueError(message)

    if isinstance(affected_users, int):
        number = affected_users
    elif isinstance(affected_users, str):
        text = affected_users.strip()
        if not (text.isascii() and text.isdigit()):
            raise ValueError(message)
        number = int(text)
    else:
        raise ValueError(message)

    if number < 1:
        raise ValueError(message)
    return number


def calculate_priority(urgency, affected_users):
    """Apply the priority rules in order and return the first match."""
    high = urgency == "high"
    many = affected_users >= 10

    if high and many:  # Rule 1
        return "critical"
    if high or many:  # Rule 2
        return "high"
    if urgency == "medium" or affected_users >= 3:  # Rule 3
        return "medium"
    return "low"  # Rule 4


def generate_ticket_id(tickets):
    """Return the next ID (T001, T002, ...) based on the highest existing ID.

    Using the existing tickets (not a counter that restarts at 1) keeps IDs
    unique after the tickets are reloaded from the JSON file.
    """
    highest = 0
    for ticket in tickets:
        highest = max(highest, int(ticket["id"][1:]))
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate the input, add a new ticket to `tickets` and return it."""
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    ticket = {
        "id": generate_ticket_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket