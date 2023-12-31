"""
Utilities for platform_plugin_superset app.
"""

import logging
import os

from crum import get_current_user
from django.conf import settings
from supersetapiclient.client import SupersetClient

if settings.DEBUG:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


logger = logging.getLogger(__name__)


def _(text):
    """
    Define a duymmy `gettext` replacement to make string extraction tools scrape strings marked for translation.
    """
    return text


def update_context(  # pylint: disable=dangerous-default-value
    context,
    superset_config={},
    dashboard_uuid="",
    filters=[],
    user=None,
):
    """
    Update context with superset token and dashboard id.

    Args:
        context (dict): the context for the instructor dashboard. It must include a course object
        superset_config (dict): superset config.
        dashboard_uuid (str): superset dashboard uuid.
        filters (list): list of filters to apply to the dashboard.
        user (User): user object.
    """
    course = context["course"]

    if user is None:
        user = get_current_user()
    superset_token, dashboard_uuid = generate_guest_token(
        user=user,
        course=course,
        superset_config=superset_config,
        dashboard_uuid=dashboard_uuid,
        filters=filters,
    )

    if superset_token:
        context.update(
            {
                "superset_token": superset_token,
                "dashboard_uuid": dashboard_uuid,
                "superset_url": settings.SUPERSET_CONFIG.get("host"),
            }
        )
    else:
        context.update(
            {
                "exception": dashboard_uuid,
            }
        )

    return context


def generate_guest_token(user, course, superset_config, dashboard_uuid, filters):
    """
    Generate a Superset guest token for the user.

    Args:
        user: User object.
        course: Course object.

    Returns:
        tuple: Superset guest token and dashboard id.
        or None, exception if Superset is missconfigured or cannot generate guest token.
    """
    if not superset_config:
        superset_config = getattr(settings, "SUPERSET_CONFIG", {})

    superset_internal_host = superset_config.get("service_url", "http://superset:8088/")
    superset_username = superset_config.get("username")
    superset_password = superset_config.get("password")

    try:
        client = SupersetClient(
            host=superset_internal_host,
            username=superset_username,
            password=superset_password,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(exc)
        return None, exc

    formatted_filters = [filter.format(course=course, user=user) for filter in filters]

    data = {
        "user": {
            "username": user.username,
            # We can send more info about the user to superset
            # but Open edX only provides the full name. For now is not needed
            # and doesn't add any value so we don't send it.
            # {
            #    "first_name": "John",
            #    "last_name": "Doe",
            # }
        },
        "resources": [{"type": "dashboard", "id": dashboard_uuid}],
        "rls": [{"clause": filter} for filter in formatted_filters],
    }

    try:
        response = client.session.post(
            url=f"{superset_internal_host}api/v1/security/guest_token/",
            json=data,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        token = response.json()["token"]

        return token, dashboard_uuid
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(exc)
        return None, exc
