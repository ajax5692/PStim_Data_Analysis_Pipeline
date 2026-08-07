from django import forms
from django.contrib import admin

from .models import Animal, ViralInjection, VisionCheck


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "animal_id",
        "owner",
        "sex",
        "genotype",
        "cage_id",
        "dob",
        "age_in_days",
        "status"
    )
    readonly_fields = ('age_in_days',)
    search_fields = ("mouse_id", "genotype", "cage_id", "sex", "owner")


# Custom Form for VisionCheck
class VisionCheckForm(forms.ModelForm):
    class Meta:
        model = VisionCheck
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change the display label in the dropdown to just animal_id
        self.fields['animal_id'].label_from_instance = lambda obj: obj.animal_id

@admin.register(VisionCheck)
class VisionCheckAdmin(admin.ModelAdmin):
    form = VisionCheckForm
    list_display = (
        "get_animal_id",
        "vision_test_type",
        "vision_test_result",
        "data_path"
    )
    # Define how you want the animal ID column to display
    @admin.display(description='Animal ID')
    def get_animal_id(self, obj):
        return f"{obj.animal_id.animal_id}"
    search_fields = ("mouse_id", "vision_test_result", "vision_test_type")
    
    
# Custom Form for ViralInjection
class ViralInjectionForm(forms.ModelForm):
    class Meta:
        model = ViralInjection
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change the display label in the dropdown to just animal_id
        self.fields['animal_id'].label_from_instance = lambda obj: obj.animal_id

@admin.register(ViralInjection)
class ViralInjectionAdmin(admin.ModelAdmin):
    form = ViralInjectionForm
    list_display = (
        "get_animal_id",
        "get_owner",
        "virus_name",
        "virus_construct",
        "injecting_person",
        "injection_date",
        "injection_site",
        "volume_ul",
        "notes",
        "expression_pattern"
    )
    # Define how you want the animal ID column to display
    @admin.display(description='Animal ID')
    def get_animal_id(self, obj):
        return f"{obj.animal_id.animal_id}"
    
    # Define how to get the Owner from the connected Animal model
    @admin.display(description='Owner')
    def get_owner(self, obj):
        return obj.animal_id.owner