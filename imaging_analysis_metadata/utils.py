def parse_unit_ranges(unit_range_string):
    """
    Convert a string like:
        "10:21,25:55"

    into:
        [10, 11, 12, ..., 21, 25, 26, ..., 55]
    """

    units = []

    for part in unit_range_string.split(","):
        part = part.strip()

        if ":" in part:
            start, end = part.split(":")
            start = int(start)
            end = int(end)

            units.extend(range(start, end + 1))

        else:
            units.append(int(part))

    return units