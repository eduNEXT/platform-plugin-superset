"""
Open edX Filters needed for Superset integration.
"""
import os

import pkg_resources
from crum import get_current_user
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from supersetapiclient.client import SupersetClient
from web_fragments.fragment import Fragment

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "superset"


def generate_guest_token(user, course):
    """
    Generate a Superset guest token for the user.

    Args:
        user: User object.
        course: Course object.

    Returns:
        tuple: Superset guest token and dashboard id.
        or None, exception if Superset is missconfigured or cannot generate guest token.
    """
    superset_config = getattr(settings, "SUPERSET_CONFIG", {})
    superset_internal_host = superset_config.get("service_url", "http://superset:8088/")
    superset_username = superset_config.get("username")
    superset_password = superset_config.get("password")

    instructor_dashboard_config = getattr(settings, "SUPERSET_INSTRUCTOR_DASHBOARD", {})
    dashboard_id = instructor_dashboard_config.get("dashboard_uuid")

    try:
        client = SupersetClient(
            host=superset_internal_host,
            username=superset_username,
            password=superset_password,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return None, exc

    course_run = course.children[0].course_key.run

    data = {
        "user": {
            "username": user.username,
            "first_name": "John",
            "last_name": "Doe",
        },
        "resources": [{"type": "dashboard", "id": dashboard_id}],
        "rls": [
            {"clause": f"org = '{(course.org)}'"},
            {"clause": f"course_name = '{(course.display_name)}'"},
            {"clause": f"course_run = '{(course_run)}'"},
        ],
    }

    try:
        response = client.session.post(
            url=f"{superset_internal_host}api/v1/security/guest_token/",
            json=data,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        token = response.json()["token"]

        return token, dashboard_id
    except Exception as exc:  # pylint: disable=broad-except
        return None, exc


class AddSupersetTab(PipelineStep):
    """Add superset tab to instructor dashboard."""

    def run_filter(
        self, context, template_name
    ):  # pylint: disable=arguments-differ, unused-argument
        """Execute filter that modifies the instructor dashboard context.
        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
        """
        course = context["course"]

        user = get_current_user()
        superset_token, dashboard_id = generate_guest_token(user, course)

        if superset_token:
            context.update(
                {
                    "superset_token": superset_token,
                    "dashboard_id": dashboard_id,
                    "superset_url": settings.SUPERSET_CONFIG.get("host"),
                }
            )
        else:
            context.update(
                {
                    "error_message": "Superset is not configured properly. Please contact your system administrator.",
                    "exception": dashboard_id,
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
