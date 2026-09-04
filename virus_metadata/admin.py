from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from animals_metadata.utils import BaseTrackChangesAdmin
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
class TrackChangesAdmin(BaseTrackChangesAdmin):
    list_display = (
        "category",
        "get_virus_id",
        "action",
        "changed_at",
        "display_changed_by",
        "changes",
    )

    @admin.display(description="Virus ID", ordering="animal_id")
    def get_virus_id(self, obj):
        return obj.animal_id
