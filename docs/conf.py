import os
import sys

sys.path.insert(0, os.path.abspath("../"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ScubaTrace"
copyright = "2025"
author = "SunBK201"
# release = v("scubatrace")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "en"

autoclass_content = "class"
autodoc_member_order = "groupwise"
autosummary_generate = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/SunBK201/ScubaTrace",
    "home_page_in_toc": False,
    "pygments_light_style": "default",
    "pygments_dark_style": "github-dark",
    "navigation_with_keys": False,
    "use_repository_button": True,
    "use_download_button": False,
    "use_fullscreen_button": False,
    "show_toc_level": 2,
    "logo": {
        "image_light": "_static/logo-black.png",
        "image_dark": "_static/logo-white.png",
    },
}

html_static_path = ["_static"]
html_title = "ScubaTrace"
# html_logo = "_static/logo.png"
# html_favicon = "_static/logo.png"
