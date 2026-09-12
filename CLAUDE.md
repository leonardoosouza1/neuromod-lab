# neuromod-lab — instruções de ciência

Leia [`docs/HANDBOOK-ENGENHARIA-CIENTIFICA.md`](docs/HANDBOOK-ENGENHARIA-CIENTIFICA.md)
antes de alterar código, métricas ou experimentos.

- Preserve [`docs/REVISAO-CHECKLIST.md`](docs/REVISAO-CHECKLIST.md) antes de GPU.
- Preserve [`controle-experimental.md`](controle-experimental.md) para controles.
- Declare hipótese e previsão antes da coleta confirmatória; análises de dados já
  existentes devem ser rotuladas como exploratórias.
- Rotule verificado, estático, inferido ou hipótese.
- Registre commit, SHA do binário, comando, seeds, unidades e horizonte.
- Não confunda campeão, população, sobreviventes ou linhagens.
- Causalidade usa pares casados e ablação isolada.
- CPU oracle é válido para unidade/I-O; não é evidência GPU.
- Falha de gate aborta; desvio não vira PASS retroativo.
- Saídas grandes usam `/media/llm-data/universe-runs/`.
- Siga a autorização de escopo do usuário sem re-perguntar itens já autorizados.
