# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Rebuild the gettext message catalogs (.pot) after editing English sources,
# then merge them into the translated .po files (requires sphinx-intl).
gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(BUILDDIR)/gettext" $(SPHINXOPTS) $(O)
	sphinx-intl update -p "$(BUILDDIR)/gettext" -d "$(SOURCEDIR)/locale" -l zh_CN

# Build the Chinese version locally (skips Manim rendering).
html-zh:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)-zh" -t skip-manim -D language=zh_CN $(SPHINXOPTS) $(O)

.PHONY: gettext html-zh

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)