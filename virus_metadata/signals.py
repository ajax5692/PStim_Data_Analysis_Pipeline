from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from animals_metadata.utils import build_history_diff_text, get_user_initials
from .models import TrackChanges, Virus


@receiver(post_create_historical_record)
def create_track_change(sender, instance, history_instance, **kwargs):
    model = instance.__class__

    if model is not Virus:
        return

    category = TrackChanges.CategoryChoices.VIRUS
    animal_id = getattr(instance, "virus_id", getattr(history_instance, "virus_id", None))
    changes_text = build_history_diff_text(history_instance)

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
