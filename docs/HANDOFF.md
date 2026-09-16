# HANDOFF — estado para uma sessão nova (reescrever, não acrescentar)

Última reescrita: 16/09/2026 17:58. Leia só isto + o que um item apontar. Não reabra
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
   por etapa, relatório ≤ 150 palavras, ≤ 3 ao mesmo tempo. O limite de chamadas no prompt
   NÃO é respeitado (16/09: pedidos de 25–45 viraram 40–76) — o que controla custo é tarefa
   pequena e bem especificada, com critério verificável. Agente grande que morreu
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

- **main 6c13756**: S0 contrato, S3 shell, S4+S5 micro integrados e testados a frio (112
  testes). Tela micro abre o trace denso do campeão; clique no pedal dispara o fluxo de
  contribuição e explica quando nada o alimenta. Repo só local (sem remote).
- **neuromod-lab main**: S1 API mesclada (102 testes); valida pista na volta inteira e
  recusa `[AVISO]`. `--lan` lê `/media/llm-data/lab-ui.env` (600, criado 16/09).
- Maior lacuna visual: cérebro 3D com 0 sinapses porque o binário congelado não grava
  L1/L2. A observação L1/L2 + máscara contrafactual do Astra está implementada e validada
  (`Universe/docs/KERNELS-OBSERVATION-L1L2.md`, `KERNELS-COUNTERFACTUAL-MASK.md`) mas SEM
  commit no checkout do Universe → pedir commit, congelar binário novo, gravar trace denso
  com L1/L2, adaptar o empacotador S2 (schema de observação 2).
- Falta: S6 (live `/ws/live`), painel contrafactual ligado à GPU, merge de `ui/s2-pack` no
  Universe (esperar checkout limpo). Defeito menor: razões técnicas em inglês no painel.

## Subir o painel (loopback)

```bash
cd ~/projects/LLM/neuromod-lab/src && setsid nohup ~/projects/LLM/.venv-rocm/bin/python -m lab_api --port 8130 \
  >> /media/llm-data/scratch/lab-ui-serve/api.log 2>&1 < /dev/null &
cd ~/projects/LLM/lab-ui && setsid nohup node_modules/.bin/vite --host 127.0.0.1 --port 5173 --strictPort \
  >> /media/llm-data/scratch/lab-ui-serve/ui.log 2>&1 < /dev/null &
```
Macro http://127.0.0.1:5173/ · micro http://127.0.0.1:5173/run/champ_nocost_s77_dense_t8005.
`node_modules` e o trace denso em `public/fixtures/trace-v1/` são symlinks para `/media/llm-data`.
Dados reais por padrão; `VITE_API_MOCK=1` força mock. Ao vivo só lista corrida com `--panel`.

## Perguntar ao Leonardo (não decidir sozinho)

- Criar remote no GitHub para `lab-ui` (hoje só local)?
