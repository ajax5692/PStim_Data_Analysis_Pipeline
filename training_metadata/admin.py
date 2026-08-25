from django.contrib import admin

from .models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "animal_id",
        "training_date",
        "bpod_file_path",
        "training_unit_range",
        "notes",
    )

    list_filter = (
        "animal_id",
    )

    search_fields = (
        "traing_session__animal__animal_id",
    )

    #ordering = ("-created_at",)