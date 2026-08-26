import re


def get_user_initials(user_or_username):
    """
    Convert a User instance or username string into initials matching
    the convention in Animal.OwnerChoices (e.g. 'abhrajyoti.chakrabarti' -> 'AC').
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
