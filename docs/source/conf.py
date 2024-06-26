import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path("../..").resolve().absolute()))

from aiorem import __version__

pyproject_toml = tomllib.loads(Path("../../pyproject.toml").read_text())

project = pyproject_toml["project"]["name"]
version = __version__
release = __version__
documentation_summary = pyproject_toml["project"]["description"]
author = pyproject_toml["project"]["authors"][0]["name"]
copyright = "2024, Hinrich Mahler"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

html_theme = "furo"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

nitpicky = True
