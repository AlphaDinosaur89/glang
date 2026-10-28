import string

TT_OP = "OP"
TT_STRING = "STRING"
TT_IDENTIFIER = "IDENTIFIER"
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_NEWLINE = "NEWLINE"
TT_KEYWORD = "KEYWORD"
TT_DOUBLECOLON = "DOUBLECOLON"
TT_LABEL = "LABEL"
TT_COMMA = "COMMA"
TT_EE = 'EE'
TT_NE = 'NE'
TT_LT = 'LT'
TT_GT = 'GT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'
TT_AND = 'AND'
TT_OR = 'OR'
TT_VARIABLE = "VARIABLE"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_EOF = "EOF"

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

KEYWORDS = [
    "push",
    "pop",
    "add",
    "sub",
    "mul",
    "div",
    "done",
    "print",
    "ld",
    "jmp",
    "call",
    "ret",
    "je",
    "jn",
    "jg",
    "jl",
    "mov",
    "cmp",
    "jt",
    "jf",
    "mod",
    "bcall",
    "pow",
    "test",
    "pt",
    "spt"
]

REGISTERS = {
    "ax": 0xa,
    "bx": 0xb,
    "cx": 0xc,
    "dx": 0xd,
    "sp": 0xe
}