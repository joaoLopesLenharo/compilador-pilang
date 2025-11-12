from tokens import Token, TipoToken
from typing import List, Union


# Classes para representar a árvore sintática abstrata (AST)
class Programa:
    def __init__(self, comandos: List['Comando']):
        self.comandos = comandos


class Comando:
    pass


class ComandoLeitura(Comando):
    def __init__(self, variavel: str):
        self.variavel = variavel


class ComandoEscrita(Comando):
    def __init__(self, variavel: str):
        self.variavel = variavel


class ComandoAtribuicao(Comando):
    def __init__(self, variavel: str, expressao: 'Expressao'):
        self.variavel = variavel
        self.expressao = expressao


class Expressao:
    pass


class ExpressaoSimples(Expressao):
    def __init__(self, termos: List[tuple[str, 'Termo']]):
        self.termos = termos  # Lista de (operador, termo)


class Termo:
    def __init__(self, fatores: List[tuple[str, 'Fator']]):
        self.fatores = fatores  # Lista de (operador, fator)


class Fator:
    def __init__(self, elementos: List[tuple[str, 'Elemento']]):
        self.elementos = elementos  # Lista de (operador, elemento)


class Elemento:
    def __init__(self, valor: Union[str, int, float, 'Expressao'], tipo: str):
        self.valor = valor
        self.tipo = tipo  # 'IDENTIFICADOR', 'NUM_INTEIRO', 'NUM_REAL', 'EXPRESSAO'

class ErroSintatico(Exception):
    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro sintático na linha {linha}, coluna {coluna}: {mensagem}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[0] if tokens else None
        
    def avancar(self):
        """Avança para o próximo token"""
        if self.posicao < len(self.tokens) - 1:
            self.posicao += 1
            self.token_atual = self.tokens[self.posicao]
    
    def verificar(self, tipo_esperado: TipoToken) -> bool:
        """Verifica se o token atual é do tipo esperado"""
        return self.token_atual.tipo == tipo_esperado
    
    def consumir(self, tipo_esperado: TipoToken, mensagem_erro: str) -> Token:
        """Consome o token atual se for do tipo esperado, caso contrário lança erro"""
        if self.verificar(tipo_esperado):
            token = self.token_atual
            self.avancar()
            return token
        else:
            raise ErroSintatico(
                mensagem_erro, 
                self.token_atual.linha, 
                self.token_atual.coluna
            )
    
    def consumir_tipo(self, tipos_esperados: List[TipoToken], mensagem_erro: str) -> Token:
        """Consome o token atual se for de um dos tipos esperados, caso contrário lança erro"""
        if self.token_atual.tipo in tipos_esperados:
            token = self.token_atual
            self.avancar()
            return token
        else:
            raise ErroSintatico(
                mensagem_erro, 
                self.token_atual.linha, 
                self.token_atual.coluna
            )
    
    def parser_programa(self) -> Programa:
        """<programa> ::= <comandos>"""
        comandos = self.parser_comandos()
        return Programa(comandos)
    
    def parser_comandos(self) -> List[Comando]:
        """<comandos> ::= <comando> <comandos> | <comando>"""
        comandos = []
        
        # Continua enquanto houver comandos válidos
        while (not self.verificar(TipoToken.EOF) and
               (self.verificar(TipoToken.LEIA) or 
                self.verificar(TipoToken.ESCREVA) or 
                self.verificar(TipoToken.IDENTIFICADOR))):
            
            comando = self.parser_comando()
            comandos.append(comando)
        
        return comandos
    
    def parser_comando(self) -> Comando:
        """<comando> ::= <comando_leitura> | <comando_escrita> | <comando_atribuicao>"""
        if self.verificar(TipoToken.LEIA):
            return self.parser_comando_leitura()
        elif self.verificar(TipoToken.ESCREVA):
            return self.parser_comando_escrita()
        elif self.verificar(TipoToken.IDENTIFICADOR):
            return self.parser_comando_atribuicao()
        else:
            raise ErroSintatico(
                "Esperado comando (LEIA, ESCREVA ou atribuição)",
                self.token_atual.linha,
                self.token_atual.coluna
            )
    
    def parser_comando_leitura(self) -> ComandoLeitura:
        """<comando_leitura> ::= LEIA IDENTIFICADOR ;"""
        self.consumir(TipoToken.LEIA, "Esperado 'LEIA'")
        
        variavel_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado identificador após LEIA")
        variavel = variavel_token.lexema
        
        self.consumir(TipoToken.PONTO_VIRGULA, "Esperado ';' após comando LEIA")
        
        return ComandoLeitura(variavel)
    
    def parser_comando_escrita(self) -> ComandoEscrita:
        """<comando_escrita> ::= ESCREVA IDENTIFICADOR ;"""
        self.consumir(TipoToken.ESCREVA, "Esperado 'ESCREVA'")
        
        variavel_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado identificador após ESCREVA")
        variavel = variavel_token.lexema
        
        self.consumir(TipoToken.PONTO_VIRGULA, "Esperado ';' após comando ESCREVA")
        
        return ComandoEscrita(variavel)
    
    def parser_comando_atribuicao(self) -> ComandoAtribuicao:
        """<comando_atribuicao> ::= IDENTIFICADOR = <expressao> ;"""
        variavel_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado identificador")
        variavel = variavel_token.lexema
        
        self.consumir(TipoToken.OP_ATRIBUICAO, "Esperado '=' após identificador")
        
        expressao = self.parser_expressao()
        
        self.consumir(TipoToken.PONTO_VIRGULA, "Esperado ';' após expressão")
        
        return ComandoAtribuicao(variavel, expressao)
    
    def parser_expressao(self) -> Expressao:
        """<expressao> ::= <expressao_simples>"""
        return self.parser_expressao_simples()
    
    def parser_expressao_simples(self) -> ExpressaoSimples:
        """<expressao_simples> ::= <termo> <resto_expressao_simples>"""
        termos = []
        
        # Primeiro termo (obrigatório)
        primeiro_termo = self.parser_termo()
        termos.append(("", primeiro_termo))  # Operador vazio para o primeiro termo
        
        # Termos adicionais com operadores + ou -
        while self.verificar(TipoToken.OP_ADICAO) or self.verificar(TipoToken.OP_SUBTRACAO):
            operador = self.token_atual.lexema
            self.avancar()
            termo = self.parser_termo()
            termos.append((operador, termo))
        
        return ExpressaoSimples(termos)
    
    def parser_termo(self) -> Termo:
        """<termo> ::= <fator> <resto_termo>"""
        fatores = []
        
        # Primeiro fator (obrigatório)
        primeiro_fator = self.parser_fator()
        fatores.append(("", primeiro_fator))  # Operador vazio para o primeiro fator
        
        # Fatores adicionais com operadores * ou /
        while self.verificar(TipoToken.OP_MULTIPLICACAO) or self.verificar(TipoToken.OP_DIVISAO):
            operador = self.token_atual.lexema
            self.avancar()
            fator = self.parser_fator()
            fatores.append((operador, fator))
        
        return Termo(fatores)
    
    def parser_fator(self) -> Fator:
        """<fator> ::= <elemento> <resto_fator>"""
        elementos = []
        
        # Primeiro elemento (obrigatório)
        primeiro_elemento = self.parser_elemento()
        elementos.append(("", primeiro_elemento))  # Operador vazio para o primeiro elemento
        
        # Elementos adicionais com operador ^
        while self.verificar(TipoToken.OP_POTENCIACAO):
            operador = self.token_atual.lexema
            self.avancar()
            elemento = self.parser_elemento()
            elementos.append((operador, elemento))
        
        return Fator(elementos)
    
    def parser_elemento(self) -> Elemento:
        """<elemento> ::= IDENTIFICADOR | NUM_INTEIRO | NUM_REAL | ( <expressao> )"""
        if self.verificar(TipoToken.IDENTIFICADOR):
            valor = self.token_atual.lexema
            self.avancar()
            return Elemento(valor, "IDENTIFICADOR")
        
        elif self.verificar(TipoToken.NUM_INTEIRO):
            valor = int(self.token_atual.lexema)
            self.avancar()
            return Elemento(valor, "NUM_INTEIRO")
        
        elif self.verificar(TipoToken.NUM_REAL):
            valor = float(self.token_atual.lexema)
            self.avancar()
            return Elemento(valor, "NUM_REAL")
        
        elif self.verificar(TipoToken.PARENTESE_ESQ):
            self.avancar()
            expressao = self.parser_expressao()
            self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após expressão")
            return Elemento(expressao, "EXPRESSAO")
        
        else:
            raise ErroSintatico(
                "Esperado identificador, número ou expressão entre parênteses",
                self.token_atual.linha,
                self.token_atual.coluna
            )
    
    # ... (início do arquivo parser.py)

    def parse(self) -> Programa:
        """Método principal que inicia a análise sintática.
        Lança ErroSintatico em caso de falha."""
        # Removemos o bloco try/except para que a exceção seja propagada para a API
        return self.parser_programa()

# ... (resto do arquivo)
    
    def imprimir_ast(self, no, nivel=0):
        """Método auxiliar para imprimir a árvore sintática"""
        indentacao = "  " * nivel
        
        if isinstance(no, Programa):
            print(f"{indentacao}Programa:")
            for comando in no.comandos:
                self.imprimir_ast(comando, nivel + 1)
        
        elif isinstance(no, ComandoLeitura):
            print(f"{indentacao}Comando Leitura: LEIA {no.variavel}")
        
        elif isinstance(no, ComandoEscrita):
            print(f"{indentacao}Comando Escrita: ESCREVA {no.variavel}")
        
        elif isinstance(no, ComandoAtribuicao):
            print(f"{indentacao}Comando Atribuição: {no.variavel} = ")
            self.imprimir_ast(no.expressao, nivel + 1)
        
        elif isinstance(no, ExpressaoSimples):
            print(f"{indentacao}Expressão:")
            for operador, termo in no.termos:
                if operador:
                    print(f"{indentacao}  Operador: {operador}")
                self.imprimir_ast(termo, nivel + 2)
        
        elif isinstance(no, Termo):
            print(f"{indentacao}Termo:")
            for operador, fator in no.fatores:
                if operador:
                    print(f"{indentacao}  Operador: {operador}")
                self.imprimir_ast(fator, nivel + 2)
        
        elif isinstance(no, Fator):
            print(f"{indentacao}Fator:")
            for operador, elemento in no.elementos:
                if operador:
                    print(f"{indentacao}  Operador: {operador}")
                self.imprimir_ast(elemento, nivel + 2)
        
        elif isinstance(no, Elemento):
            if no.tipo == "EXPRESSAO":
                print(f"{indentacao}Elemento: (expressão)")
                self.imprimir_ast(no.valor, nivel + 1)
            else:
                print(f"{indentacao}Elemento: {no.valor} ({no.tipo})")
