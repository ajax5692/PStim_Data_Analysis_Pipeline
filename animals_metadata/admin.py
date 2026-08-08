from django.contrib import admin
from django.utils.safestring import mark_safe
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
    def get_changes(self, obj):
        prev_record = obj.prev_record
        
        if not prev_record:
            return mark_safe('<span style="color: #27ae60; font-weight: bold;">Initial Entry</span>')
        
        if obj.history_type == '-':
            return mark_safe('<span style="color: #c0392b; font-weight: bold;">Deleted Record</span>')

        changes = []
        try:
            delta = obj.diff_against(prev_record)
            for change in delta.changes:
                changes.append(
                    f"<b>{change.field}</b>: "
                    f"<span style='color: #c0392b;'>'{change.old}'</span> → "
                    f"<span style='color: #27ae60; font-weight: bold;'>'{change.new}'</span>"
                )
        except TypeError:
            excluded_fields = {'history_id', 'history_date', 'history_type', 'history_user_id', 'history_change_reason'}
            for field in obj._meta.fields:
                if field.name in excluded_fields:
                    continue
                old_val = getattr(prev_record, field.name, None)
                new_val = getattr(obj, field.name, None)
                if old_val != new_val:
                    changes.append(
                        f"<b>{field.name}</b>: "
                        f"<span style='color: #c0392b;'>'{old_val}'</span> → "
                        f"<span style='color: #27ae60; font-weight: bold;'>'{new_val}'</span>"
                    )

        if not changes:
            return "No field changes"
            
        # FIX: Replace format_html with mark_safe here
        return mark_safe("<br>".join(changes))

    get_changes.short_description = "Modified Fields"


# Register All History Models
@admin.register(Animal.history.model)
class AnimalHistoryAdmin(BaseHistoryAdmin):
    list_display = ("history_id", "animal_id", "history_type", "history_date", "get_changes", "history_user")
    list_filter = ("history_type",)
    search_fields = ("animal_id",)

@admin.register(VisionCheck.history.model)
class VisionCheckHistoryAdmin(BaseHistoryAdmin):
    list_display = ("history_id", "animal_id", "history_type", "history_date", "get_changes", "history_user")
    list_filter = ("history_type",)
    search_fields = ("animal_id__animal_id",)

@admin.register(ViralInjection.history.model)
class ViralInjectionHistoryAdmin(BaseHistoryAdmin):
    list_display = ("history_id", "animal_id", "history_type", "history_date", "get_changes", "history_user")
    list_filter = ("history_type",)
    search_fields = ("animal_id__animal_id",)