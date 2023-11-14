from pygments import highlight
from pygments.lexers import Python3Lexer
from pygments.formatters import TerminalFormatter

def highlight_code(code:str) -> str:
    """
    Highlight the given code using syntax highlighting.

    Args:
        code (str): The code to be highlighted.

    Returns:
        str: The highlighted code.
    """
    return highlight(code, Python3Lexer(), TerminalFormatter())
