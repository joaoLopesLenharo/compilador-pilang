class TipoToken:
    """Representa os tipos de tokens sem depender de Enum."""

    # Palavras Reservadas - Estrutura Teatral
    CENA = "CENA"
    FIM_CENA = "FIM_CENA"
    PERSONAGEM = "PERSONAGEM"
    MEMORIA = "MEMORIA"
    FIM_MEMORIA = "FIM_MEMORIA"
    FALA = "FALA"
    DIZ = "DIZ"
    FALA_PARA = "FALA_PARA"
    APROXIMA = "APROXIMA"
    SAI = "SAI"
    
    # Tipos e Comandos
    VARCHAR = "VARCHAR"  # Tipo string/texto
    INT = "INT"  # Tipo inteiro
    FLOAT = "FLOAT"  # Tipo real
    LEIA = "LEIA"

    # Identificadores e Literais
    IDENTIFICADOR = "IDENTIFICADOR"
    NUM_INTEIRO = "NUM_INTEIRO"
    NUM_REAL = "NUM_REAL"
    STRING = "STRING"  # String literal entre aspas duplas

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
    COLCHETE_ESQ = "COLCHETE_ESQ"  # [
    COLCHETE_DIR = "COLCHETE_DIR"  # ]
    CHAVE_ESQ = "CHAVE_ESQ"  # {
    CHAVE_DIR = "CHAVE_DIR"  # }
    VIRGULA = "VIRGULA"  # ,
    PONTO = "PONTO"  # .
    EXCLAMACAO = "EXCLAMACAO"  # !
    MAIOR_QUE = "MAIOR_QUE"  # >
    ASPAS_DUPLAS = "ASPAS_DUPLAS"  # "

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

# Tabela de palavras reservadas - DRAMATICA (CASE-SENSITIVE - apenas MAIÚSCULAS)
PALAVRAS_RESERVADAS = {
    # Estrutura teatral
    'CENA': TipoToken.CENA,
    'FIM_CENA': TipoToken.FIM_CENA,
    'PERSONAGEM': TipoToken.PERSONAGEM,
    'MEMORIA': TipoToken.MEMORIA,
    'FIM_MEMORIA': TipoToken.FIM_MEMORIA,
    'FALA': TipoToken.FALA,
    'DIZ': TipoToken.DIZ,
    'FALA_PARA': TipoToken.FALA_PARA,
    'APROXIMA': TipoToken.APROXIMA,
    'SAI': TipoToken.SAI,
    # Tipos de banco de dados
    'VARCHAR': TipoToken.VARCHAR,
    'INT': TipoToken.INT,
    'FLOAT': TipoToken.FLOAT,
    # Comandos
    'LEIA': TipoToken.LEIA
}
