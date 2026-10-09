"""Reports: totals and breakdowns by status and priority."""

STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")


def generate_report(tickets):
    """Return a dict with the total and counts by status and priority.

    Every status and priority is always present (with 0 if there are none),
    so an empty ticket list still produces a correct report.
    """
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}

    for ticket in tickets:
        by_status[ticket["status"]] += 1
        by_priority[ticket["priority"]] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }


def format_report(report):
    """Turn the report dict into text for printing."""
    lines = [f"Total tickets: {report['total']}", "", "By status:"]
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")
    lines.append("")
    lines.append("By priority:")
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")
    return "\n".join(lines)