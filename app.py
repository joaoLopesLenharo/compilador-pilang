import io
from contextlib import redirect_stdout
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tokens import TipoToken
from lexer import Lexer
from parser import Parser, ErroSintatico
from interpreter import InterpretadorPiLang

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve a página HTML principal"""
    return send_from_directory('.', 'index.html') 

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
    except Exception as e:
        # Captura qualquer outro erro inesperado
        return jsonify({'status': 'erro', 'tipo': 'desconhecido', 'mensagem': str(e)})

@app.route('/executar', methods=['POST'])
def executar_codigo():
    """Endpoint para executar o código e retornar a saída."""
    data = request.get_json()
    codigo = data.get('codigo', '')
    entradas = data.get('entradas', [])

    try:
        # 1. Análise Léxica
        lexer = Lexer(codigo)
        tokens, erros_lexicos = lexer.tokenizar()
        if erros_lexicos:
            return jsonify({'status': 'erro', 'output': '\n'.join(erros_lexicos)})

        # 2. Análise Sintática
        parser = Parser(tokens)
        ast = parser.parse()

        # 3. Execução (Interpretador)
        interpretador = InterpretadorPiLang()
        interpretador.definir_entrada(entradas)

        # Captura a saída do console (prints do interpretador)
        f = io.StringIO()
        with redirect_stdout(f):
            interpretador.executar_programa(ast)
        
        output = f.getvalue()
        
        return jsonify({
            'status': 'sucesso',
            'output': output,
            'variaveis_finais': interpretador.variaveis
        })

    except ErroSintatico as e:
        output = f"Erro de Sintaxe na linha {e.linha}, coluna {e.coluna}:\n{e.mensagem}"
        return jsonify({'status': 'erro', 'output': output})
    except Exception as e:
        return jsonify({'status': 'erro', 'output': f"Erro de execução:\n{str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)