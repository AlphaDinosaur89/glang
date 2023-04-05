import string

LETTERS = string.ascii_letters
DIGITS = string.digits
LETTERS_DIGITS = LETTERS + DIGITS

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_STRING = 'STRING'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_MOD = 'MOD'
TT_EQ = 'EQ'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_RSQUARE = 'RSQUARE'
TT_LSQUARE = 'LSQUARE'
TT_COMMA = 'COMMA'
TT_NEWLINE = 'NEWLINE'
TT_EE = 'EE'
TT_NE = 'NE'
TT_LT = 'LT'
TT_GT = 'GT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'
TT_DCOLON = 'DCOLON'
TT_DOT = 'DOT'
TT_EOF = 'EOF'

KEYWORDS = [
    'var',
    'if',
    'else',
    'elif',
    'end',
    'and',
    'or',
    'for',
    'to',
    'step',
    'continue',
    'break',
    'while',
    'def',
    'return',
    'include',
    'class'
]
