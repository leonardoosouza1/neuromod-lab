# `flymap` v2 — layout de bytes, decisão de binding e mapa para quem escreve o kernel

Status: implementado e exportado (14/09/2026). Escrito por `src/fly_export.py` +
`src/flybrain/flymap_file.py` + `src/flybrain/eye.py`; consumido pelo lado Rust/WGSL
descrito em `Universe/docs/FLY-MAP-BRAIN.md` §1 e `Universe/docs/KERNELS-FLY-SPIKING.md`
(formato combinado byte a byte com quem escreve o reader lá).

Todos os identificadores de código abaixo (nomes de campo, flags, funções) estão em
inglês, como o resto do projeto; a prosa é em português.

---

## 1. Layout de bytes (little-endian)

Magic `FLYMAP02` (ou `FLYMAP01` quando nenhum bloco opcional é pedido — ver §1.3).

### 1.1 Header — 8 × u32, offset de bytes 8..40

| word (0-based) | byte offset | campo | significado |
|---|---|---|---|
| 0 | 8..12 | `n` | número de neurônios |
| 1 | 12..16 | `m` | número de arestas (sinapses agregadas pre→post) |
| 2 | 16..20 | `n_types` | número de cell-types (com fallback `class?super_class`) |
| 3 | 20..24 | `k_in` | número de grupos aferentes (`in_group_of`) |
| 4 | 24..28 | `k_out` | número de grupos eferentes (`out_indptr`/`out_members`) |
| 5 | 28..32 | `out_members_len` | tamanho de `out_members` |
| 6 | 32..36 | `flags` | bit 0 = presynaptic CSR; bit 1 = pixel binding; bit 2 = no-refractory bitmap |
| 7 | 36..40 | `reserved` | sempre 0 |

**Importante**: `flags` é a palavra 6 (penúltima), `reserved` é a palavra 7 (última). Uma
tentativa anterior tinha isso invertido (reserved na 6, flags na 7) — corrigido nesta
versão porque é o campo que o reader Rust lê para decidir quais blocos vêm a seguir.

### 1.2 Corpo v1 (sempre presente, offset 40 em diante)

| campo | tipo | tamanho | conteúdo |
|---|---|---|---|
| `indptr` | `u32[n+1]` | `4(n+1)` | CSR por linha = neurônio **PÓS**-sináptico |
| `indices` | `u32[m]` | `4m` | neurônio **PRÉ**-sináptico de cada aresta |
| `weights` | `f32[m]` | `4m` | contagem de sinapse com sinal (+ excitatório, − inibitório) |
| `type_of` | `u32[n]` | `4n` | id de cell-type 0..n_types-1 |
| `in_group_of` | `u32[n]` | `4n` | id de grupo aferente, ou `NONE=0xFFFFFFFF` |
| `out_indptr` | `u32[k_out+1]` | `4(k_out+1)` | CSR de membership dos grupos eferentes |
| `out_members` | `u32[out_members_len]` | `4·oml` | índices de neurônio por grupo eferente |

Isso é **byte-idêntico** ao exportador v1 antigo quando nenhum bloco opcional é escrito
(`write_flymap` sem os argumentos `pre_*`/`pixel_of_neuron`/`no_refractory` produz magic
`FLYMAP01` e os mesmos bytes de sempre — provado por
`test_flymap_v1_bytes_unchanged_by_v2` em `src/fly_tests.py`).

### 1.3 Blocos opcionais v2 (só presentes se o bit de `flags` estiver ligado, nesta ordem)

| bit | flag | bloco | tipo | conteúdo |
|---|---|---|---|---|
| 0 | `FLAG_PRE_CSR` | `pre_indptr` | `u32[n+1]` | CSR por linha = neurônio **PRÉ**-sináptico |
| | | `pre_indices` | `u32[m]` | neurônio **PÓS**-sináptico de cada aresta (parceiro do CSR por-post) |
| | | `pre_weights` | `f32[m]` | mesmo multiset de arestas do CSR v1, reordenado |
| 1 | `FLAG_PIXEL_BINDING` | `pixel_of_neuron` | `u32[n]` | índice de pixel da retina renderizada (row-major, `row*cols+col`), `0xFFFFFFFF` = não dirigido pelo olho |
| 2 | `FLAG_NO_REFRACTORY` | `no_refractory` | `u32[⌈n/32⌉]` | bitmap LSB-first (bit `i&31` da word `i>>5`): neurônio Poisson/dirigido roda sem período refratário |

`pre_csr` garante o mesmo multiset de arestas `(pre, post, weight)` que o CSR v1 — testado
em `test_flymap_v2_pre_csr_is_the_same_edge_multiset` comparando as triplas ordenadas dos
dois lados. `no_refractory` tem exatamente um bit ligado por neurônio com pixel binding
(`no_rfc = pixel_of != NONE` em `fly_export.py`).

Sidecar `<nome>.json`: nomes de type/in-group/out-group, geometria da retina, alvo do
olho (`eye_target`), fit (`eye_fit`), contagens de binding nos dois fits, SHA-256 da
fonte, filtros (`min_weight`, `exclude_optic`, `shuffle_targets`).

---

## 2. Decisão de binding: `pixel_of_neuron`

### 2.1 Por que existe mais de um alvo (`--eye-target`)

Uma medição de 14/09/2026 (`PREDICOES.md` #189v, `src/fly_diag_vision.py`) mostrou que, no
modelo **spiking** (LIF), dirigir os 7 932 fotorreceptores R1-6 não propaga: a lâmina
dispara (L1/L2 a 26 Hz) mas o estágio seguinte é liquidamente inibitório — Mi1 recebe
−3214 synapse·Hz, Tm3 −1348, T4 −1059, T5 −1997, HS −219. Nada depois do primeiro hop
dispara. A razão é biológica: fotorreceptor e lâmina/médula são **graded** (não disparam
spike de verdade); um LIF sem excitação tônica não representa esse estágio. Já dirigir os
detectores de movimento T4/T5 diretamente alcança LPLC2, HS/VS e a fibra gigante DNp01 a
95,6 Hz (100% dos trials).

Por isso `--eye-target`:

- `photoreceptor` (padrão do exportador): liga os R1-6 via `flybrain.eye.photoreceptor_chart`.
  Correto para o modelo de **taxa** (`fly_step`/`fly_read`, já em produção), que trata bem
  os estágios graded.
- `motion`: liga T4+T5 via `flybrain.eye.motion_chart` (chart novo, construído do mesmo
  jeito que `photoreceptor_chart` — PCA das posições `pos_x/y/z` por lado sobre um chart
  2-D, depois mapeado para azimute/elevação). Correto para o **kernel spiking** (K2
  `fly_eye_drive`), que é o único caminho que demonstrou propagar até os efetores.

Os dois charts compartilham a mesma máquina (`flybrain.eye._sheet_chart`); só a seleção de
cell-type muda (`cell_type == 'R1-6'` vs. regex `^(T4|T5)`).

### 2.2 `--eye-fit {strip, stretch}` e a inversão do warp

A retina renderizada do Universe (`src/config.rs`, `src/gpu/retina.wgsl`, verificado
14/09/2026) é 14 linhas × 126 colunas, FOV 120°, pitch de −0.012 a −0.06 rad — ou seja
**cobre só ~0,69° a ~3,44° de elevação**. A linha 0 (fóvea) é tan-warped
(`tan(u·K)/tan(K)`, K=1,25): mais densa perto do centro. `flybrain.eye.retina_pixel_angles`
reproduz esse warp exatamente (copiado do shader); `pixel_of_neuron(fit='strip')` **inverte**
esse warp para achar a coluna certa — dado o ângulo real de um neurônio, busca qual pixel
warped realmente amostra aquele ângulo (`_bin_into_cells`), em vez de assumir índice de
coluna linear.

- `strip` (honesto angularmente): um neurônio só é ligado se seu (azimute, elevação) cai
  dentro da janela minúscula que a retina realmente renderiza. Poucos neurônios sobram.
- `stretch` (padrão do exportador, `--eye-fit stretch`): o span completo de azimute E
  elevação do chart é mapeado linearmente sobre as 14×126 colunas/linhas, então **todo**
  neurônio do chart é usado. Não é fiel a ângulo por construção — existe porque a retina
  renderizada é uma tira fina demais para amarrar quase nada de forma anatômica.

Padrão é `stretch` porque `strip` liga menos de 2% do olho em qualquer alvo (tabela
abaixo).

### 2.3 Contagens medidas (14/09/2026, `flymap_783*_v2.bin`)

| alvo | total de neurônios no chart | `strip` ligados | `stretch` ligados |
|---|---|---|---|
| `photoreceptor` (R1-6) | 7 932 | **77** (0,97%) | **7 932** (100%) |
| `motion` (T4+T5, 6 241+6 005) | 12 246 | **188** (1,54%) | **12 246** (100%) |

Números confirmados por `src/fly_export.py` (que agora calcula e reporta os dois fits em
todo export, independente de qual foi realmente gravado no arquivo) e reproduzem o achado
da tentativa anterior (77/7932 para fotorreceptor/strip).

---

## 3. Para quem escreve o kernel

| bloco do `flymap` v2 | quem usa | kernel/host |
|---|---|---|
| `indptr`/`indices`/`weights` (CSR por POST, v1) | modelo de taxa, já em produção | `fly_step`/`fly_read` (`src/gpu/fly_map/`, Universe) |
| `pre_indptr`/`pre_indices`/`pre_weights` (CSR por PRE, flag bit 0) | modelo spiking novo | **K1** `fly_spike_step` — evento-dirigido, cada neurônio que disparou empurra pros vizinhos; precisa do CSR indexado por PRE porque caminha "saindo" do neurônio que disparou |
| `pixel_of_neuron` (flag bit 1) | drive do olho | **K2** `fly_eye_drive` — lê o buffer de retina/percepção e usa este binding para converter brilho de pixel em taxa de spike Poisson por neurônio; `--eye-target motion` é o que faz sentido hoje (ver §2.1) |
| `no_refractory` (flag bit 2) | drive do olho | **K1**/**K2** — todo neurônio com pixel binding roda como `PoissonInput` (sem período refratário), o bit já vem pronto do exportador, não precisa recalcular no kernel |
| `type_of`/`in_group_of`/`out_indptr`/`out_members` (v1) | ambos os modelos | seleção de tipo (pruning), binding de canal de entrada, leitura de comando (**K3** `fly_spike_readout` usa `out_indptr`/`out_members` igual ao `fly_read` de hoje) |

`n_types`, `k_in`, `k_out` do header já batem com os tamanhos desses blocos — nenhum
recálculo em runtime é necessário do lado GPU, que é o objetivo desta v2.

---

## 4. Arquivos exportados (14/09/2026)

Checado `df -h /media/llm-data` antes (4,9 GB livres); nada foi apagado.

| arquivo | flags | `eye_target` | `eye_fit` gravado | tamanho |
|---|---|---|---|---|
| `flymap_783_v2.bin` | `0x7` (pre-CSR + pixel + no-refractory) | `photoreceptor` | `stretch` | 244 269 836 bytes (≈244 MB) |
| `flymap_783_motion_v2.bin` | `0x7` | `motion` | `stretch` | 244 269 836 bytes (≈244 MB) |
| `flymap_783_w3_v2.bin` (`--min-weight 3`, 4 916 231 arestas) | `0x7` | `photoreceptor` | `stretch` | 81 457 804 bytes (≈81 MB) |

Espaço livre depois das três exportações: 4,4 GB (verificado — havia folga; nada precisou
ser apagado). Os arquivos v1 antigos (`flymap_783.bin`, `flymap_783_w3*.bin`,
`flymap_783_shuf0.bin`, ...) continuam no lugar, intactos.

Comando usado (idêntico para os três, variando `--min-weight`/`--eye-target`/`--name`):

```
python src/fly_export.py --out-dir /media/llm-data/datasets/flywire \
    --eye-target {photoreceptor,motion} [--min-weight 3] --name <nome>
```
