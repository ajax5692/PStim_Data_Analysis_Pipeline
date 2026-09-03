"""
Custom template context processors for PStim_DAP.
"""

from typing import Any, Dict
from django.apps import apps
from django.http import HttpRequest


def enabled_apps(request: HttpRequest) -> Dict[str, Any]:
    """
    Expose active INSTALLED_APPS to all templates dynamically.

    Returns a dictionary structured as:
        {
            "installed_apps": {
                "animals_metadata": True,
                "virus_metadata": True,
                "imaging_metadata": True,
                ...
            }
        }
    """
    return {
        "installed_apps": {
            app_config.name: True for app_config in apps.get_app_configs()
        }
    }

