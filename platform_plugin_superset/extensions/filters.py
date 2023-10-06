"""
Open edX Filters needed for Superset integration.
"""
import pkg_resources
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment
import os
from crum import get_current_user

from supersetapiclient.client import SupersetClient

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "superset"


def load_guest_token(user, course):
    superset_host = "http://superset:8088/"
    superset_username = "9T2Oz1iw0455"
    superset_password = "SMVWlysdQH1l7NFQMKouJ9NO"
    dashboard_id = "776a7457-ffb1-4aa1-802e-17e8a00fbcb9"

    client = SupersetClient(
        host=superset_host,
        username=superset_username,
        password=superset_password,
    )

    course_run = course.children[0].course_key.run

    data = {
        "user": {
            "username": user.username,
            "first_name": "John",
            "last_name": "Doe",
        },
        "resources": [
            {"type": "dashboard", "id": dashboard_id}
        ],
        "rls": [
            {"clause": f"org = '{(course.org)}'"},
            {"clause": f"course_name = '{(course.display_name)}'"},
            {"clause": f"course_run = '{(course_run)}'"},
            ]
    }

    response = client.session.post(
        url=superset_host + "api/v1/security/guest_token/",
        json=data,
        headers={"Content-Type": "application/json"},
    )

    return response.json()["token"], dashboard_id


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
        superset_token, dashboard_id = load_guest_token(user, course)
        context.update(
            {
                "superset_token": superset_token,
                "dashboard_id": dashboard_id,
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
