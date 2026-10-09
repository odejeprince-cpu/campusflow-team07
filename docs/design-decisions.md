Design Decisions

Agreed by both fellows before writing feature code.
1. Where tickets live

Tickets are a plain Python list of dictionaries. Every function takes the list as its first argument and changes it in place. main.py owns the list while the program runs.
2. Ticket shape

{
  "id": "T001", "title": "...", "category": "Network", "urgency": "high",
  "affected_users": 15, "priority": "critical", "status": "open", "assigned_to": None
}

3. Signaling invalid input

Functions raise ValueError with a clear message. They validate BEFORE changing anything, so a failed call never corrupts a ticket. main.py catches the error and prints it. Storage problems raise StorageError (from campusflow/storage.py).
4. Return values

create_ticket, assign_ticket, change_status and reopen_ticket return the ticket they created or changed. get_work_queue returns a sorted list. generate_report returns a dict.
5. Function contracts

    create_ticket(tickets, title, category, urgency, affected_users) receives raw text from the menu, validates it, appends the new ticket and returns it.
    assign_ticket(tickets, ticket_id, staff_name)
    change_status(tickets, ticket_id, new_status) and reopen_ticket(tickets, ticket_id)
    get_work_queue(tickets) and generate_report(tickets)
    load_tickets(path) and save_tickets(tickets, path)

6. JSON storage

Only campusflow/storage.py reads or writes the file (data/tickets.json). Missing file: start fresh. Malformed JSON: raise StorageError and leave the file untouched.
7. Unique IDs after reload

The next ID is the highest existing numeric ID plus 1, so IDs stay unique after a restart.
8. Testing without input()

Business logic never calls input() or print(). Tests call the functions directly.
9. Work queue meaning

The queue shows tickets with status open only (not in_progress or resolved), ordered critical -> high -> medium -> low, with ties broken by the lower numeric ID.