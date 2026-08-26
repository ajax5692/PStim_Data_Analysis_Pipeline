from django.contrib import admin
from django.utils.html import format_html

from .models import ImagingSession


@admin.register(ImagingSession)
class ImagingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "animal",
        "acquisition_date",
        "imaging_region",
        "measurement_unit_ranges",
        "display_mesc_file_path",
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

    @admin.display(description="MESC File Path", ordering="mesc_file_path")
    def display_mesc_file_path(self, obj):
        mesc_path = obj.mesc_file_path or "Not available"

        return format_html(
            '<div style="display: grid; '
            'grid-template-columns: max-content 1fr; '
            'column-gap: 6px; '
            'align-items: start;">'

                '<button type="button" '
                'class="pstim-copy-button" '
                'data-copy-text="{}" '
                'title="Copy MESC file path" '
                'aria-label="Copy MESC file path">'

                    '<svg '
                    'width="16" '
                    'height="16" '
                    'viewBox="0 0 24 24" '
                    'fill="none" '
                    'stroke="currentColor" '
                    'stroke-width="2" '
                    'stroke-linecap="round" '
                    'stroke-linejoin="round" '
                    'aria-hidden="true">'

                        '<rect '
                        'x="8" '
                        'y="8" '
                        'width="12" '
                        'height="12" '
                        'rx="2">'
                        '</rect>'

                        '<path '
                        'd="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2">'
                        '</path>'

                    '</svg>'

                '</button>'

                '<span style="overflow-wrap: anywhere;">'
                '{}'
                '</span>'

            '</div>',
            mesc_path,
            mesc_path,
        )