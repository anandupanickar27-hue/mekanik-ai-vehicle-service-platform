def categorize_issue(issue):

    issue = issue.lower()

    if "brake" in issue:
        return "Brake"

    elif "battery" in issue:
        return "Battery"

    elif "engine" in issue:
        return "Engine"

    elif "tire" in issue or "tyre" in issue:
        return "Tire"

    return "General"