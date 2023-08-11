# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from typing import Dict

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# I'd love to simply import the project (so I could also use sphinx.ext.doctest), but RTD builds on Ubuntu
# Get version.py without importing project
windows_toasts: Dict[str, str] = {}
with open("../src/windows_toasts/_version.py", "r") as f:
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

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_toolbox.more_autodoc.typevars",
    "enum_tools.autoenum",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_mock_imports = ["toasts_winrt"]
autodoc_default_options = {"members": True, "member-order": "bysource", "undoc-members": True}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_logo = "images/logo.png"
html_static_path = ["_static"]
