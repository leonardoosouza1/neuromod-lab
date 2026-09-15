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

## Run database — read this before building another viewer

Every battery lands in **`/media/llm-data/lab.db`** (SQLite). Query it directly; do not
grow a new panel or a new CSV parser per experiment.

```python
import sys; sys.path.insert(0, 'src')
import lab_db
db = lab_db.connect()
lab_db.batteries(db)                                   # what exists
lab_db.runs(db, battery='b1')                          # runs, status, configuration
lab_db.paired(db, 'b1', 'fixed', 'nocost', 'brake_pct_alive')   # the standard comparison
lab_db.curve(db, 'b1_fixed_s31')                       # progress per generation
lab_db.predictions(db, battery='b1')                   # index into the markdown ledgers
```

No server, no dependency, no port: `sqlite3` is in the standard library. The HTTP panel
(`python src/lab_api.py --port 8130`) reads the same file and exists for the browser.

- Ingestion is idempotent, so it is safe mid-battery:
  `python src/lab_db.py ingest /media/llm-data/universe-runs/neuromod-lab-taxi`
- The database INDEXES; it does not own. Replays and genomes stay as files and the
  `artifact` table carries path, size and checksum. The markdown ledgers stay the written
  record.
- `prediction.status` is written only by hand (`lab_db.py verdict <code> <status>`) or by
  the ✓/✗ glyphs. It is never inferred from prose: "refutada se X" is a criterion every
  good bet contains, so guessing produces a column agents would wrongly trust.
- `paired()` excludes unfinished runs by default — `v_last5` means the last five
  generations that EXIST, and comparing a run stopped at generation 6 with one that
  reached 30 is the effective-generations confound that invalidated prediction 180.
