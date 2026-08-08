# animals_metadata/apps.py

from django.apps import AppConfig


class AnimalsMetadataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'animals_metadata'

    def ready(self):
        from django.contrib import admin
        
        # Save Django's original get_app_list method
        original_get_app_list = admin.AdminSite.get_app_list

        def custom_get_app_list(self, request, app_label=None):
            app_list = original_get_app_list(self, request, app_label)
            
            for app in app_list:
                if app['app_label'] == 'animals_metadata':
                    # Desired order for models in the sidebar
                    order = ['Animals', 'Viral Injections', 'Vision Check', 'Entry History']
                    
                    # Sort models based on the order list
                    app['models'].sort(
                        key=lambda x: order.index(x['name']) if x['name'] in order else 999
                    )
            return app_list

        # Override admin site get_app_list method dynamically
        admin.AdminSite.get_app_list = custom_get_app_list