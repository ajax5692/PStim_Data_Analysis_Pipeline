from django.apps import AppConfig


class TrainingMetadataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "training_metadata"
    verbose_name = "TRAINING METADATA"

    def ready(self):
        from . import signals  # noqa: F401

