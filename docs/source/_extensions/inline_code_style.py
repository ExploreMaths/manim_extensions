"""Custom Sphinx extension to render inline code without a background.

Inline literals (``code.literal``) keep their monospace font and text
color, but lose the background, border, padding and font-size override
applied by the furo theme, so they appear at the same size as the
surrounding text.

The CSS is injected as a ``<style>`` block via ``html-page-context``.
Because that block lands before the theme's stylesheets in ``<head>``,
the rules use ``!important`` to win over furo's equally specific
selectors.
"""

CSS = """
/* Strip inline-code chrome; keep font family and text color. */
code.docutils.literal {
    background: none !important;
    border: none !important;
    border-radius: 0 !important;
    font-size: inherit !important;
    padding: 0 !important;
}
"""


def _add_inline_code_style(app, pagename, templatename, context, doctree):
    """Inject the inline-code CSS into every HTML page."""
    context["metatags"] = context.get("metatags", "") + f"<style>{CSS}</style>"


def setup(app):
    app.connect("html-page-context", _add_inline_code_style)
    return {"version": "1.0", "parallel_read_safe": True}
