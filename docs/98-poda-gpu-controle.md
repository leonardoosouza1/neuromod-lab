# 98 — Controle de poda na GPU: `generate` × `generate_fine` × `prune` (14/09/2026)

Responde `docs/97` §2 (revisão do Astra, confirmada por re-derivação): a comparação
publicada em `docs/93`/`docs/94` (`gerar` × `podar`, +1,50 de fitness de treino,
p=1,7e-4, 18/20 sementes) muda **duas** variáveis ao mesmo tempo — σ 0,30 → 0,15
**e** a máscara. O controle que isola σ, `gerar_fino` (σ=0,15, sem máscara), existe
em `colab/pruning/poda2.py:21` e nunca foi rodado nas 20 sementes. Sem ele, docs/97
concluiu: **"não se pode afirmar que a poda vence; pode ser só σ menor"**.

Este documento porta o operador de máscara para o motor GPU do lab
(`evolve_masked` em `src/lab.py`) e roda os três braços — `generate` (σ .30),
`generate_fine` (σ .15, sem máscara), `prune` (σ .15 + máscara heritável) — com
as MESMAS cidades e MESMAS sementes evolutivas, avaliando em cidades held-out.

## Operador (código)

- `src/lab.py::evolve_masked` — mega-lote de sementes (como `evoluir_sementes`)
  com máscara binária `M` (P, NP) **heritável por indivíduo**: o filho herda a
  máscara do pai e só DEPOIS sofre a mutação do modo. A política nunca lê `W`
  puro — sempre `Wef = W*M`. Três modos, exatos a `colab/pruning/poda2.py:19-27`:
  `generate` (σ .30, sem máscara), `generate_fine` (σ .15, sem máscara), `prune`
  (σ .15, máscara nasce toda ligada, desliga p=.05/religa p=.015 por geração).
- Com `mode='generate'`, o bloco de mutação da máscara nunca desenha do gerador
  (p_off=p_on=0 → sem draw, não só "sem efeito"): o stream de RNG e os pesos
  finais são **bit-exatos** a `evoluir_sementes(sigma_mut=.30)` de hoje.
  Verificado em `src/test_evolve_masked.py::test_evolve_masked_generate_matches_evoluir_sementes`
  (rodado localmente, GPU, 14/09 12:51 — PASSOU, ver §Verificação abaixo).
- `src/rodar.py::prune_control_battery` — roda os três braços em um processo
  (mesmas cidades por construção), avalia os campeões em `n_teste` cidades
  held-out com `eval_reps` réplicas, grava um JSON por (modo, semente).
- CLI: `--prune-battery` (novo flag em `src/rodar.py`), whitelisted via o script
  `rodar` (já liberado em `_nmd/whitelist.json`).

## Previsão — escrita ANTES de rodar a bateria (14/09/2026, ~13:00)

Hipótese sob teste: o "poda supera mutação livre" de docs/93/94 é artefato do
passo de mutação menor (σ), não da máscara em si. Não tenho os números deste
motor GPU ainda (a política `Reativo` aqui tem NP=44 num mundo mais rico que os
24 nós numpy — a escala absoluta do fitness pode diferir da do protótipo).
Previsão qualitativa e de significância, não valor absoluto:

1. **`prune` × `generate`** (a comparação original, replicada aqui): diferença
   **positiva** a favor de `prune`, provavelmente **significativa** (p<0,05) em
   fitness de treino — replica a direção de docs/94, porque muda duas variáveis
   a favor de `prune` (σ menor + máscara).
2. **`prune` × `generate_fine`** (o teste decisivo, o que falta): diferença
   **pequena e NÃO significativa** em fitness de treino — se a hipótese do
   artefato de σ estiver certa, isolar o σ deve fazer a vantagem da máscara
   encolher para perto de zero. Prevejo `|Δ| < 0,5` na mesma escala de fitness
   e p>0,10. Em generalização (held-out), prevejo os dois braços dentro do
   ruído um do outro.
3. **`generate_fine` × `generate`** (σ isolado): diferença **positiva e
   significativa** a favor de `generate_fine` — a maior parte do ganho que
   docs/94 atribuiu à poda deve reaparecer aqui, só com σ menor.

**Se a previsão 2 se confirmar** (prune ≈ generate_fine, generate_fine >
generate): o achado "poda vence" de docs/93/94 era artefato de σ, não evidência
de que desligar conexões seja superior a ajustá-las — e isso tem que ser dito
sem rodeio, porque é exatamente o mecanismo que `docs/95`/`src/flybrain/selection.py`
citam como justificativa para usar poda no conectoma da mosca (docs/94 §2).
**Se a previsão 2 for refutada** (prune bate generate_fine de forma clara e
consistente): a máscara carrega informação além do σ, e o mecanismo de
docs/95 §5 ganha suporte — nesse caso o próximo teste é MEDIR o que a máscara
descobre (quais features ficam ligadas em 20/20 sementes, como em docs/94 §1
"núcleo convergente").

## Comando (reprodução)

```bash
cd /home/leonardo/projects/LLM/neuromod-lab
/home/leonardo/projects/LLM/.venv-rocm/bin/python src/rodar.py --prune-battery \
  -P 512 -G 60 -R 1 --tevo 450 --taval 1200 \
  --treino 6 --teste 5 --n-cidade 24 \
  --evo-seeds 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 \
  --eval-reps 64 --modes generate generate_fine prune \
  --out /media/llm-data/universe-runs/neuromod-lab-taxi/poda-gpu-controle
```

Rodado pela fila do `nmd` (pedido `_nmd/pedidos/poda_gpu_controle.json`,
script `rodar`, `out=poda-gpu-controle`), não invocado diretamente — a GPU já
tinha a bateria `fly_f2_*` em curso; o `nmd` serializa.

## Estimativa de tempo (medida ANTES de enfileirar, 14/09 12:51-12:56)

Sondas locais na mesma GPU, mesma escala-alvo (ver histórico do comando —
`time_probe.py`/`time_probe2.py`/`time_probe3.py`, descartadas depois):

- `P=512, S=20 sementes empilhadas, treino=6 cidades, T_evo=450, R=1`: 6
  gerações em 45,8 s → **7,64 s/geração** (média COM o warmup do
  `torch.compile`, que só paga uma vez por shape — os 3 modos reusam o mesmo
  shape, então só o primeiro paga).
- Evolução: 3 modos × 60 gerações × 7,64 s ≈ **1375 s ≈ 23 min** (limite
  superior; o real deve ficar abaixo porque só a 1ª geração da bateria inteira
  paga compile).
- Avaliação held-out: `eval_reps=64, teste=5 cidades, T_aval=1200`: 1,25
  s/campeão em regime estável (+16,7 s de compile uma vez) → 60 campeões
  (20 sementes × 3 modos) ≈ **1,5 min**.
- VRAM de pico na sonda: 0,20/12,9 GB (2%) — folga enorme sobre o teto de 80%.
- **Total estimado: ~25-30 min de GPU**, bem abaixo do orçamento de ~2h pedido
  (a bateria `fly_f2_*` roda em paralelo/antes via a fila; este job é exclusivo
  e espera a vez, o relógio acima é só o tempo que ELE consome depois de
  começar).

## Verificação (smoke barato, rodado localmente antes de enfileirar)

```
$ /home/leonardo/projects/LLM/.venv-rocm/bin/python src/test_evolve_masked.py
  evolve_masked(mode=generate) == evoluir_sementes(sigma_mut=.30)  bit-exato (2 sementes)  OK
  evolve_masked(mode=generate_fine)  mascara permanece 1.0  OK
  evolve_masked(mode=prune)  deterministico + mascara move (densidade < 1)  OK
  evolve_masked(mode=prune)  1 geracao: densidade 1.000 perto de 1 (heranca OK)  OK
ok
```

---

## Resultados (verificado — 14/09/2026 13:00-13:13, nmd `poda_gpu_controle`)

Bateria terminou com `exit_code=0` em **740,3 s (12,3 min)** de GPU — abaixo da
estimativa conservadora de ~25-30 min (sem o overhead de warmup repetido entre
modos, o custo real por geração ficou menor que na sonda). Tempo por braço:
`generate` 242 s, `generate_fine` 240 s, `prune` 258 s.

- JSON bruto: `/media/llm-data/universe-runs/neuromod-lab-taxi/poda-gpu-controle/poda-gpu-controle-20260914-1313.json` (77,9 KB, 20 sementes × 3 modos, histórico completo de fitness por geração + máscara do campeão)
- Análise pareada: `.../poda-gpu-controle-20260914-1313-analise.json`
- Log completo: `_nmd/log/poda_gpu_controle.log`; manifesto: `.../poda-gpu-controle/manifest.json`
- **Reprodutibilidade verificada**: `sha256sum src/rodar.py` no working tree e
  `git show 18b14c7:src/rodar.py | sha256sum` batem exatamente
  (`47a7a139...6bd247`) com o `script_sha256` do manifest — o commit `18b14c7`
  é byte a byte o código que rodou (o `evolve_masked` de `src/lab.py` está no
  commit `f8f7263`, ver nota de proveniência abaixo).
- Comando: o mesmo do bloco acima, reproduzido pelo `nmd` a partir do pedido
  `_nmd/pedidos/poda_gpu_controle.json` (arquivado em `_nmd/feitos/` ao terminar).

### Fitness de treino (última geração, 20 sementes pareadas, `ttest_rel`)

| comparação (A − B) | média A | média B | Δ pareado | IC95% | t | p | vitórias A/B |
|---|---|---|---|---|---|---|---|
| prune − generate | 8,774 | 8,067 | **+0,707** | [+0,401, +1,014] | 4,84 | **1,1×10⁻⁴** | 17/20 |
| prune − generate_fine | 8,774 | 7,824 | **+0,950** | [+0,659, +1,241] | 6,83 | **1,6×10⁻⁶** | 19/20 |
| generate_fine − generate | 7,824 | 8,067 | −0,243 | [−0,518, +0,033] | −1,84 | 0,082 | 4/20 |

### Entregas held-out (5 cidades nunca vistas no treino, 64 réplicas/campeão, `T=1200`)

| comparação (A − B) | média A | média B | Δ pareado | IC95% | t | p | vitórias A/B |
|---|---|---|---|---|---|---|---|
| prune − generate | 13,75 | 9,95 | **+3,80** | [+3,20, +4,40] | 13,18 | **5,2×10⁻¹¹** | 20/20 |
| prune − generate_fine | 13,75 | 10,31 | **+3,44** | [+2,51, +4,36] | 7,79 | **2,5×10⁻⁷** | 19/20 |
| generate_fine − generate | 10,31 | 9,95 | +0,36 | [−0,53, +1,25] | 0,85 | 0,41 | 11/20 |

### Avarias held-out (mesma amostra)

`prune` tem MAIS avarias em absoluto (21,0 vs 15,6 em `generate`, p=7,8e-7; vs
17,3 em `generate_fine`, p=0,002) — mas também entrega muito mais. Normalizando
por entrega, avarias/entrega fica em **1,53** (`prune`), **1,56** (`generate`)
e **1,67** (`generate_fine`): `prune` não é proporcionalmente mais arriscado,
é mais ativo (mais viagens, logo mais exposição).

### Densidade final da máscara (`prune`, 20 sementes)

Média **0,288** (dp 0,050; min 0,205; max 0,386) — o campeão converge para
~29% das 44 conexões ligadas. Mesma ordem de grandeza do 0,34 relatado no
protótipo CPU (docs/94), numa política de 44 parâmetros contra 24 do protótipo
e num mundo bem mais rico (`mundo=base` do `lab.py`, não o táxi numpy de 24
nós).

## Veredito

A minha previsão pré-registrada (seção acima) estava **errada no ponto
central**. Previ que isolar σ (`generate_fine`) recuperaria a maior parte do
que docs/93/94 atribuíram à poda, e que `prune` × `generate_fine` sairia
pequeno e não significativo — a leitura "era só o passo de mutação". Aconteceu
o oposto:

1. **`prune` bate `generate_fine` com folga**: treino +0,950 (p=1,6×10⁻⁶,
   19/20 sementes), held-out +3,44 entregas (p=2,5×10⁻⁷, 19/20 sementes).
   Isolar σ NÃO fecha o gap para a poda. A máscara carrega sinal que o passo
   de mutação sozinho não entrega.
2. **`generate_fine` NÃO bate `generate`**: a diferença é pequena, NÃO
   significativa, e vai na direção ERRADA no treino (`generate_fine`
   numericamente pior, p=0,082) e também não significativa no held-out
   (p=0,41). Reduzir σ sozinho, sem a máscara, não ajudou neste motor —
   contraria tanto a intuição de "mutação fina converge melhor" quanto a
   minha previsão.
3. **Consequência**: o achado "poda supera mutação livre" de docs/93/94
   **sobrevive ao controle que faltava** (docs/97 §2). Não é artefato de σ —
   é a MÁSCARA (o canal discreto liga/desliga) que faz o trabalho, tanto em
   fitness de treino quanto, ainda mais fortemente, em generalização
   held-out.

**Mecanismo (hipótese, consistente com o dado mas não isolado aqui)**: a
máscara não pode ADICIONAR expressividade à política — `W*M` com `M` binário
é sempre um subconjunto do que `W` sozinho alcança (zerar um peso é um ponto
já presente no espaço de `W`). A vantagem de `prune` não vem de mais
capacidade; vem da DINÂMICA de busca: congelar ~70% das coordenadas por
geração reduz o σ efetivo por coordenada ATIVA muito mais do que baixar o σ
global de .30 para .15 (que ainda perturba as 44 em bloco todo passo), e a
herança da máscara deixa a evolução ACUMULAR uma escolha de "quais ~13 de 44
pesos importam" em vez de ressorteá-la a cada geração — mais perto de
coordinate descent que de random walk. Isso é exatamente a aposta citada em
docs/94 §2 ("desligar uma conexão é um sinal de seleção discreto e
atribuível; mexer um peso é difuso"), agora com um controle que faltava.

Isto reforça (não substitui) a aposta de `src/flybrain/selection.py`/docs/95
de usar poda sobre o conectoma real em vez de gerar do zero — mas o teste
aqui é **um** operador (`evolve_masked`), **uma** arquitetura (`Reativo`, 44
parâmetros), **um** mundo (`mundo=base`), um conjunto fixo de 6 cidades de
treino e 20 sementes evolutivas. Não testei: outras arquiteturas (`BancoEMA`,
`Hibrido`, ...), outros mundos (`cego`, `ruas`, `semgps`), sensibilidade a
p_off/p_on (a olho, como no protótipo), nem se o "núcleo convergente" de
features (quais dos 44 pesos ficam ligados em 20/20 sementes) é estável —
esse é o próximo teste discriminante natural (ver docs/94 §1, "núcleo
convergente").

**Nota lateral exploratória (não pré-registrada)**: `generate_fine` performar
pior que `generate` no treino (não significativo, p=0,082, mas na direção
consistente também no held-out) é candidato a um achado por si: σ menor SEM
mecanismo de congelamento pode reduzir a taxa de exploração sem ganho de
estabilidade suficiente para compensar em 60 gerações. Rotulado aqui como
observação exploratória de um dado já coletado, não uma previsão testada —
precisaria de bateria dedicada para virar afirmação.

## Nota de proveniência do código (git)

`src/lab.py::evolve_masked` e `src/test_evolve_masked.py` foram editados no
working tree compartilhado (sem worktree) e acabaram absorvidos pelo commit
`f8f7263` ("fly_reflex: ...") de uma tarefa paralela que rodou algo como
`git commit -a` antes de eu commitar — o conteúdo está correto e é exatamente
o que rodou (conferido por `git blame`/`sha256sum`), mas a mensagem daquele
commit não descreve esta mudança. Registrado aqui para quem for ler o log
depois não estranhar a atribuição. `src/rodar.py` (CLI, `prune_control_battery`)
ficou em commit próprio (`18b14c7`), feito por mim.
