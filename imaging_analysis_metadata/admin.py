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
        "display_status",
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
        "frame_rate",
        "started_at",
        "completed_at",
        "display_output_resources",
    )

    @admin.display(description="Animal ID")
    def animal_id(self, obj):
        return obj.animal_id

    @admin.display(description="Status", ordering="status")
    def display_status(self, obj):
        if obj.status == AnalysisRun.StatusChoices.RUNNING:
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 6px;">'
                    '<span>{}</span>'
                    '<span style="'
                        'width: 12px;'
                        'height: 12px;'
                        'border: 2px solid rgba(255,255,255,0.35);'
                        'border-top-color: currentColor;'
                        'border-radius: 50%;'
                        'display: inline-block;'
                        'animation: analysis-spin 0.8s linear infinite;'
                        'flex-shrink: 0;'
                    '"></span>'
                '</span>',
                obj.get_status_display(),
            )

        return obj.get_status_display()

    @admin.display(description="Output Resource Path")
    def display_output_resources(self, obj):
        output_path = obj.output_path
        log_path = obj.output_log_path

        # ---------------------------------------------------------
        # Fallback for older AnalysisRun records where
        # output_log_path was not stored in the database.
        # ---------------------------------------------------------
        if not log_path and output_path:
            output_dir = Path(output_path)

            # First check the old log filename.
            old_log = output_dir / "pipeline_log.txt"

            if old_log.exists():
                log_path = str(old_log)

            else:
                # Otherwise look for the new timestamped run logs.
                run_logs = list(output_dir.glob("*_runlog.txt"))

                if run_logs:
                    # Use the most recently modified run log.
                    newest_log = max(
                        run_logs,
                        key=lambda path: path.stat().st_mtime,
                    )
                    log_path = str(newest_log)

        log_text = log_path or "Not available"
        output_text = output_path or "Not available"

        return format_html(
            '<div style="white-space: normal; min-width: 450px;">'

                '<div style="display: grid; '
                'grid-template-columns: max-content 1fr; '
                'column-gap: 5px; '
                'align-items: start;">'
                    '<strong>• Log:</strong>'
                    '<span style="overflow-wrap: anywhere;">{}</span>'
                '</div>'

                '<div style="height: 8px;"></div>'

                '<div style="display: grid; '
                'grid-template-columns: max-content 1fr; '
                'column-gap: 5px; '
                'align-items: start;">'
                    '<strong>• Suite2p:</strong>'
                    '<span style="overflow-wrap: anywhere;">{}</span>'
                '</div>'

            '</div>',
            log_text,
            output_text,
        )