
cli_logo = r"""
  __  __          _   _ _____ __  __           _    _ _______ ____  __  __       _______          _____ _      _____ 
 |  \/  |   /\   | \ | |_   _|  \/  |     /\  | |  | |__   __/ __ \|  \/  |   /\|__   __|/\      / ____| |    |_   _|
 | \  / |  /  \  |  \| | | | | \  / |    /  \ | |  | |  | | | |  | | \  / |  /  \  | |  /  \    | |    | |      | |  
 | |\/| | / /\ \ | . ` | | | | |\/| |   / /\ \| |  | |  | | | |  | | |\/| | / /\ \ | | / /\ \   | |    | |      | |  
 | |  | |/ ____ \| |\  |_| |_| |  | |  / ____ \ |__| |  | | | |__| | |  | |/ ____ \| |/ ____ \  | |____| |____ _| |_ 
 |_|  |_/_/    \_\_| \_|_____|_|  |_| /_/    \_\____/   |_|  \____/|_|  |_/_/    \_\_/_/    \_\  \_____|______|_____|

"""





class ManimAutomataCLI():


    """Interactive command-line assistant for building automata paths.

    When activated via the ``cli=True`` flag on an automaton constructor,
    this class prints a banner and guides the user through the creation of
    a deterministic or non-deterministic finite automaton, or a pushdown
    automaton.  The recorded path can later be replayed without the CLI.

    Examples
    --------

    .. manim:: ManimAutomataCLIExample
      :save_last_frame:

        from manim import *
        from manim_extensions.automata.mobjects.manim_cli import ManimAutomataCLI

        class ManimAutomataCLIExample(Scene):
            def construct(self):
                cli = ManimAutomataCLI()
"""
    def __init__(self) -> None:
        """Initialize the ManimAutomataCLI instance."""
        print(cli_logo)

    def creation_menu(self) -> None:
        """Prompt the user to choose an automaton type and schema file path."""
        options = ["Deterministic Finite Automaton", "Non-determinstic Finite Automaton", "Pushdown Automaton"]
        self.creation_option = self.display_options(options)
        self.file_path = input("Schema File Path: ")

    def display_nda_options(self) -> None:
        """Prompt the user to choose an NDA-specific option."""
        options = ["Non-deterministic Automaton Path Builder"]
        self.nda_option = self.display_options(options)

    def display_options(self, options: list[str]) -> int:
        """Print a list of options and return the user's choice.

        Parameters
        ----------
        options : list of str
            The options to display.

        Returns
        -------
        int
            The user's zero-based choice index.
        """
        for index, option in enumerate(options):
            print(str(index) + ": " + option)

        return int(input("Choice: "))

    def display_dictionary_options(self, options: dict) -> int:
        """Print dictionary keys with their first value column and return the user's choice.

        Parameters
        ----------
        options : dict
            Mapping from option keys to tuples whose first element is shown.

        Returns
        -------
        int
            The user's chosen key.
        """
        for index in options:
            print(f"{index}: {options[index][0]}")

        return int(input("Choice: "))

    def non_determinstic_finite_automata_path_builder_callback(self) -> None:
        """Handle the NDA path-builder menu callback.

        .. note::

            This method is not yet implemented and raises
            :class:`NotImplementedError`.
        """
        raise NotImplementedError("Not yet implemented")


if __name__ == "__main__":
    cli = ManimAutomataCLI()