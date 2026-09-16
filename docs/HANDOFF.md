# HANDOFF — estado para uma sessão nova (reescrever, não acrescentar)

Última reescrita: 16/09/2026 17:15. Leia só isto + o que um item apontar. Não reabra
transcripts antigos.

## Modo autônomo econômico (medido 16/09: 84 % do custo é reler contexto)

1. **Esperar custa 0 token.** Baterias andam sozinhas:
   `python scripts/battery_runner.py run batteries/<b>.json` (detached: `setsid nohup ... &`).
   Treino → avaliação dos campeões → `lab_db ingest` → análise, sem LLM.
2. **Acordar só no evento.** Em Bash com `run_in_background`:
   `python scripts/battery_runner.py wait --max-hours 3` — sai com a linha DONE/FAIL/IDLE.
   Fallback: ScheduleWakeup ≥ 3600 s. Nunca loop curto de checagem.
3. **Olhar o estado em 2 linhas:** `python scripts/battery_runner.py status`.
4. **Subagente:** Sonnet, 1 tarefa, ≤ 50–80 chamadas, saída cortada (`tail`, `-q`), commit
   por etapa, relatório ≤ 150 palavras, ≤ 3 ao mesmo tempo. Agente grande que morreu
   (rate limit) NÃO é retomado: agente novo lê o último commit + nota.
5. **Sessão principal:** `/compact` ou sessão nova passando de ~200k de contexto.
6. Python só `/home/leonardo/projects/LLM/.venv-rocm/bin/python`; dados só em
   `/media/llm-data`; GPU só via fila `nmd`; predição registrada ANTES de rodar;
   matar processo por PID em comando separado (nunca `pkill -f`).

## Baterias

| bateria | estado | onde |
|---|---|---|
| B5 | **fechada** (B5v): gate não informativa; rand ≈ rot generalizam, param no grampo de 12 m da 8200; long ≡ ctrl até alguém viver além do tique 12 000 | `b5-analise/b5.json` |
| B6r | **rodando pelo runner** desde 17:09: 12 treinos (tight11/tight8/tight11rand × 31/77/113/137, ~65 min) → 80 avaliações (8005/8200/8250/8218) → ingest → `src/analyze_b6.py` | `_battery/b6/state.json`, ledger `Universe/docs/PREDICOES-CEREBRO.md` linha B6r |

Ao receber `DONE b6`: ler a saída de `_battery/b6/analyze.out` (≤ 40 linhas), escrever
B6v no ledger (apostas a–e, com ressalvas já declaradas), commitar só esse arquivo
(`git commit -- docs/PREDICOES-CEREBRO.md`; o checkout do Universe tem trabalho do Astra
sem commit — não tocar). Próximo: confirmatória grande (6 sementes, 48 seres) da
distribuição de treino vencedora, com segunda held-out por dose — registrar antes.

Pistas: `pista_check --ate <volta>` sempre; `gpu_evolve` recusa pista com defeito (P1.8)
com exit 1 em 0 s. Censo com defeitos: `/media/llm-data/scratch/track_census_8100_8299.tsv`.

## lab-ui (PRD `LLM/lab-ui/PRD.md`)

- main: S0 contrato, S3 shell, S2 schema adotado. `ui/integrate-micro` (S4+S5 integrados,
  rodada 3): agente finalizando commit + screenshots v3 em
  `/media/llm-data/scratch/integrate/screens/v3/`. Depois: testador frio → merge na main.
- S1 API (`ui/s1-api`, neuromod-lab): testador frio terminando itens LAN/CSRF/audit.
  PASS → merge na main do neuromod-lab.
- Falta: S6 (live `/ws/live`), contrafactual real na UI (máscara na GPU já existe:
  `Universe/docs/KERNELS-COUNTERFACTUAL-MASK.md`), observação L1/L2 (Astra implementou,
  checkout do Universe ainda sem commit).
- Universe `ui/s2-pack` publicado, NÃO mesclado em race-world-v3 (esperar checkout limpo).

## Perguntar ao Leonardo (não decidir sozinho)

- Limpar `~/.npm` (5,7 GB no disco do sistema)?
- Criar remote no GitHub para `lab-ui` (hoje só local)?
