from django.contrib import admin

from .models import ImagingSession


@admin.register(ImagingSession)
class ImagingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "animal_identifier",
        "acquisition_date",
        "imaging_region",
        "measurement_unit_ranges",
        "number_of_planes",
    )

    list_filter = (
        "acquisition_date",
        "imaging_region",
        "number_of_planes",
    )

    search_fields = (
        "animal_identifier",
        "imaging_region",
        "mesc_file_path",
        "measurement_unit_ranges",
    )

    ordering = ("-acquisition_date",)