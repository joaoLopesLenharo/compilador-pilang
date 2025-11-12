import os
from lexer import Lexer
from parser import Parser

def testar_arquivo_pi(nome_arquivo):
    """Testa um arquivo .pi individual"""
    print(f"\n=== Testando arquivo: {nome_arquivo} ===")
    
    try:
        # Lê o arquivo
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        print("Código fonte:")
        print(codigo)
        
        # Análise léxica
        print("\nTokens gerados:")
        lexer = Lexer(codigo)
        tokens, erros_lexicos = lexer.tokenizar()
        
        if erros_lexicos:
            print("\nErros léxicos encontrados:")
            for erro in erros_lexicos:
                print(erro)
        
        for token in tokens:
            if token.tipo != 'EOF':  # Não mostra o token EOF
                print(token)
        
        # Análise sintática
        print("\nAnálise sintática:")
        parser = Parser(tokens)
        programa = parser.parse()
        
        if programa:
            print("\nÁrvore Sintática Abstrata (AST):")
            parser.imprimir_ast(programa)
            print("\n[OK] Análise concluída com sucesso!")
        else:
            print("\n[ERRO] Falha na análise sintática!")
            
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {nome_arquivo}")
    except Exception as e:
        print(f"[ERRO] Erro ao processar arquivo: {e}")

def main():
    """Função principal que testa todos os exemplos"""
    print("=== Testador de Programas PiLang ===")
    
    # Lista de arquivos de exemplo
    exemplos = [
        "exemplos/exemplo_simples.pi",
        "exemplos/exemplo_matematico.pi",
        "exemplos/exemplo_reais.pi",
        "exemplos/exemplo_sem_variaveis.pi",
        "exemplos/exemplo_com_erros.pi"
    ]
    
    # Testa cada arquivo
    for exemplo in exemplos:
        testar_arquivo_pi(exemplo)
        print("\n" + "="*60)

if __name__ == "__main__":
    main()
