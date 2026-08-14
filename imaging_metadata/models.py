from django.db import models

from .validators import validate_measurement_unit_ranges


class ImagingSession(models.Model):
    animal = models.ForeignKey(
        "animals_metadata.Animal",
        on_delete=models.PROTECT,
        related_name="imaging_sessions",
    )

    acquisition_date = models.DateField()

    imaging_region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    mesc_file_path = models.CharField(
        max_length=500,
        help_text="Path to the source .mesc file.",
    )

    measurement_unit_ranges = models.CharField(
        max_length=200,
        validators=[validate_measurement_unit_ranges],
        help_text="Example: 10:21,25:55",
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Imaging Session"
        verbose_name_plural = "Imaging Sessions"
        ordering = ["-acquisition_date"]

    def __str__(self):
        return f"{self.animal.animal_id} - {self.acquisition_date}"