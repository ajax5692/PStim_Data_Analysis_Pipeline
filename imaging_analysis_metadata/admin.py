from django.contrib import admin

from .models import AnalysisRun


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "animal_id",
        "imaging_session",
        "status",
        "frame_rate",
        "default_diameter",
        "tau",
        "created_at",
        "started_at",
        "completed_at",
        "parameter_log_path",
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