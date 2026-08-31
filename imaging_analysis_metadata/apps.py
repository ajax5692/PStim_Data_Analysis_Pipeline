from django.apps import AppConfig


class ImagingAnalysisMetadataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "imaging_analysis_metadata"
    verbose_name = "IMAGING ANALYSIS METADATA"

    def ready(self):
        from . import signals  # noqa: F401

