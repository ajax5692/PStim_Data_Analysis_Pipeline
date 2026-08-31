from django.core.exceptions import ValidationError


def validate_measurement_unit_ranges(value):
    """
    Validate measurement unit ranges such as:
        10:21,25:55
        3,5:8,12
    """

    if not value or not value.strip():
        raise ValidationError(
            "Measurement unit ranges cannot be empty."
        )

    for part in value.split(","):
        part = part.strip()

        if not part:
            raise ValidationError(
                "Invalid measurement unit range."
            )

        if ":" in part:
            values = part.split(":")

            if len(values) != 2:
                raise ValidationError(
                    f"Invalid range '{part}'. Use the format start:end."
                )

            try:
                start = int(values[0])
                end = int(values[1])
            except ValueError:
                raise ValidationError(
                    f"Invalid range '{part}'. Unit numbers must be integers."
                )

            if start > end:
                raise ValidationError(
                    f"Invalid range '{part}'. Start must not be greater than end."
                )

        else:
            try:
                int(part)
            except ValueError:
                raise ValidationError(
                    f"Invalid unit '{part}'. Unit numbers must be integers."
                )