EPSILON = "ε"


class Grammar:
    def __init__(self):
        self.start_symbol = "Programa"
        self.nonterminals = [
            "S'",
            "Programa",
            "Comandos",
            "Comando",
            "ComandoLeitura",
            "ComandoEscrita",
            "ComandoAtribuicao",
            "Expressao",
            "ExpressaoSimples",
            "Termo",
            "Fator",
            "Elemento",
        ]
        self.terminals = [
            "LEIA",
            "ESCREVA",
            "IDENTIFICADOR",
            "NUM_INTEIRO",
            "NUM_REAL",
            "OP_ADICAO",
            "OP_SUBTRACAO",
            "OP_MULTIPLICACAO",
            "OP_DIVISAO",
            "OP_POTENCIACAO",
            "OP_ATRIBUICAO",
            "PONTO_VIRGULA",
            "PARENTESE_ESQ",
            "PARENTESE_DIR",
            "EOF",
        ]
        self.productions = []
        self._build_productions()

    def _build_productions(self):
        p = self.productions
        # 0: S' -> Programa
        p.append(("S'", ["Programa"]))
        # 1: Programa -> Comandos
        p.append(("Programa", ["Comandos"]))
        # 2: Comandos -> Comando Comandos
        p.append(("Comandos", ["Comando", "Comandos"]))
        # 3: Comandos -> Comando
        p.append(("Comandos", ["Comando"]))
        # 4: Comando -> ComandoLeitura
        p.append(("Comando", ["ComandoLeitura"]))
        # 5: Comando -> ComandoEscrita
        p.append(("Comando", ["ComandoEscrita"]))
        # 6: Comando -> ComandoAtribuicao
        p.append(("Comando", ["ComandoAtribuicao"]))
        # 7: ComandoLeitura -> LEIA IDENTIFICADOR PONTO_VIRGULA
        p.append(("ComandoLeitura", ["LEIA", "IDENTIFICADOR", "PONTO_VIRGULA"]))
        # 8: ComandoEscrita -> ESCREVA IDENTIFICADOR PONTO_VIRGULA
        p.append(("ComandoEscrita", ["ESCREVA", "IDENTIFICADOR", "PONTO_VIRGULA"]))
        # 9: ComandoAtribuicao -> IDENTIFICADOR OP_ATRIBUICAO Expressao PONTO_VIRGULA
        p.append(("ComandoAtribuicao", ["IDENTIFICADOR", "OP_ATRIBUICAO", "Expressao", "PONTO_VIRGULA"]))
        # 10: Expressao -> ExpressaoSimples
        p.append(("Expressao", ["ExpressaoSimples"]))
        # 11: ExpressaoSimples -> ExpressaoSimples OP_ADICAO Termo
        p.append(("ExpressaoSimples", ["ExpressaoSimples", "OP_ADICAO", "Termo"]))
        # 12: ExpressaoSimples -> ExpressaoSimples OP_SUBTRACAO Termo
        p.append(("ExpressaoSimples", ["ExpressaoSimples", "OP_SUBTRACAO", "Termo"]))
        # 13: ExpressaoSimples -> Termo
        p.append(("ExpressaoSimples", ["Termo"]))
        # 14: Termo -> Termo OP_MULTIPLICACAO Fator
        p.append(("Termo", ["Termo", "OP_MULTIPLICACAO", "Fator"]))
        # 15: Termo -> Termo OP_DIVISAO Fator
        p.append(("Termo", ["Termo", "OP_DIVISAO", "Fator"]))
        # 16: Termo -> Fator
        p.append(("Termo", ["Fator"]))
        # 17: Fator -> Fator OP_POTENCIACAO Elemento
        p.append(("Fator", ["Fator", "OP_POTENCIACAO", "Elemento"]))
        # 18: Fator -> Elemento
        p.append(("Fator", ["Elemento"]))
        # 19: Elemento -> IDENTIFICADOR
        p.append(("Elemento", ["IDENTIFICADOR"]))
        # 20: Elemento -> NUM_INTEIRO
        p.append(("Elemento", ["NUM_INTEIRO"]))
        # 21: Elemento -> NUM_REAL
        p.append(("Elemento", ["NUM_REAL"]))
        # 22: Elemento -> PARENTESE_ESQ Expressao PARENTESE_DIR
        p.append(("Elemento", ["PARENTESE_ESQ", "Expressao", "PARENTESE_DIR"]))


class SLRAnalyzer:
    def __init__(self):
        self.grammar = Grammar()
        self.first = self._compute_first()
        self.follow = self._compute_follow()
        self.states, self.transitions = self._build_lr0_items()
        self.action_table, self.goto_table = self._build_tables()

    def analisar(self, tokens):
        """Executa a análise SLR com base na sequência de tokens."""
        # Extrai os tipos de token e garante o marcador de fim de arquivo
        entrada = [token.tipo for token in tokens if token.tipo != "ERRO"]
        if not entrada or entrada[-1] != "EOF":
            entrada.append("EOF")

        pilha = [0]
        indice = 0
        passos = []

        while True:
            estado = pilha[-1]
            lookahead = entrada[indice] if indice < len(entrada) else "EOF"
            acao = self.action_table.get(estado, {}).get(lookahead)

            passo_info = {
                "pilha": list(pilha),
                "entrada": entrada[indice:],
            }

            if acao is None:
                return {
                    "sucesso": False,
                    "mensagem": f"Nenhuma ação para o estado {estado} com lookahead '{lookahead}'.",
                    "passos": len(passos),
                    "passos_realizados": passos,
                }

            tipo_acao = acao[0]

            if tipo_acao == "shift":
                proximo_estado = acao[1]
                pilha.append(proximo_estado)
                indice += 1
                passo_info["acao"] = f"shift para estado {proximo_estado} consumindo '{lookahead}'"
                passos.append(passo_info)
            elif tipo_acao == "reduce":
                prod_idx = acao[1]
                cabeca, corpo = self.grammar.productions[prod_idx]
                if corpo:
                    for _ in corpo:
                        if len(pilha) > 1:
                            pilha.pop()
                estado_atual = pilha[-1]
                goto_estado = self.goto_table.get(estado_atual, {}).get(cabeca)
                if goto_estado is None:
                    return {
                        "sucesso": False,
                        "mensagem": f"Goto indefinido após redução por {cabeca} -> {' '.join(corpo) or 'ε'}.",
                        "passos": len(passos),
                        "passos_realizados": passos,
                    }
                pilha.append(goto_estado)
                producao_texto = " ".join(corpo) if corpo else "ε"
                passo_info["acao"] = f"reduce usando {cabeca} -> {producao_texto}"
                passos.append(passo_info)
            elif tipo_acao == "accept":
                passo_info["acao"] = "accept"
                passos.append(passo_info)
                return {
                    "sucesso": True,
                    "mensagem": "Análise SLR concluída com sucesso.",
                    "passos": len(passos),
                    "passos_realizados": passos,
                }

    # ==================== Construção de Tabelas ====================

    def _compute_first(self):
        first = {nt: set() for nt in self.grammar.nonterminals}

        changed = True
        while changed:
            changed = False
            for head, body in self.grammar.productions[1:]:  # ignora produção S' -> Programa
                if not body:
                    if EPSILON not in first[head]:
                        first[head].add(EPSILON)
                        changed = True
                    continue

                adiciona_epsilon = True
                for simbolo in body:
                    simbolo_first = self._first_of_symbol(simbolo, first)
                    tamanho_antes = len(first[head])
                    first[head].update(simbolo_first - {EPSILON})
                    if len(first[head]) != tamanho_antes:
                        changed = True

                    if EPSILON not in simbolo_first:
                        adiciona_epsilon = False
                        break

                if adiciona_epsilon:
                    if EPSILON not in first[head]:
                        first[head].add(EPSILON)
                        changed = True

        return first

    def _compute_follow(self):
        follow = {nt: set() for nt in self.grammar.nonterminals}
        follow[self.grammar.start_symbol].add("EOF")

        changed = True
        while changed:
            changed = False
            for head, body in self.grammar.productions[1:]:
                if not body:
                    continue
                trailer = follow[head].copy()
                for simbolo in reversed(body):
                    if simbolo in self.grammar.nonterminals:
                        tamanho_antes = len(follow[simbolo])
                        follow[simbolo].update(trailer)
                        if len(follow[simbolo]) != tamanho_antes:
                            changed = True

                        simbolo_first = self._first_of_symbol(simbolo, self.first)
                        if EPSILON in simbolo_first:
                            trailer = trailer.union(simbolo_first - {EPSILON})
                        else:
                            trailer = simbolo_first
                    else:
                        trailer = {simbolo}
        return follow

    def _build_lr0_items(self):
        productions = self.grammar.productions
        nonterminals = set(self.grammar.nonterminals)
        symbols = set(self.grammar.terminals + self.grammar.nonterminals)

        def closure(items):
            fecho = set(items)
            mudou = True
            while mudou:
                mudou = False
                for prod_idx, ponto in list(fecho):
                    cabeca, corpo = productions[prod_idx]
                    if ponto < len(corpo):
                        simbolo = corpo[ponto]
                        if simbolo in nonterminals:
                            for idx, prod in enumerate(productions):
                                if prod[0] == simbolo:
                                    item_novo = (idx, 0)
                                    if item_novo not in fecho:
                                        fecho.add(item_novo)
                                        mudou = True
            return frozenset(fecho)

        def goto(estado, simbolo):
            itens = set()
            for prod_idx, ponto in estado:
                cabeca, corpo = productions[prod_idx]
                if ponto < len(corpo) and corpo[ponto] == simbolo:
                    itens.add((prod_idx, ponto + 1))
            if not itens:
                return frozenset()
            return closure(itens)

        estados = []
        transicoes = {}
        inicial = closure({(0, 0)})
        estados.append(inicial)
        fila = [inicial]

        while fila:
            estado_atual = fila.pop(0)
            indice_estado = estados.index(estado_atual)
            for simbolo in symbols:
                proximo = goto(estado_atual, simbolo)
                if not proximo:
                    continue
                if proximo not in estados:
                    estados.append(proximo)
                    fila.append(proximo)
                transicoes[(indice_estado, simbolo)] = estados.index(proximo)

        return estados, transicoes

    def _build_tables(self):
        action = {}
        goto = {}
        productions = self.grammar.productions
        terminals = set(self.grammar.terminals)
        nonterminals = set(self.grammar.nonterminals)

        for indice_estado, estado in enumerate(self.states):
            action[indice_estado] = {}
            goto[indice_estado] = {}
            for prod_idx, ponto in estado:
                cabeca, corpo = productions[prod_idx]
                if ponto < len(corpo):
                    simbolo = corpo[ponto]
                    if simbolo in terminals:
                        destino = self.transitions.get((indice_estado, simbolo))
                        if destino is not None:
                            self._adicionar_acao(action[indice_estado], simbolo, ("shift", destino))
                    else:
                        destino = self.transitions.get((indice_estado, simbolo))
                        if destino is not None:
                            goto[indice_estado][simbolo] = destino
                else:
                    if cabeca == "S'":
                        self._adicionar_acao(action[indice_estado], "EOF", ("accept",))
                    else:
                        for a in self.follow[cabeca]:
                            self._adicionar_acao(action[indice_estado], a, ("reduce", prod_idx))

        return action, goto

    def _adicionar_acao(self, tabela_estado, simbolo, acao):
        existente = tabela_estado.get(simbolo)
        if existente is not None and existente != acao:
            raise ValueError(f"Conflito na tabela SLR para símbolo '{simbolo}': {existente} vs {acao}")
        tabela_estado[simbolo] = acao

    def _first_of_symbol(self, simbolo, first_map):
        if simbolo in self.grammar.nonterminals:
            return first_map.get(simbolo, set())
        return {simbolo}
