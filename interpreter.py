# Em interpreter.py

from typing import Dict, Any, Union
from parser import *

class InterpretadorPiLang:
    def __init__(self):
        self.variaveis: Dict[str, Union[int, float, str]] = {}
        self.tipos_variaveis: Dict[str, str] = {}  # Armazena o tipo de cada variável
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
            self.tipos_variaveis[declaracao.nome] = declaracao.tipo  # Armazena o tipo
            if declaracao.tipo == "VARCHAR":
                self.variaveis[declaracao.nome] = ""
            elif declaracao.tipo == "INT":
                self.variaveis[declaracao.nome] = 0
            elif declaracao.tipo == "FLOAT":
                self.variaveis[declaracao.nome] = 0.0
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
    
    def executar_leia(self, comando: ComandoLeitura):
        """Executa comando LEIA com validação de tipos"""
        nome_variavel = comando.variavel
        
        # Verifica se a variável foi declarada
        if nome_variavel not in self.tipos_variaveis:
            # Variável não declarada - permite qualquer tipo (compatibilidade)
            tipo_variavel = None
        else:
            tipo_variavel = self.tipos_variaveis[nome_variavel]
        
        valor_entrada = None
        
        if self.indice_entrada < len(self.entrada_simulada):
            valor_entrada = self.entrada_simulada[self.indice_entrada]
            self.indice_entrada += 1
            print(f"LEIA {nome_variavel} -> {valor_entrada}")
        else:
            # Em ambiente web, não usa input() - usa valor padrão
            if tipo_variavel == "VARCHAR":
                valor_entrada = ""
            elif tipo_variavel == "INT":
                valor_entrada = 0
            elif tipo_variavel == "FLOAT":
                valor_entrada = 0.0
            else:
                valor_entrada = ""
            print(f"LEIA {nome_variavel} -> '{valor_entrada}' (sem entrada, usando valor padrão)")

        # Valida e converte o valor conforme o tipo da variável
        valor_final = self._validar_e_converter_valor(nome_variavel, valor_entrada, tipo_variavel)
        self.variaveis[nome_variavel] = valor_final
    
    def _validar_e_converter_valor(self, nome_variavel: str, valor_entrada, tipo_variavel: str = None):
        """Valida e converte valor de entrada conforme o tipo da variável"""
        if isinstance(valor_entrada, str):
            valor_entrada_limpo = valor_entrada.strip('"\'')
        else:
            valor_entrada_limpo = str(valor_entrada)
        
        # Se não há tipo definido, aceita qualquer coisa (compatibilidade)
        if tipo_variavel is None:
            # Tenta converter para número se possível
            if valor_entrada_limpo and (valor_entrada_limpo.replace('.', '', 1).replace('-', '', 1).isdigit()):
                try:
                    return float(valor_entrada_limpo) if '.' in valor_entrada_limpo else int(valor_entrada_limpo)
                except (ValueError, TypeError):
                    return valor_entrada_limpo
            return valor_entrada_limpo
        
        # Validação baseada no tipo
        if tipo_variavel == "VARCHAR":
            # VARCHAR aceita qualquer coisa (incluindo números como string)
            return valor_entrada_limpo
        
        elif tipo_variavel == "INT":
            # INT só aceita números inteiros
            if not valor_entrada_limpo or not valor_entrada_limpo.replace('-', '', 1).isdigit():
                raise ValueError(f"Erro de tipo: variável '{nome_variavel}' é do tipo INT, mas recebeu valor não numérico: '{valor_entrada_limpo}'")
            try:
                return int(valor_entrada_limpo)
            except ValueError:
                raise ValueError(f"Erro de tipo: variável '{nome_variavel}' é do tipo INT, mas recebeu valor inválido: '{valor_entrada_limpo}'")
        
        elif tipo_variavel == "FLOAT":
            # FLOAT só aceita números (inteiros ou reais)
            if not valor_entrada_limpo or not valor_entrada_limpo.replace('.', '', 1).replace('-', '', 1).isdigit():
                raise ValueError(f"Erro de tipo: variável '{nome_variavel}' é do tipo FLOAT, mas recebeu valor não numérico: '{valor_entrada_limpo}'")
            try:
                return float(valor_entrada_limpo)
            except ValueError:
                raise ValueError(f"Erro de tipo: variável '{nome_variavel}' é do tipo FLOAT, mas recebeu valor inválido: '{valor_entrada_limpo}'")
        
        return valor_entrada_limpo

    def executar_escreva(self, comando: ComandoEscrita):
        """Executa comando diz (escrita teatral)"""
        try:
            valor = self.avaliar_expressao(comando.expressao)
            print(f"{comando.personagem} diz: {valor}")
        except Exception as e:
            print(f"Erro ao executar diz: {e}")
    
    def executar_atribuicao(self, comando: ComandoAtribuicao):
        """Executa comando de atribuição"""
        try:
            valor = self.avaliar_expressao(comando.expressao)
            self.variaveis[comando.variavel] = valor
            print(f"{comando.variavel} = {valor}")
        except Exception as e:
            print(f"Erro ao executar atribuição: {e}")
    
    def avaliar_expressao(self, expressao: Expressao) -> Union[int, float, str]:
        """Avalia uma expressão e retorna seu valor"""
        if isinstance(expressao, ExpressaoSimples):
            return self.avaliar_expressao_simples(expressao)
        else:
            raise Exception(f"Tipo de expressão não suportado: {type(expressao)}")
    
    def avaliar_expressao_simples(self, expressao: ExpressaoSimples) -> Union[int, float, str]:
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
                # Se ambos são strings, concatena; caso contrário, soma números
                if isinstance(resultado, str) or isinstance(valor_termo, str):
                    resultado = str(resultado) + str(valor_termo)
                else:
                    resultado += valor_termo
            elif operador == '-':
                # Subtração só funciona com números
                if isinstance(resultado, str) or isinstance(valor_termo, str):
                    raise Exception("Operador '-' não pode ser usado com strings")
                resultado -= valor_termo
            else:
                raise Exception(f"Operador não suportado em expressão: {operador}")
        
        return resultado
    
    def avaliar_termo(self, termo: Termo) -> Union[int, float, str]:
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
    
    def avaliar_fator(self, fator: Fator) -> Union[int, float, str]:
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
    
    def avaliar_elemento(self, elemento: Elemento) -> Union[int, float, str]:
        """Avalia um elemento"""
        if elemento.tipo == 'IDENTIFICADOR':
            if elemento.valor not in self.variaveis or self.variaveis[elemento.valor] is None:
                raise Exception(f"Variável '{elemento.valor}' não inicializada")
            return self.variaveis[elemento.valor]
        elif elemento.tipo == 'NUM_INTEIRO':
            return int(elemento.valor)
        elif elemento.tipo == 'NUM_REAL':
            return float(elemento.valor)
        elif elemento.tipo == 'STRING':
            # Remove as aspas da string
            return elemento.valor.strip('"\'')
        elif elemento.tipo == 'EXPRESSAO':
            return self.avaliar_expressao(elemento.valor)
        else:
            raise Exception(f"Tipo de elemento não suportado: {elemento.tipo}")
    
    def limpar(self):
        """Limpa o estado do interpretador"""
        self.variaveis.clear()
        self.entrada_simulada.clear()
        self.indice_entrada = 0