from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import MouseBodyWeightRecord, TrackChanges, TrainingSession


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


@admin.register(MouseBodyWeightRecord)
class MouseBodyWeightRecordAdmin(SimpleHistoryAdmin):
    list_display = (
        "get_mouse_id",
        "get_owner",
        "date",
        "body_weight_g",
        "display_percent_body_weight",
        "notes",
    )

    list_filter = (
        "animal",
        "animal__owner",
        "date",
    )

    search_fields = (
        "animal__animal_id",
        "animal__owner",
        "notes",
    )

    ordering = (
        "-date",
        "animal",
    )

    readonly_fields = (
        "percent_body_weight",
    )

    @admin.display(description="Mouse ID", ordering="animal__animal_id")
    def get_mouse_id(self, obj):
        return obj.animal.animal_id if obj.animal else "-"

    @admin.display(description="Owner", ordering="animal__owner")
    def get_owner(self, obj):
        return obj.animal.owner if obj.animal else "-"

    @admin.display(description="% Body Weight Compared to Start", ordering="percent_body_weight")
    def display_percent_body_weight(self, obj):
        if obj.percent_body_weight is not None:
            return f"{obj.percent_body_weight:.1f} %"
        return "-"


from animals_metadata.utils import get_user_initials


@admin.register(TrackChanges)
class TrackChangesAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "animal_id",
        "action",
        "changed_at",
        "display_changed_by",
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

    @admin.display(description="Changed by", ordering="changed_by")
    def display_changed_by(self, obj):
        return get_user_initials(obj.changed_by)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False