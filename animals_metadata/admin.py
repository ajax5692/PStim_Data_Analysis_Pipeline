from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from animals_metadata.models import Animal, ViralInjection, VisionCheck


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
        "status"
    )
    readonly_fields = ('age_in_days',)
    search_fields = ("mouse_id", "genotype", "cage_id", "sex", "owner")


@admin.register(VisionCheck)
class VisionCheckAdmin(SimpleHistoryAdmin):
    list_display = (
        "get_animal_id",
        "vision_test_type",
        "vision_test_result",
        "data_path"
    )
    # Define how you want the animal ID column to display
    @admin.display(description='Animal ID')
    def get_animal_id(self, obj):
        return obj.animal_id
    search_fields = ("mouse_id", "vision_test_result", "vision_test_type")
    

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
        "expression_pattern"
    )
    # Define how you want the animal ID column to display
    @admin.display(description='Animal ID')
    def get_animal_id(self, obj):
        return obj.animal_id
    
    # Define how to get the Owner from the connected Animal model
    @admin.display(description='Owner')
    def get_owner(self, obj):
        return obj.animal_id.owner
    
    # Define how to get the Injecting Person from the connected Animal model
    @admin.display(description='Injecting Person')
    def get_inj_person(self, obj):
        return obj.injecting_person
    


Animal.history.model._meta.verbose_name_plural = "Entry History: Animals"
VisionCheck.history.model._meta.verbose_name_plural = "Entry History: Vision Checks"
ViralInjection.history.model._meta.verbose_name_plural = "Entry History: Viral Injections"


# Base Class for Read-Only Historical Logs
class BaseHistoryAdmin(admin.ModelAdmin):
    # Prevent manual editing of raw audit history entries
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register All History Models
@admin.register(Animal.history.model)
class AnimalHistoryAdmin(BaseHistoryAdmin):
    list_display = ("history_id", "animal_id", "history_type", "history_date", "history_user", "status")
    list_filter = ("history_type", "status", "genotype")
    search_fields = ("animal_id",)

@admin.register(VisionCheck.history.model)
class VisionCheckHistoryAdmin(BaseHistoryAdmin):
    list_display = ("history_id", "animal_id", "vision_test_type", "history_type", "history_date", "history_user")
    list_filter = ("history_type", "vision_test_type", "vision_test_result")
    search_fields = ("animal_id__animal_id",)

@admin.register(ViralInjection.history.model)
class ViralInjectionHistoryAdmin(BaseHistoryAdmin):
    list_display = ("history_id", "animal_id", "virus_name", "history_type", "history_date", "history_user")
    list_filter = ("history_type", "virus_name")
    search_fields = ("animal_id__animal_id",)