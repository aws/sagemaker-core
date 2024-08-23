# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Sagemaker Core'
copyright = "2024, Amazon Web Services, Inc. or its affiliates. All rights reserved."
author = "AWS Sagemaker Codex"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
]

autodoc_member_order = 'bysource'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 6,
    "includehidden": True,
    "titles_only": False,
}

htmlhelp_basename = "%sdocs" % project

# For Adobe Analytics
html_js_files = [
    "https://a0.awsstatic.com/s_code/js/3.0/awshome_s_code.js",
    "https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js",
    "https://kit.fontawesome.com/a076d05399.js",
    "js/datatable.js",
]

html_css_files = [
    "https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css",
]

html_context = {
    "css_files": [
        "_static/theme_overrides.css",
        "_static/pagination.css",
        "_static/search_accessories.css",
    ]
}

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("http://docs.python.org/", None)}

# -- Options for autodoc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"

# autosummary
autosummary_generate = True

# autosectionlabel
autosectionlabel_prefix_document = True