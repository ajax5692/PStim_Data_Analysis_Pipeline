from typing import Any

from django.db import models
from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from animals_metadata.utils import record_track_change
from .models import TrackChanges, Virus


@receiver(post_create_historical_record)
def create_track_change(
    sender: Any,
    instance: models.Model,
    history_instance: Any,
    **kwargs: Any,
) -> None:
    """
    Record an audit trail entry in TrackChanges upon historical record creation for Virus.
    """
    model = instance.__class__

    if model is not Virus:
        return

    animal_id = getattr(instance, "virus_id", getattr(history_instance, "virus_id", None))

    record_track_change(
        track_changes_model=TrackChanges,
        category=TrackChanges.CategoryChoices.VIRUS,
        entity_id=animal_id,
        history_instance=history_instance,
    )
