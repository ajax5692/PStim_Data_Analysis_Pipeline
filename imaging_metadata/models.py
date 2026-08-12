from django.db import models


class ImagingSession(models.Model):
    animal_identifier = models.CharField(
        max_length=100,
        help_text="Animal or subject identifier used for this imaging session.",
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
        help_text="Example: 10:21,25:55",
    )

    number_of_planes = models.PositiveIntegerField()

    notes = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Imaging Session"
        verbose_name_plural = "Imaging Sessions"
        ordering = ["-acquisition_date"]

    def __str__(self):
        return f"{self.animal_identifier} - {self.acquisition_date}"