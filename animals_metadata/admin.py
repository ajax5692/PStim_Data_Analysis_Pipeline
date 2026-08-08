from django.contrib import admin

from animals_metadata.models import Animal, ViralInjection, VisionCheck


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
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
class VisionCheckAdmin(admin.ModelAdmin):
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
class ViralInjectionAdmin(admin.ModelAdmin):
    list_display = (
        "get_animal_id",
        "get_owner",
        "virus_name",
        "virus_construct",
        "injecting_person",
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