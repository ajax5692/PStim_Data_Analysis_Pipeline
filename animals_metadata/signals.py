from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from .models import Animal, TrackChanges, ViralInjection, VisionCheck
from .utils import format_initial_entry, get_user_initials


@receiver(post_create_historical_record)
def create_track_change(sender, instance, history_instance, **kwargs):

    model = instance.__class__

    if model not in (Animal, VisionCheck, ViralInjection):
        return

    if model is Animal:
        category = TrackChanges.CategoryChoices.ANIMAL
        animal_id = history_instance.animal_id

    elif model is VisionCheck:
        category = TrackChanges.CategoryChoices.VISION_CHECK
        animal_id = instance.animal_id.animal_id

    elif model is ViralInjection:
        category = TrackChanges.CategoryChoices.VIRAL_INJECTION
        animal_id = instance.animal_id.animal_id

    else:
        return

    # Build human-readable change description
    prev_record = history_instance.prev_record

    if history_instance.history_type == "+":
        changes_text = format_initial_entry(history_instance)

    elif history_instance.history_type == "-":
        changes_text = "Deleted Record"

    elif prev_record:
        changes = []

        try:
            delta = history_instance.diff_against(prev_record)

            for change in delta.changes:
                changes.append(
                    f"{change.field}: '{change.old}' → '{change.new}'"
                )

        except TypeError:
            excluded_fields = {
                "history_id",
                "history_date",
                "history_type",
                "history_user_id",
                "history_change_reason",
            }

            for field in history_instance._meta.fields:
                if field.name in excluded_fields:
                    continue

                old_val = getattr(prev_record, field.name, None)
                new_val = getattr(history_instance, field.name, None)

                if old_val != new_val:
                    changes.append(
                        f"{field.name}: '{old_val}' → '{new_val}'"
                    )

        changes_text = "\n".join(changes) if changes else "No field changes"

    else:
        changes_text = "No previous record"

    TrackChanges.objects.create(
        category=category,
        animal_id=animal_id,
        action=history_instance.history_type,
        changed_at=history_instance.history_date,
        changed_by=(
            get_user_initials(history_instance.history_user)
            if history_instance.history_user
            else None
        ),
        changes=changes_text,
    )