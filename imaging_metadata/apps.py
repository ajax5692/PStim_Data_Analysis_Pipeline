from django.apps import AppConfig


class ImagingMetadataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "imaging_metadata"
    verbose_name = "IMAGING METADATA"

    def ready(self):
        from . import signals  # noqa: F401