import re
from typing import Any, Optional


def get_user_initials(user_or_username: Any) -> str:
    """
    Convert a User instance or username string into initials matching
    the convention in Animal.OwnerChoices (e.g. 'abhrajyoti.chakrabarti' -> 'AC').

    Args:
        user_or_username: Django User instance, username string, or None.

    Returns:
        A uppercase 2-letter or 3-letter initials string.
    """
    if not user_or_username:
        return ""

    # Known mappings for project members / usernames
    known_initials_map = {
        "abhrajyoti.chakrabarti": "AC",
        "abhrajyoti": "AC",
        "ac": "AC",
        "balazs": "TB",
        "balázs": "TB",
        "tb": "TB",
        "varada": "VK",
        "vk": "VK",
    }

    # Handle User model instance
    if hasattr(user_or_username, "username"):
        user = user_or_username
        if user.first_name and user.last_name:
            return f"{user.first_name[0]}{user.last_name[0]}".upper()

        raw_name = user.username or ""
    else:
        raw_name = str(user_or_username).strip()

    if not raw_name:
        return ""

    lower_name = raw_name.lower()
    if lower_name in known_initials_map:
        return known_initials_map[lower_name]

    # If already 2-3 characters (e.g. 'AC', 'TB', 'VK')
    if len(raw_name) <= 3 and raw_name.isalpha():
        return raw_name.upper()

    # If formatted as 'firstname.lastname', 'firstname_lastname', or 'first last'
    parts = [p for p in re.split(r"[._\s-]+", raw_name) if p]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()

    if len(parts) == 1:
        from animals_metadata.models import Animal

        for choice_val, choice_label in Animal.OwnerChoices.choices:
            if parts[0].lower() in choice_label.lower():
                return choice_val

        return parts[0][:2].upper()

    return raw_name


def format_initial_entry(history_instance: Any) -> str:
    """
    Generate a detailed multi-line string of all field values present at record creation.

    Args:
        history_instance: The newly created simple_history historical instance.

    Returns:
        Formatted multi-line text listing initial non-empty field values.
    """
    if not history_instance:
        return "Initial Entry"

    excluded_fields = {
        "id",
        "history_id",
        "history_date",
        "history_type",
        "history_user",
        "history_user_id",
        "history_change_reason",
    }

    entries = []
    for field in history_instance._meta.fields:
        if field.name in excluded_fields:
            continue
        val = getattr(history_instance, field.name, None)
        if val is not None and str(val).strip() != "":
            entries.append(f"{field.name}: '{val}'")

    if entries:
        return "Initial Entry:\n" + "\n".join(entries)
    return "Initial Entry"


def build_history_diff_text(history_instance: Any) -> str:
    """
    Construct a human-readable summary of changes for a historical record event.
    Handles record creation (+), deletion (-), and field updates (~) with fallback.

    Args:
        history_instance: The simple_history historical model instance.

    Returns:
        A concise or multi-line string describing modified field names and old->new values.
    """
    if not history_instance:
        return ""

    if history_instance.history_type == "+":
        return format_initial_entry(history_instance)

    if history_instance.history_type == "-":
        return "Deleted Record"

    prev_record = getattr(history_instance, "prev_record", None)
    if not prev_record:
        return "No previous record"

    changes = []

    try:
        delta = history_instance.diff_against(prev_record)
        for change in delta.changes:
            changes.append(f"{change.field}: '{change.old}' → '{change.new}'")

    except Exception:
        excluded_fields = {
            "history_id",
            "history_date",
            "history_type",
            "history_user",
            "history_user_id",
            "history_change_reason",
        }

        for field in history_instance._meta.fields:
            if field.name in excluded_fields:
                continue

            old_val = getattr(prev_record, field.name, None)
            new_val = getattr(history_instance, field.name, None)

            if old_val != new_val:
                changes.append(f"{field.name}: '{old_val}' → '{new_val}'")

    return "\n".join(changes) if changes else "No field changes"
