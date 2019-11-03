### Abrindo arquivo fonte ###
NOME_ARQUIVO = 'arquivo.txt'
fd = open(NOME_ARQUIVO, 'r')
stream = fd.read()

### Constantes ###
Digitos = '0123456789'
Alfabeto = 'abcdefghijklmnopqrstuvwxyz'
Reservadas = 'if'
START_REL = ['<', '>', '!', '=']
RELACIONAIS = ['<', '>', '<=', '>=', '==', '!=']

### Tratando erros ###


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}, column {self.pos_start.col}'
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

### Posição ###


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


### Tokens ###
TT_INT = 'Int'
TT_FLOAT = 'Float'
TT_ARIT = 'Operador aritmético'
TT_LPAREN = 'Abre paren'
TT_RPAREN = 'Fecha paren'
TT_LKEY = 'Abre chave'
TT_RKEY = 'Fecha chave'
TT_IDENT = 'Identificadores'
TT_RES = 'Palavra reservada'
TT_REL = 'Operador relacional'
TT_ATRIB = 'Atribuição'
TT_COM = 'Comentario'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

### Lexer ###


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t\n':
                self.advance()

            elif self.current_char == '/':
                guarda = self.current_char
                self.advance()
                if guarda + self.current_char == '//':
                    self.advance()
                    porco = ''
                    while self.current_char != '\n':
                        self.advance()
                        porco += self.current_char
                    tokens.append(Token(TT_COM, porco))
                elif guarda + self.current_char == '/*':
                    self.advance()
                    porco = ''
                    # loop infinito
                    while self.current_char != '*/':
                        self.advance()
                        porco += str(self.current_char)
                    tokens.append(Token(TT_COM, porco))
                else:
                    tokens.append(Token(TT_ARIT, '/'))
                    self.advance()

            elif self.current_char.isalpha():
                tokens.append(self.identifiers())
            elif self.current_char in Digitos:
                tokens.append(self.make_number())
            elif self.current_char in START_REL:
                tokens.append(self.relacionais())
            elif self.current_char == '+':
                tokens.append(Token(TT_ARIT, '+'))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_ARIT, '-'))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_ARIT, '*'))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, '('))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, ')'))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_LKEY, '{'))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RKEY, '}'))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        return tokens, None

    def relacionais(self):
        guarda = self.current_char
        self.advance()
        if self.current_char != None:

            # Ignora espaço em branco
            while self.current_char in ' \t\n':
                self.advance()

            relacional = guarda + self.current_char

            if relacional in RELACIONAIS:
                self.advance()
                return Token(TT_REL, relacional)
            elif guarda in RELACIONAIS:
                return Token(TT_REL, guarda)
            elif guarda == '=':
                return Token(TT_ATRIB, guarda)

    def identifiers(self):
        guarda = self.current_char
        self.advance()
        while (self.current_char != None) and self.current_char.isalnum():
            guarda += self.current_char
            self.advance()

        if guarda + self.current_char in Reservadas:
            return Token(TT_RES, guarda)
        else:
            return Token(TT_IDENT, guarda)

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in Digitos + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


lexer = Lexer(NOME_ARQUIVO, stream)

if __name__ == '__main__':
    tokens, erro = lexer.make_tokens()
    if len(tokens) != 0:
        for token in tokens:
            print(token)
    else:
        print(erro.as_string())

fd.close()
