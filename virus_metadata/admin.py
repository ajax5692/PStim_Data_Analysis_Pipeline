from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from animals_metadata.utils import get_user_initials
from .models import TrackChanges, Virus


@admin.register(Virus)
class VirusAdmin(SimpleHistoryAdmin):
    list_display = (
        "virus_id",
        "viral_construct",
        "titre",
        "location_in_fridge",
        "virus_owner",
    )

    list_filter = (
        "virus_owner",
    )

    search_fields = (
        "virus_id",
        "viral_construct",
        "titre",
        "location_in_fridge",
        "virus_owner",
    )

    ordering = (
        "virus_id",
    )


@admin.register(TrackChanges)
class TrackChangesAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "get_virus_id",
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

    @admin.display(description="Virus ID", ordering="animal_id")
    def get_virus_id(self, obj):
        return obj.animal_id

    @admin.display(description="Changed by", ordering="changed_by")
    def display_changed_by(self, obj):
        return get_user_initials(obj.changed_by)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

