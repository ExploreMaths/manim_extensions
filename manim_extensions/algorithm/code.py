import manim
from .utils.debug import index_code_labels

class Code(manim.Code):
    r"""Visual code block with built-in line labels and helper utilities.

    This wrapper keeps the functionality of Manim's built-in code renderer but
    exposes additional utility objects such as the background, line numbers, and
    per-character index labels used for animation and annotation.

    Examples
    --------
    .. manim:: CodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.code import Code

       class CodeExample(Scene):
           def construct(self):
               code_src = "def hello():\n    print('Hello, Manim!')\n"
               code = Code(code=code_src, language="python")
               self.add(code)
    """

    def __init__(self, *args, **kwargs):
        """Initialize the Code block.

        Accepts the same parameters as :class:`manim.Code`, plus a few
        conveniences: the ``code`` argument is aliased to ``code_string``,
        ``style`` is aliased to ``formatter_style``, and
        ``insert_line_no`` is aliased to ``add_line_numbers``. When no
        formatter style is provided, ``"monokai"`` is used by default.

        The resulting mobject exposes three child components that can be
        animated individually:

        - ``background_mobject``: the code panel background.
        - ``line_numbers``: the optional line-number column.
        - ``code``: the actual source lines.
        """
        if "code" in kwargs and "code_string" not in kwargs:
            kwargs["code_string"] = kwargs.pop("code")
        if "style" in kwargs and "formatter_style" not in kwargs:
            kwargs["formatter_style"] = kwargs.pop("style")
        if "insert_line_no" in kwargs and "add_line_numbers" not in kwargs:
            kwargs["add_line_numbers"] = kwargs.pop("insert_line_no")
        if "formatter_style" not in kwargs:
            kwargs["formatter_style"] = "monokai"
        super().__init__(*args, **kwargs)
    
    def generate_index_labels(self, label_height: float = 0.1, **kwargs) -> manim.VGroup:
        r"""Generate index labels for each displayed character in the code block.

        This is useful for pointing at specific characters during an
        explanation. The returned :class:`~manim.VGroup` is organised as a
        2D structure: the outer level iterates over code lines, and each
        inner entry holds the numeric labels for every character on that
        line.

        Parameters
        -----------
        label_height : float
            Height of the generated index labels. Defaults to ``0.1``.
        **kwargs
            Forwarded to the :class:`~manim.Integer` constructor used for
            each label.

        Returns
        -------
        manim.VGroup
            A 2D :class:`~manim.VGroup` of labels; the first level
            corresponds to source lines, the second level to the labels
            inside each line.

        Examples
        --------
        .. manim:: GenerateIndexLabelsExample
           :save_last_frame:

           from manim import *
           from manim_extensions.algorithm.code import PythonCode

           class GenerateIndexLabelsExample(Scene):
               def construct(self):
                   src = "x = 1\\ny = x + 2\\n"
                   code = PythonCode(code=src).to_edge(LEFT)
                   labels = code.generate_index_labels(label_height=0.08)
                   labels.next_to(code, DOWN, buff=0.8)
                   self.add(code, labels)
        """
        return index_code_labels(self, label_height=label_height, **kwargs)

class PythonCode(Code):
    r"""Convenience code block configured for Python source listings.

    Examples
    --------
    .. manim:: PythonCodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.code import PythonCode

       class PythonCodeExample(Scene):
           def construct(self):
               code_src = (
                   "def fib(n):\n"
                   "    a, b = 0, 1\n"
                   "    for _ in range(n):\n"
                   "        a, b = b, a + b\n"
                   "    return a\n"
               )
               code = PythonCode(code=code_src)
               self.add(code)
    """

    def __init__(self, *args, **kwargs):
        """Initialize the PythonCode instance."""
        if "language" not in kwargs:
            kwargs["language"] = "python"
        super().__init__(*args, **kwargs)

class JavaCode(Code):
    r"""Convenience code block configured for Java source listings.

    Examples
    --------
    .. manim:: JavaCodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.code import JavaCode

       class JavaCodeExample(Scene):
           def construct(self):
               code_src = (
                   "public class Main {\n"
                   "    public static void main(String[] args) {\n"
                   "        System.out.println(\"Hello, Manim!\");\n"
                   "    }\n"
                   "}\n"
               )
               code = JavaCode(code=code_src)
               self.add(code)
    """

    def __init__(self, *args, **kwargs):
        """Initialize the JavaCode instance."""
        if "language" not in kwargs:
            kwargs["language"] = "java"
        super().__init__(*args, **kwargs)

class CppCode(Code):
    r"""Convenience code block configured for C++ source listings.

    Examples
    --------
    .. manim:: CppCodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.code import CppCode

       class CppCodeExample(Scene):
           def construct(self):
               code_src = (
                   "#include <iostream>\n"
                   "int main() {\n"
                   "    std::cout << \"Hello, Manim!\" << std::endl;\n"
                   "    return 0;\n"
                   "}\n"
               )
               code = CppCode(code=code_src)
               self.add(code)
    """

    def __init__(self, *args, **kwargs):
        """Initialize the CppCode instance."""
        if "language" not in kwargs:
            kwargs["language"] = "cpp"
        super().__init__(*args, **kwargs)