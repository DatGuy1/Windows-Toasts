.. Windows-Toasts documentation master file, created by
   sphinx-quickstart on Fri Mar 10 09:44:43 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Windows-Toasts
==========================================

Release v\ |version|.

.. image:: https://static.pepy.tech/badge/windows-toasts/month
    :target: https://pepy.tech/project/windows-toasts
    :alt: Downloads Per Month Badge

.. image:: https://img.shields.io/pypi/l/windows-toasts.svg
    :target: https://pypi.org/project/windows-toasts/
    :alt: License Badge

.. image:: https://img.shields.io/pypi/wheel/windows-toasts.svg
    :target: https://pypi.org/project/windows-toasts/
    :alt: Wheel Support Badge

.. image:: https://img.shields.io/pypi/pyversions/windows-toasts.svg
    :target: https://pypi.org/project/windows-toasts/
    :alt: Python Version Support Badge

.. image:: https://codecov.io/gh/DatGuy1/Windows-Toasts/branch/master/graph/badge.svg?token=ZD8OF2SF61)
    :target: https://codecov.io/gh/DatGuy1/Windows-Toasts
    :alt: Test Coverage Badge

Windows-Toasts is a Python library used to send `toast notifications <https://docs.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts>`_ on Windows machines.

Why Windows-Toasts?
-------------------

As opposed to other toast notification libraries, Windows-Toasts uses `Windows SDK <https://learn.microsoft.com/en-gb/windows/apps/windows-app-sdk/>`_ bindings to create and deliver notifications.
This means no less-than-pretty Powershell hackyness and the like, and is in turn scalable, maintainable, and easy to use.

The other packages I've seen also don't use tests or have no active maintainers, while Windows-Toasts has decent test coverage, is fully typed and documented, and has additional features.
Any issues or feature requests you put on `GitHub <https://github.com/DatGuy1/Windows-Toasts/issues>`_ shouldn't stand there for too long without receiving a response.

Contents
--------

.. toctree::
   :maxdepth: 3

   getting_started
   interactable
   advanced_usage
   custom_aumid

.. toctree::
   :maxdepth: 2
   :caption: User reference

   user/toasters
   user/toast
   user/audio
   user/wrappers
   user/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Developer reference

   dev/toast_document
   dev/metadata

.. toctree::
   :maxdepth: 1
   :caption: Migration

   migration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
