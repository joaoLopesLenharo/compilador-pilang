# Adaptação do Projeto para DRAMATICA

## Resumo das Mudanças

O projeto foi adaptado para implementar a linguagem **DRAMATICA** - uma linguagem de programação inspirada em teatro, mantendo todos os requisitos acadêmicos do trabalho de compiladores.

## Estrutura da Linguagem DRAMATICA (Versão Simplificada)

### Palavras-chave Teatrais

- `scene` - Início do programa (substitui INICIO)
- `FIM_CENA` - Fim do programa (substitui FIM)
- `character` - Declara um personagem/ator
- `memory:` - Bloco de declaração de variáveis (substitui VARIAVEIS)
- `FIM_MEMORY` - Fim do bloco de variáveis (substitui FIM_VARIAVEIS)
- `says` - Comando de escrita teatral (substitui ESCREVA)
- `LEIA` - Comando de leitura (mantido)

### Estrutura de um Programa

```
scene NomeCena:
    character NomePersonagem:
        memory:
            variavel1: number;
            variavel2: number;
        FIM_MEMORY

    LEIA variavel1;
    variavel2 = variavel1 + 5;
    Personagem says variavel2;
FIM_CENA
```

## Requisitos Acadêmicos Atendidos

✅ **Palavras-chave para início e fim:** `scene` e `FIM_CENA`  
✅ **Cabeçalho para declaração de variáveis:** `memory:` dentro de `character`  
✅ **Tipos numéricos:** `number` (suporta inteiros e reais)  
✅ **Comandos de escrita e leitura:** `LEIA` e `Personagem says`  
✅ **Operações de adição e subtração:** `+` e `-` (também `*`, `/`, `^`)  
✅ **Atribuição:** `=` com um ou dois operandos  
✅ **Símbolo de pontuação:** `;` ao final de cada comando  

## Arquivos Modificados

1. **tokens.py** - Adicionados tokens teatrais (SCENE, CHARACTER, MEMORY, SAYS, etc.)
2. **parser.py** - Gramática adaptada para estrutura teatral
3. **interpreter.py** - Execução adaptada para cenas e personagens
4. **exemplos/** - Criados exemplos em formato `.dramatica`

## Próximos Passos

- [ ] Atualizar README.md com documentação completa de DRAMATICA
- [ ] Criar diagramas visuais dos autômatos para DRAMATICA
- [ ] Testar todos os exemplos
- [ ] Atualizar interface web se necessário

