#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste completo do compilador DRAMATICA"""

from lexer import Lexer
from parser import Parser, ErroSintatico
from interpreter import InterpretadorPiLang

def teste_case_sensitive():
    """Testa se o compilador é case-sensitive"""
    print("=" * 60)
    print("TESTE 1: Case-sensitive")
    print("=" * 60)
    
    # Teste com minúsculas - deve falhar
    codigo_erro = "cena Teste:\n    PERSONAGEM Teste:\n        MEMORIA:\n            x: INT;\n        FIM_MEMORIA\n    FIM_CENA"
    lexer = Lexer(codigo_erro)
    tokens, erros = lexer.tokenizar()
    
    if erros:
        print("✓ Erros léxicos detectados (esperado)")
    else:
        # Verifica se 'cena' foi reconhecido como identificador
        token_cena = tokens[0] if tokens else None
        if token_cena and token_cena.tipo == "IDENTIFICADOR":
            print("[OK] 'cena' em minusculas reconhecido como IDENTIFICADOR (correto)")
        else:
            print("[ERRO] Problema: 'cena' nao foi tratado corretamente")
    
    # Teste com maiúsculas - deve funcionar
    codigo_ok = "CENA Teste:\n    PERSONAGEM Teste:\n        MEMORIA:\n            x: INT;\n        FIM_MEMORIA\n    FIM_CENA"
    lexer = Lexer(codigo_ok)
    tokens, erros = lexer.tokenizar()
    
    if not erros and tokens[0].tipo == "CENA":
        print("[OK] 'CENA' em maiusculas reconhecido corretamente")
    else:
        print("[ERRO] Problema com 'CENA' em maiusculas")
    
    print()

def teste_tipos():
    """Testa os tipos VARCHAR, INT, FLOAT"""
    print("=" * 60)
    print("TESTE 2: Tipos de dados")
    print("=" * 60)
    
    codigo = """CENA Teste:
    PERSONAGEM Teste:
        MEMORIA:
            nome: VARCHAR;
            idade: INT;
            altura: FLOAT;
        FIM_MEMORIA
    LEIA nome;
    LEIA idade;
    LEIA altura;
    Teste DIZ nome;
FIM_CENA"""
    
    lexer = Lexer(codigo)
    tokens, erros = lexer.tokenizar()
    
    if erros:
        print(f"[ERRO] Erros lexicos: {erros}")
        return
    
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("[OK] Parse OK - tipos VARCHAR, INT, FLOAT aceitos")
        
        # Verifica tipos nas declarações
        tipos_encontrados = [d.tipo for d in ast.personagem.declaracoes]
        tipos_esperados = ["VARCHAR", "INT", "FLOAT"]
        
        if set(tipos_encontrados) == set(tipos_esperados):
            print(f"[OK] Tipos corretos: {tipos_encontrados}")
        else:
            print(f"[ERRO] Tipos incorretos: {tipos_encontrados}")
    except ErroSintatico as e:
        print(f"[ERRO] Erro sintatico: {e}")
    
    print()

def teste_validacao_tipos():
    """Testa validação de tipos no LEIA"""
    print("=" * 60)
    print("TESTE 3: Validação de tipos no LEIA")
    print("=" * 60)
    
    codigo = """CENA Teste:
    PERSONAGEM Teste:
        MEMORIA:
            x: INT;
            y: FLOAT;
            nome: VARCHAR;
        FIM_MEMORIA
    LEIA x;
    LEIA y;
    LEIA nome;
    Teste DIZ x;
FIM_CENA"""
    
    lexer = Lexer(codigo)
    tokens, erros = lexer.tokenizar()
    parser = Parser(tokens)
    ast = parser.parse()
    
    interp = InterpretadorPiLang()
    
    # Teste 1: VARCHAR aceita número (como string)
    print("Teste 3.1: VARCHAR aceita numero")
    interp.definir_entrada(["123"])
    try:
        interp.executar_programa(ast)
        print("[OK] VARCHAR aceitou numero como string")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
    
    # Reset
    interp = InterpretadorPiLang()
    
    # Teste 2: INT rejeita letras
    print("Teste 3.2: INT rejeita letras")
    interp.definir_entrada(["abc"])
    try:
        interp.executar_programa(ast)
        print("[ERRO] INT aceitou letras (ERRO!)")
    except ValueError as e:
        if "INT" in str(e) and ("nao numerico" in str(e) or "não numérico" in str(e) or "não num" in str(e)):
            print(f"[OK] INT rejeitou letras corretamente")
        else:
            print(f"[OK] INT rejeitou letras (mensagem: {str(e)[:60]}...)")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
    
    # Reset
    interp = InterpretadorPiLang()
    
    # Teste 3: FLOAT rejeita letras
    print("Teste 3.3: FLOAT rejeita letras")
    interp.definir_entrada(["10", "abc"])
    try:
        interp.executar_programa(ast)
        print("[ERRO] FLOAT aceitou letras (ERRO!)")
    except ValueError as e:
        if "FLOAT" in str(e) and ("nao numerico" in str(e) or "não numérico" in str(e) or "não num" in str(e)):
            print(f"[OK] FLOAT rejeitou letras corretamente")
        else:
            print(f"[OK] FLOAT rejeitou letras (mensagem: {str(e)[:60]}...)")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
    
    # Reset
    interp = InterpretadorPiLang()
    
    # Teste 4: INT aceita números inteiros
    print("Teste 3.4: INT aceita numeros inteiros")
    interp.definir_entrada(["42", "3.14", "texto"])
    try:
        interp.executar_programa(ast)
        print("[OK] INT aceitou numero inteiro")
    except ValueError as e:
        print(f"[ERRO] Erro inesperado: {e}")
    
    print()

def teste_exemplo_simples():
    """Testa o exemplo simples"""
    print("=" * 60)
    print("TESTE 4: Exemplo simples")
    print("=" * 60)
    
    try:
        with open("exemplos/exemplo_simples.dramatica", "r", encoding="utf-8") as f:
            codigo = f.read()
        
        lexer = Lexer(codigo)
        tokens, erros = lexer.tokenizar()
        
        if erros:
            print(f"[ERRO] Erros lexicos: {erros}")
            return
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interp = InterpretadorPiLang()
        interp.definir_entrada([10, 20])
        interp.executar_programa(ast)
        
        print("[OK] Exemplo simples executado com sucesso")
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
    
    print()

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("TESTES COMPLETOS DO COMPILADOR DRAMATICA")
    print("=" * 60 + "\n")
    
    teste_case_sensitive()
    teste_tipos()
    teste_validacao_tipos()
    teste_exemplo_simples()
    
    print("=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

if __name__ == "__main__":
    main()

