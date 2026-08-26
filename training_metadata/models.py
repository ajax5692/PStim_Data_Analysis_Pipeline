from django.db import models
from simple_history.models import HistoricalRecords


class TrainingSession(models.Model):
    animal = models.ForeignKey(
        "animals_metadata.Animal",
        on_delete=models.PROTECT,
        related_name="training_sessions",
    )

    training_date = models.DateField()

    bpod_file_path = models.CharField(
        max_length=500,
        help_text="Path to the source .mesc file.",
    )

    training_unit_range = models.CharField(
        max_length=200,
        help_text="Example: 10:21,25:55",
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Training Session"
        verbose_name_plural = "Training Sessions"
        ordering = ["-training_date"]

    def __str__(self):
        return f"{self.animal.animal_id} - {self.training_date}"


class TrackChanges(models.Model):

    class CategoryChoices(models.TextChoices):
        TRAINING_SESSION = "training_session", "Training Session"

    class ActionChoices(models.TextChoices):
        CREATED = "+", "Created"
        UPDATED = "~", "Updated"
        DELETED = "-", "Deleted"

    category = models.CharField(
        max_length=30,
        choices=CategoryChoices.choices,
    )

    animal_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    action = models.CharField(
        max_length=1,
        choices=ActionChoices.choices,
    )

    changed_at = models.DateTimeField()

    changed_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    changes = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Track Change"
        verbose_name_plural = "Track Changes"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.animal_id}"