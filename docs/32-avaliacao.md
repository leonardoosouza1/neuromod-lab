# 32 — Avaliação honesta como padrão + infraestrutura de fila (E18, 2026-09-02)

Este doc é do agente E18 (doc 28-sociedade.md §1). Entrega: `src/avaliacao.py`,
`src/runner_comum.py`, `scripts/fila.sh`. Não toca `lab.py`, `e13_corpo.py`
nem `PREDICOES.md` — só arquivos novos.

## 1. O que é "padrão honesto" e por quê

O doc 27 (§6.5, §6.18–6.21) e o doc 00-NEGATIVOS (N17/N18, regras 13–14)
descobriram, do jeito caro (baterias inteiras jogadas fora), duas armadilhas
de avaliação neste laboratório:

- **Regra 13 — mortalidade só conta com n ≥ 5 sementes.** Com n=3 o sinal
  trocou de sinal 5 vezes num único dia ("a dor ensina" +0.75 → −0.45; sono
  em bloco −3pp → +3pp e −10pp → +2pp). A variância entre sementes de
  evolução é ±8pp em mortos e ±1.5 em fitness — menor que isso é ruído, não
  efeito.
- **Regra 14 — um evento raro (morte, pane, greve) só é visível na seleção
  se `vidas_por_genoma ≳ 1/p²`.** Com mortalidade p≈0.18–0.25 e só R=4
  vidas/genoma na avaliação de cada indivíduo durante a evolução, o ruído da
  morte (±10pp) afoga qualquer sinal de 5pp — a seleção fica CEGA, não
  fraca. R=16 (o padrão adotado) resolve isso no regime medido aqui;
  `1/p²` com p=0.18 pede ~30+, então R=16 é uma aposta deliberadamente
  conservadora-mas-não-máxima (custo cresce ~linear com R).
- **Doc 27 §6.5 — cidades 1000+ são ~30% otimistas.** O campeão medido só em
  cidades-seed 1000+ caiu −42% ao trocar pra 2000+. Daí a "média de 6
  cidades" = 2 conjuntos de 3 cidades nunca vistas no treino (seeds 1000+ e
  2000+), sempre reportada — nunca só o conjunto fácil.

**Padrão honesto = as três regras juntas:** evoluir com R=16 vidas/genoma e
≥5 sementes, avaliar cada campeão em ≥2 conjuntos de cidades nunca vistas, e
reportar a MÉDIA entre conjuntos (não só o mais fácil). Isso é o preset
`honesto` de `runner_comum.PRESETS` e o que `avaliacao.evoluir_e_avaliar` +
`avaliacao.avaliar_honesto` fazem por padrão.

O que isso NÃO é: uma regra sobre TODA avaliação do laboratório. Exploração
rápida (achar se uma ideia tem qualquer chance) continua legítima com R=4 e
3 sementes — só não decide nada sobre mortalidade/evento raro nesse regime
(é fumaça, não veredito). O padrão honesto é para quando a pergunta envolve
morte, pane ou qualquer evento raro selecionado.

## 2. `src/avaliacao.py` — API

- `telemetria(m, T)` — cópia EXATA da função homônima de `e13_corpo.py`
  (mesmos campos: fit, ent, avar, av_fuel/furo/oleo/quente, mortos, t_vida,
  vida_fim, dano, n_oficina, n_posto, pobre_frac, dinh, n_mob, conv_por_dia,
  res_media, sono, par_fad, fuel_22, n_bloco, par_noite_frac, ent_noite).
  Copiada e não importada de propósito — E18 não deve depender de
  `e13_corpo.py` (cada agente só mexe nos próprios arquivos, doc 28 §2).
  `mortos` = fração de réplicas com `vida <= 0`.
- `avaliar_honesto(Arq, W_por_semente, cfg, T=1200, conjuntos=(1000,2000), n_cid=3, R=128)`
  roda cada campeão (uma política por semente) em cada conjunto de `n_cid`
  cidades nunca vistas (seeds `base..base+n_cid-1`), com R réplicas por
  campeão/cidade. Devolve telemetria por conjunto, por conjunto médio-entre-
  sementes, e a MÉDIA HONESTA entre conjuntos.
- `evoluir_e_avaliar(Arq, cfg, P=1024, G=60, T_evo=1200, seeds=(0,1,2,3,4), R=16, ...)`
  chama `evoluir_sementes` (do `lab.py`) e depois `avaliar_honesto`; se
  `out_dir`+`nome` forem passados, salva um JSON (escrita atômica, com `W` e
  `hist` dos campeões — dá pra retomar uma linha de investigação sem
  reevoluir).
- `tabela(jsons, colunas=('fit','mortos'), por_semente=False)` — markdown, 1
  linha por braço, colunas = cada item de `colunas` por conjunto + a média
  honesta. Aceita 1+ caminhos de JSON (ou dicts já carregados), tanto no
  formato de 1 braço (`evoluir_e_avaliar`) quanto no combinado de
  `rodar_bracos` (chave `'bracos'`). `por_semente=True` acrescenta os
  valores individuais entre colchetes (regra 13: sempre olhar a dispersão).
- `resumo_para_painel(jsons) -> dict` — resumo compacto por braço (fit,
  mortos, por conjunto, n_sementes), no espírito dos dados que
  `docs/painel-27-corpo-carro.html` usa (o painel hoje tem os arrays escritos
  à mão; isto poupa a conta na hora de atualizar, não substitui a curadoria
  visual).

## 3. Fila: `scripts/fila.sh`

Padroniza o que já se fazia à mão em
`/media/llm-data/universe-runs/neuromod-lab-taxi/fila_e13*.sh`: uma
sequência de comandos python, cada um virando `<tag>.log` + `<tag>.done`, e
`<fila>_TUDO.done` no fim.

```
scripts/fila.sh <arquivo_de_fila> [--out DIR] [--depois-de ARQUIVO.done]
```

Arquivo de fila: uma etapa por linha, `tag | comando shell completo`
(`#` comenta, linha em branco é ignorada). `--depois-de` espera outro
`.done` aparecer antes da 1ª etapa — o mesmo `until [ -f ... ]; do sleep 5;
done` que já era usado pra encadear filas (ex.: `fila_e13l.sh` esperava
`fila_e13.sh` terminar). Ver `scripts/exemplo_fila.txt`.

Cada etapa grava seu `.done` mesmo se falhar (status ≠ 0 fica registrado
dentro do arquivo, e um aviso vai pro stderr) — assim quem está esperando
nunca trava por uma etapa que quebrou; olhe o `.log` da etapa pra saber o
que houve.

## 4. `src/runner_comum.py` — como e15/e16/e17 migram

O runner de cada linha (`e13_corpo.py` hoje; `e15_economia.py`,
`e16_glandulas.py`, `e17_produtos.py` sendo escritos em paralelo no mesmo
padrão) tem 3 peças que se repetem: um `cfg_XXX(**kwargs)` que liga flags
no `Cfg`, uma lista `BRACOS = [(nome, kwargs), ...]`, e um `main()` que
evolui+avalia+salva+imprime cada braço. `runner_comum.py` fatora a 3ª peça:

```python
from runner_comum import criar_parser, rodar_bracos

if __name__ == '__main__':
    ap = criar_parser()
    ap.set_defaults(tag='e15_economia')       # nome do JSON de saída
    ap.add_argument('--arq', default='reativo', choices=(...))   # o que for específico do runner
    args = ap.parse_args()
    Arq = {...}[args.arq]
    rodar_bracos(BRACOS, Arq, cfg_economia, args)
```

Isso dá de graça: `--preset rapido|longo|honesto`, `--seeds`, `--R`,
`--teste-seed` (lista — os conjuntos de cidades), `--T-aval`, `--G`,
`--T-evo`, `--tag`, `--out`; e a avaliação honesta com telemetria completa
(não só fit/mortos) por braço, salva incrementalmente (um braço não perde o
anterior se a máquina cair no meio). O que cada runner mantém seu: `Cfg`
(não é tocado por E18), a lista de `BRACOS` e a resolução de `--arq`/`--fase`
(flags específicas continuam sendo `ap.add_argument` extra no mesmo parser,
igual ao que `e13_corpo.py` já faz com argparse puro).

Migração de um runner já escrito no padrão do e13 (main() manual): trocar o
laço `for nome, kw in bracos: ... braco(...)` por uma chamada a
`rodar_bracos(BRACOS, Arq, cfg_fn, args)` e apagar o parsing manual de
G/R/T-evo/T-aval/seeds/tag/out (fica em `criar_parser()`). O formato do JSON
de saída muda (chaves por conjunto em vez de um `T_aval` só) — `tabela()` e
`resumo_para_painel()` leem o formato novo; JSONs antigos do e13 não são
compatíveis com essas duas funções (são de outro agente, E18 não os toca).

## 5. Custo em tempo (GPU compartilhada — medir de novo se a carga mudar)

Números do dia (E13/E14, mesma GPU, mundo-corpo, T=1200, ~26 nós/cidade):

| preset | R (vidas/genoma) | sementes | 1 braço |
|---|---|---|---|
| rápido/longo | 4 | 3–5 | ~80 s |
| **honesto** | **16** | **5** | **~540 s** (9 min) |
| honesto, treino 10 dias (T_evo/T_aval=2400) | 16 | 5 | ~1800 s (30 min) |

Regra prática: uma fila com N braços no preset honesto custa `N × 9 min`
(ou `N × 30 min` em vida de 10 dias) — dimensionar o `--so`/lista de braços
por rodada pensando nisso, e usar `scripts/fila.sh` pra não precisar ficar
olhando o terminal.
