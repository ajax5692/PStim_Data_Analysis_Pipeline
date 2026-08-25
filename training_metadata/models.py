from django.db import models


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

    class Meta:
        verbose_name = "Training Session"
        verbose_name_plural = "Training Sessions"
        ordering = ["-training_date"]

    def __str__(self):
        return f"{self.animal.animal_id} - {self.acquisition_date}"