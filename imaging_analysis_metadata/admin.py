from pathlib import Path

from django.contrib import admin
from django.utils.html import format_html

from .models import AnalysisRun


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "animal_id",
        "imaging_session",
        "status",
        "frame_rate",
        "created_at",
        "started_at",
        "completed_at",
        "display_output_resources",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "imaging_session__animal__animal_id",
        "imaging_session__mesc_file_path",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
    )

    @admin.display(description="Animal ID")
    def animal_id(self, obj):
        return obj.animal_id

    @admin.display(description="Output Resource Path")
    def display_output_resources(self, obj):
        output_path = obj.output_path

        # Use the stored log path if available
        log_path = obj.output_log_path

        # Fallback for older analysis runs where the log path
        # was not yet stored in the database
        if not log_path and output_path:
            candidate_log = Path(output_path) / "pipeline_log.txt"

            if candidate_log.exists():
                log_path = str(candidate_log)

        log_text = log_path or "Not available"
        output_text = output_path or "Not available"

        return format_html(
            '<div style="white-space: normal; min-width: 450px;">'
            '• <strong>Log:</strong> {}<br>'
            '• <strong>Suite2p:</strong> {}'
            '</div>',
            log_text,
            output_text,
        )