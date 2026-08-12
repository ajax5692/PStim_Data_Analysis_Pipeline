from django.apps import AppConfig


class AnimalsMetadataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "animals_metadata"
    verbose_name = 'ANIMALS METADATA'

    def ready(self):
        from django.contrib import admin

        original_get_app_list = admin.AdminSite.get_app_list

        def custom_get_app_list(self, request, app_label=None):
            app_list = original_get_app_list(
                self,
                request,
                app_label,
            )

            for app in app_list:
                if app["app_label"] == "animals_metadata":
                    order = [
                        "Animals",
                        "Viral Injections",
                        "Vision Check",
                        "Track Changes",
                    ]

                    app["models"].sort(
                        key=lambda x: (
                            order.index(x["name"])
                            if x["name"] in order
                            else 999
                        )
                    )

            return app_list

        admin.AdminSite.get_app_list = custom_get_app_list

        # Must stay inside ready()
        from . import signals  # noqa: F401