# DRAMATICA — Linguagem de Programação Teatral

> **Resumo:** DRAMATICA é uma linguagem de programação inspirada em dramaturgia. Cada programa é uma peça; cada arquivo é uma cena; cada personagem é um ator (thread); cada fala é uma função. A sintaxe foi desenhada para ser expressiva, legível e naturalmente concorrente — ideal para ensinar atores/atores-threads, modelar sistemas orientados a agentes e criar programas que pareçam roteiros.

---

## Sumário

1. Proposta e objetivos  
2. Palavras-chave e símbolos (tabela)  
3. Estrutura de um programa / convenções de arquivo  
4. Exemplo completo — Cena: Mercado  
5. Tokens e especificação léxica  
6. Gramática formal (EBNF detalhada)  
7. Exemplo de derivação passo a passo (programa simples)  
8. Modelo de execução (runtime): atores, filas e palco  
9. Concurrency teatral: semântica de mensagens e sincronização  
10. Pipeline do compilador (lexer → parser → IR → runtime)  
11. Exemplos adicionais (concorrência, props compartilhados, transições entre cenas)  
12. Dicas de implementação (linguagens alvo para runtime)  
13. Referências de design e analogias

---

## 1. Proposta e objetivos

DRAMATICA tem como objetivos principais:

- **Legibilidade narrativizada:** o código parece um roteiro, facilitando leitura por não-programadores e estimulando criatividade.
- **Modelo de concorrência claro:** cada personagem é um ator isolado (state encapsulation) com fila de mensagens.
- **Controle explícito de recursos compartilhados:** `props` modelam recursos do palco com mecanismos de atomicidade/lock.
- **Anotações diretas para runtime:** direções (`direction`) permitem controlar temporizações, logging e instrumentação.
- **Ferramenta didática:** ótimo para ensino de atores/atores-modelo, concorrentismo e compiladores.

---

## 2. Palavras‑chave e símbolos

| Elemento | Palavra‑chave / Símbolo | Descrição |
|---|---:|---|
| Definição de cena | `scene` | Início de um arquivo/cena. |
| Definição de personagem | `character` | Declara um ator (thread). |
| Bloco de props | `props:` | Variáveis compartilhadas da cena. |
| Bloco de abertura | `opening:` | Ações iniciais executadas ao carregar a cena. |
| Declaração de fala | `speech` | Define uma fala (função) associada a um/mais personagens. |
| Envio de fala | `X speaks Y` | Empilha a fala `Y` na fila do personagem `X`. |
| Emissão | `X says "texto"` | Saída/print feita pelo personagem `X`. |
| Ação de mover | `X approaches Y` | Cria vínculo/contexto entre personagens. |
| Sair | `X exits` | Termina a thread/personagem `X`. |
| Direção | `direction [timing="..."]` | Metadados de tempo/modo para o runtime. |
| Comentário | `# comentário` | Comentário de linha. |
| Atribuição | `=` | Atribui valor a variável (memória do personagem ou prop). |
| If / else | `if ...:`, `else:` | Controle condicional (indentação como em Python). |
| Repeat | `repeat N times:` | Repetição. |
| Call | `call Person.speech` | Chamada direta (sincronia opcional). |

---

## 3. Estrutura de um programa / convenções de arquivo

Cada arquivo fonte em DRAMATICA representa **uma cena**:

```
scene <NomeCena>:

    character <NomePersonagem>:
        memory:
            var1: tipo = valor
            var2: tipo = valor

    props:
        sharedVar: tipo = valor

    opening:
        <ações iniciais — envios de fala, binds, etc>

    speech nomeFala(Personagem, [params...]):
        <corpo da fala>
```

- Indentação significativa (estilo Python) é recomendada e facilita parsing baseado em blocos.
- `character` pode conter um bloco `memory:` com variáveis privadas do ator.
- `props` existem no palco (shared) e devem ser acessadas com cuidado.

---

## 4. Exemplo completo — Cena: Mercado

```dramatica
scene Mercado:

    character Joao:
        memory:
            moeda: number = 10
            inventario: list = []

    character Vendedor:
        memory:
            estoque: number = 3
            preco: number = 3

    props:
        aberto: flag = true

    opening:
        Joao approaches Vendedor
        Joao speaks comprar

    speech comprar(Joao):
        if Joao.moeda >= Vendedor.preco:
            Joao says "Quero comprar!"
            call Vendedor.venderItem with 1
        else:
            Joao says "Não tenho dinheiro :("

    speech venderItem(Vendedor, quantidade):
        if Vendedor.estoque >= quantidade:
            Vendedor.estoque -= quantidade
            Joao.inventario.append("moeda")
            Joao.moeda -= Vendedor.preco
            Vendedor says "Aqui está!"
        else:
            Vendedor says "Acabou o estoque."
```

**Notas semânticas:**
- `call Vendedor.venderItem with 1` pode ser interpretado como **chamada síncrona** (espera) ou **assincrona** dependendo do qualificativo (ver seção de concurrency).
- `Joao.inventario.append(...)` demonstra acesso ao estado interno do personagem `Joao`. Por segurança, chamadas que modificam outro ator devem ser feitas via mensagens ou por `props` com mecanismos atômicos.

---

## 5. Tokens e especificação léxica

**Tokens principais (lexemas):**

- `scene` — literal
- `character` — literal
- `props` — literal
- `opening` — literal
- `speech` — literal
- `speaks` — literal
- `says` — literal
- `approaches`, `exits` — literais
- `call`, `with` — literais
- `if`, `else`, `repeat`, `true`, `false`, `null` — literais
- `ID` — identificador: `[a-zA-Z_][a-zA-Z0-9_]*`
- `NUMBER` — inteiro ou real: `([0-9]+(\.[0-9]+)?)`
- `STRING` — `"[^"\n]*"`
- `INDENT` / `DEDENT` — para delimitar blocos (opcional se usar `{}`)
- `:`  — dois pontos
- `(` `)` `,` — separadores
- `=` — operador de atribuição
- `.` — acesso a atributos
- `;` — fim de comando (opcional; preferir newline/indentation)

**Observação:** A análise léxica deve reconhecer `INDENT` / `DEDENT` se optar por parsing sensível a indentação (recomendado para estética teatral).

---

## 6. Gramática formal (EBNF detalhada)

A gramática abaixo é apresentada em EBNF (estilo legível), pensada para um parser descendente recursivo com `lookahead`.

```
<program> ::= { <scene> }

<scene> ::= "scene" <ID> ":" <scene_body>

<scene_body> ::= { <character_decl> | <props_block> | <opening_block> | <speech_decl> }

<character_decl> ::= "character" <ID> ":" [ <character_body> ]

<character_body> ::= "memory" ":" <memory_list>

<memory_list> ::= <memory_decl> { <memory_decl> }

<memory_decl> ::= <ID> ":" <type> "=" <expression>

<props_block> ::= "props" ":" <props_list>

<props_list> ::= <prop_decl> { <prop_decl> }

<prop_decl> ::= <ID> ":" <type> "=" <expression>

<opening_block> ::= "opening" ":" <statement_list>

<speech_decl> ::= "speech" <ID> "(" <param_list_opt> ")" ":" <statement_list>

<param_list_opt> ::= ε | <param> { "," <param> }

<param> ::= <ID>

<statement_list> ::= { <statement> }

<statement> ::= <send_stmt> | <say_stmt> | <call_stmt> | <assign_stmt> | <if_stmt> | <repeat_stmt> | <approach_stmt> | <exit_stmt>

<send_stmt> ::= <ID> "speaks" <ID>

<say_stmt> ::= <ID> "says" <STRING>

<call_stmt> ::= "call" <ID> "." <ID> [ "with" <expr_list> ]

<assign_stmt> ::= <expr_lvalue> "=" <expression>

<if_stmt> ::= "if" <expression> ":" <statement_list> [ "else" ":" <statement_list> ]

<repeat_stmt> ::= "repeat" <NUMBER> "times" ":" <statement_list>

<approach_stmt> ::= <ID> "approaches" <ID>

<exit_stmt> ::= <ID> "exits"

<expr_list> ::= <expression> { "," <expression> }

<expr_lvalue> ::= <ID> | <ID> "." <ID>

<expression> ::= <term> { ("+" | "-" | "*" | "/") <term> }

<term> ::= <NUMBER> | <STRING> | <ID> | <ID> "." <ID> | "(" <expression> ")"

<type> ::= "number" | "string" | "list" | "flag" | "any"

<ID> ::= token identificador
<NUMBER> ::= token número (inteiro/real)
<STRING> ::= token string
```

---

## 7. Exemplo de derivação passo a passo (programa simples)

**Programa alvo (texto DRAMATICA):**

```
scene Curta:

    character Ator:
        memory:
            contador: number = 0

    opening:
        Ator speaks iniciar

    speech iniciar(Ator):
        repeat 2 times:
            Ator says "Começo"
            call Ator.incrementar
        Ator exits

    speech incrementar(Ator):
        Ator.contador = Ator.contador + 1
```

**Derivação (leftmost derivation) — passos essenciais:**

1. Símbolo inicial: `<program>`

2. Expandir `<program> ::= { <scene> }` → `<scene>`

3. Expandir `<scene> ::= "scene" <ID> ":" <scene_body>` → `scene Curta: <scene_body>`

4. `<scene_body>` contém `<character_decl>`, `<opening_block>`, `<speech_decl>` — expandir `<character_decl>` primeiro:

   - `<character_decl> ::= "character" <ID> ":" <character_body>`

   → `character Ator: <character_body>`

5. Expandir `<character_body>` → `memory : <memory_list>` → `contador: number = 0`

6. Expandir `<opening_block>` → `Ator speaks iniciar`

7. Expandir `<speech_decl>` para `iniciar` e `incrementar` com seus `<statement_list>` correspondentes.

8. Dentro de `speech iniciar`, `repeat 2 times: <statement_list>` e cada `statement` mapeia para `Ator says "Começo"` e `call Ator.incrementar`.

9. `speech incrementar` contém `Ator.contador = Ator.contador + 1` que atende `<assign_stmt>` e `<expression>` regras.

10. Quando todas as produções não-terminais foram substituídas por terminais, obtemos a sequência de tokens idêntica ao programa alvo.

**Observação:** o parser consome tokens produzidos pelo lexer; a derivação mostra que o programa está gerado por regras da gramática (portanto será aceito por um parser correto).

---

## 8. Modelo de execução (runtime): atores, filas e palco

**Entidades principais:**

- **Ator (Actor):** possui uma identidade (`ID`), estado privado (`memory`), e uma **fila de mensagens** FIFO.
- **Palco (Stage):** contém `props` compartilhados, global state (opcional) e mecanismos de sincronização.
- **Scheduler:** gerencia execução dos atores; políticas possíveis:
  - *Round-robin* (fair scheduling)
  - *Prioridade por mensagem* (direções podem indicar prioridade)
  - *Temporizações* (directions com `timing`)

**Fluxo de execução:**

1. Ao carregar uma cena, o runtime instancia atores e props.
2. `opening` executa enviando mensagens (falar/`speaks`) e chamando falas síncronas se indicado.
3. Cada `speaks` empilha um job na fila do ator alvo.
4. Scheduler seleciona um ator com trabalho pendente e executa a fala (consumindo a mensagem).
5. Fala (speech) executa no contexto do ator, podendo:
   - acessar/modificar sua memória (`Ator.var`)
   - enviar mensagens (`X speaks Y`)
   - alterar props via operações atômicas
   - chamar `call` (síncrono) ou enviar mensagem (assíncrono) dependendo do qualifier

**Falhas e isolamento:**
- Atores isolados evitam data races; mudanças no estado de outro ator devem usar mensagens ou props atômicos.
- Para operações atômicas em `props`, o runtime oferece primitives: `atomic_increment(props.name, value)` ou `locked { ... }`.

---

## 9. Concurrency teatral: semântica de mensagens e sincronização

**Modelos de chamada:**

- `X speaks Y` → **assincrono**: empilha Y na fila de X e retorna imediatamente.
- `call X.Y` → **síncrono**: bloqueia o chamador até X terminar Y (opcional: se chamador e alvo são o mesmo ator, executa localmente).
- Qualificador `await` pode ser adicionado: `await X speaks Y` para esperar conclusão.

**Primitivas de sincronização:**

- `locked props.name:` … blocos que obtêm lock exclusivo sobre a prop.
- `await condition:` suspende a execução até que `condition` seja verdadeira (útil para coordenação de cena).
- `broadcast` — envia uma fala para múltiplos atores.

**Exemplo de sincronização:**

```dramatica
props:
    caixa: number = 1

speech usarCaixa(Ator):
    locked caixa:
        if caixa > 0:
            caixa = caixa - 1
            Ator says "Usando..."
            # operação demorada simulada
            caixa = caixa + 1
```

---

## 10. Pipeline do compilador

1. **Analisador Léxico (Lexer):**
   - Tokeniza o arquivo; reconhece `INDENT/DEDENT` se usar indentação.
   - Produz stream de tokens: `scene`, `ID`, `:`, `character`, `memory`, etc.

2. **Analisador Sintático (Parser):**
   - Constrói a AST (Abstract Syntax Tree) baseada na gramática EBNF.
   - Valida estruturas (tipos básicos, parâmetros de fala, existência de personagens referenciados).

3. **Análise Semântica / Type Checking:**
   - Verifica acessos válidos (`Joao.moeda` existe?), tipos de expressões e assinatura de falas.
   - Resolve referências entre cenas (se aplicável).

4. **IR (Intermediary Representation):**
   - Converte AST para IR orientada a atores: lista de atores, falas como handlers, inicializadores de fila.

5. **Codegen / Runtime Binding:**
   - Emite bytecode para VM teatral ou código em linguagens como Rust/Go/NodeJS para execução.
   - Instruções IR = `send(actor, speech, args)`, `atomic_read`, `atomic_write`, `sleep`, `log`.

6. **Runtime:**
   - Scheduler de atores, filas, primitives atômicas, I/O teatral (logs estilizados).

---

## 11. Exemplos adicionais

### Exemplo A — Concorrência simples (duas falas simultâneas)
```dramatica
scene PalcoDuplo:

    character Alice:
        memory: { step: number = 0 }

    character Bob:
        memory: { step: number = 0 }

    opening:
        Alice speaks cantar
        Bob speaks dançar

    speech cantar(Alice):
        repeat 3 times:
            Alice says "La la la"
            Alice.step = Alice.step + 1

    speech dançar(Bob):
        repeat 2 times:
            Bob says "Olha o passo!"
            Bob.step = Bob.step + 1
```

### Exemplo B — Uso de props atômicos (recurso compartilhado)
```dramatica
scene Banco:

    character Caixa:
        memory: {}

    character Cliente:
        memory: { saldo: number = 50 }

    props:
        dinheiro: number = 1000

    opening:
        Cliente speaks sacar

    speech sacar(Cliente):
        call Caixa.processarSaque with 200

    speech processarSaque(Caixa, valor):
        locked dinheiro:
            if dinheiro >= valor:
                dinheiro = dinheiro - valor
                Caixa says "Saque efetuado"
            else:
                Caixa says "Fundo insuficiente"
```

### Exemplo C — Broadcast e espera (coordenação)
```dramatica
scene Reuniao:

    character Lider:
        memory: {}

    character Membro1:
        memory: {}

    character Membro2:
        memory: {}

    opening:
        Lider speaks convocar

    speech convocar(Lider):
        broadcast Membro1.sala
        broadcast Membro2.sala
        await Membro1.presente and Membro2.presente
        Lider says "Reunião iniciada"

    speech sala(Membro1):
        Membro1.presente = true

    speech sala(Membro2):
        Membro2.presente = true
```

---

## 12. Dicas de implementação

- **Linguagens recomendadas para runtime:** Rust (segurança e performance), Go (goroutines) ou Node.js (ecosistema e facilidade).
- **Modelo de atores:** use canais/queues por ator; em Rust, `tokio::mpsc`; em Go, `chan`.
- **Parsing:** construir lexer com `logos` (Rust) ou `moo` (JS), parser com `lalrpop`/`pest` (Rust) ou `nearley` (JS).
- **Testes:** criar suíte de testes que verifica interleavings e condições de corrida usando uma VM determinística (replay).
- **Ferramentas auxiliares:** PLT (Pretty-Printer) para renderizar a peça com anotações; visualizador que mostra filas dos atores em tempo real.

---

## 13. Referências de design e analogias

- O modelo de concorrência é inspirado em **Actor Model** (Erlang/Elixir, Akka).
- A estética textual e indentação lembram **Python** e DSLs narrativas.
- `props` ≈ recursos compartilhados com locks, parecido com **shared memory** em sistemas tradicionais.
- Direções (`direction`) são análogas a metadados usados em sistemas de instrumentação.

---

### Próximos passos que eu posso fazer por você (escolha um ou mais):

- Gerar o **arquivo .md completo** (pronto para download).  
- Criar o **lexer** e **parser** em Rust/Go/TypeScript (com código).  
- Implementar um **runtime mínimo** em Node.js ou Rust com scheduler e filas.  
- Produzir documentação reduzida apta a ser publicada no GitHub Pages.  

--- 
