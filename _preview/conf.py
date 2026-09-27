import os
import sys

sys.path.insert(0, os.path.abspath("../docs/source/_extensions"))

project = "nbcell preview"
extensions = ["nbcell_directive", "sphinx_copybutton"]
html_theme = "furo"
html_static_path = ["_static"]
copybutton_exclude = ".linenos, .gp, .prompt"
