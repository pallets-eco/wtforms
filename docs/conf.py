import os
import sys
from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

def _fix_import_path():
    """
    Don't want to pollute the config globals, so do path munging
    here in this function
    """

    try:
        import wtforms
    except ImportError:
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        build_lib = os.path.join(parent_dir, 'build', 'lib')
        if os.path.isdir(build_lib):
            sys.path.insert(0, build_lib)
        else:
            sys.path.insert(0, parent_dir)

_fix_import_path()

# Project --------------------------------------------------------------

project = "WTForms"
copyright = "2008-2020 by the WTForms team"
release, version = get_version("WTForms")

# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "pallets_sphinx_themes",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_issues",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}
issues_github_path = "wtforms/wtforms"

# HTML -----------------------------------------------------------------

html_theme = "werkzeug"
html_context = {
    "project_links": [
        ProjectLink(
            "Discord",
            "https://discordapp.com/channels/531221516914917387/590290790241009673",
        ),
        ProjectLink("PyPI releases", "https://pypi.org/project/WTForms/"),
        ProjectLink("Source Code", "https://github.com/wtforms/wtforms/"),
        ProjectLink("Issue Tracker", "https://github.com/wtforms/wtforms/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["_static"]
html_logo = "_static/wtforms.png"
html_title = "WTForms Documentation ({})".format(version)
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    ('index', 'WTForms.tex', 'WTForms Documentation', 'WTForms team', 'manual'),
]
