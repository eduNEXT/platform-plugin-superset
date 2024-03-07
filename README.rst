platform-plugin-superset
#############################

|ci-badge| |pyversions-badge| |license-badge| |status-badge|

Purpose
*******

An Open edX plugin to integrate Superset with Open edX.

This plugin allows to integrate any Superset Dashboard into Open edX as course content
and to integrate the Aspects Instructor Dashboard into the Open edX Instructor Dashboard.

Getting Started
***************

Install this plugin:

.. code-block::

  pip install git+https://github.com/eduNEXT/platform-plugin-superset.git@main

If you have already configured your Aspects instance, you can skip the next step.

Configure Superset Dashboard integration
-----------------------------------------

1. In your tutor environment add the following inline plugin:

.. code-block:: yaml

    name: platform-plugin-superset
    version: 0.1.0
    patches:
        openedx-common-settings: |
         OPEN_EDX_FILTERS_CONFIG = {
           "org.openedx.learning.instructor.dashboard.render.started.v1": {
             "fail_silently": False,
             "pipeline": [
               "platform_plugin_superset.extensions.filters.AddSupersetTab",
             ]
           },
         }

        openedx-development-settings: |
         SUPERSET_CONFIG = {
             "service_url": "http://superset:{{ SUPERSET_PORT }}/",
             "host": "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ SUPERSET_HOST }}:{{ SUPERSET_PORT }}",
             "username": "{{ SUPERSET_LMS_USERNAME }}",
             "password": "{{ SUPERSET_LMS_PASSWORD }}",
             "email": "{{ SUPERSET_LMS_EMAIL }}",
         }

        openedx-common-settings: |
         SUPERSET_CONFIG = {
             "service_url": "http://superset:{{ SUPERSET_PORT }}/",
             "host": "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ SUPERSET_HOST }}",
             "username": "{{ SUPERSET_LMS_USERNAME }}",
             "password": "{{ SUPERSET_LMS_PASSWORD }}",
             "email": "{{ SUPERSET_LMS_EMAIL }}",
         }

2. Enable the tutor inline plugin in your tutor environment:

.. code-block::

      tutor plugins enable platform-plugin-superset

3. Restart your tutor environment:

.. code-block::

      tutor local|dev restart

Superset XBlock
---------------
1. In Studio, go to the advanced settings of the course where you want to add the Superset Dashboard.
2. In the setting Advanced Module List add the following XBlock: 'superset'.
3. Add the Superset XBlock to the course.
4. In the Superset XBlock settings, edit the default values as needed:

- Display Name: The name of the Superset Dashboard.
- Superset URL: The URL of the Superset instance.
- Superset Username: The username of the Superset user.
- Superset Password: The password of the Superset user.
- Filters: The list of SQL filters to apply to the Superset Dashboard. Keep in mind that all the datasets in your Dashboard must have the same filters column name.


Developing
==========

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:eduNEXT/platform-plugin-superset.git
  cd platform-plugin-superset

  # Set up a virtualenv with the same name as the repo and activate it
  # Here's how you might do that if you have virtualenvwrapper setup.
  mkvirtualenv -p python3.8 platform-plugin-superset


Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  # Here's how you might do that if you're using virtualenvwrapper.
  workon platform-plugin-superset

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

Ensure you follow the steps in the "Getting Started" section above.

Tutor environments
------------------

To use this plugin in a Tutor environment, you must install it as a requirement of the ``openedx`` image. To achieve this, follow these steps:

.. code-block:: bash

    tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edunext/platform-plugin-superset@vX.Y.Z
    tutor images build openedx

Then, deploy the resultant image in your environment.

Documentation
=============

By default the plugin will try to connect to the Superset instance running in the same
environment as the Open edX instance. If you want to connect to a different Superset
instance, you can configure the following settings in the ``tutor`` configuration file:

.. code-block:: python

    SUPERSET_CONFIG = {
        "service_url": "http://superset:{{ SUPERSET_PORT }}/",
        "host": "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ SUPERSET_HOST }}:{{ SUPERSET_PORT }}",
        "username": "{{ SUPERSET_LMS_USERNAME }}",
        "password": "{{ SUPERSET_LMS_PASSWORD }}",
        "email": "{{ SUPERSET_LMS_EMAIL }}",
    }

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/platform-plugin-superset

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@edunext.co.

.. |ci-badge| image:: https://github.com/eduNEXT/platform-plugin-superset/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/eduNEXT/platform-plugin-superset/actions
    :alt: CI

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/platform-plugin-superset.svg
    :target: https://pypi.python.org/pypi/platform-plugin-superset/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/eduNEXT/platform-plugin-superset.svg
    :target: https://github.com/eduNEXT/platform-plugin-superset/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
