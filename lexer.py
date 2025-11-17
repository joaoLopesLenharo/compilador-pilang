from tokens import Token, TipoToken, PALAVRAS_RESERVADAS

class Lexer:
    def __init__(self, codigo_fonte):
        self.codigo_fonte = codigo_fonte
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.codigo_fonte += '\0'  # Marcador de fim de arquivo
        
    def proximo_caractere(self):
        if self.posicao < len(self.codigo_fonte):
            return self.codigo_fonte[self.posicao]
        return '\0'
    
    def avancar(self):
        if self.posicao < len(self.codigo_fonte) and self.codigo_fonte[self.posicao] != '\0':
            if self.codigo_fonte[self.posicao] == '\n':
                self.linha += 1
                self.coluna = 1
            else:
                self.coluna += 1
            self.posicao += 1
    
    def pular_espaco_branco(self):
        while self.proximo_caractere() in ' \t\n\r':
            self.avancar()
    
    def estado_q0(self):
        """Estado inicial do autômato - decide qual caminho seguir"""
        self.pular_espaco_branco()
        
        char = self.proximo_caractere()
        
        # Fim do arquivo
        if char == '\0':
            return Token(TipoToken.EOF, '', self.linha, self.coluna)
        
        # Comentários (maior prioridade)
        if char == '/':
            return self.estado_comentario()
        
        # Strings (aspas duplas)
        elif char == '"':
            return self.estado_string()
        
        # Letras - podem ser palavras reservadas ou identificadores
        elif char.isalpha():
            return self.estado_palavra()
        
        # Dígitos - podem ser números inteiros ou reais
        elif char.isdigit():
            return self.estado_numero()
        
        # Operadores e símbolos
        elif char in '+-*/^=:;()[]{}"\'!,.>':
            return self.estado_operador()
        
        # Caractere inválido
        else:
            token = Token(TipoToken.ERRO, char, self.linha, self.coluna)
            self.avancar()
            return token
    
    def estado_comentario(self):
        """Estado para reconhecimento de comentários //"""
        linha_inicial = self.linha
        coluna_inicial = self.coluna
        
        # O caractere atual já é '/', avança para verificar o próximo
        self.avancar()  # Consome o primeiro '/'
        
        # Verifica se o próximo caractere também é '/'
        if self.proximo_caractere() == '/':
            self.avancar()  # Consome o segundo '/'
            
            # Consome tudo até o fim da linha
            while self.proximo_caractere() != '\n' and self.proximo_caractere() != '\0':
                self.avancar()
            
            # Retorna ao estado inicial para encontrar o próximo token
            return self.estado_q0()
        else:
            # Era apenas um '/', retorna operador de divisão
            # O primeiro '/' já foi consumido, então retornamos o token correto
            return Token(TipoToken.OP_DIVISAO, '/', linha_inicial, coluna_inicial)
    
    def estado_string(self):
        """Estado para reconhecimento de strings entre aspas duplas"""
        linha_inicial = self.linha
        coluna_inicial = self.coluna
        lexema = '"'  # Inclui a aspas inicial
        
        # Consome a aspas inicial
        self.avancar()
        
        # Consome caracteres até encontrar a aspas de fechamento
        while self.proximo_caractere() != '"' and self.proximo_caractere() != '\0':
            # Se encontrar quebra de linha sem fechar aspas, é erro
            if self.proximo_caractere() == '\n':
                token = Token(TipoToken.ERRO, lexema, linha_inicial, coluna_inicial)
                return token
            
            lexema += self.proximo_caractere()
            self.avancar()
        
        # Verifica se encontrou a aspas de fechamento
        if self.proximo_caractere() == '"':
            lexema += '"'  # Inclui a aspas final
            self.avancar()
            return Token(TipoToken.STRING, lexema, linha_inicial, coluna_inicial)
        else:
            # String não fechada (fim de arquivo)
            return Token(TipoToken.ERRO, lexema, linha_inicial, coluna_inicial)
    
    def estado_palavra(self):
        """Estado para reconhecimento de palavras reservadas e identificadores"""
        linha_inicial = self.linha
        coluna_inicial = self.coluna
        lexema = ''
        
        # Consome letras, números e underscores
        while (self.proximo_caractere().isalnum() or self.proximo_caractere() == '_'):
            lexema += self.proximo_caractere()
            self.avancar()
        
        # Verifica se é palavra reservada
        if lexema in PALAVRAS_RESERVADAS:
            return Token(PALAVRAS_RESERVADAS[lexema], lexema, linha_inicial, coluna_inicial)
        else:
            return Token(TipoToken.IDENTIFICADOR, lexema, linha_inicial, coluna_inicial)
    
    def estado_numero(self):
        """Estado para reconhecimento de números inteiros e reais"""
        linha_inicial = self.linha
        coluna_inicial = self.coluna
        lexema = ''
        tem_ponto = False
        
        # Consome a parte inteira
        while self.proximo_caractere().isdigit():
            lexema += self.proximo_caractere()
            self.avancar()
        
        # Verifica se há parte decimal
        if self.proximo_caractere() == '.':
            # Salva a posição atual antes de avançar
            self.avancar()  # Consome o ponto
            proximo_char = self.proximo_caractere()  # Verifica o próximo caractere após o ponto
            
            # Verifica se há dígitos após o ponto
            if proximo_char.isdigit():
                tem_ponto = True
                lexema += '.'  # Adiciona o ponto ao lexema
                
                # Consome a parte decimal
                while self.proximo_caractere().isdigit():
                    lexema += self.proximo_caractere()
                    self.avancar()
            else:
                # Ponto sem dígitos depois - trata como número inteiro
                # O ponto já foi consumido, então retorna o número inteiro
                return Token(TipoToken.NUM_INTEIRO, lexema, linha_inicial, coluna_inicial)
        
        # Classifica o token
        if tem_ponto:
            return Token(TipoToken.NUM_REAL, lexema, linha_inicial, coluna_inicial)
        else:
            return Token(TipoToken.NUM_INTEIRO, lexema, linha_inicial, coluna_inicial)
    
    def estado_operador(self):
        """Estado para reconhecimento de operadores e símbolos de pontuação"""
        char = self.proximo_caractere()
        linha_inicial = self.linha
        coluna_inicial = self.coluna
        
        self.avancar()
        
        if char == '+':
            return Token(TipoToken.OP_ADICAO, '+', linha_inicial, coluna_inicial)
        elif char == '-':
            return Token(TipoToken.OP_SUBTRACAO, '-', linha_inicial, coluna_inicial)
        elif char == '*':
            return Token(TipoToken.OP_MULTIPLICACAO, '*', linha_inicial, coluna_inicial)
        elif char == '/':
            return Token(TipoToken.OP_DIVISAO, '/', linha_inicial, coluna_inicial)
        elif char == '^':
            return Token(TipoToken.OP_POTENCIACAO, '^', linha_inicial, coluna_inicial)
        elif char == '=':
            return Token(TipoToken.OP_ATRIBUICAO, '=', linha_inicial, coluna_inicial)
        elif char == ':':
            return Token(TipoToken.DOIS_PONTOS, ':', linha_inicial, coluna_inicial)
        elif char == ';':
            return Token(TipoToken.PONTO_VIRGULA, ';', linha_inicial, coluna_inicial)
        elif char == '(':
            return Token(TipoToken.PARENTESE_ESQ, '(', linha_inicial, coluna_inicial)
        elif char == ')':
            return Token(TipoToken.PARENTESE_DIR, ')', linha_inicial, coluna_inicial)
        elif char == '[':
            return Token(TipoToken.COLCHETE_ESQ, '[', linha_inicial, coluna_inicial)
        elif char == ']':
            return Token(TipoToken.COLCHETE_DIR, ']', linha_inicial, coluna_inicial)
        elif char == '{':
            return Token(TipoToken.CHAVE_ESQ, '{', linha_inicial, coluna_inicial)
        elif char == '}':
            return Token(TipoToken.CHAVE_DIR, '}', linha_inicial, coluna_inicial)
        elif char == ',':
            return Token(TipoToken.VIRGULA, ',', linha_inicial, coluna_inicial)
        elif char == '.':
            return Token(TipoToken.PONTO, '.', linha_inicial, coluna_inicial)
        elif char == '!':
            return Token(TipoToken.EXCLAMACAO, '!', linha_inicial, coluna_inicial)
        elif char == '>':
            return Token(TipoToken.MAIOR_QUE, '>', linha_inicial, coluna_inicial)
        elif char == '"':
            # Aspas duplas são tratadas em estado_string(), mas incluímos aqui como fallback
            return Token(TipoToken.ASPAS_DUPLAS, '"', linha_inicial, coluna_inicial)
        elif char == "'":
            # Aspas simples (pode ser usado em alguns contextos)
            return Token(TipoToken.ASPAS_DUPLAS, "'", linha_inicial, coluna_inicial)
    
    def proximo_token(self):
        """Método principal que retorna o próximo token"""
        return self.estado_q0()
    
    # ... (início do arquivo lexer.py)

    def tokenizar(self):
        """Tokeniza todo o código fonte e retorna uma lista de tokens e uma lista de erros."""
        tokens = []
        erros = []
        token = self.proximo_token()
        
        while token.tipo != TipoToken.EOF:
            if token.tipo == TipoToken.ERRO:
                # Adiciona o erro na lista em vez de imprimir
                erros.append(f"Erro léxico na linha {token.linha}, coluna {token.coluna}: caractere inválido '{token.lexema}'")
            else:
                tokens.append(token)
            
            token = self.proximo_token()
        
        tokens.append(token)  # Adiciona o token EOF
        return tokens, erros

# ... (resto do arquivo)
    
    def __str__(self):
        """Retorna uma representação string dos tokens"""
        tokens = self.tokenizar()
        resultado = []
        for token in tokens:
            resultado.append(str(token))
        return '\n'.join(resultado)
