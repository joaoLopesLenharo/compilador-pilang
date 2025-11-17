from tokens import Token, TipoToken
from typing import List, Union


# Classes para representar a árvore sintática abstrata (AST) - DRAMATICA
class Programa:
    def __init__(self, nome_cena: str, personagem: 'Personagem', comandos: List['Comando']):
        self.nome_cena = nome_cena
        self.personagem = personagem
        self.comandos = comandos


class Personagem:
    def __init__(self, nome: str, declaracoes: List['Declaracao']):
        self.nome = nome
        self.declaracoes = declaracoes


class Declaracao:
    def __init__(self, nome: str, tipo: str):
        self.nome = nome
        self.tipo = tipo  # 'VARCHAR', 'INT' ou 'FLOAT'


class Comando:
    pass


class ComandoLeitura(Comando):
    def __init__(self, variavel: str):
        self.variavel = variavel


class ComandoEscrita(Comando):
    def __init__(self, personagem: str, expressao: 'Expressao'):
        self.personagem = personagem
        self.expressao = expressao


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
        self.tipo = tipo  # 'IDENTIFICADOR', 'NUM_INTEIRO', 'NUM_REAL', 'STRING', 'EXPRESSAO'

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
        """<programa> ::= CENA IDENTIFICADOR : <personagem> <comandos> FIM_CENA"""
        # Consome cena
        self.consumir(TipoToken.CENA, "Esperado 'CENA' no início do programa")
        
        # Nome da cena
        nome_cena_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome da cena após 'CENA'")
        nome_cena = nome_cena_token.lexema
        
        # Dois pontos
        self.consumir(TipoToken.DOIS_PONTOS, "Esperado ':' após nome da cena")
        
        # Parse personagem (obrigatório)
        personagem = self.parser_personagem()
        
        # Parse comandos
        comandos = self.parser_comandos()
        
        # Consome FIM_CENA
        self.consumir(TipoToken.FIM_CENA, "Esperado 'FIM_CENA' no final do programa")
        
        return Programa(nome_cena, personagem, comandos)
    
    def parser_personagem(self) -> Personagem:
        """<personagem> ::= PERSONAGEM IDENTIFICADOR : <declaracao_variaveis>"""
        # Consome personagem
        self.consumir(TipoToken.PERSONAGEM, "Esperado 'PERSONAGEM'")
        
        # Nome do personagem
        nome_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome do personagem")
        nome = nome_token.lexema
        
        # Dois pontos
        self.consumir(TipoToken.DOIS_PONTOS, "Esperado ':' após nome do personagem")
        
        # Parse declarações de variáveis
        declaracoes = self.parser_declaracao_variaveis()
        
        return Personagem(nome, declaracoes)
    
    def parser_declaracao_variaveis(self) -> List[Declaracao]:
        """<declaracao_variaveis> ::= MEMORIA : <lista_declaracoes> FIM_MEMORIA | ε"""
        declaracoes = []
        
        # Se não houver memoria, retorna lista vazia (declarações são opcionais)
        if not self.verificar(TipoToken.MEMORIA):
            return declaracoes
        
        # Consome memoria
        self.consumir(TipoToken.MEMORIA, "Esperado 'MEMORIA'")
        
        # Dois pontos
        self.consumir(TipoToken.DOIS_PONTOS, "Esperado ':' após 'MEMORIA'")
        
        # Parse lista de declarações
        declaracoes = self.parser_lista_declaracoes()
        
        # Consome FIM_MEMORIA
        self.consumir(TipoToken.FIM_MEMORIA, "Esperado 'FIM_MEMORIA' após declarações")
        
        return declaracoes
    
    def parser_lista_declaracoes(self) -> List[Declaracao]:
        """<lista_declaracoes> ::= <declaracao> <lista_declaracoes> | <declaracao>"""
        declaracoes = []
        
        # Continua enquanto houver declarações (identificadores seguidos de :)
        while self.verificar(TipoToken.IDENTIFICADOR):
            declaracao = self.parser_declaracao()
            declaracoes.append(declaracao)
        
        return declaracoes
    
    def parser_declaracao(self) -> Declaracao:
        """<declaracao> ::= IDENTIFICADOR : (VARCHAR | INT | FLOAT) ;"""
        # Nome da variável
        nome_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado identificador na declaração")
        nome = nome_token.lexema
        
        # Dois pontos
        self.consumir(TipoToken.DOIS_PONTOS, "Esperado ':' após identificador")
        
        # Tipo (VARCHAR, INT ou FLOAT)
        tipo = None
        if self.verificar(TipoToken.VARCHAR):
            self.avancar()
            tipo = "VARCHAR"
        elif self.verificar(TipoToken.INT):
            self.avancar()
            tipo = "INT"
        elif self.verificar(TipoToken.FLOAT):
            self.avancar()
            tipo = "FLOAT"
        else:
            raise ErroSintatico(
                "Esperado tipo (VARCHAR, INT ou FLOAT)",
                self.token_atual.linha,
                self.token_atual.coluna
            )
        
        # Ponto e vírgula
        self.consumir(TipoToken.PONTO_VIRGULA, "Esperado ';' após declaração")
        
        return Declaracao(nome, tipo)
    
    def parser_comandos(self) -> List[Comando]:
        """<comandos> ::= <comando> <comandos> | <comando>"""
        comandos = []
        
        # Continua enquanto houver comandos válidos (até encontrar FIM_CENA ou EOF)
        while (not self.verificar(TipoToken.EOF) and
               not self.verificar(TipoToken.FIM_CENA) and
               (self.verificar(TipoToken.LEIA) or 
                self.verificar(TipoToken.DIZ) or 
                self.verificar(TipoToken.IDENTIFICADOR))):
            
            comando = self.parser_comando()
            comandos.append(comando)
        
        return comandos
    
    def parser_comando(self) -> Comando:
        """<comando> ::= <comando_leitura> | <comando_escrita> | <comando_atribuicao>"""
        if self.verificar(TipoToken.LEIA):
            return self.parser_comando_leitura()
        elif self.verificar(TipoToken.IDENTIFICADOR):
            # Precisa fazer lookahead para distinguir entre "Personagem diz" e "variavel ="
            if self.posicao + 1 < len(self.tokens) and self.tokens[self.posicao + 1].tipo == TipoToken.DIZ:
                return self.parser_comando_escrita()
            else:
                return self.parser_comando_atribuicao()
        else:
            raise ErroSintatico(
                "Esperado comando (LEIA, DIZ ou atribuição)",
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
        """<comando_escrita> ::= IDENTIFICADOR DIZ <expressao> ;"""
        # Nome do personagem
        personagem_token = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome do personagem")
        personagem = personagem_token.lexema
        
        # diz
        self.consumir(TipoToken.DIZ, "Esperado 'DIZ' após nome do personagem")
        
        # Expressão (pode ser variável ou número)
        expressao = self.parser_expressao()
        
        # Ponto e vírgula
        self.consumir(TipoToken.PONTO_VIRGULA, "Esperado ';' após comando DIZ")
        
        return ComandoEscrita(personagem, expressao)
    
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
        """<elemento> ::= IDENTIFICADOR | NUM_INTEIRO | NUM_REAL | STRING | ( <expressao> )"""
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
        
        elif self.verificar(TipoToken.STRING):
            valor = self.token_atual.lexema
            self.avancar()
            return Elemento(valor, "STRING")
        
        elif self.verificar(TipoToken.PARENTESE_ESQ):
            self.avancar()
            expressao = self.parser_expressao()
            self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após expressão")
            return Elemento(expressao, "EXPRESSAO")
        
        else:
            raise ErroSintatico(
                "Esperado identificador, número, string ou expressão entre parênteses",
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
            print(f"{indentacao}Programa (Cena: {no.nome_cena}):")
            print(f"{indentacao}  Personagem: {no.personagem.nome}")
            if no.personagem.declaracoes:
                print(f"{indentacao}    Declarações:")
                for decl in no.personagem.declaracoes:
                    print(f"{indentacao}      {decl.nome}: {decl.tipo}")
            print(f"{indentacao}  Comandos:")
            for comando in no.comandos:
                self.imprimir_ast(comando, nivel + 2)
        
        elif isinstance(no, ComandoLeitura):
            print(f"{indentacao}Comando Leitura: LEIA {no.variavel}")
        
        elif isinstance(no, ComandoEscrita):
            print(f"{indentacao}Comando Escrita: {no.personagem} diz")
            self.imprimir_ast(no.expressao, nivel + 1)
        
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
