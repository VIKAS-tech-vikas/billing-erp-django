from django.apps import AppConfig
import importlib

class ItemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'items'

    def ready(self):
        """
        Ensure custom template filters are registered on app load.
        """
        try:
            importlib.import_module('items.templatetags.custom_filters')
        except Exception as e:
            print(f"⚠️ Could not import custom_filters: {e}")
