from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from animals_metadata.models import (
    Animal,
    TrackChanges,
    ViralInjection,
    VisionCheck,
)


@admin.register(Animal)
class AnimalAdmin(SimpleHistoryAdmin):
    list_display = (
        "animal_id",
        "owner",
        "sex",
        "genotype",
        "cage_id",
        "ogr_id",
        "project_id",
        "dob",
        "age_in_days",
        "status",
    )

    list_filter = (
        "status",
        "sex",
        "owner",
        "genotype",
        "project_id",
    )

    readonly_fields = (
        "age_in_days",
    )

    search_fields = (
        "animal_id",
        "genotype",
        "cage_id",
        "sex",
        "owner",
    )


@admin.register(VisionCheck)
class VisionCheckAdmin(SimpleHistoryAdmin):
    list_display = (
        "get_animal_id",
        "vision_test_type",
        "vision_test_result",
        "data_path",
    )

    list_filter = (
        "vision_test_type",
        "vision_test_result",
        "animal_id",
    )

    search_fields = (
        "animal_id__animal_id",
        "vision_test_result",
        "vision_test_type",
    )

    @admin.display(description="Animal ID")
    def get_animal_id(self, obj):
        return obj.animal_id


@admin.register(ViralInjection)
class ViralInjectionAdmin(SimpleHistoryAdmin):
    list_display = (
        "get_animal_id",
        "get_owner",
        "virus_name",
        "virus_construct",
        "get_inj_person",
        "injection_date",
        "injection_site",
        "volume_ul",
        "surgery_date",
        "surgery_person",
        "notes",
        "expression_pattern",
    )

    list_filter = (
        "animal_id",
        "virus_name",
        "virus_construct",
        "injecting_person",
        "injection_date",
        "injection_site",
        "surgery_date",
        "surgery_person",
        "expression_pattern",
    )

    search_fields = (
        "animal_id__animal_id",
        "virus_name",
        "virus_construct",
        "injecting_person",
        "surgery_person",
    )

    @admin.display(description="Animal ID")
    def get_animal_id(self, obj):
        return obj.animal_id

    @admin.display(description="Owner")
    def get_owner(self, obj):
        return obj.animal_id.owner

    @admin.display(description="Injecting Person")
    def get_inj_person(self, obj):
        return obj.injecting_person


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