# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Get __version__.py without importing project
windows_toasts = {}
with open("../src/windows_toasts/__version__.py", "r") as f:
    exec(f.read(), None, windows_toasts)

project = windows_toasts["__title__"]
copyright = "2023, DatGuy"
author = windows_toasts["__author__"]


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = windows_toasts["__version__"]
# The full version, including alpha/beta/rc tags.
release = windows_toasts["__version__"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["autodoc2"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc2_packages = [{"path": "../src/windows_toasts", "auto_mode": False}]
autodoc2_hidden_objects = ["private", "inherited"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

autodoc_default_options = {"members": True, "member-order": "bysource", "undoc-members": True}
