from django.db import models


class AnalysisRun(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    imaging_session = models.ForeignKey(
        "imaging_metadata.ImagingSession",
        on_delete=models.PROTECT,
        related_name="analysis_runs",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    output_path = models.CharField(
        max_length=500,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    @property
    def animal_id(self):
        return self.imaging_session.animal.animal_id

    class Meta:
        verbose_name = "Analysis Run"
        verbose_name_plural = "Analysis Runs"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.animal_id} - "
            f"{self.imaging_session.acquisition_date} - "
            f"Run {self.pk or 'New'}"
        )