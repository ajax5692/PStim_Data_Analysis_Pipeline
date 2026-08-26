from django import forms
from django.contrib import admin
from django.utils.html import format_html, format_html_join
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
        "display_data_path",
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
    
    @admin.display(description="Data Path", ordering="data_path")
    def display_data_path(self, obj):
        data_path = obj.data_path or "Not available"

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
            data_path,
            data_path,
        )


class ViralInjectionAdminForm(forms.ModelForm):
    class Meta:
        model = ViralInjection
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        # -------------------------------------------------
        # VIRUS 2
        # -------------------------------------------------
        virus_2 = cleaned_data.get("virus_id_2")
        volume_2 = cleaned_data.get("volume_nl_2")
        site_2 = cleaned_data.get("site_2")
        depth_2 = cleaned_data.get("depth_2")

        virus_2_values = (
            virus_2,
            volume_2,
            site_2,
            depth_2,
        )

        if any(value not in (None, "") for value in virus_2_values):
            if not virus_2:
                self.add_error(
                    "virus_id_2",
                    "Please select Virus ID 2.",
                )

            if volume_2 is None:
                self.add_error(
                    "volume_nl_2",
                    "Please enter Volume 2.",
                )

            if not site_2:
                self.add_error(
                    "site_2",
                    "Please select Injection Site 2.",
                )

            if depth_2 is None:
                self.add_error(
                    "depth_2",
                    "Please enter Depth 2.",
                )

        # -------------------------------------------------
        # VIRUS 3
        # -------------------------------------------------
        virus_3 = cleaned_data.get("virus_id_3")
        volume_3 = cleaned_data.get("volume_nl_3")
        site_3 = cleaned_data.get("site_3")
        depth_3 = cleaned_data.get("depth_3")

        virus_3_values = (
            virus_3,
            volume_3,
            site_3,
            depth_3,
        )

        if any(value not in (None, "") for value in virus_3_values):
            if not virus_3:
                self.add_error(
                    "virus_id_3",
                    "Please select Virus ID 3.",
                )

            if volume_3 is None:
                self.add_error(
                    "volume_nl_3",
                    "Please enter Volume 3.",
                )

            if not site_3:
                self.add_error(
                    "site_3",
                    "Please select Injection Site 3.",
                )

            if depth_3 is None:
                self.add_error(
                    "depth_3",
                    "Please enter Depth 3.",
                )

        return cleaned_data


@admin.register(ViralInjection)
class ViralInjectionAdmin(SimpleHistoryAdmin):
    form = ViralInjectionAdminForm

    list_display = (
        "get_animal_id",
        "get_owner",
        "display_virus_injections",
        "get_inj_person",
        "injection_date",
        "surgery_date",
        "get_surgery_person",
        "display_expression_mescfile_path",
        "notes",
    )

    list_filter = (
        "animal_id",
        "virus_id",
        "virus_id_2",
        "virus_id_3",
        "injecting_person",
        "site",
        "site_2",
        "site_3",
    )

    search_fields = (
        "animal_id__animal_id",
        "virus_id",
        "virus_id_2",
        "virus_id_3",
        "injecting_person",
        "site",
        "site_2",
        "site_3",
    )

    fieldsets = (
        (
            "Animal",
            {
                "fields": (
                    "animal_id",
                ),
            },
        ),
        (
            "Virus Injection 1",
            {
                "fields": (
                    (
                        "virus_id",
                        "volume_ul",
                        "site",
                        "depth",
                    ),
                ),
            },
        ),
        (
            "Virus Injection 2",
            {
                "fields": (
                    (
                        "virus_id_2",
                        "volume_nl_2",
                        "site_2",
                        "depth_2",
                    ),
                ),
            },
        ),
        (
            "Virus Injection 3",
            {
                "fields": (
                    (
                        "virus_id_3",
                        "volume_nl_3",
                        "site_3",
                        "depth_3",
                    ),
                ),
            },
        ),
        (
            "Injection Details",
            {
                "fields": (
                    "injection_date",
                    "injecting_person",
                ),
            },
        ),
        (
            "Surgery",
            {
                "fields": (
                    "surgery_date",
                    "surgery_person",
                ),
            },
        ),
        (
            "Other",
            {
                "fields": (
                    "expression",
                    "notes",
                ),
            },
        ),
    )

    @admin.display(description="Animal ID")
    def get_animal_id(self, obj):
        return obj.animal_id

    @admin.display(description="Owner")
    def get_owner(self, obj):
        return obj.animal_id.owner

    @admin.display(description="Virus / Volume / Site / Depth")
    def display_virus_injections(self, obj):
        injections = []

        # Virus 1
        if obj.virus_id:
            injections.append(
                (
                    obj.virus_id,
                    obj.volume_ul,
                    obj.site,
                    obj.depth,
                )
            )

        # Virus 2
        if obj.virus_id_2:
            injections.append(
                (
                    obj.virus_id_2,
                    obj.volume_nl_2,
                    obj.site_2,
                    obj.depth_2,
                )
            )

        # Virus 3
        if obj.virus_id_3:
            injections.append(
                (
                    obj.virus_id_3,
                    obj.volume_nl_3,
                    obj.site_3,
                    obj.depth_3,
                )
            )

        if not injections:
            return "-"

        return format_html_join(
            "",
            (
                '<div style="margin-bottom: 6px;">'
                '• <strong>{}</strong>'
                ' — {} nL'
                ' — {}'
                ' — {} μm'
                '</div>'
            ),
            injections,
        )

    @admin.display(description="Inj. Person")
    def get_inj_person(self, obj):
        return obj.injecting_person

    @admin.display(description="Sur. Person")
    def get_surgery_person(self, obj):
        return obj.surgery_person
    
    @admin.display(description="Expression (Checkup MESC File)", ordering="expression")
    def display_expression_mescfile_path(self, obj):
        expression = obj.expression or "Not available"

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
            expression,
            expression,
        )


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