from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from animals_metadata.utils import get_user_initials
from .models import AnalysisRun, TrackChanges


@receiver(post_create_historical_record)
def create_track_change(sender, instance, history_instance, **kwargs):

    model = instance.__class__

    if model is not AnalysisRun:
        return

    category = TrackChanges.CategoryChoices.ANALYSIS_RUN

    try:
        animal_id = instance.animal_id
    except Exception:
        animal_id = None

    # Build human-readable change description
    prev_record = history_instance.prev_record

    if history_instance.history_type == "+":
        changes_text = "Initial Entry"

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

