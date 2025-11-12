class TipoToken:
    """Representa os tipos de tokens sem depender de Enum."""

    # Palavras Reservadas
    LEIA = "LEIA"
    ESCREVA = "ESCREVA"

    # Identificadores e Literais
    IDENTIFICADOR = "IDENTIFICADOR"
    NUM_INTEIRO = "NUM_INTEIRO"
    NUM_REAL = "NUM_REAL"

    # Operadores
    OP_ADICAO = "OP_ADICAO"
    OP_SUBTRACAO = "OP_SUBTRACAO"
    OP_MULTIPLICACAO = "OP_MULTIPLICACAO"
    OP_DIVISAO = "OP_DIVISAO"
    OP_POTENCIACAO = "OP_POTENCIACAO"
    OP_ATRIBUICAO = "OP_ATRIBUICAO"

    # Símbolos de Pontuação
    DOIS_PONTOS = "DOIS_PONTOS"
    PONTO_VIRGULA = "PONTO_VIRGULA"
    PARENTESE_ESQ = "PARENTESE_ESQ"
    PARENTESE_DIR = "PARENTESE_DIR"

    # Especial
    EOF = "EOF"
    ERRO = "ERRO"


class Token:
    """Estrutura simples de token."""

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"Token({self.tipo}, '{self.lexema}', linha={self.linha}, coluna={self.coluna})"

    def __repr__(self):
        return self.__str__()

# Tabela de palavras reservadas
PALAVRAS_RESERVADAS = {
    'LEIA': TipoToken.LEIA,
    'ESCREVA': TipoToken.ESCREVA,
    'leia': TipoToken.LEIA,
    'escreva': TipoToken.ESCREVA
}
