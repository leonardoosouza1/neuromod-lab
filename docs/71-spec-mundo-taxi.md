# 71 — SPEC EXECUTÁVEL do mundo do táxi (v0, porta para o Universe)

Escrita em 2026-09-10 pelo arquiteto (Opus). **Fonte única da verdade para a
reimplementação em Rust.** Toda constante abaixo cita o arquivo e a linha de onde saiu.
Nada aqui foi executado — é leitura de código.

Alvo do v0: **o mesmo mundo, o mesmo cérebro (Linear), a mesma trajetória.** Sem retina,
sem regime, sem reprodução, sem prefeito, sem jardim comum, sem temperatura de decisão,
sem custo de gene.

Motivo da porta (`docs/70-reprojeto.md` §2.1): o tique em torch custa **4 486 lançamentos
de kernel ≈ 11.0 ms**; o Universe faz o tique inteiro em WGSL em **0.63 ms**. O ganho
buscado é de lançamento, não de aritmética.

---

## 0. Nomenclatura e módulos de origem

| símbolo | valor | origem |
|---|---|---|
| `G` | 9 (8 direções + ficar) | `src/campo.py:9` |
| `GR` | 128 (grade dos campos pré-computados) | `src/campo.py:10` |
| `TIPOS` | `[posto, comida, agua, descanso, oficina]` | `src/campo.py:13` |
| `ACOES` | 10 (ver §6) | `src/campo.py:16-17` |
| `S` | 10 | `src/campo.py:18` |
| `NF` | 29 (com `NM_RISCO=1` e `NM_PONTO=1`) | `src/campo.py:33` |
| `NP` | 40 = `NF + S + 1` | `src/campo.py:486` |
| `B` | seres no lote = `P · NC · R` | `src/campo.py:131` |

`DIRS` (`src/campo.py:11-12`), normalizado por linha, índice 8 zerado:

| esc | dx | dy |
|---|---|---|
| 0 | 1 | 0 |
| 1 | 0.70710678 | 0.70710678 |
| 2 | 0 | 1 |
| 3 | −0.70710678 | 0.70710678 |
| 4 | −1 | 0 |
| 5 | −0.70710678 | −0.70710678 |
| 6 | 0 | −1 |
| 7 | 0.70710678 | −0.70710678 |
| 8 | 0 | 0 (ficar) |

**A constante da diagonal é `1/√2` calculada em f32.** O Rust deve usar
`std::f32::consts::FRAC_1_SQRT_2` (0.70710678118654752440 arredondado a f32), não um
literal truncado.

---

## 1. Estado por ser

Tudo escalar por ser, exceto onde marcado. Faixa = o que o código garante por `clamp`.
Valor inicial de `Campo.__init__` (`src/campo.py:154-172`); **no v0 o Rust NÃO gera esses
valores — ele os LÊ do `traco_ref.json`** (§11).

| variável | tipo | faixa | inicial | origem |
|---|---|---|---|---|
| `pos` | f32×2 | `[0, L]²` | `rand(B,2)·L` | `campo.py:154` |
| `casa` | u32 | `[0, K)` | `distrito(pos)` | `campo.py:155` |
| `fuel` | f32 | `[0, 100]` | 85 | `campo.py:156` |
| `agua` | f32 | `[0, 100]` | 85 | `campo.py:156` |
| `fome` | f32 | `(−∞, 100]` | 10 | `campo.py:156` |
| `fad` | f32 | `[0, 100]` | 10 | `campo.py:157` |
| `calor` | f32 | `[25, 120]` | 30 | `campo.py:157` |
| `vida` | f32 | `[0, 100]` | 100 | `campo.py:157` |
| `dinh` | f32 | `[−LIMITE_DIVIDA, ∞)` | `cfg.dinh0` = **20** | `campo.py:158`, `campo.py:39` |
| `res` (reserva) | f32 | `[0, RES_MAX]` | 0 | `campo.py:158` |
| `tpar` (tiques parado) | f32 | `[0, ∞)` | 0 | `campo.py:158` |
| `metab` | f32 | ≥ 1 | 1.0 (v0: `custo_gene=0`) | `campo.py:158` |
| `cons` (consumo L/m, EMA) | f32 | > 0 | `fuel_passo·2` = **0.30** | `campo.py:159` |
| `ent` (entregas) | f32 | ≥ 0 | 0 | `campo.py:160` |
| `rec` (receita) | f32 | ≥ 0 | 0 | `campo.py:160` |
| `avar` (avarias) | f32 | ≥ 0 | 0 | `campo.py:160` |
| `av_fuel` (panes) | f32 | ≥ 0 | 0 | `campo.py:160` |
| `n_posto`,`litros`,`n_oficina`,`n_come`,`n_agua` | f32 | ≥ 0 | 0 | `campo.py:161,171` |
| `dano_soma` | f32 | ≥ 0 | 0 | `campo.py:162` |
| `t_vida` | f32 | `[0, T]` | 0 | `campo.py:162` |
| `px` | f32×`NPX`×2 | `[0, L]²` | `_perto(pos, 12)` | `campo.py:163` |
| `pxd` (destino do pax) | f32×`NPX`×2 | `[0, L]²` | `_destino(px)` | `campo.py:163` |
| `px_ok` (vaga ativa) | bool×`NPX` | — | todas `true` | `campo.py:165` |
| `pd_` (carrega pax) | f32 | −1 ou +1 | −1 | `campo.py:164` |
| `dest` | f32×2 | `[0, L]²` | (0,0) | `campo.py:164` |
| `emb` (local do embarque) | f32×2 | `[0, L]²` | (0,0) | `campo.py:164` |
| `orig_d` (distrito do embarque) | u32 | `[0, K)` | 0 | `campo.py:164` |
| `t_ult` (tiques desde embarque) | f32 | ≥ 0 | 0 | `campo.py:166` |
| `recusa` | bool | — | `false` (nunca muda no v0) | `campo.py:170` |
| `fase` | f32 | `[0, dia)` | `rand(NC)·dia`, **igual para todos os seres do mesmo mapa** | `campo.py:150` |
| `t` | i64 | global, não por ser | 0 | `campo.py:169` |

Não usados no v0 (existem mas ficam em 0): `filhos`, `res_filhos`, `n_vem`, `imp`,
`subs`, `parado_dia`, `bem_soma`.

`pref_mult` (alavancas do prefeito, `campo.py:172`) é **1.0 em todas as 6 colunas** no v0.
Todo termo `pf[:, k]` some.

---

## 2. Mapa

### 2.1 Estruturas

| campo | forma | conteúdo |
|---|---|---|
| `custo` | f32 `[tex, tex]` = `[64, 64]` | textura de custo do terreno; rua = `ruas[0]` = **1.0**, fora = `ruas[1]` = **3.0** |
| `serv[t]` | f32 `[N_t, 2]`, um por tipo | pontos de serviço, ordem `TIPOS` |
| `centros` | f32 `[K, 2]` | centros dos distritos (Voronoi) |
| `campo_dist` | u32 `[GR, GR]` = `[128, 128]` | distrito da célula (pré-computado) |
| `aliq` | f32 `[K]` | alíquota por distrito |
| `pmul` | f32 `[K]` | multiplicador de preço por distrito (base `pmul0`) |
| `alug` | f32 `[K]` | aluguel por distrito |
| `demanda` | f32 `[K]` | demanda de passageiro por distrito |
| `fase_preco` | f32 `[K]` | fase do ciclo de preço por distrito |
| `perfil` | i32 `[K]` | índice do perfil (0..3) |

Geração: `gerar_mapa` (`src/campo.py:73-120`), ramo `distinto=True`.
`K = max(3, round(6·L/200))` (`campo.py:77`); com `L = 200` ⇒ **K = 6**.
`tex = 64` (`campo.py:39`).

Perfis de distrito (`src/campo.py:66-71`), idênticos aos de `cenarios/mundo_vivo_v1.json`:

| perfil | pmul | aliq | alug | dem | dens (posto, comida, agua, descanso, oficina) |
|---|---|---|---|---|---|
| centro | 2.0 | 0.35 | 2.5 | 2.0 | 1.0, 1.5, 1.0, 0.5, 1.0 |
| industrial | 0.6 | 0.10 | 0.8 | 0.7 | 2.5, 0.0, 1.0, 0.0, 2.0 |
| residencial | 1.0 | 0.15 | 1.0 | 1.0 | 0.0, 2.0, 1.5, 2.0, 0.0 |
| periferia | 0.5 | 0.00 | 0.8 | 0.3 | 0.5, 0.5, 0.5, 0.5, 0.0 |

`DENS` base por tipo (`campo.py:14`): posto 1/2500, comida 1/2500, agua 1/2000,
descanso 1/3000, oficina 1/2000 (pontos por m²).

### 2.2 O Rust NÃO gera o mapa no v0

`gerar_mapa` usa `torch.rand`, `torch.randint` e um `conv2d` de suavização
(`campo.py:79-82`) com o `Generator` do torch. **Não existe reimplementação viável do
Philox do torch em WGSL que garanta bit-igualdade.** Portanto:

- **v0: o mapa vem do JSON** (`traco_ref.json` → chave `mapa`), carregado como buffers.
- **v1: geração própria em Rust**, com uma semente própria — o mundo passa a ser
  *estatisticamente* o mesmo, não *numericamente* o mesmo. O portão de identidade §11 só
  vale sobre mapa carregado.

### 2.3 Indexação — duas convenções DIFERENTES, não unifique

| função | grade | fórmula do índice | origem |
|---|---|---|---|
| `custo_em(p)` | `tex = 64` | `ix = round(p.x/L·(tex−1)).clamp(0, tex−1)`, idem `iy`; devolve `custo[iy, ix]` | `campo.py:174-177` |
| `_cel(p)` / `distrito(p)` | `GR = 128` | `ix = floor(p.x/L·GR).clamp(0, GR−1)`, idem `iy`; devolve `campo_dist[iy, ix]` | `campo.py:178-182` |

**Armadilha 1:** `custo_em` usa `(tex−1) = 63` e **arredondamento**, `_cel` usa `GR = 128`
e **truncamento**. Reproduzir as duas separadamente.
**Armadilha 2:** `torch.round` é *round-half-to-even* (banqueiro). Rust `f32::round` é
*round-half-away-from-zero*. Use `(x + 0.5).floor()` só se você provar que o meio-termo
nunca aparece — o correto é implementar round-half-to-even explicitamente (ou usar
`x.round_ties_even()`, estável desde Rust 1.77).
**Armadilha 3:** a ordem dos eixos é `[iy, ix]` (linha = y). Errar isso dá um mundo
transposto que "quase funciona".

`_perto_exata(p)` (`campo.py:209-215`): para cada tipo, na ORDEM de `TIPOS`, distância
euclidiana de `p` a todos os pontos daquele tipo com máscara (`1e9` nos slots vazios),
`argmin`. Devolve `_ptos (B,5,2)` e `_dist (B,5)`. **É varredura exata, não a grade.**
(`cfg.varredura = 'exata'`, `campo.py:44`.)

---

## 3. Ordem exata do tique

Um tique = `um_passo(m, a, Wb)` (`src/campo.py:469-483`). O contador `t` só é incrementado
**dentro** de `passo()`; portanto `obs()` e `serv_need()` de um tique veem `t`, e a física
do mesmo tique vê `t+1`. **Isso não é bug, é a spec.**

```
um_passo:
  1. F, val    = obs()                      # §4  — usa t
  2. sc        = einsum(F, W[0..NF])        # (B,9)
  3. sc       -= mean(sc, dim=1)            # G1 (campo.py:472)
  4. svn, sv   = serv_need()                # §6  — usa t
  5. ss        = svn * W[NF..NF+S] + W[NF+S] # (B,10)
  6. ss[sv <= 0] = -1e9                     # (campo.py:475)
  7. tudo      = concat(sc, ss)             # (B,19)
  8. esc       = argmax(tudo, dim=1)        # empate → PRIMEIRO índice
  9. passo(esc)                             # §3.1 — incrementa t na 1ª linha
```

### 3.1 `passo(esc)` — `src/campo.py:384-467`

| # | linha | operação |
|---|---|---|
| 1 | 385 | `t += 1` |
| 2 | 387-388 | `dia = floor(t / cfg.dia)`; `pmul = pmul0·(1 + amp_preco·sin(2π·(dia/periodo_preco + fase_preco)))` — **`amp_preco = 0.5`, `periodo_preco = 3.0`** (`campo.py:59`); só ativo porque o mapa é `distinto` (`campo.py:149`). É por MAPA, não por ser. |
| 3 | 390 | `vivo = vida > 0`; `livre = (tpar ≤ 0) & vivo`; **depois** `tpar = max(tpar − 1, 0)` |
| 4 | 391 | `nv = noite_()` (com `t` já incrementado); `v = nv ? vel_noite : vel` = `0.7 : 1.0` (`campo.py:38`) |
| 5 | 392 | `mov = livre & (esc < 9) & (esc ≠ 8)` |
| 6 | 393 | `d = DIRS[min(esc, 8)]` |
| 7 | 394 | `cu = custo_em(pos)`; `peso = 1 + 0.15·(pd_ ≥ 0) + 0.002·res` |
| 8 | 396-398 | `pane = mov & (fuel < fuel_passo·cu·peso)`; `mov &= ¬pane` |
| 9 | 399 | `pos = clamp(pos + mov·v·d, 0, L)` |
| 10 | 400 | `marcha = livre & ¬mov` (parado com motor ligado) |
| 11 | 401 | `fuel = max(fuel − fuel_passo·cu·peso·mov − fuel_passo·0.33·marcha, 0)` |
| 12 | 402 | `cons = mov ? cons + (fuel_passo·cu·peso/max(v,1e−3) − cons)·0.05 : cons` |
| 13 | 403 | `calor = clamp(calor + calor_sobe·cu·mov − calor_desce·¬mov, 25, 120)` |
| 14 | 405 | `agua = max(agua − agua_passo·vivo − agua_calor·(calor > 60)·vivo, 0)` (v0: `custo_canais = ('fome',)` ⇒ sem fator `metab`) |
| 15 | 406 | `fome = min(fome + fome_passo·metab·vivo, 100)`; `fad = clamp(fad + fad_passo·mov − 0.1·¬mov, 0, 100)` |
| 16 | 407 | `exausto = livre & (fad ≥ 95)` ⇒ `tpar = 12`, `fad = 40`, `avar += 1` |
| 17 | 408 | `res = max(res·(1 − perda_res), 0)`, `perda_res = 0.02/240` |
| 18 | 413 | `pane` ⇒ `avar += 1`, `av_fuel += 1`, `tpar = 18` |
| 19 | 414-415 | `pane` ⇒ `pos = _ptos[:,0]` (posto mais perto, **calculado no `obs()` deste tique**), `fuel = FUEL_POS_PANE = 15`, `dinh −= GUINCHO = 0` |
| 20 | 416-417 | `kcal = min(res, KCAL_PANE=20)`; `res −= kcal·pane`; `dn = D_PANE·pane + (KCAL_PANE − kcal)·pane` |
| 21 | 419-420 | `qt = livre & (calor > CALOR_MAX=92)` ⇒ `avar += 1`, `tpar = 10`, `calor = 60`; `dn += D_QUENTE·qt + D_RODAR·(mov & (calor > 80))` — **`calor` aqui já é o valor pós-reset**; um ser que superaqueceu não paga `D_RODAR` no mesmo tique |
| 22 | 422 | `sv, pm = serv_ab()` (§6) — **usa `_dist` do `obs()` (posição ANTIGA) mas `distrito(pos)` da posição NOVA**; se houve pane, a incoerência é visível. Reproduzir. |
| 23 | 422-425 | `pode = livre & (esc ≥ 9)`; `k = clamp(esc − 9, 0, 9)`; `usa = onehot(k)·pode·sv·(dinh ≥ cs)`; `dinh −= Σ(usa·cs)` |
| 24 | 428-431 | `litros = 25·usa₀ + 50·usa₁ + 75·usa₂ + 100·usa₃ + 150·usa₄`; `novo = fuel + litros`; `sobra = max(novo − 100, 0)`; `fuel = min(novo, 100)`; `res = min(res + sobra·(1 − PERDA_ARMAZ), RES_MAX)` |
| 25 | 432 | `agua = min(agua + 50·usa₅ + 100·usa₆, 100)` |
| 26 | 433 | `usa₇ > 0` ⇒ `fome = max(fome − REFEICAO, 0)` |
| 27 | 434 | `usa₈ > 0` ⇒ `fad = min(fad, 40)`, `tpar = 12` |
| 28 | 435 | `usa₉ > 0` ⇒ `vida = min(vida + REPARO, 100)`, `calor = 25` |
| 29 | 443-450 | passageiros: embarque (§7) |
| 30 | 451-453 | respawn (§7) — **DESLIGADO no teste de identidade** |
| 31 | 454-457 | entrega e tarifa (§7) |
| 32 | 459 | `meia = ((t + fase) mod dia) < 1`; `dinh −= aluguel·alug[casa]·meia·vivo` |
| 33 | 463 | `dn += fome_mata·clamp((fome − FOME_CRIT)/(100 − FOME_CRIT), 0, 1) + agua_mata·clamp((AGUA_CRIT − agua)/AGUA_CRIT, 0, 1)` |
| 34 | 464 | `dinh = max(dinh, −LIMITE_DIVIDA)`; `dn += 2.0·clamp(−dinh/LIMITE_DIVIDA, 0, 1)²` |
| 35 | 465 | `vida = max(vida − dn·vivo, 0)`; `dano_soma += dn·vivo`; `t_vida += vivo` |

### 3.2 Constantes de `CfgCampo` (`src/campo.py:36-63`) — valores do v0

`traco_referencia.py:13` cria `CfgCampo(L=200., fitness='vida')` e depois só muda
`respawn`, `ponto`, `grava_acoes`, `horizonte`. **Tudo o mais é o default.**

| constante | valor | linha |
|---|---|---|
| `L` | 200.0 | `traco_referencia.py:13` |
| `dia` | 240 tiques | `campo.py:38` |
| `vel` / `vel_noite` | 1.0 / 0.7 | `campo.py:38` |
| `NPX` | 12 | `campo.py:39` |
| `K` | 6 (de `L=200`) | `campo.py:39` |
| `tex` | 64 | `campo.py:39` |
| `raio` (uso de serviço e embarque) | 6.0 | `campo.py:39` |
| `raio_px` (anel de nascimento do pax) | 45.0 | `campo.py:39` |
| `dinh0` | 20.0 | `campo.py:39` |
| `loja_no_posto` | `true` | `campo.py:39` |
| `fuel_passo` | 0.15 | `campo.py:40` |
| `agua_passo` | 0.08 | `campo.py:40` |
| `agua_calor` | 0.12 | `campo.py:40` |
| `fome_passo` | 0.32 | `campo.py:40` |
| `fad_passo` | 0.15 | `campo.py:40` |
| `calor_sobe` / `calor_desce` | 0.15 / 0.6 | `campo.py:41` |
| `CALOR_MAX` | 92.0 | `campo.py:42` |
| `D_QUENTE` / `D_PANE` / `D_RODAR` | 6.0 / 6.0 / 0.15 | `campo.py:42` |
| `fome_mata` / `FOME_CRIT` | 0.15 / 90.0 | `campo.py:43` |
| `agua_mata` / `AGUA_CRIT` | 0.15 / 10.0 | `campo.py:43` |
| `KCAL_PANE` | 20.0 | `campo.py:43` |
| `custo_gene` | 0.0 | `campo.py:44` |
| `margem_risco` | 30.0 | `campo.py:44` |
| `GUINCHO` | 0.0 | `campo.py:44` |
| `FUEL_POS_PANE` | 15.0 | `campo.py:44` |
| `nevoa` | +∞ (mundo onisciente) | `campo.py:44` |
| `k_cego` | 2.0 (inerte com `nevoa=∞`) | `campo.py:44` |
| `respawn` | **1e9 no traço**, 20.0 na bateria | `traco_referencia.py:14`, `campo.py:46` |
| `ponto` | **0.0 no traço**, 0.0 na bateria v1 | `traco_referencia.py:14`, `campo.py:58` |
| `amp_preco` / `periodo_preco` | 0.5 / 3.0 | `campo.py:59` |
| `preco_L` | 0.3 /L | `campo.py:60` |
| `preco_agua` | 0.05 /L | `campo.py:60` |
| `preco_comida` | 2.0 | `campo.py:60` |
| `HOTEL` | 8.0 | `campo.py:60` |
| `preco_oficina` | 10.0 | `campo.py:60` |
| `REPARO` | 25.0 | `campo.py:60` |
| `tarifa_base` / `tarifa_km` | 3.0 / 0.25 | `campo.py:61` |
| `aluguel` | 4.0 | `campo.py:61` |
| `LIMITE_DIVIDA` | 60.0 | `campo.py:61` |
| `PERDA_ARMAZ` | 0.15 | `campo.py:61` |
| `RES_MAX` | 120.0 | `campo.py:61` |
| `perda_res` | 0.02/240 | `campo.py:61` |
| `REFEICAO` | 90.0 | `campo.py:62` |
| `fitness` | `'vida'` | `traco_referencia.py:13` |
| `w_trab` | 1.0 | `campo.py:57` |

`hora() = ((t + fase) mod dia) / dia · 24` (`campo.py:243`).
`noite_() = (hora ≥ 22) | (hora < 6)` (`campo.py:254`) — v0 sem regime.

---

## 4. As colunas de `F` — 10 por opção + 19 de corpo = `NF = 29`

`_obs_lento` (`src/campo.py:301-340`). `F` tem forma `(B, 9, 29)`. As 10 primeiras colunas
variam por opção de movimento; as 19 seguintes são o corpo, **iguais nas 9 opções**.

Pré-cálculo do `obs()`:
- `nv = noite_()` (com `t` do tique, pré-incremento)
- `v = nv ? 0.7 : 1.0`
- `pn[g] = clamp(pos + v·DIRS[g], 0, L)` — posição projetada de cada opção `(B,9,2)`
- `esc_ = 1/vel = 1.0`
- `_ptos, _dist = _perto_exata(pos)` (ordem `TIPOS`)
- `_dist_v = _dist` (porque `nevoa = ∞`)
- `alvo()` (`campo.py:256-259`): `k = argmin‖px − pos‖` sobre **as 12 vagas, SEM máscara
  `px_ok`**; `po = px[k]`; devolve `pd_ ≥ 0 ? dest : po`

> **Quirk que deve ser reproduzido:** `alvo()` ignora `px_ok`. Um ser que já usou todas as
> vagas continua "vendo" um passageiro fantasma no `d_alvo`. É o sentido que dirige o
> movimento e ele mente. Não conserte no v0 — o portão de identidade quebra.

### 4.1 `NOMES_OP` (`campo.py:19`) — colunas 0..9, uma por opção `g`

| # | nome | fórmula | linha |
|---|---|---|---|
| 0 | `d_alvo` | `‖pn[g] − alvo‖ · esc_` | 305 |
| 1 | `d_posto` | `min(‖pn[g] − _ptos[0]‖, nevoa) · esc_` | 322-323 (`j=0`) |
| 2 | `d_comida` | `min(‖pn[g] − _ptos[1]‖, nevoa) · esc_` | 322-323 (`j=1`) |
| 3 | `d_agua` | `min(‖pn[g] − _ptos[2]‖, nevoa) · esc_` | 322-323 (`j=2`) |
| 4 | `d_oficina` | `min(‖pn[g] − _ptos[4]‖, nevoa) · esc_` | 322-323 (`j=4`) |
| 5 | `d_descanso` | `min(‖pn[g] − _ptos[3]‖, nevoa) · esc_` | 322-323 (`j=3`) |
| 6 | `custo_frente` | `custo_em(pn[g])` | 324 |
| 7 | `preco_frente` | `pmul[distrito(pn[g])]` | 325 |
| 8 | `aliq_frente` | `aliq[distrito(pn[g])]` | 325 |
| 9 | `casa_frente` | `distrito(pn[g]) == casa ? 1 : 0` | 325 |

> **A ordem do laço é `for j in (0, 1, 2, 4, 3)`** (`campo.py:322`): oficina (índice 4 de
> `TIPOS`) vem ANTES de descanso (índice 3). Ler `_ptos` na ordem de `TIPOS` e escrever em
> `F` na ordem de `NOMES_OP` são coisas diferentes. Esta permutação já custou um bug no
> lado Python (`s.PERM_F = [0,1,2,4,3]`, `campo.py:143`).

### 4.2 `NOMES_CORPO` (`campo.py:20,22,24`) — colunas 10..28

| # | nome | fórmula | linha |
|---|---|---|---|
| 10 | `e_fuel` | `fuel/100` | 330 |
| 11 | `e_agua` | `agua/100` | 330 |
| 12 | `e_fome` | `fome/100` | 330 |
| 13 | `e_fadiga` | `fad/100` | 330 |
| 14 | `e_calor` | `calor/120` | 330 |
| 15 | `e_vida` | `vida/100` | 330 |
| 16 | `e_dinheiro` | `clamp(dinh/150, −1, 1)` | 330 |
| 17 | `e_reserva` | `res/RES_MAX` | 330 |
| 18 | `e_tem_pax` | `pd_ ≥ 0 ? 1 : 0` | 331 |
| 19 | `h_sin` | `sin(hora()·2π/24)` | 328, 331 |
| 20 | `h_cos` | `cos(hora()·2π/24)` | 328, 331 |
| 21 | `e_noite` | `nv ? 1 : 0` | 331 |
| 22 | `custo_aqui` | `custo_em(pos)` | 331 |
| 23 | `bias` | `1.0` | 331 |
| 24 | `e_consumo` | `cons/(fuel_passo·3)` = `cons/0.45` | 332 |
| 25 | `e_autonomia` | `clamp((fuel/max(cons,1e−3) − _dist_v[0])/100, −2, 4)` | 329, 332 |
| 26 | `e_risco` | `clamp((_dist_v[0] + margem_risco − fuel/max(cons,1e−3))/100, 0, 3)` | 333 |
| 27 | `e_demanda` | `demanda[distrito(pos)]/2` | 334 |
| 28 | `e_espera` | `min(t_ult/100, 2)` | 334 |

`e_risco` e `e_demanda`/`e_espera` só existem com `NM_RISCO=1` e `NM_PONTO=1`
(`campo.py:21-24`). **Elas mudam `NF` e portanto `NP`** — o Rust lê `nomes_corpo` do JSON
e recusa rodar se o comprimento não bater com o genoma.

### 4.3 `NOMES_F` — os 40 nomes do genoma (`campo.py:34`)

```
0..9    NOMES_OP           (pesos de movimento)
10..28  NOMES_CORPO        (pesos de movimento, mas iguais nas 9 opções → ver nota)
29..38  sv_posto25, sv_posto50, sv_posto75, sv_posto100, sv_posto150,
        sv_agua50, sv_agua100, sv_comida, sv_descanso, sv_oficina
39      sv_bias
```

> **Achado estrutural E58 (`campo.py:1094` docstring de `Bilinear`)**: como os sentidos do
> corpo são iguais nas 9 opções e o passo 3 do tique subtrai a média, **nenhum peso das
> colunas 10..28 muda a direção**. Eles só entram na decisão pelo `sv_bias`/serviços. Isto
> não é uma otimização a fazer — é a explicação de por que o ser linear "nunca procura o
> posto". Manter a conta como está (o Rust pode omitir o termo? **não**: a média é
> subtraída depois, então o termo se cancela exatamente em f32 só se calculado do mesmo
> jeito; calcular e subtrair é mais barato de provar do que argumentar).

---

## 5. Decisão

```
sc[g] = Σ_f F[g,f] · W[f]           f = 0..28        (campo.py:471)
sc[g] = sc[g] − (1/9)·Σ_h sc[h]                      (campo.py:472)  ← G1
ss[a] = svn[a] · W[29+a] + W[39]    a = 0..9         (campo.py:473)
ss[a] = −1e9   onde sv[a] ≤ 0                        (campo.py:475)
tudo  = [sc(9) ; ss(10)]                             (campo.py:476)
esc   = argmax(tudo)                                 (campo.py:481)
```

`esc ∈ [0,8]` → movimento (8 = ficar). `esc ∈ [9,18]` → serviço `esc − 9`.

**Desempate: primeiro índice.** O Rust deve usar `>` estrito na varredura crescente
(`if v > melhor { melhor = v; idx = i }`), começando em `idx = 0`.
`torch.argmax` na GPU **não garante** o primeiro índice em empate exato; §11 trata isso
como fonte de divergência conhecida e mede a margem.

**Ordem de redução do produto interno.** `torch.einsum` de 29 termos usa uma ordem de
redução própria do ROCm. O Rust deve somar sequencialmente `f = 0..28` em f32 e a §11
mede se a diferença resultante chega a mudar o `argmax`. **Não** acumular em f64 no v0:
mudaria a distribuição de empates e mascararia o problema real (v1 pode revisitar).

---

## 6. Ações de serviço

`ACOES` (`campo.py:16-17`), índice de ação = `esc − 9`:

| a | tipo | q | custo em dinheiro (`custos`, `campo.py:367-376`) | efeito |
|---|---|---|---|---|
| 0 | posto | 25 L | `0.3 · 25 · pm` | `fuel += 25` (transborda p/ `res`) |
| 1 | posto | 50 L | `0.3 · 50 · pm` | idem |
| 2 | posto | 75 L | `0.3 · 75 · pm` | idem |
| 3 | posto | 100 L | `0.3 · 100 · pm` | idem |
| 4 | posto | 150 L | `0.3 · 150 · pm` | idem |
| 5 | agua | 50 L | `0.05 · 50 · pm` | `agua = min(agua + 50, 100)` |
| 6 | agua | 100 L | `0.05 · 100 · pm` | `agua = min(agua + 100, 100)` |
| 7 | comida | — | `2.0 · pm` | `fome = max(fome − 90, 0)` |
| 8 | descanso | — | `(1 − casa?) · 8.0 · pm` | `fad = min(fad, 40)`, `tpar = 12` |
| 9 | oficina | — | `10.0 · pm` | `vida = min(vida + 25, 100)`, `calor = 25` |

`pm = pmul[distrito(pos)]` (`campo.py:360`), com `pmul` do **dia corrente** (§3.1 #2).
`casa?` em (8) é `distrito(pos) == casa` (`campo.py:368`): dormir em casa é de graça.

### 6.1 Disponibilidade — `serv_ab` (`campo.py:356-366`)

```
perto[t] = _dist[t] ≤ raio(=6)                para t em TIPOS      # _dist do obs()
se loja_no_posto (true):
    perto[comida] |= perto[posto]                                  # PRIMEIRO
    perto[agua]   |= perto[posto] | perto[comida]                  # DEPOIS (já com o |= acima)
sv[a] = perto[tipo(a)] ; se tipo(a) == posto: sv[a] &= ¬noite_()
```

> A ordem das duas linhas importa: `agua` herda a `comida` **já ampliada**. O resultado
> líquido é `agua_ok = agua ∨ posto ∨ comida_original`, mas escreva na mesma ordem para
> não errar quando `loja_no_posto` mudar.
> **Posto fecha à noite** (`campo.py:364`) — `nv` aqui é o do tique corrente do chamador
> (`t` em `um_passo`, `t+1` em `passo`).

### 6.2 Necessidade — `serv_need` (`campo.py:377-382`)

```
cs   = custos(pm)                                    # (B,10)
paga = dinh ≥ cs                                     # elemento a elemento
cabe      = 100 − fuel
sobra_res = max(RES_MAX − res, 0)

nec[a] para a=0..4 (posto, q ∈ {25,50,75,100,150}):
    min(q, cabe)/100  +  max(min(q − cabe, sobra_res), 0)/100 · 0.5
nec[5] = min(50,  100 − agua)/100
nec[6] = min(100, 100 − agua)/100
nec[7] = fome/100
nec[8] = fad/100
nec[9] = 1 − vida/100

svn = sv · nec · paga        # entra na nota
sv_ = sv · paga              # máscara: ss[a] = −1e9 onde sv_[a] ≤ 0
```

---

## 7. Passageiros

`NPX = 12` vagas **privadas por ser** (não há competição entre seres). Cada vaga tem
posição `px[k]`, destino `pxd[k]` e um bit `px_ok[k]`.

### 7.1 Nascimento (só na inicialização, e no JSON no v0)

- `_perto(pos, n)` (`campo.py:222-224`): `n` pontos num anel de raio `[8, raio_px=45]`
  em volta de `pos`, ângulo uniforme, `clamp(0, L)`.
- `_destino(po)` (`campo.py:230-235`): ângulo uniforme, raio `L·(0.05 + 0.45·u²)`,
  `clamp(0, L)` — concentra perto, cauda longa.

Ambos consomem RNG do torch. **v0 lê do JSON, não gera.**

### 7.2 Embarque — `campo.py:443-450`

```
dpx[k] = ‖px[k] − pos‖, com 1e9 onde ¬px_ok[k]
kx     = argmin(dpx)
pega   = livre & (pd_ < 0) & (dpx[kx] ≤ raio=6) & ¬recusa & ¬pode
pega ⇒ dest = pxd[kx] ; emb = pos ; orig_d = distrito(pos) ; pd_ = +1
       px[kx], pxd[kx] ← novo sorteio (_perto/_destino)      ← ver nota
       px_ok[kx] = false
t_ult  = pega ? 0 : t_ult + 1
```

> **A chave do teste de identidade.** As linhas 447-448 sorteiam um passageiro novo **todo
> tique** (mesmo quando `pega` é falso — o valor é descartado), e a linha 449 desativa a
> vaga usada. Como no traço `respawn = 1e9`, a vaga **nunca** volta a ficar ativa, e a
> posição sorteada **nunca é lida de novo** (`dpx` a mascara com `1e9`, e `alvo()`… veja o
> quirk do §4). Logo:
>
> **o Rust NÃO precisa reproduzir o RNG do torch para o teste de identidade** — basta
> marcar `px_ok[kx] = false` e deixar `px[kx]`/`pxd[kx]` como estão.
>
> **Exceção medida:** `alvo()` (§4) lê `px` **sem** a máscara `px_ok`. Portanto o valor
> sorteado É lido, por `d_alvo`. **Consequência dura: o `d_alvo` do Python depende do RNG
> a partir do primeiro embarque, e o Rust não pode reproduzi-lo.**
>
> **Correção obrigatória no gerador do traço (tarefa T0):** gravar, por tique, o vetor
> `alvo (B,2)` — ou, melhor, gravar `px`/`pxd` completos a cada tique em que houver
> embarque. Sem isso o portão de identidade morre no primeiro embarque (tipicamente < 50
> tiques). Alternativa mais barata e preferida: gravar `alvo` por tique (`T·B·2` f32 =
> 2400·16·2 = 76 800 floats ≈ 600 KB) e o Rust **lê** `alvo` do traço durante o portão,
> comparando o resto. Isso isola exatamente o que o RNG contamina.

### 7.3 Respawn — `campo.py:451-453` (**desligado no teste de identidade**)

```
dem_v = demanda[distrito(pos)]              # pax_cidade = false
volta = rand(B, NPX) < dem_v / (respawn · pref_mult[5]=1)
px_ok |= volta
```

Na bateria, `respawn = 20`. No traço, `respawn = 1e9` ⇒ probabilidade ~2e−9 por vaga por
tique; em 2400·16·12 = 460 800 sorteios a chance de UM hit é ≈ 0.1 %. **Declarado como
risco residual**: se o traço tiver um respawn espúrio, o Rust diverge e o harness deve
apontar o tique exato — regerar o traço resolve.

### 7.4 Entrega e tarifa — `campo.py:454-457`

```
cheg   = livre & (pd_ ≥ 0) & (‖pos − dest‖ ≤ raio=6)
aliq_  = clamp(aliq[orig_d] · 1, 0, 0.6)
dist   = ‖dest − emb‖
bruta  = (tarifa_base=3 + tarifa_km=0.25 · dist) · pmul[orig_d] · 1
tarifa = bruta · (1 − aliq_)
cheg ⇒ dinh += tarifa ; rec += tarifa ; ent += 1 ; pd_ = −1
```

`pmul[orig_d]` é o do **dia corrente**, não o do dia do embarque.
`pd_` pode ser setado por `pega` e zerado por `cheg` **no mesmo tique** (embarque e
entrega no mesmo raio de 6 m): a ordem das linhas 446 → 454 garante isso.

### 7.5 Ponto de táxi — `campo.py:437-442` (`cfg.ponto = 0` no v0: bloco inteiro pulado)

Só entra na bateria quando `ponto > 0`. **Não implementar no v0** — consome RNG e quebra
o determinismo do portão.

---

## 8. Morte, `t_vida`, réguas

Dano por tique (`dn`), acumulado nas linhas 417, 420, 463, 464:

| fonte | fórmula | linha |
|---|---|---|
| pane | `D_PANE=6` + `(KCAL_PANE=20 − kcal)` | 417 |
| superaquecimento | `D_QUENTE=6` quando `calor > 92` | 420 |
| rodar quente | `D_RODAR=0.15` quando `mov & calor > 80` | 420 |
| fome | `0.15 · clamp((fome − 90)/10, 0, 1)` | 463 |
| sede | `0.15 · clamp((10 − agua)/10, 0, 1)` | 463 |
| dívida | `2.0 · clamp(−dinh/60, 0, 1)²` | 464 |

`vida = max(vida − dn·vivo, 0)`; morte quando `vida ≤ 0`. Um morto tem `vivo = false`,
`livre = false`, e portanto congela em tudo — mas continua ocupando o lote.
`t_vida += vivo` a cada tique (`campo.py:465`): é o número de tiques vividos.

Régua `vida` (`_fit`, `campo.py:590-591`):

```
fit = t_vida/240 + w_trab · rec/300          # w_trab = 1.0
```

Sem pena de morte, sem teto. Todo mundo morre; a pergunta é **quando** e **quanto fez**.
As outras réguas (`sobrevive`, `riqueza`, `bemestar`, `padrao`, `filhos`,
`campo.py:586-601`) **não entram no v0**.

Horizonte (`campo.py:57`, `rodar` linha 555): `aberto` = roda até `T_max` ou até a fração
de vivos cair a `corte_vivos` (checado **1× por dia simulado**, `t % 240 == 239`).
No traço, `horizonte = 'fixo'` e `T = 2400`.

---

## 9. Juiz

`medidas` (`campo.py:610-640`): **128 cópias do MESMO genoma**, semente do mundo
**7777**, `R = 1`, `T = T_aval`, `jardim_comum = False`. Com `NC` mapas de teste,
`B = 128 · NC`. Os mapas de teste são `gerar_mapa(1000 + s)` para `s ∈ {0,1,2}`
(`e43_campo.py`, `--teste-seed 1000`), **diferentes** dos 4 mapas de treino
(`gerar_mapa(0..3)`).

Medidas exportadas relevantes ao v0: `fit`, `mortos`, `ent`, `panes` (`av_fuel`),
`fome_fim`, `agua_fim`, `dinh`, `res`, `litros_por_abast`, `n_posto`, `n_come`,
`oficina`, `rec`, e o bloco `t_vida = {media, mediana, p10, p90, frac_teto}`.

> **`frac_teto > 0.05` invalida o resultado** (`campo.py:56-57`, `e43_campo.py`): significa
> que o horizonte amarrou e o número mede o teto, não o ser.

---

## 10. Evolução (GA)

`evoluir_sementes` (`src/lab.py:1706-1772`), chamada via `campo.evoluir` (`campo.py:606`).

| parâmetro | valor do protocolo v0 | origem |
|---|---|---|
| `P` (pop. por semente) | 128 | `cenarios/mundoA_seres.json` (`protocolo.P`) |
| `G` (gerações) | 30 | idem |
| `paciencia` | 15 | idem |
| `R` (réplicas por mapa) | 4 | idem |
| `seeds` | `[0,1,2,3,4]` | idem |
| `sigma_mut` | **0.1** | idem (pred 161: σ .3 era grande demais, `PREDICOES.md`) |
| `elite` | 0.15 | `lab.py:1707` |
| `sigma0` / `sigma_espinha` | 0.2 / 0.05 | `lab.py:1707` |
| `crn` | `rotativo` | `lab.py:1736` |
| `campeao` | `ultimo` | `lab.py:1770` |
| `T_evo` = `T_aval` | 7200 (horizonte aberto, `T_max`) | `mundo_vivo_v1.json` |

Laço, por geração `it`:

1. `f = avaliar(W, mapas, T, seed = 777000 + 13·it, R)` → `(S, P)`
   `avaliar` (`campo.py:603-605`) roda `B = P·NC·R` seres e faz
   `fit.view(P, NC·R).mean(1)` — a aptidão de um genoma é a **média** sobre `NC·R` mundos.
   Layout do lote: `cidx = arange(NC).repeat_interleave(R).repeat(P)`,
   `gidx = arange(P).repeat_interleave(NC·R)` (`campo.py:132-133`) ⇒
   **índice `b = p·(NC·R) + c·R + r`** (genoma na dimensão externa).
2. ordena `f[si]` decrescente; `ne = max(2, ⌊P·0.15⌋)` = 19 para P=128
3. a elite `Wb[:ne]` passa **intacta**
4. filhos: `idx ~ U{0..ne−1}` (`P − ne` sorteios), `fil = clamp(Wb[idx] + N(0, σ_mut), −5, +5)`
5. `Wn = concat(elite, filhos)`
6. parada por janela (`lab.py:1759-1763`), a partir de `it ≥ paciencia`:
   `agora = mean_s max(hist_s[−pac:])`, `antes = mean_s max(hist_s[:−pac])`;
   para se `agora ≤ antes + 0.01·|antes| + 1e−6`
7. campeão = `W[si][0]` da última geração

**Inicialização**: sem `W0`, `W ~ N(0, 0.8²)` de forma `(P, NP)` com um `Generator` por
semente (`lab.py:1722`). Com `W0` (semeadura do campeão): espinha copiada + `N(0, σ_espinha)`,
genes novos `N(0, σ0)` (`lab.py:1724-1729`).

> O RNG do GA (`torch.randn`/`randint` com `Generator` por semente) **não** precisa ser
> bit-igual: a evolução é uma medida estatística, não um portão de identidade. O Rust usa
> um PRNG próprio (ChaCha8 / PCG) semeado da mesma forma. O que precisa bater é a
> **distribuição do resultado**, testada em §11.3.

---

## 11. Teste de identidade

### 11.0 Pré-requisito: gerar o traço (não existe ainda)

`ls /media/llm-data/universe-runs/neuromod-lab-taxi/e81/` → **diretório inexistente em
2026-09-10 11:00.** O `traco_ref.json` **ainda não foi produzido**. Comando (a rodar
quando a GPU estiver livre — a fila `nmd` está ocupada):

```bash
cd /home/leonardo/projects/LLM/neuromod-lab/src
NM_RISCO=1 NM_PONTO=1 NM_COMPILE=0 \
  /home/leonardo/projects/LLM/.venv-rocm/bin/python traco_referencia.py \
  --B 16 --T 2400 --seed-mapa 1000 \
  --out /media/llm-data/universe-runs/neuromod-lab-taxi/e81
```

> **`traco_referencia.py` não fixa `NM_RISCO`/`NM_PONTO` no ambiente**
> (`traco_referencia.py:7-8` só fixa `NM_COMPILE=0`). Sem as duas flags o traço sai com
> `NF = 26` e o Rust construído contra `NF = 29` recusa o arquivo. As flags DEVEM estar no
> comando; o JSON grava `nomes_f`, então o Rust valida em vez de supor.

### 11.1 Emendas obrigatórias ao gerador (tarefa T0, ~15 linhas)

Sem elas o portão não fecha:

| # | o quê | por quê |
|---|---|---|
| a | gravar `alvo (T,B,2)` por tique | `alvo()` lê `px` sem a máscara `px_ok` (§7.2) — depende do RNG do torch, irreproduzível em Rust |
| b | gravar `F (B,9,NF)`, `sc`, `svn`, `sv`, `tudo` **no tique 0** | é o único teste que separa "sentidos errados" de "física errada"; custa 16·9·29 + 16·(9+10+10+19) ≈ 5 000 floats |
| c | gravar `_ptos (B,5,2)` e `_dist (B,5)` no tique 0 | valida `_perto_exata` e a indexação do mapa isoladamente |
| d | gravar `margem (T,B)` = `max(tudo) − segundo_maior(tudo)` | classifica cada divergência em "empate numérico" vs "bug" (§11.2) |
| e | gravar `esc_livre (T,B)` = quantas opções estavam desmascaradas | diagnóstico de máscara de serviço |
| f | fixar `os.environ['NM_RISCO']='1'` e `NM_PONTO='1'` no topo do arquivo, antes do `import campo` | tirar a dependência de shell |

### 11.2 Portões (mapa carregado, `respawn = 1e9`, `ponto = 0`, `B = 16`)

| portão | horizonte | critério de aceite | o que falha nele |
|---|---|---|---|
| **P0 — sentidos** | tique 0 | `max\|ΔF\| ≤ 1e−4` em todas as `16·9·29` entradas; `max\|Δ_dist\| ≤ 1e−4`; `Δ_ptos` idênticos | indexação do mapa, ordem `(0,1,2,4,3)`, eixos `[iy,ix]`, normalização de `DIRS` |
| **P1 — nota** | tique 0 | `max\|Δsc\| ≤ 1e−3`, `max\|Δsvn\| ≤ 1e−5`, `Δsv` idêntico (bool), `esc` idêntico em 16/16 | ordem de redução do produto interno, centragem G1, máscara `−1e9` |
| **P2 — dia 1 (duro)** | 240 tiques | **ações idênticas em 16/16 × 240 = 3 840 pares (100 %)**; `\|Δpos\| ≤ 1e−4` m por componente; `\|Δfuel\|, \|Δagua\|, \|Δfome\|, \|Δcalor\|, \|Δfad\|, \|Δres\|, \|Δvida\| ≤ 1e−3`; `\|Δdinh\| ≤ 1e−3`; `pd_` idêntico | ordem das operações do `passo()`, pane, serviços, aluguel de meia-noite (tique 240) |
| **P3 — vida inteira (estatístico)** | 2400 tiques | ações iguais ≥ **95 %** dos pares; primeira divergência **mediana ≥ 600** tiques; **toda** divergência com `margem > 1e−2` conta como FALHA (não é empate); ao final `\|Δt_vida\| ≤ 2` tiques e `\|Δrec\| ≤ 1 %` em ≥ 14/16 seres | caos legítimo (argmax em empate) vs bug real |

**Justificativa das tolerâncias.** `pos` é `pos + v·d` com `d` unitário: em f32 o erro é
~1 ULP a 200 m ≈ 1.2e−5 por tique, e o passeio aleatório sobre 240 tiques dá
√240·1.2e−5 ≈ 1.9e−4 no pior caso — a folga de 1e−4 por componente presume que a **ordem
das operações é a mesma** (é o requisito, não a esperança). Se P2 falhar por margem
estreita, o diagnóstico correto é comparar `F` (P0) tique a tique, não afrouxar a
tolerância. `sc` é uma soma de 29 termos de módulo até ~200·5 = 1000: erro relativo f32
~6e−8 · √29 ≈ 3e−7 ⇒ ~3e−4 absoluto; daí `1e−3` em P1.

**Regra de classificação de divergência (P3).** Para cada tique em que `esc_rust ≠
esc_py`, ler `margem[t,b]` do traço:

| margem | veredito |
|---|---|
| `< 1e−3` | empate numérico — **aceitável**, conta na cota dos 5 % |
| `1e−3 .. 1e−2` | zona cinzenta — reportar, não falhar; se > 1 % dos pares, investigar |
| `> 1e−2` | **BUG** — falha o portão e aponta o tique/ser/coluna |

O harness deve imprimir, na falha, o `t`, o `b`, `esc_py`, `esc_rust`, `tudo` dos dois
lados e o `argmax` das diferenças por coluna de `F`. Sem isso o portão diz "falhou" e não
diz onde.

### 11.3 Teste estatístico com passageiros LIGADOS

Aqui o RNG divergiu de propósito (`respawn = 20`, `_perto`/`_destino` sorteando de
verdade): não há trajetória a comparar, só **distribuição**.

Protocolo:
1. Python: `medidas(Linear, W_campeao, [mapa_1000], cfg_bateria, T=7200, seed=7777,
   R=1, copias=128)` — as 128 cópias já dão a amostra.
2. Rust: 128 seres no **mesmo mapa carregado**, mesmo genoma, PRNG próprio semeado 7777,
   `respawn = 20`, `ponto = 0`, `horizonte = aberto`, `T_max = 7200`.
3. Comparar, para `t_vida/240` e `rec`:

| estatística | critério |
|---|---|
| média | a média do Rust cai dentro do IC 95 % da média do Python (`x̄ ± 1.96·s/√128`) |
| desvio-padrão | razão `s_rust / s_py ∈ [0.8, 1.25]` |
| distribuição | Kolmogorov–Smirnov de duas amostras, `p > 0.01` (n=128 vs 128, D crítico ≈ 0.20) |
| `mortos` | fração de mortos dentro de ±5 pp |
| `panes` (`av_fuel`) | média dentro de ±15 % |

Repetir com **3 mapas** (`gerar_mapa(1000..1002)` exportados no JSON) para não julgar por
um mapa sortudo. **Falha em 2 de 3 mapas = falha.**

> **Nota honesta sobre poder do teste**: com n=128 e `σ(t_vida) ≈ 1.4 d` sobre média
> ≈ 4–5 d (`PREDICOES.md`, entrada 160), o IC 95 % da média é ±0.24 d ≈ ±5 %. O teste
> detecta um viés de 5 %; não detecta 2 %. Se um viés de 2 % importar, o portão certo é o
> P2/P3 (determinístico), não este.

---

## 12. O que fica de fora do v0 — e por quê

| deixado de fora | motivo | onde entra |
|---|---|---|
| retina (`NM_RETINA`, `campo.py:341-355`) | 8 raios × 15 amostras × 16 células = o trecho mais caro; muda `NF` | v2 |
| regime/estações (`NM_REGIME`, `campo.py:244-254`) | muda `NF`, e `docs/70` §3.1 mostra que o período de 5 d > vida de 4.3 d ⇒ inaprendível | v2, com período redimensionado |
| reprodução (`campo.py:409-411`) | muda o tamanho do lote em tempo de execução | v2 |
| prefeito (`campo.py:236-242, 642-651`) | segundo agente; `pref_mult` ≠ 1 | v2 |
| ponto de táxi (`cfg.ponto`) | consome RNG por tique ⇒ mata o portão | v1 (depois do portão fechar) |
| jardim comum (`cfg.jardim_comum`) | sorteio por bloco; só afeta a evolução | v1 |
| temperatura de decisão (`cfg.temp_decisao`) | gumbel por tique ⇒ RNG | v2 |
| custo de gene / ativação (`custo_gene`, `custo_modo`) | `Linear` tem `dof = 0`: é identidade | v2 (com cérebros não-lineares) |
| cérebros não-lineares (`Reflexo`, `Produto`, `Modos`, `Cerebro`, `SerCompleto`) | o portão precisa de UM cérebro; o `Linear` é a espinha | v1/v2, um por vez, cada um com portão "genes 0 ⇒ idêntico ao Linear" |
| geração própria do mapa | RNG do torch (`conv2d` de suavização inclusive) | v1, com portão estatístico e não de identidade |
| `varredura = 'grade'` (`campo.py:187-208`) | aproximação com erro 0.37 m — é a otimização do `docs/70` §2.2, não a spec | v1, com portão de tolerância próprio |

---

## 13. Checklist de armadilhas (a ler antes de escrever a primeira linha de Rust)

1. `obs()` vê `t`; `passo()` vê `t+1`. Duas chamadas de `noite_()` por tique com valores
   possivelmente diferentes.
2. `custo_em` usa `tex−1 = 63` + round-half-to-even; `_cel` usa `GR = 128` + truncamento.
3. Ordem `(0, 1, 2, 4, 3)` no laço de serviços do `obs()`.
4. Eixos `[iy, ix]` em todas as texturas.
5. `alvo()` ignora `px_ok` — passageiro fantasma (§7.2, e é o que quebra o portão sem a
   emenda T0-a).
6. `serv_ab()` mistura `_dist` da posição antiga com `distrito(pos)` da nova.
7. `D_RODAR` usa o `calor` **depois** do reset por superaquecimento.
8. `tpar` é decrementado **antes** de ser sobrescrito por pane/exausto/descanso.
9. `res −= kcal·pane` com `kcal = min(res, 20)` calculado para todos.
10. `pega` e `cheg` podem ocorrer no mesmo tique.
11. `esc == 8` ("ficar") **não** é movimento, mas **é** `marcha` (queima 1/3 de gasolina).
12. Empate no `argmax` → primeiro índice; `torch` não garante isso na GPU.
13. `fase` é por MAPA, não por ser (`campo.py:150`).
14. `pmul` do dia é aplicado no `passo()` **após** o `obs()` do mesmo tique — no tique 0 o
    `obs()` usa `pmul0` puro.
