from lexer import Lexer

def testar_lexer():
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
    
    print("=== Teste do Analisador Léxico ===")
    print("Código fonte:")
    print(codigo_pi)
    print("\nTokens gerados:")
    
    lexer = Lexer(codigo_pi)
    tokens, erros_lexicos = lexer.tokenizar()
    
    if erros_lexicos:
        print("\nErros léxicos encontrados:")
        for erro in erros_lexicos:
            print(erro)
    
    for token in tokens:
        print(token)

def testar_lexer_com_erros():
    # Código com erros léxicos
    codigo_com_erros = """
    INICIO
        VARIAVEIS
            a@: INTEIRO;  // @ é inválido
            b: INTEIRO;
        FIM_VARIAVEIS
        
        LEIA a;
        b = 3.14;  // número real
        c = a + #b;  // # é inválido
    FIM
    """
    
    print("\n=== Teste do Analisador Léxico com Erros ===")
    print("Código fonte com erros:")
    print(codigo_com_erros)
    print("\nTokens gerados:")
    
    lexer = Lexer(codigo_com_erros)
    tokens, erros_lexicos = lexer.tokenizar()
    
    if erros_lexicos:
        print("\nErros léxicos encontrados:")
        for erro in erros_lexicos:
            print(erro)
    
    for token in tokens:
        print(token)

if __name__ == "__main__":
    testar_lexer()
    testar_lexer_com_erros()
