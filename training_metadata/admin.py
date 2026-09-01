from django import forms
from django.contrib import admin
from django.db import models
from simple_history.admin import SimpleHistoryAdmin

from animals_metadata.utils import get_user_initials
from .models import BodyWeightEntry, MouseBodyWeight, TrackChanges, TrainingSession


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


class BodyWeightEntryInline(admin.TabularInline):
    model = BodyWeightEntry
    extra = 0
    fields = (
        "date",
        "body_weight_g",
        "display_percent_body_weight",
        "notes",
    )
    readonly_fields = (
        "display_percent_body_weight",
    )
    formfield_overrides = {
        models.FloatField: {
            "widget": forms.NumberInput(attrs={"min": "0", "step": "0.1"}),
        },
    }

    @admin.display(description="% Body Weight Compared to Start")
    def display_percent_body_weight(self, obj):
        if obj and obj.percent_body_weight is not None:
            return f"{obj.percent_body_weight:.1f} %"
        return "-"


@admin.register(MouseBodyWeight)
class MouseBodyWeightAdmin(SimpleHistoryAdmin):
    change_form_template = "admin/training_metadata/mousebodyweight/change_form.html"
    inlines = [BodyWeightEntryInline]

    list_display = (
        "get_animal_id",
        "get_owner",
    )

    list_filter = (
        "animal__owner",
    )

    search_fields = (
        "animal__animal_id",
        "animal__owner",
    )

    ordering = (
        "animal__animal_id",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "animal",
                    "get_owner_display",
                ),
            },
        ),
    )

    readonly_fields = (
        "get_owner_display",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("animal",)
        return self.readonly_fields

    @admin.display(description="Animal ID", ordering="animal__animal_id")
    def get_animal_id(self, obj):
        return obj.animal.animal_id if obj.animal else "-"

    @admin.display(description="Owner", ordering="animal__owner")
    def get_owner(self, obj):
        return obj.animal.owner if obj.animal else "-"

    @admin.display(description="Owner")
    def get_owner_display(self, obj):
        if obj and obj.animal:
            owner_label = obj.animal.get_owner_display() if hasattr(obj.animal, "get_owner_display") else obj.animal.owner
            return f"{owner_label} ({obj.animal.owner})"
        return "-"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_percentages()


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
