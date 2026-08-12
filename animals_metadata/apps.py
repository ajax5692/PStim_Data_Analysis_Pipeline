from django.apps import AppConfig


class AnimalsMetadataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "animals_metadata"
    verbose_name = "ANIMALS METADATA"

    def ready(self):
        from django.contrib import admin

        original_get_app_list = admin.AdminSite.get_app_list

        def custom_get_app_list(self, request, app_label=None):
            app_list = original_get_app_list(
                self,
                request,
                app_label,
            )

            # Order models inside Animals Metadata
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

            # Order the apps in the Django admin sidebar
            app_order = {
                "animals_metadata": 0,
                "imaging_metadata": 1,
                "auth": 2,
            }

            app_list.sort(
                key=lambda app: app_order.get(
                    app["app_label"],
                    999,
                )
            )

            return app_list

        admin.AdminSite.get_app_list = custom_get_app_list

        # Load signals when Django has finished loading the app registry
        from . import signals  # noqa: F401