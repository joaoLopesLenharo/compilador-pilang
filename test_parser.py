from lexer import Lexer
from parser import Parser

def testar_parser():
    # Código de exemplo em PiLang
    codigo_pi = """
    INICIO
        VARIAVEIS
            a: INTEIRO;
            b: INTEIRO;
            resultado: INTEIRO;
        FIM_VARIAVEIS
        
        // Este é um comentário
        LEIA a;
        LEIA b;
        resultado = a + b;
        ESCREVA resultado;
    FIM
    """
    
    print("=== Teste do Analisador Sintático ===")
    print("Código fonte:")
    print(codigo_pi)
    print("\nAnálise sintática:")
    
    # Primeiro, tokeniza o código
    lexer = Lexer(codigo_pi)
    tokens, erros_lexicos = lexer.tokenizar()
    
    if erros_lexicos:
        print("\nErros léxicos encontrados:")
        for erro in erros_lexicos:
            print(erro)
    
    # Depois, faz a análise sintática
    parser = Parser(tokens)
    programa = parser.parse()
    
    if programa:
        print("\nÁrvore Sintática Abstrata (AST):")
        parser.imprimir_ast(programa)
        print("\nAnálise sintática concluída com sucesso!")
    else:
        print("\nFalha na análise sintática!")

def testar_parser_com_expressoes_complexas():
    # Código com expressões mais complexas
    codigo_complexo = """
    INICIO
        VARIAVEIS
            x: INTEIRO;
            y: INTEIRO;
            z: REAL;
        FIM_VARIAVEIS
        
        LEIA x;
        LEIA y;
        z = x + y * 2 ^ 3;
        ESCREVA z;
    FIM
    """
    
    print("\n=== Teste do Analisador Sintático com Expressões Complexas ===")
    print("Código fonte:")
    print(codigo_complexo)
    print("\nAnálise sintática:")
    
    lexer = Lexer(codigo_complexo)
    tokens, erros_lexicos = lexer.tokenizar()
    
    if erros_lexicos:
        print("\nErros léxicos encontrados:")
        for erro in erros_lexicos:
            print(erro)
    
    parser = Parser(tokens)
    programa = parser.parse()
    
    if programa:
        print("\nÁrvore Sintática Abstrata (AST):")
        parser.imprimir_ast(programa)
        print("\nAnálise sintática concluída com sucesso!")
    else:
        print("\nFalha na análise sintática!")

def testar_parser_com_erros():
    # Código com erros sintáticos
    codigo_com_erros = """
    INICIO
        VARIAVEIS
            a: INTEIRO
            b: INTEIRO;
        FIM_VARIAVEIS
        
        LEIA a
        b = a + 
        ESCREVA b;
    FIM
    """
    
    print("\n=== Teste do Analisador Sintático com Erros ===")
    print("Código fonte com erros:")
    print(codigo_com_erros)
    print("\nAnálise sintática:")
    
    lexer = Lexer(codigo_com_erros)
    tokens, erros_lexicos = lexer.tokenizar()
    
    if erros_lexicos:
        print("\nErros léxicos encontrados:")
        for erro in erros_lexicos:
            print(erro)
    
    parser = Parser(tokens)
    programa = parser.parse()
    
    if programa:
        print("\nÁrvore Sintática Abstrata (AST):")
        parser.imprimir_ast(programa)
        print("\nAnálise sintática concluída com sucesso!")
    else:
        print("\nFalha na análise sintática!")

if __name__ == "__main__":
    testar_parser()
    testar_parser_com_expressoes_complexas()
    testar_parser_com_erros()
