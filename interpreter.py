# Em interpreter.py

from typing import Dict, Any, Union
from parser import *

class InterpretadorPiLang:
    def __init__(self):
        self.variaveis: Dict[str, Union[int, float]] = {}
        self.entrada_simulada = []
        self.indice_entrada = 0
    
    def definir_entrada(self, valores: list):
        """Define valores de entrada simulados para os comandos LEIA"""
        self.entrada_simulada = valores
        self.indice_entrada = 0
    
    def executar_programa(self, programa: Programa):
        """Executa um programa DRAMATICA completo"""
        print(f"\n=== EXECUÇÃO DA CENA: {programa.nome_cena} ===")
        print(f"Personagem: {programa.personagem.nome}")
        
        # Processa declarações de variáveis do personagem (inicializa com valor padrão)
        for declaracao in programa.personagem.declaracoes:
            if declaracao.tipo == "NUMBER":
                self.variaveis[declaracao.nome] = 0
            print(f"Declarada: {declaracao.nome}: {declaracao.tipo}")
        
        # Executa os comandos
        for comando in programa.comandos:
            self.executar_comando(comando)
        
        print("\n=== ESTADO FINAL DAS VARIÁVEIS ===")
        for nome, valor in self.variaveis.items():
            print(f"{nome} = {valor}")
    
    def executar_comando(self, comando: Comando):
        """Executa um comando individual"""
        if isinstance(comando, ComandoLeitura):
            self.executar_leia(comando)  # A chamada está aqui
        elif isinstance(comando, ComandoEscrita):
            self.executar_escreva(comando)
        elif isinstance(comando, ComandoAtribuicao):
            self.executar_atribuicao(comando)
    
    def executar_leia(self, comando: ComandoLeitura): # A definição está aqui, com nome e indentação corretos
        """Executa comando LEIA com conversão de tipo"""
        nome_variavel = comando.variavel
        valor_entrada = None
        
        if self.indice_entrada < len(self.entrada_simulada):
            valor_entrada = self.entrada_simulada[self.indice_entrada]
            self.indice_entrada += 1
            print(f"LEIA {nome_variavel} -> {valor_entrada}")
        else:
            # Em ambiente web, não usa input() - usa valor padrão 0
            valor_entrada = 0
            print(f"LEIA {nome_variavel} -> {valor_entrada} (sem entrada, usando 0)")

        try:
            if '.' in str(valor_entrada):
                valor_convertido = float(valor_entrada)
            else:
                valor_convertido = int(valor_entrada)
            self.variaveis[nome_variavel] = valor_convertido
        except (ValueError, TypeError):
            print(f"Aviso: entrada '{valor_entrada}' para '{nome_variavel}' não é um número válido. Tratando como 0.")
            self.variaveis[nome_variavel] = 0

    def executar_escreva(self, comando: ComandoEscrita):
        """Executa comando says (escrita teatral)"""
        try:
            valor = self.avaliar_expressao(comando.expressao)
            print(f"{comando.personagem} says: {valor}")
        except Exception as e:
            print(f"Erro ao executar says: {e}")
    
    def executar_atribuicao(self, comando: ComandoAtribuicao):
        """Executa comando de atribuição"""
        try:
            valor = self.avaliar_expressao(comando.expressao)
            self.variaveis[comando.variavel] = valor
            print(f"{comando.variavel} = {valor}")
        except Exception as e:
            print(f"Erro ao executar atribuição: {e}")
    
    def avaliar_expressao(self, expressao: Expressao) -> Union[int, float]:
        """Avalia uma expressão e retorna seu valor"""
        if isinstance(expressao, ExpressaoSimples):
            return self.avaliar_expressao_simples(expressao)
        else:
            raise Exception(f"Tipo de expressão não suportado: {type(expressao)}")
    
    def avaliar_expressao_simples(self, expressao: ExpressaoSimples) -> Union[int, float]:
        """Avalia uma expressão simples"""
        if not expressao.termos:
            return 0
        
        primeiro_operador, primeiro_termo = expressao.termos[0]
        if primeiro_operador:
            raise Exception("Expressão mal formada")
        
        resultado = self.avaliar_termo(primeiro_termo)
        
        for operador, termo in expressao.termos[1:]:
            valor_termo = self.avaliar_termo(termo)
            if operador == '+':
                resultado += valor_termo
            elif operador == '-':
                resultado -= valor_termo
            else:
                raise Exception(f"Operador não suportado em expressão: {operador}")
        
        return resultado
    
    def avaliar_termo(self, termo: Termo) -> Union[int, float]:
        """Avalia um termo"""
        if not termo.fatores:
            return 0
        
        primeiro_operador, primeiro_fator = termo.fatores[0]
        if primeiro_operador:
            raise Exception("Termo mal formado")
        
        resultado = self.avaliar_fator(primeiro_fator)
        
        for operador, fator in termo.fatores[1:]:
            valor_fator = self.avaliar_fator(fator)
            if operador == '*':
                resultado *= valor_fator
            elif operador == '/':
                if valor_fator == 0:
                    raise Exception("Divisão por zero")
                resultado /= valor_fator
            else:
                raise Exception(f"Operador não suportado em termo: {operador}")
        
        return resultado
    
    def avaliar_fator(self, fator: Fator) -> Union[int, float]:
        """Avalia um fator - potência tem associatividade à direita"""
        if not fator.elementos:
            return 0
        
        primeiro_operador, primeiro_elemento = fator.elementos[0]
        if primeiro_operador:
            raise Exception("Fator mal formado")
        
        # Se há apenas um elemento, retorna seu valor
        if len(fator.elementos) == 1:
            return self.avaliar_elemento(primeiro_elemento)
        
        # Potência tem associatividade à direita: avalia da direita para a esquerda
        # Exemplo: 2^3^2 = 2^(3^2) = 2^9 = 512
        # Começa pelo último elemento (que tem o operador ^)
        resultado = self.avaliar_elemento(fator.elementos[-1][1])
        
        # Avalia da direita para a esquerda, pulando o primeiro elemento (que tem operador vazio)
        for i in range(len(fator.elementos) - 2, 0, -1):
            operador, elemento = fator.elementos[i]
            if operador == '^':
                valor_elemento = self.avaliar_elemento(elemento)
                resultado = valor_elemento ** resultado
            else:
                raise Exception(f"Operador não suportado em fator: {operador}")
        
        # Avalia o primeiro elemento com o resultado acumulado
        valor_primeiro = self.avaliar_elemento(primeiro_elemento)
        resultado = valor_primeiro ** resultado
        
        return resultado
    
    def avaliar_elemento(self, elemento: Elemento) -> Union[int, float]:
        """Avalia um elemento"""
        if elemento.tipo == 'IDENTIFICADOR':
            if elemento.valor not in self.variaveis or self.variaveis[elemento.valor] is None:
                raise Exception(f"Variável '{elemento.valor}' não inicializada")
            return self.variaveis[elemento.valor]
        elif elemento.tipo == 'NUM_INTEIRO':
            return int(elemento.valor)
        elif elemento.tipo == 'NUM_REAL':
            return float(elemento.valor)
        elif elemento.tipo == 'EXPRESSAO':
            return self.avaliar_expressao(elemento.valor)
        else:
            raise Exception(f"Tipo de elemento não suportado: {elemento.tipo}")
    
    def limpar(self):
        """Limpa o estado do interpretador"""
        self.variaveis.clear()
        self.entrada_simulada.clear()
        self.indice_entrada = 0