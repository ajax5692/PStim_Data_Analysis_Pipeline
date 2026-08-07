from django import forms
from django.contrib import admin

from .models import Animal, VisionCheck


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "animal_id",
        "owner",
        "sex",
        "genotype",
        "cage_id",
        "dob",
        "age_in_days"
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
        "vision_test_result"
    )
    # Define how you want the animal ID column to display
    @admin.display(description='Animal ID')
    def get_animal_id(self, obj):
        return f"{obj.animal_id.animal_id} - {obj.animal_id.owner} - {obj.animal_id.genotype} - {obj.animal_id.sex}"
    search_fields = ("mouse_id", "vision_test_result", "vision_test_type")