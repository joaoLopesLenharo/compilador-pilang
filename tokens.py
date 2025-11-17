class TipoToken:
    """Representa os tipos de tokens sem depender de Enum."""

    # Palavras Reservadas - Estrutura Teatral
    SCENE = "SCENE"
    FIM_CENA = "FIM_CENA"
    CHARACTER = "CHARACTER"
    MEMORY = "MEMORY"
    FIM_MEMORY = "FIM_MEMORY"
    SPEECH = "SPEECH"
    SAYS = "SAYS"
    SPEAKS = "SPEAKS"
    APPROACHES = "APPROACHES"
    EXITS = "EXITS"
    
    # Tipos e Comandos
    NUMBER = "NUMBER"  # Tipo numérico (inteiro ou real)
    LEIA = "LEIA"

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

# Tabela de palavras reservadas - DRAMATICA
PALAVRAS_RESERVADAS = {
    # Estrutura teatral
    'scene': TipoToken.SCENE,
    'SCENE': TipoToken.SCENE,
    'FIM_CENA': TipoToken.FIM_CENA,
    'fim_cena': TipoToken.FIM_CENA,
    'character': TipoToken.CHARACTER,
    'CHARACTER': TipoToken.CHARACTER,
    'memory': TipoToken.MEMORY,
    'MEMORY': TipoToken.MEMORY,
    'FIM_MEMORY': TipoToken.FIM_MEMORY,
    'fim_memory': TipoToken.FIM_MEMORY,
    'speech': TipoToken.SPEECH,
    'SPEECH': TipoToken.SPEECH,
    'says': TipoToken.SAYS,
    'SAYS': TipoToken.SAYS,
    'speaks': TipoToken.SPEAKS,
    'SPEAKS': TipoToken.SPEAKS,
    'approaches': TipoToken.APPROACHES,
    'APPROACHES': TipoToken.APPROACHES,
    'exits': TipoToken.EXITS,
    'EXITS': TipoToken.EXITS,
    # Tipos e comandos
    'number': TipoToken.NUMBER,
    'NUMBER': TipoToken.NUMBER,
    'LEIA': TipoToken.LEIA,
    'leia': TipoToken.LEIA
}
