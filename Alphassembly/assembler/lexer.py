from consts import *

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


class Lexer:
    def __init__(self, text):
        self.current_char = None
        self.text = text
        self.idx = -1
        self.ln = 0
        self.advance()

    def advance(self):
        self.idx += 1
        self.current_char = self.text[self.idx] if self.idx < len(self.text) else None
        if self.current_char == "\n":
            self.ln += 1

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in "#":
                sln = self.ln
                while self.ln == sln:
                    self.advance()
            elif self.current_char == "\n":
                tokens.append(Token(TT_NEWLINE))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '"' or self.current_char == "'":
                tokens.append(self.make_string())
            elif self.current_char in LETTERS + "_.":
                toks = self.make_keyword()
                for tok in toks:
                    tokens.append(tok)
            elif self.current_char in ',':
                tokens.append(Token(TT_COMMA))
                self.advance()
            elif self.current_char == '!':
                token = self.make_not_equals()
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    tokens.append(Token(TT_AND))
                    self.advance()
                else:
                    raise Exception(f"Illegal character: '{self.current_char}'")
            elif self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    tokens.append(Token(TT_OR))
                    self.advance()
                else:
                    raise Exception(f"Illegal character: '{self.current_char}'")
            elif self.current_char == '[':
                tokens.append(self.make_variable())
            elif self.current_char == '{':
                tokens.append(Token(TT_LCURLY))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RCURLY))
                self.advance()
            else:
                raise Exception(f"Illegal character: '{self.current_char}'")

        tokens.append(Token(TT_EOF))
        return tokens

    def make_variable(self):
        var_name = ''

        self.advance()
        while self.current_char != ']':
            if self.current_char == '\n':
                raise Exception(f"Expected ']' line: {self.ln}")
            elif self.current_char == ']':
                break

            var_name += self.current_char
            self.advance()
            
        self.advance()

        return Token(TT_VARIABLE, var_name)

    def make_keyword(self):
        id_str = ''
        tokens = []

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '._:':
            id_str += self.current_char
            self.advance()
        
        if id_str in KEYWORDS:
            tok_type = TT_KEYWORD

            tokens.append(Token(tok_type, id_str))
        else:
            if not id_str[len(id_str)-1] == ":": 
                tokens.append(Token(TT_IDENTIFIER, id_str))
                return tokens
        
        if not id_str in KEYWORDS:
            strlen = len(id_str)
            i = 1
            for char in id_str:
                if char == ":":
                    if i != strlen:
                        raise SyntaxError(f"Illegal character at line {self.ln}")
                    else:
                        tokens.append(Token(TT_LABEL))
                        tokens.append(Token(TT_STRING, id_str[0:-1]))

                i += 1

        return tokens

    def make_number(self):
        num_str = ''
        dot_count = 0

        i = 0
        while self.current_char != None and self.current_char in DIGITS + '-.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()
            i += 1
        
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
    
    def make_string(self):
        string = ''
        start_char = self.current_char
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t',
            '"': '"',
            "'": "'",
            "\\": "\\"
        }

        while self.current_char != None and (self.current_char != start_char or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == "\\":
                    escape_character = True
                    self.advance()
                    continue
                else:
                    string += self.current_char
            self.advance()
            escape_character = False
        
        self.advance()
        return Token(TT_STRING, string)
        
    def make_not_equals(self):
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE)

        self.advance()
        raise Exception("Expected '='")

    def make_equals(self):
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_EE)
        
        raise Exception("Expected '='")

    def make_less_than(self):
        tok_type = TT_LT
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type)

    def make_greater_than(self):
        tok_type = TT_GT
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type)
