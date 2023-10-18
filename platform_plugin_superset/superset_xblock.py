"""XBlock to embed a Superset dashboards in Open edX."""
from __future__ import annotations

import logging
from typing import Tuple

import pkg_resources
from django.utils import translation
from django.conf import settings
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import List, Scope, String
from xblockutils.resources import ResourceLoader

import json

from platform_plugin_superset.extensions.filters import update_context
from platform_plugin_superset.utils import _

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


@XBlock.wants("user")
@XBlock.needs("i18n")
class SupersetXBlock(XBlock):
    """
    Superset XBlock provides a way to embed dashboards from Superset in a course.
    """

    display_name = String(
        display_name=_("Display name"),
        help=_("Display name"),
        default="Superset Dashboard",
        scope=Scope.settings,
    )

    superset_internal_url = String(
        display_name=_("Superset URL"),
        help=_("Superset internal URL to generate authentication information."
               "Contact with your Open edX operator for more information."
               ),
        default="http://superset:8088/",
        scope=Scope.settings,
    )

    superset_url = String(
        display_name=_("Superset URL"),
        help=_("Superset URL to embed the dashboard."),
        default="http://superset.local.overhang.io:8088/",
        scope=Scope.settings,
    )

    superset_username = String(
        display_name=_("Superset Username"),
        help=_("Superset Username"),
        default="",
        scope=Scope.settings,
    )

    superset_password = String(
        display_name=_("Superset Password"),
        help=_("Superset Password"),
        default="",
        scope=Scope.settings,
    )

    dashboard_uuid = String(
        display_name=_("Dashboard UUID"),
        help=_("The ID of the dashboard to embed. Available in the embed dashboard UI."),
        default="1d6bf904-f53f-47fd-b1c9-6cd7e284d286",
        scope=Scope.settings,
    )

    filters = List(
        display_name=_("Filters"),
        help=_("Filters to apply to the dashboard."),
        default=[],
        scope=Scope.settings,
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context=None) -> str:
        """
        Render a template with the given context.

        The template is translatedaccording to the user's language.

        args:
            template_path: The path to the template
            context: The context to render in the template

        returns:
            The rendered template
        """
        return loader.render_django_template(
            template_path, context, i18n_service=self.runtime.service(self, "i18n")
        )

    def user_is_staff(self, user) -> bool:
        """
        Check whether the user has course staff permissions for this XBlock.
        """
        return user.opt_attrs.get("edx-platform.user_is_staff")

    def is_student(self, user) -> bool:
        """
        Check if the user is a student.
        """
        return user.opt_attrs.get("edx-platform.user_role") == "student"

    def anonymous_user_id(self, user) -> str:
        """
        Return the anonymous user ID of the user.
        """
        return user.opt_attrs.get("edx-platform.anonymous_user_id")

    def student_view(self, show_survey):
        """
        Render the view shown to students.
        """
        user_service = self.runtime.service(self, "user")
        user = user_service.get_current_user()

        context = {
            "self": self,
            "show_survey": show_survey,
            "user": user,
            "course": self.course_id,
        }

        superset_config = getattr(settings, "SUPERSET_CONFIG", {})
        context = update_context(
            context=context,
            superset_config={
                "service_url": self.superset_internal_url,
                "username": self.superset_username or superset_config.get("username"),
                "password": self.superset_password or superset_config.get("password"),
            },
            dashboard_uuid=self.dashboard_uuid,
            filters=self.filters,
        )

        if context.get("exception"):
            raise Exception(context.get("exception"))

        frag = Fragment()
        frag.add_content(self.render_template("static/html/superset.html", context))
        frag.add_css(self.resource_string("static/css/superset.css"))
        frag.add_javascript(self.resource_string("static/js/install_required.js"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )
        frag.add_javascript(self.resource_string("static/js/embed_dashboard.js"))
        frag.add_javascript(self.resource_string("static/js/superset.js"))
        frag.initialize_js("SupersetXBlock", json_args={
            "superset_url": self.superset_url,
            "superset_username": self.superset_username,
            "superset_password": self.superset_password,
            "dashboard_uuid": self.dashboard_uuid,
            "superset_token": context.get("superset_token"),
        })
        return frag

    def studio_view(self, context=None):
        """
        Render the view shown to course authors.
        """
        context = {
            "display_name": self.display_name,
            "superset_internal_url": self.superset_internal_url,
            "superset_url": self.superset_url,
            "superset_username": self.superset_username,
            "superset_password": self.superset_password,
            "dashboard_uuid": self.dashboard_uuid,
            "filters": self.filters,
            "display_name_field": self.fields["display_name"],
            "superset_internal_url_field": self.fields["superset_internal_url"],
            "superset_url_field": self.fields["superset_url"],
            "superset_username_field": self.fields["superset_username"],
            "superset_password_field": self.fields["superset_password"],
            "dashboard_uuid_field": self.fields["dashboard_uuid"],
            "filters_field": self.fields["filters"],
        }

        frag = Fragment()
        frag.add_content(
            self.render_template("static/html/superset_edit.html", context)
        )
        frag.add_css(self.resource_string("static/css/superset.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string("static/js/superset_edit.js"))
        frag.initialize_js("SupersetXBlock")
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=""):  # pylint: disable=unused-argument
        """
        Save studio updates.
        """
        print(data)
        self.display_name = data.get("display_name")
        self.superset_internal_url = data.get("superset_internal_url")
        self.superset_url = data.get("superset_url")
        self.superset_username = data.get("superset_username")
        self.superset_password = data.get("superset_password")
        self.dashboard_uuid = data.get("dashboard_uuid")
        # filters = json.loads(filters)
        # self.filters = data.get("filters")

    @staticmethod
    def get_fullname(user) -> Tuple[str, str]:
        """
        Return the full name of the user.

        args:
            user: The user to get the fullname

        returns:
            A tuple containing the first name and last name of the user
        """
        first_name, last_name = "", ""

        if user.full_name:
            fullname = user.full_name.split(" ", 1)
            first_name = fullname[0]

            if fullname[1:]:
                last_name = fullname[1]

        return first_name, last_name

    @staticmethod
    def workbench_scenarios():
        """Return a canned scenario for display in the workbench."""
        return [
            (
                "SupersetXBlock",
                """<superset/>
             """,
            ),
            (
                "Multiple SupersetXBlock",
                """<vertical_demo>
                <superset/>
                <superset/>
                <superset/>
                </vertical_demo>
             """,
            ),
        ]

    @staticmethod
    def _get_statici18n_js_url():
        """
        Return the Javascript translation file for the currently selected language, if any.

        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = "public/js/translations/{locale_code}/text.js"
        lang_code = locale_code.split("-")[0]
        for code in (locale_code, lang_code, "en"):
            if pkg_resources.resource_exists(
                loader.module_name, text_js.format(locale_code=code)
            ):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Return dummy method to generate initial i18n.
        """
        return translation.gettext_noop("Dummy")
