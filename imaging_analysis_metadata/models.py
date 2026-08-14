from django.db import models

from .utils import parse_unit_ranges


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
    
    frame_rate = models.FloatField(
        blank=True,
        null=True,
        help_text="Frame rate detected by the imaging analysis pipeline (Hz).",
    )
    
    default_diameter = models.FloatField(
        default=12.0,
        help_text="Expected cell diameter used for Suite2p cell detection.",
    )

    tau = models.FloatField(
        default=0.7,
        help_text="Calcium indicator decay time constant used for analysis.",
    )
    
    suite2p_version = models.CharField(
        max_length=100,
        blank=True,
        help_text="Suite2p version used for this analysis run.",
    )

    suite2p_git_commit = models.CharField(
        max_length=64,
        blank=True,
        help_text="Git commit hash of the customized Suite2p code used for this run.",
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
    
    parameter_log_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to the Suite2p parameter log generated for this analysis run.",
    )

    notes = models.TextField(
        blank=True,
    )

    @property
    def animal_id(self):
        return self.imaging_session.animal.animal_id
    
    @property
    def unit_indices(self):
        return parse_unit_ranges(
            self.imaging_session.measurement_unit_ranges
        )

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