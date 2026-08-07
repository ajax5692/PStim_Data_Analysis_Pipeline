from django import forms
from django.contrib import admin

from .models import Animal, VisionCheck


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "animal_id",
        "sex",
        "genotype",
        "cage_id",
        "dob",
        "age_in_days"
    )
    readonly_fields = ('age_in_days',)
    search_fields = ("mouse_id", "genotype", "cage_id", "sex")


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
        "animal_id",
         "vision_test_type",
        "vision_test_result"
    )
    search_fields = ("mouse_id", "vision_test_result", "vision_test_type")