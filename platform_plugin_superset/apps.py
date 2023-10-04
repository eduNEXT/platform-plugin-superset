"""
platform_plugin_superset Django application initialization.
"""

from django.apps import AppConfig


class PlatformPluginSupersetConfig(AppConfig):
    """
    Configuration for the platform_plugin_superset Django application.
    """

    name = "platform_plugin_superset"

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }

    def ready(self):
        """Load modules of platform_plugin_superset."""
        from platform_plugin_superset.extensions import (  # pylint: disable=unused-import, import-outside-toplevel
            filters,
        )
