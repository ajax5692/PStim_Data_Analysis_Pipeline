from typing import Any

from django.db import models
from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from .models import Animal, TrackChanges, ViralInjection, VisionCheck
from .utils import record_track_change


@receiver(post_create_historical_record)
def create_track_change(
    sender: Any,
    instance: models.Model,
    history_instance: Any,
    **kwargs: Any,
) -> None:
    """
    Record an audit trail entry in TrackChanges upon historical record creation.
    """
    model = instance.__class__

    if model is Animal:
        category = TrackChanges.CategoryChoices.ANIMAL
        animal_id = getattr(history_instance, "animal_id", "")

    elif model is VisionCheck:
        category = TrackChanges.CategoryChoices.VISION_CHECK
        animal_id = str(getattr(instance, "animal_id", ""))

    elif model is ViralInjection:
        category = TrackChanges.CategoryChoices.VIRAL_INJECTION
        animal_id = str(getattr(instance, "animal_id", ""))

    else:
        return

    record_track_change(
        track_changes_model=TrackChanges,
        category=category,
        entity_id=animal_id,
        history_instance=history_instance,
    )