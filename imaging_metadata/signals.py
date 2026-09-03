from typing import Any

from django.db import models
from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from animals_metadata.utils import record_track_change
from .models import ImagingSession, TrackChanges


@receiver(post_create_historical_record)
def create_track_change(
    sender: Any,
    instance: models.Model,
    history_instance: Any,
    **kwargs: Any,
) -> None:
    """
    Record an audit trail entry in TrackChanges upon historical record creation for ImagingSession.
    """
    model = instance.__class__

    if model is not ImagingSession:
        return

    try:
        animal_id = instance.animal.animal_id
    except Exception:
        animal_id = getattr(history_instance, "animal_id", None)
        if animal_id is not None:
            animal_id = str(animal_id)

    record_track_change(
        track_changes_model=TrackChanges,
        category=TrackChanges.CategoryChoices.IMAGING_SESSION,
        entity_id=animal_id,
        history_instance=history_instance,
    )
