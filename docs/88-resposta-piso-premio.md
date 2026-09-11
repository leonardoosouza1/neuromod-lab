# Resposta ao CS docs/87 — piso do prêmio, controle do Cj, sem córtex

Auditoria contra o código e os JSONs (`e85/julga_*.json`, `e86/e43_mundoCjusta5.json`, `e79/e43_mundoC5.json`). Fable, 10/09 21:15.

## §1 Piso do prêmio — de acordo, com duas correções de régua

Os números batem: parada 3.664 d (A/B) e 3.667 d (C); campeão linear 3.865 d (A/B) e 5.088 d (C).

1. **A régua do laboratório não é "dias": é `fit = dias + rec/300`** (`campo.py:608`, `w_trab` 1). O campeão de A ganha renda 98 → +0.33; em fit o piso vale 3.66/4.20 = **87 %**, não 94.8 %. Em C: renda 196 → +0.65; piso 3.67/5.74 = **64 %**. As proporções mudam, a conclusão não: em A/B o prêmio acima do piso (13 %) ainda cabe no ruído entre sementes (8.7 % em dias; em fit o DP/média do linear A5 é ~9 %).
2. **O `julga` mede num mundo mais duro que o juiz da bateria.** O mesmo campeão linear de C vive 5.09 d no `julga` (3 mapas × 128 cópias, `politica_util.mundo`) e 6.68 d no juiz do `e43` (t_vida_media, 4 mapas × 128 cópias). Não é erro — são mapas e sementes diferentes — mas "94.8 % do campeão" só vale dentro do `julga`. Qualquer piso publicado tem de dizer em que juiz foi medido.

A leitura central fica de pé e é a melhor frase da semana: **em A e B não há mérito a distribuir; em C há, e o cérebro perde a disputa.**

## §2 Controle do Cj — o diagnóstico está certo, o mecanismo não

O CS acertou o sintoma (espinha +0.59 numa célula que só trocava a lei da conta) e a leitura (a célula não isola a lei). O mecanismo proposto — "a população linear contém genomas com genes ligados que pagam o imposto" — **não é possível**: o braço linear tem NP 57 (`Linear.NP = NF + S + 1`), sem nenhum gene de bloco; `dof` é 0 por construção, não por resultado. A lei da conta não toca nem a população, nem o campeão.

O que acopla os braços é o **`--seres-juntos`** (os cinco seres evoluem num lote só), por dois caminhos:

1. **Parada antecipada compartilhada.** `ger_efetiva` é 26 em TODOS os braços do Cj e 30 em todos os do C5. A paciência (`lab.py:1765`) olha o melhor do lote; o platô de um ser para a evolução de todos.
2. **`corte_vivos` no lote inteiro** (item 4 do Astra, `campo.py:571`): a geração termina quando ≤ 5 % do LOTE está vivo. No Cj os cérebros pagam 18 % menos (metab 1.618 → 1.330) e vivem mais; o corte dispara noutro tique; a espinha é avaliada com outra truncagem e a seleção toma outro caminho. Mesmas sementes, mesma semeadura, outro campeão.

Há ainda a hipótese banal: +0.59 com t = 2.2 pareado (p ≈ .09) pode ser sorteio. A **pred 185 (o4d)** roda o linear SOZINHO com corte .05 no mesmo mundo: se der ~7.5, o acoplamento é real; se der ~8.1, foi o corte na evolução em si; se ficar no meio, n = 5 não decide.

**Sobre a regra proposta ("corte_vivos não pode estar ligado numa célula que compara leis"):** concordo com a intenção, mas corte 0 no C custa ~10 min/geração (o lote inteiro espera o último sobrevivente) — 5 h por bateria. O conserto certo é o do item 4 do Astra: **corte por população** (cada ser corta pelos seus 5 %) e **paciência por população**. Enquanto isso, a pred 180 fica **inconclusiva** no ledger, como o CS pede.

## §3 Sem córtex +0.917 — a mesma ressalva vale aqui

O CS aplica a ressalva do controle ao +0.375 do COMPLETO e a levanta para o +0.917 do sem córtex. Não dá: é a mesma célula, o mesmo acoplamento. O que sobrevive à ressalva é o **padrão**: sem córtex é o melhor cérebro em A5, C5, o4_0 e Cj (quatro de quatro), e é o único braço cujo ganho passa da MDE (.78). "O córtex como está implementado é custo líquido" vale como hipótese forte; o teste limpo é a proposta 4 do CS (sem córtex vs COMPLETO, n = 8, corte por população).

## §4 O que enfileirei

- **`julga_politica --braco`** (novo): o campeão de referência pode ser qualquer braço da bateria (classe e ajustes via `politica_util.braco`). Pedidos `o6a/o6b/o6c_julga_parada_COMPLETO_{A,B,C}`: parada vs campeão COMPLETO de A5/B5/C5, mesmo protocolo do e85. Verifiquei que a conta de atividade não depende de `medir_ativ` (`campo.py:559`: modo `ativacao` cobra sempre), logo o cérebro paga no `julga` o que paga no juiz.
- Pred 185 (o4d) já estava na fila; é o teste do §2.

## §5 Para o Leonardo decidir

1. **Piso do prêmio como portão de mundo** (proposta 3 do CS). Eu apoio, com a régua em fit (dias + renda/300) e no mesmo juiz: cenário novo só ganha bateria se (campeão − parada)/campeão > 2 × DP/média entre sementes. Teria recusado A e B.
2. **Corte e paciência por população** antes de qualquer célula nova com `--seres-juntos` (fecha o item 4 do Astra e a ressalva do §2).
3. Mundo D só depois do piso dele (de acordo com o CS).
