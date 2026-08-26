from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import TrackChanges, TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(SimpleHistoryAdmin):
    list_display = (
        "animal",
        "training_date",
        "bpod_file_path",
        "training_unit_range",
        "notes",
    )

    list_filter = (
        "animal",
        "training_date",
    )

    search_fields = (
        "animal__animal_id",
        "bpod_file_path",
        "training_unit_range",
        "notes",
    )

    ordering = ("-training_date",)


@admin.register(TrackChanges)
class TrackChangesAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "animal_id",
        "action",
        "changed_at",
        "changed_by",
        "changes",
    )

    list_filter = (
        "category",
        "action",
        "changed_at",
    )

    search_fields = (
        "animal_id",
        "changed_by",
        "changes",
    )

    ordering = (
        "-changed_at",
    )

    readonly_fields = (
        "category",
        "animal_id",
        "action",
        "changed_at",
        "changed_by",
        "changes",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False