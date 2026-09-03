from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from animals_metadata.utils import build_history_diff_text, get_user_initials
from .models import ImagingSession, TrackChanges


@receiver(post_create_historical_record)
def create_track_change(sender, instance, history_instance, **kwargs):
    model = instance.__class__

    if model is not ImagingSession:
        return

    category = TrackChanges.CategoryChoices.IMAGING_SESSION

    try:
        animal_id = instance.animal.animal_id
    except Exception:
        animal_id = getattr(history_instance, "animal_id", None)
        if animal_id is not None:
            animal_id = str(animal_id)

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
