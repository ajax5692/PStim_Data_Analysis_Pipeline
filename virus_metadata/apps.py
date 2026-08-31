from django.apps import AppConfig


class VirusMetadataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "virus_metadata"
    verbose_name = "VIRUS METADATA"

    def ready(self):
        from . import signals  # noqa: F401

