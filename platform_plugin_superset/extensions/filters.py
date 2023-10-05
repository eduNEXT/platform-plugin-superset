"""
Open edX Filters needed for Superset integration.
"""
import pkg_resources
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "superset"

ASSET_CONFIG = {
    "title": getattr(settings, "SUPERSET_TITLE", "Superset"),
    "asset_type": getattr(settings, "SUPERSET_ASSET_TYPE", "slice"),
    "asset_id": getattr(settings, "SUPERSET_ASSET_ID", "mjRp3DX3EYQ"),
    "extra_url_params": getattr(settings, "SUPERSET_EXTRA_URL_PARAMS", {}),
    "superset_url": getattr(settings, "SUPERSET_URL", ""),
}

def process_config(config):
    if config.get("asset_type") == "dashboard":
        config["iframe_url"] = "{superset_url}/superset/dashboard/{asset_id}?standalone=3&show_filters=0&expand_filters=0".format(
            **config
        )
    if config.get("asset_type") == "slice":
        config["iframe_url"] = "{superset_url}/superset/explore/p/{asset_id}?standalone=1".format(
            **config
        )

    for extra_url_param in config["extra_url_params"]:
        config["iframe_url"] += "&{}={}".format(
            extra_url_param, config["extra_url_params"][extra_url_param]
        )

    return config



class AddSupersetTab(PipelineStep):
    """Add superset tab to instructor dashboard."""

    def run_filter(self, context, template_name):  # pylint: disable=arguments-differ, unused-argument
        """Execute filter that modifies the instructor dashboard context.
        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
        """
        course = context["course"]
        context.update(
            {
                "superset_config": process_config(ASSET_CONFIG),
            }
        )
        template = Template(self.resource_string("static/html/superset.html"))

        html = template.render(Context(context))
        frag = Fragment(html)

        frag.add_css(self.resource_string("static/css/superset.css"))
        frag.add_javascript(self.resource_string("static/js/superset.js"))

        section_data = {
            "fragment": frag,
            "section_key": BLOCK_CATEGORY,
            "section_display_name": "Superset",
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)
        return {
            "context": context,
        }

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string("platform_plugin_superset", path)
        return data.decode("utf8")
