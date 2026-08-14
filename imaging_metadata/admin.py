from django.contrib import admin

from .models import ImagingSession


@admin.register(ImagingSession)
class ImagingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "animal",
        "acquisition_date",
        "imaging_region",
        "measurement_unit_ranges",
        "mesc_file_path",
    )

    list_filter = (
        "acquisition_date",
        "imaging_region",
    )

    search_fields = (
        "animal__animal_id",
        "imaging_region",
        "mesc_file_path",
        "measurement_unit_ranges",
    )

    ordering = ("-acquisition_date",)