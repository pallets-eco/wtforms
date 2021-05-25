from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "WTForms"
copyright = "2008 WTForms"
author = "WTForms"
release, version = get_version("WTForms")

# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "pallets_sphinx_themes",
    "sphinx_issues",
    "sphinxcontrib.log_cabinet",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}
issues_github_path = "wtforms/wtforms"

# HTML -----------------------------------------------------------------

html_theme = "werkzeug"
html_context = {
    "project_links": [
        ProjectLink("PyPI Releases", "https://pypi.org/project/WTForms/"),
        ProjectLink("Source Code", "https://github.com/wtforms/wtforms/"),
        ProjectLink(
            "Discord Chat",
            "https://discord.gg/F65P7Z9",
        ),
        ProjectLink("Issue Tracker", "https://github.com/wtforms/wtforms/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["_static"]
html_logo = "_static/logo_joined.svg"
html_favicon = "_static/logo_square.svg"
html_title = f"WTForms Documentation ({version})"
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    ("index", f"WTForms-{version}.tex", html_title, author, "manual"),
]
