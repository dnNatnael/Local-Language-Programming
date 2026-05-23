# -*- coding: utf-8 -*-
"""
Amharic-friendly error messages for the AML compiler.
"""


class AmharicSyntaxError(Exception):
    """Syntax error with line/column and Amharic message."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format())

    def format(self) -> str:
        if self.line > 0:
            return f"ስህተት (ረድፍ {self.line}, አምድ {self.column}): {self.message}"
        return f"ስህተት: {self.message}"


# Common error message templates (Amharic)
MSG_UNEXPECTED_TOKEN = "ያልተጠበቀ ምልክት '{token}'"
MSG_EXPECTED_END = "መጨረሻ ተጠበቀ"
MSG_EXPECTED_ELSE_OR_END = "ካልሆነ ወይም መጨረሻ ተጠበቀ"
MSG_EXPECTED_EXPRESSION = "ገላጭ ተጠበቀ"
MSG_EXPECTED_IDENTIFIER = "ስም ተጠበቀ"
MSG_EXPECTED_RPAREN = "የተዘጋ ገላጭ '(' ተጠበቀ"
MSG_EXPECTED_COLON_OR_NEWLINE = "አዲስ መስመር ተጠበቀ"
MSG_UNTERMINATED_STRING = "ያልተጠናቀቀ ጽሑፍ"
MSG_INVALID_NUMBER = "ልክ ያልሆነ ቁጥር"
MSG_UNKNOWN_KEYWORD = "ያልታወቀ ቁልፍ ቃል"
MSG_EOF_UNEXPECTED = "ፕሮግራሙ በድንገት አበቃ"
