import io
import uuid
from contextlib import redirect_stdout
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tokens import TipoToken
from lexer import Lexer
from parser import Parser, ErroSintatico, ErroSemantico, ComandoLeitura, ComandoEscrita, ComandoAtribuicao
from interpreter import InterpretadorPiLang

app = Flask(__name__)
CORS(app)

# Armazena sessões de execução ativas
sessoes_execucao = {}

@app.route('/')
def index():
    """Serve a página HTML principal"""
    return send_from_directory('.', 'index.html')

@app.route('/arquivo/<path:arquivo>')
def servir_arquivo(arquivo):
    """Serve arquivos de exemplo para carregar no editor"""
    try:
        return send_from_directory('.', arquivo)
    except Exception as e:
        return jsonify({'erro': str(e)}), 404 

@app.route('/tokenizar', methods=['POST'])
def tokenizar_codigo():
    """Endpoint para realizar apenas a tokenização do código."""
    data = request.get_json()
    codigo = data.get('codigo', '')

    if not codigo.strip():
        return jsonify({'status': 'erro', 'output': 'Digite seu código para começar.'})

    try:
        # Análise Léxica
        lexer = Lexer(codigo)
        tokens, erros_lexicos = lexer.tokenizar()
        
        if erros_lexicos:
            output = "=== ERROS LÉXICOS ===\n"
            output += '\n'.join(erros_lexicos)
            output += "\n\n=== TOKENS ENCONTRADOS ATÉ O ERRO ===\n"
            for token in tokens:
                output += str(token) + '\n'
            return jsonify({'status': 'erro', 'output': output})
        
        # Formata os tokens para exibição
        output = "=== TOKENIZAÇÃO CONCLUÍDA ===\n"
        output += f"Total de tokens encontrados: {len(tokens)}\n\n"
        output += "=== LISTA DE TOKENS ===\n"
        for i, token in enumerate(tokens, 1):
            output += f"{i:3d}. {str(token)}\n"
        
        return jsonify({'status': 'sucesso', 'output': output})

    except Exception as e:
        return jsonify({'status': 'erro', 'output': f"Erro durante tokenização:\n{str(e)}"})

@app.route('/analise_sintatica', methods=['POST'])
def analise_sintatica_codigo():
    """Endpoint para realizar análise sintática (requer tokens válidos)."""
    data = request.get_json()
    codigo = data.get('codigo', '')

    if not codigo.strip():
        return jsonify({'status': 'erro', 'output': 'Digite seu código para começar.'})

    try:
        # 1. Análise Léxica (necessária para análise sintática)
        lexer = Lexer(codigo)
        tokens, erros_lexicos = lexer.tokenizar()
        if erros_lexicos:
            output = "=== ERRO: Não é possível realizar análise sintática com erros léxicos ===\n\n"
            output += "Erros léxicos encontrados:\n"
            output += '\n'.join(erros_lexicos)
            return jsonify({'status': 'erro', 'output': output})

        # 2. Análise Sintática
        parser = Parser(tokens)
        ast = parser.parse()

        # Formata informações da AST
        output = "=== ANÁLISE SINTÁTICA CONCLUÍDA ===\n\n"
        output += f"Cena: {ast.nome_cena}\n"
        output += f"Personagem: {ast.personagem.nome}\n\n"
        
        if ast.personagem.declaracoes:
            output += "=== DECLARAÇÕES DE VARIÁVEIS ===\n"
            for decl in ast.personagem.declaracoes:
                output += f"  {decl.nome}: {decl.tipo}\n"
            output += "\n"
        
        output += f"=== COMANDOS ENCONTRADOS: {len(ast.comandos)} ===\n"
        for i, comando in enumerate(ast.comandos, 1):
            if isinstance(comando, ComandoLeitura):
                output += f"{i}. LEIA {comando.variavel}\n"
            elif isinstance(comando, ComandoEscrita):
                output += f"{i}. {comando.personagem} DIZ [expressão]\n"
            elif isinstance(comando, ComandoAtribuicao):
                output += f"{i}. {comando.variavel} = [expressão]\n"
        
        output += "\n✓ Sintaxe válida! O código está pronto para compilação/execução."
        
        return jsonify({'status': 'sucesso', 'output': output})

    except ErroSintatico as e:
        output = "=== ERRO DE SINTAXE ===\n\n"
        output += f"Linha: {e.linha}, Coluna: {e.coluna}\n"
        output += f"Mensagem: {e.mensagem}\n"
        return jsonify({'status': 'erro', 'output': output})
    except ErroSemantico as e:
        output = "=== ERRO SEMÂNTICO ===\n\n"
        if e.linha is not None and e.coluna is not None:
            output += f"Linha: {e.linha}, Coluna: {e.coluna}\n"
        output += f"Mensagem: {e.mensagem}\n"
        return jsonify({'status': 'erro', 'output': output})
    except Exception as e:
        return jsonify({'status': 'erro', 'output': f"Erro durante análise sintática:\n{str(e)}"})

@app.route('/analisar', methods=['POST'])
def analisar_codigo():
    data = request.get_json()
    codigo = data.get('codigo', '')

    if not codigo.strip():
        return jsonify({'status': 'sucesso', 'mensagem': 'Digite seu código para começar.'})

    try:
        # 1. Análise Léxica
        lexer = Lexer(codigo)
        tokens, erros_lexicos = lexer.tokenizar()
        if erros_lexicos:
            # Se houver erros léxicos, retorna o primeiro deles
            return jsonify({'status': 'erro', 'tipo': 'lexico', 'mensagem': erros_lexicos[0]})

        # 2. Análise Sintática
        parser = Parser(tokens)
        parser.parse() # Se houver erro, vai lançar ErroSintatico

        return jsonify({'status': 'sucesso', 'mensagem': 'Sintaxe válida!'})

    except ErroSintatico as e:
        # Captura o erro sintático e o formata para o frontend
        return jsonify({
            'status': 'erro', 
            'tipo': 'sintatico',
            'mensagem': e.mensagem,
            'linha': e.linha,
            'coluna': e.coluna
        })
    except ErroSemantico as e:
        # Captura o erro semântico e o formata para o frontend
        return jsonify({
            'status': 'erro',
            'tipo': 'semantico',
            'mensagem': e.mensagem,
            'linha': e.linha if e.linha else None,
            'coluna': e.coluna if e.coluna else None
        })
    except Exception as e:
        # Captura qualquer outro erro inesperado
        return jsonify({'status': 'erro', 'tipo': 'desconhecido', 'mensagem': str(e)})

class InterpretadorInterativo(InterpretadorPiLang):
    """Interpretador que suporta entrada interativa"""
    def __init__(self):
        super().__init__()
        self.aguardando_entrada = False
        self.variavel_aguardando = None
        self.output_buffer = []
    
    def executar_leia(self, comando: ComandoLeitura):
        """Executa comando LEIA com entrada interativa"""
        nome_variavel = comando.variavel
        
        # Se não há entrada simulada disponível, solicita entrada interativa
        if self.indice_entrada >= len(self.entrada_simulada):
            self.aguardando_entrada = True
            self.variavel_aguardando = nome_variavel
            print(f"LEIA {nome_variavel}: ", end='', flush=True)
            raise InterruptedError("Aguardando entrada do usuário")
        
        # Usa entrada simulada se disponível
        valor_entrada = self.entrada_simulada[self.indice_entrada]
        self.indice_entrada += 1
        print(f"LEIA {nome_variavel} -> {valor_entrada}")
        
        # Processa o valor
        self._processar_valor_leia(nome_variavel, valor_entrada)
    
    def fornecer_entrada(self, valor_entrada: str):
        """Fornece entrada para o comando LEIA que estava aguardando"""
        if not self.aguardando_entrada:
            raise Exception("Nenhum comando LEIA aguardando entrada")
        
        nome_variavel = self.variavel_aguardando
        print(f"{valor_entrada}")
        self._processar_valor_leia(nome_variavel, valor_entrada)
        
        self.aguardando_entrada = False
        self.variavel_aguardando = None
    
    def _processar_valor_leia(self, nome_variavel: str, valor_entrada):
        """Processa o valor de entrada do LEIA com validação de tipos"""
        tipo_variavel = self.tipos_variaveis.get(nome_variavel)
        valor_final = self._validar_e_converter_valor(nome_variavel, valor_entrada, tipo_variavel)
        self.variaveis[nome_variavel] = valor_final

@app.route('/executar', methods=['POST'])
def executar_codigo():
    """Endpoint para executar o código com suporte a entrada interativa."""
    data = request.get_json()
    codigo = data.get('codigo', '')

    try:
        # 1. Análise Léxica
        lexer = Lexer(codigo)
        tokens, erros_lexicos = lexer.tokenizar()
        if erros_lexicos:
            return jsonify({'status': 'erro', 'output': '\n'.join(erros_lexicos)})

        # 2. Análise Sintática
        parser = Parser(tokens)
        ast = parser.parse()

        # 3. Execução (Interpretador Interativo)
        interpretador = InterpretadorInterativo()
        session_id = str(uuid.uuid4())
        
        # Armazena a sessão
        sessoes_execucao[session_id] = {
            'interpretador': interpretador,
            'ast': ast,
            'comandos_restantes': ast.comandos.copy(),
            'indice_comando': 0
        }
        
        # Mostra informações iniciais
        f = io.StringIO()
        with redirect_stdout(f):
            print(f"\n=== EXECUÇÃO DA CENA: {ast.nome_cena} ===")
            print(f"Personagem: {ast.personagem.nome}")
            print()
        
        output_inicial = f.getvalue()
        
        # Executa o programa
        resultado = executar_programa_interativo(session_id)
        
        # Adiciona o output inicial ao resultado
        dados = resultado.get_json()
        dados['output'] = output_inicial + dados.get('output', '')
        return jsonify(dados)

    except ErroSintatico as e:
        output = f"Erro de Sintaxe na linha {e.linha}, coluna {e.coluna}:\n{e.mensagem}"
        return jsonify({'status': 'erro', 'output': output})
    except ErroSemantico as e:
        output = "=== ERRO SEMÂNTICO ===\n\n"
        if e.linha is not None and e.coluna is not None:
            output += f"Linha: {e.linha}, Coluna: {e.coluna}\n"
        output += f"Mensagem: {e.mensagem}\n"
        return jsonify({'status': 'erro', 'output': output})
    except Exception as e:
        return jsonify({'status': 'erro', 'output': f"Erro de execução:\n{str(e)}"})

@app.route('/continuar_execucao', methods=['POST'])
def continuar_execucao():
    """Continua a execução de um programa que estava aguardando entrada."""
    data = request.get_json()
    session_id = data.get('session_id')
    entrada = data.get('entrada', '')
    
    if session_id not in sessoes_execucao:
        return jsonify({'status': 'erro', 'output': 'Sessão inválida ou expirada.'})
    
    sessao = sessoes_execucao[session_id]
    interpretador = sessao['interpretador']
    
    # Fornece a entrada ao interpretador
    try:
        interpretador.fornecer_entrada(entrada)
    except Exception as e:
        return jsonify({'status': 'erro', 'output': f"Erro ao processar entrada: {str(e)}"})
    
    # Incrementa o índice do comando, pois já processamos a entrada do LEIA atual
    sessao['indice_comando'] += 1
    
    # Continua a execução
    return executar_programa_interativo(session_id)

def executar_programa_interativo(session_id):
    """Executa o programa de forma interativa, parando quando precisa de entrada."""
    sessao = sessoes_execucao[session_id]
    interpretador = sessao['interpretador']
    ast = sessao['ast']
    comandos_restantes = sessao['comandos_restantes']
    indice_comando = sessao['indice_comando']
    
    # Inicializa o interpretador se necessário
    if indice_comando == 0:
        # Processa declarações de variáveis do personagem
        for declaracao in ast.personagem.declaracoes:
            interpretador.tipos_variaveis[declaracao.nome] = declaracao.tipo
            if declaracao.tipo == "VARCHAR":
                interpretador.variaveis[declaracao.nome] = ""
            elif declaracao.tipo == "INT":
                interpretador.variaveis[declaracao.nome] = 0
            elif declaracao.tipo == "FLOAT":
                interpretador.variaveis[declaracao.nome] = 0.0
    
    # Captura a saída
    f = io.StringIO()
    
    try:
        with redirect_stdout(f):
            # Executa os comandos restantes
            while indice_comando < len(comandos_restantes):
                comando = comandos_restantes[indice_comando]
                
                try:
                    interpretador.executar_comando(comando)
                    indice_comando += 1
                except InterruptedError:
                    # Precisa de entrada do usuário
                    output = f.getvalue()
                    sessao['indice_comando'] = indice_comando
                    return jsonify({
                        'status': 'aguardando_entrada',
                        'session_id': session_id,
                        'output': output,
                        'variavel': interpretador.variavel_aguardando
                    })
                except ValueError as e:
                    # Erro de validação de tipo
                    output = f.getvalue()
                    output += f"\nERRO: {str(e)}"
                    del sessoes_execucao[session_id]
                    return jsonify({
                        'status': 'erro',
                        'output': output
                    })
            
            # Execução completa - mostra estado final
            print("\n=== ESTADO FINAL DAS VARIÁVEIS ===")
            for nome, valor in interpretador.variaveis.items():
                print(f"{nome} = {valor}")
            
            output = f.getvalue()
            del sessoes_execucao[session_id]
            return jsonify({
                'status': 'sucesso',
                'output': output,
                'variaveis_finais': interpretador.variaveis
            })
            
    except Exception as e:
        output = f.getvalue() + f"\nErro: {str(e)}"
        if session_id in sessoes_execucao:
            del sessoes_execucao[session_id]
        return jsonify({'status': 'erro', 'output': output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)