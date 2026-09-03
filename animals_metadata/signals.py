from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from .models import Animal, TrackChanges, ViralInjection, VisionCheck
from .utils import build_history_diff_text, get_user_initials


@receiver(post_create_historical_record)
def create_track_change(sender, instance, history_instance, **kwargs):
    model = instance.__class__

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