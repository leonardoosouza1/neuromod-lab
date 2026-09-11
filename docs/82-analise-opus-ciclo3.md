# 82 — Opus analista, ciclo 3 (10/09, 19:00): A × B × C pareado, o eixo P medido, e o olho que ninguém dimensionou

Tudo abaixo é pareado por semente (n = 5, sementes 0–4 idênticas nos quatro arquivos, conferido) sobre
`fit_por_semente`. `fit = t_vida/240 + rec/300` (`campo.py:608`, `w_trab` 1.0 nos três mundos); p exploratórios.
Régua do protocolo (o próprio `o3a` imprime): **DP da diferença pareada 0.468 → com n = 5 só se enxerga
efeito ≥ 0.78** — vale para TODA comparação mundo × mundo desta página.

**Os seis números que mudam a leitura de hoje:**
1. A lacuna do Mundo C **não é a conta**: a lei de custo ajustada em A × B prevê 1.11 d para o metab do C; o
   medido é 2.32 d. **52 % da lacuna do C não vem de custo nenhum.**
2. O que o dimensionamento fez sem ninguém contar: **`retina/L` foi de 0.30 (A) para 0.65 (C)** e o "cego"
   (`k_cego·R_dia` = 120 m) de 0.60·L para **1.30·L, maior que o mapa**. Encolher a cidade sem encolher o olho
   tornou o mundo **2.2× mais observável**: o Mundo C não deu repetição às peças, tirou delas o motivo.
3. O G120 **terminou** (18:40, 2052 s) e a lacuna **não fechou**: linear − melhor cérebro +0.756 [+0.28,+1.23]
   contra +0.750 [+0.26,+1.24] em G30. O que cresceu foi o `dof`: 194.6 → **363.8** (+87 %) e o metab
   1.744 → 2.053, com fit −0.248. **Mais gerações compraram genes, não aptidão.**
4. O eixo P fechou no kernel (h1c, 18:46–18:50, 74–125 s/célula): **+0.085 [−0.053,+0.223] por dobro de P**;
   h2c: G240 − G60 = **−0.109 [−1.02,+0.80]**. Nem P nem G pagam nesta faixa.
5. `sem córtex` ganha do COMPLETO **pagando mais aluguel** (dof 202.6 vs 194.8, metab 1.651 vs 1.618), e o
   `cor_dmax` (.39–.43 em todos os braços dos dois mundos) é a estatística de ordem da deriva
   (`0.5·tanh(0.5·2.55) = .427`): **a autoridade do córtex não é selecionada, é o máximo de um passeio.**
6. **`g0a` nunca rodou** (`exit=2 em 0 s`, `unrecognized arguments: --out`) e a fila seguiu: o portão que o
   Fable pôs como condição para commitar o código do Astra é verde falso.

---

## 1. A × B × C pareado — e o que o `sem córtex` diz sobre o córtex

### 1.1 A lacuna, por mundo (pareado por semente, IC95, n = 5)

| lacuna linear − … | Mundo A | Mundo B | Mundo C | A em G120 |
|---|---|---|---|---|
| COMPLETO | +0.861 [+0.32,+1.40] p .012 (5/5) | +0.501 [−0.09,+1.09] p .077 (4/5) | +2.319 [+1.49,+3.14] p .0015 (5/5) | +1.050 [+0.78,+1.32] p .0004 (5/5) |
| melhor cérebro | +0.750 [+0.26,+1.24] p .014 | +0.311 [−0.16,+0.78] p .137 | +1.422 [+0.87,+1.98] p .002 | +0.756 [+0.28,+1.23] p .012 |
| % da espinha (COMPLETO) | 16.9 % | 9.7 % | **30.8 %** | 21.3 % |

Diferença de lacuna entre mundos, pareada: **A − B = +0.360 [−0.24,+0.95] p .17 (3/5)** no COMPLETO e
**+0.438 [+0.10,+0.78] p .023 (4/5)** no melhor cérebro; **B − C = −1.818 [−2.81,−0.83] p .007 (0/5)**;
**A − C = −1.458 [−2.73,−0.18] p .034 (0/5)**. Ou seja: a conta justa fecha um pedaço da lacuna que só é
significativo no eixo "melhor cérebro", e o dimensionamento abre **4× mais** do que a conta fechou.

### 1.2 A lacuna é TEMPO DE VIDA, não renda — e o cérebro trabalha MAIS

| | A | B | C | A-G120 |
|---|---|---|---|---|
| lacuna vinda de dias | +0.811 (94 %) | +0.468 (93 %) | +2.098 (90 %) | +0.982 (94 %) |
| lacuna vinda de renda | +0.050 (6 %) | +0.033 (7 %) | +0.221 (10 %) | +0.068 (6 %) |
| entregas/dia linear × COMPLETO | 2.84 × **3.01** | 2.84 × **2.89** | 6.22 × **6.54** | 2.57 × **2.61** |

Em todos os mundos o cérebro **entrega mais por dia que a espinha** e mesmo assim perde: morre antes. O
déficit é 100 % sobrevivência, o que põe o `metab` (multiplica `fome_passo`, `campo.py:422`) no centro.

### 1.3 Conta (B) e dimensionamento (C) são leis INDEPENDENTES — a conta de dois termos

A e B são o mesmo mundo com duas contas: dão dois pontos e uma lei do custo.
`lacuna_relativa = 0.191·(metab − 1) + 0.031`. Aplicada ao Mundo C (metab 1.618 do COMPLETO):

* previsto **rel 0.149 → lacuna 1.11 d**;
* medido **rel 0.310 → lacuna 2.32 d**;
* **excesso +1.21 d = 52 % da lacuna do C que nenhum custo explica.**

E o sinal do custo vai ao contrário do mecanismo do CS (docs/79 §3): o metab do COMPLETO no C é **1.618**,
**menor** que os 1.744 do A. A alegação "no C o ser é 2.2× mais ativo, logo paga mais" **não aparece no
número que a conta produz**. O que aparece é um preço por unidade de metab 2× maior no C
(−0.508 de razão de vida por unidade, contra −0.238 no A e −0.279 no B): o mundo C não cobra mais, ele
**pune mais qualquer cobrança** — e ainda sobra metade da lacuna fora disso.

### 1.4 O córtex: |δ| ≤ .5 e o aluguel que continua sendo pago

`completo.py:52,88`: `w_ef = w·(1 + δ_{d,f})`, `δ = cortex_amp·tanh(gene)`, em quatro colunas da espinha
(`IDX_CORTEX = [0,1,6,7]` = d_alvo, d_posto, custo_frente, preco_frente), por distrito. Com |δ| ≤ .5 o peso
efetivo fica em [0.5w, 1.5w]: **perturba, nunca inverte**. A ablação `SemCortex` zera `s.DLT` mas **não tira
os 48 genes do genoma nem do `dof`** — por isso `sem córtex` tem `dof` 202.6 contra 194.8 do COMPLETO e
metab 1.651 contra 1.618. **Ele paga mais e ganha +0.732 [−0.12,+1.58] p .075 (4/5).**

Conclusão que isso força: o ganho não pode ser economia de metabolismo (é negativa), então é a **remoção da
perturbação**. E a perturbação não é aprendida: `cor_dmax` = .402 / .394 / .425 / .401 (A) e .403 / .387 /
.395 / .413 (B) — invariante a braço, a mundo e a ablação, e igual ao que a deriva produz sozinha
(`0.5·tanh(σ√g · E[max|z|]_{n=48}) = 0.5·tanh(0.5·2.55) = .427`). Com `gene_min` .5 um gene de 0.4 já dá
δ = 0.19 **sem pagar nada** no `dof`: o córtex perturba de graça e a seleção precisaria zerar 48 genes
contra σ = .1 por geração para desligá-lo. Ela não zera — em nenhum horizonte que rodamos (§2, §4d).

### 1.5 O que do o4a/o4b/o4c separa as hipóteses — e o que NÃO separa

* **H_conta (CS):** a lacuna do C é a conta do A amplificada → `o4a` deve dar
  `gap_C_justa ≈ 2.319·(0.365/0.618) = 1.37` (ganho **+0.95**).
* **H_mundo (minha):** a conta rende no C o mesmo *em relativo* que rendeu no A→B (7.2 % da espinha) →
  `gap_C_justa ≈ 2.319 − 0.072·7.469 = 1.78` (ganho **+0.54**).
* As duas diferem por **0.41 e o MDE do protocolo é 0.78**. **`o4a` com n = 5 NÃO separa as hipóteses**;
  ele só decide a pergunta grossa "a lacuna caiu abaixo de 1.0?". Separar exige n ≈ 19 sementes
  (5·(0.78/0.41)²) — ou trocar de instrumento: fazer a regressão de mediação `rel_gap ~ (metab−1) + mundo`
  sobre as células A, B, C, C_justa, A_L92 (5 mundos × 5 sementes = 25 pontos, com o `metab` medido por
  semente que já está nos JSONs). O coeficiente do termo `mundo` **é** a resposta, e ele tem 5× mais graus
  de liberdade que o contraste de fit.
* **`o4b` (A com só L 92) não isola dimensionamento**: L 92 arrasta `retina/L` de 0.30 para 0.65 junto. O
  controle que falta é o Mundo D (§5).

---

## 2. Eixo P e G no kernel — MEDIDO (h1c/h2c chegaram às 18:50)

`mundo_vivo_v1_semretina`, G 60, σ .1, R 4, 5 sementes, `--motor hip`, juiz em torch.

| célula | P | fit | DP | ger_efetiva | segundos |
|---|---|---|---|---|---|
| h1c | 128 | 5.152 | 0.322 | 60 | 75 |
| h1c | 256 | 5.051 | 0.669 | 60 | 74 |
| h1c | 512 | 5.290 | 0.644 | 60 | 86 |
| h1c | 1024 | 5.356 | 0.397 | 60 | 125 |
| h3 (torch) | 256 | 5.389 | 0.284 | 60 | **728** |
| h2c | 256, G 240 | 4.943 | — | **68** (paciência 30) | 76 |

* **Inclinação por dobro de P: +0.085 [−0.053, +0.223].** P1024 − P128 = +0.204 [−0.36, +0.77] p .37 (3/5).
* **G240 − G60 = −0.109 [−1.02, +0.80] p .76 (2/5).**
* **kernel P256 − torch P256 = −0.338 [−1.05, +0.37] p .25 (2/5).**
* **Custo:** 9.8× fim a fim (74 s vs 728 s); 8× a população custa 1.67× o tempo → o kernel é limitado por **lançamento**, não por cálculo: aumentar P é quase de graça e mesmo assim não paga.

**Critério de decisão (registrado como pred 184, para o Fable aplicar):** o MDE pareado desta célula é
**0.75** (DP pareada .454). A tolerância ±0.20 da pred 178b é **3.5× mais estreita que a resolução** — logo
**178b fica INCONCLUSIVA, nem ✓ nem ✗**, e dizer "±0.20 ✓" com este n seria afirmar o que o dado não vê.
O que fazer com o 143×: **não é rodar mais P, é rodar mais SEMENTE.** 8 células de kernel × 40 sementes
≈ 17 min de GPU levam o MDE a 0.27. Regra: **P só entra em relatório se a inclinação por dobro tiver IC95
sem o zero; G só entra se G240 − G60 ≥ +0.30 com p < .05.** E o desvio kernel × torch **não** deve ser
perseguido com horas de torch: a identidade do simulador já está verde no c9j (100 % das ações, erro ≤ 6e-6,
`t_vida` bit a bit em 16/16); o que difere é o fluxo de RNG do GA, e isso se mede com sementes do lado barato.

---

## 3. Velocidade: a medição que proponho (e por que vale)

O que os dados já dizem: z5 (845 s) reproduziu o e78 (813/832 s) **bit a bit nas 5 sementes**
([5.167 5.747 5.667 5.222 4.987]) → o código não regrediu, e o `perf_snapshot` (0.97×) concorda. As duas
células lentas têm mecanismo próprio, não contenção: **z1 = `reavaliado`** (`lab.py:1768` avalia a elite de
novo num mundo novo a cada geração — e a elite é quem vive mais, num horizonte aberto que corre até o último
morrer) e **z2 = σ .2** (mais dispersão → maior máximo de `t_vida` → cauda mais longa). O argumento das 15:45
("não é a cauda: fit menor, tempo maior") não se sustenta: o relógio é fixado pelo **máximo** de `t_vida` do
lote, não pela média do fit.

**Medição proposta e feita (1 das 2 alterações): `src/lab.py:1735,1762`** — a linha de log a cada 5 gerações
passa a trazer `[Δs carga]` (tempo do bloco + `os.getloadavg()[0]`). Custa uma chamada de sistema a cada 5
gerações, não entra em conta nenhuma, e separa as duas hipóteses no próximo run que a fila rodar:
**contenção de CPU** = carga alta e ritmo uniforme; **cauda do horizonte aberto** = carga baixa e blocos
irregulares. `src/e43_campo.py` está travado (Astra), e é em `lab.py` que o laço vive — é o lugar certo.

---

## 4. Auditoria das decisões do Fable (10/09)

**(a) `corte_vivos .05` só na evolução — concordo com a lei, discordo da ordem.** O juiz sem corte é meu
próprio conserto (`campo.py:613`, pred 172) e está certo. Mas **.05 nunca foi medido**: a única medição é
.02 (−0.138 de fit, p .34, n = 5, uma amostra só) e o .05 está ligado no C5, no G120 e nos três o4 — a
comparação A × C carrega uma diferença de protocolo não medida no braço que importa. O controle existe
(`o4c`) e está **por último** na fila. Se a madrugada morrer em 01:30, ficamos com os tratamentos sem o
controle. Recomendo rodar `o4c` **antes** de `o4a`/`o4b`.

**(b) `campeao=ultimo` mantido (166 ✗) — concordo, sem ressalva.** 5.028 × 5.358, pior em 5/5, e 2097 s
contra 813 s. O `reavaliado` é regra de ESCOLHA (`lab.py:1768`), não de medição, e escolhe pior. Anoto só
que a média do juiz sobre as k melhores elites (CS docs/78 §2) é outra coisa e segue sem medida; cabe dentro de uma célula existente (k chamadas de `medidas`, ~20 s), não precisa de célula própria.

**(c) Rust parado até o P4 — concordo.** `c9n` não é ruído: n_come +16 %, n_posto +12 %, oficina +31 %,
litros/abast −8.6 %, rec +12 %. É comportamento sistemático, e o portão de identidade nunca exercitou respawn (o traço roda com `respawn 1e9`). Distribuições, não bit a bit.

**(d) A × B G120 — terminou, e o veredito da 177 é mais duro do que parecia.** `e79/e43_G120juntos.json`
(18:40, 2052 s, ger_efetiva 84 em 5/5):
(a) **✗** — a lacuna ao melhor cérebro é +0.756 em G120 contra +0.750 em G30: não caiu para ≤ +0.60, não
caiu nada; (b) **✓** — 84 > 60 em 5/5; (c) parcial — o pior com cérebro em G120 é o COMPLETO (3.866), não
`sem hipocampo` (4.040); (d) **✓** — linear −0.059 [−0.85,+0.73].
Pareado G120 − G30 por braço: linear −0.059, COMPLETO −0.248 (1/5), sem hip +0.073, sem reflexo −0.096,
tálamo fixo +0.171 (5/5, p .099). **Nada se move, e o `dof` explode**: COMPLETO 194.6 → 363.8, sem reflexo
199.8 → 343.6, tálamo fixo 180.2 → 360.0; metab 1.744 → 2.053. Contra o nulo do c6 (dof .52 em g60, .65 em
g120 → ~.57 em g84) o campeão de G120 está em .476, os mesmos ~0.09 abaixo do nulo que ele estava em G30
(.254 vs .317). **O `dof` do campeão acompanha a deriva nos dois horizontes: a seleção não poda em
horizonte nenhum que este laboratório já rodou.**
Ressalva de método: o G120 rodou no protocolo do lote (juntos + obs_rapido + corte .05) e o A5 não — o mesmo confundidor do C. `o4c` é o controle dos dois.

**(e) Código de proveniência do Astra — aceito, com um NÃO grave.** O `g0c` passou de verdade (exit 0,
192 s) e produziu `e84/e43_gate_prov.json` com `manifesto` (cfg/protocolo/mapas/flags/codigo/ambiente/
runtime/nomes_f), `config_hash` `41423a73…` e `tempos` (`evolucao_conjunta_s` 54.3, `avaliacao_s` 21.9 por
braço, `evolucao_s` null no lote): o Risco 1 da docs/81 está descarregado empiricamente. **Mas `g0a` não
rodou**: `exit=2 em 0 s`, `unrecognized arguments: --out` — o daemon acrescenta `--out <dir>` a todo script e
`unittest.main()` morre no argparse antes do primeiro teste. Os "5 testes do Astra" continuam **não
verificados**, e a condição que o próprio Fable escreveu ("commit só com g0a/g0b/g0c verdes") está sendo
lida de um exit code que nunca viu um teste. Consertado (§6, alteração 1) e re-enfileirado como
`o5_ga_testes_proveniencia`; **não commitei `src/testes_proveniencia.py`** — o arquivo é do Astra e a
decisão de commitar é do Fable. Segundo ponto: com `--legado`, todo A/B/C fica legado para sempre; o
pareamento desta página foi feito à mão conferindo que `seeds == [0,1,2,3,4]` nos quatro arquivos.

**(f) A fila da madrugada — dois reparos.** (1) `o4b` não isola dimensionamento (§1.5, §5): muda `retina/L`
junto com L. (2) `o4a` não tem potência para a pergunta que o motivou (§1.5). Os controles `o3e`/`o3f`
(pred 179) são os mais baratos e informativos da fila e estão bem posicionados.
Já chegaram, aliás: `o3b` (retrato do C) devolve a **delegação com o sinal trocado** — pearson **+0.12**
(spearman +0.16) no C, contra −0.17 no A, −0.56 no B e −0.76 no e77 do CS: "a conta justa reforça a
delegação" não sobrevive ao terceiro mundo. E `o3c`: no C o `dof` dos campeões é .24–.38 na geração 30
contra .36 do nulo — de novo em cima da deriva.

---

## 5. Mundo D e dois seres novos

**`cenarios/mundoD_olho_proporcional.json` = Mundo C com UMA lei trocada.** `diff` contra o C:
`nome`, `predicao`, `retina.R_dia` 60 → **27**, `retina.R_noite` 15 → **7** (mesmo fator .45; passo, custo e
`k_cego` intactos), e os dois seres novos.

**Mecanismo no código, e é o achado que sustenta o mundo:** com `NM_RETINA=1` — que é como A, B e C todos
rodaram — `campo.py:292-301` e `:329-341` **sobrescrevem** `s._dist_v` e as distâncias por opção com o que os
8 raios enxergam; `cfg.nevoa` (E63, `campo.py:291,328`) **nunca é consultado**. Logo `nevoa` é um botão morto
sob retina, e **o alcance do olho é a lei de observabilidade deste laboratório** — e ela nunca foi
dimensionada. `dimensiona.py` imprime `retina/L` **0.30 no Mundo A e 0.65 no Mundo C**, e o "cego"
(`k_cego·R_dia` = 120 m) passou de 0.60·L para **1.30·L: maior que o mapa inteiro**. O Mundo C não deu
repetição às peças que dependem de contexto; **tirou delas o motivo de existir**, tornando o mundo 2.2× mais
observável. É a explicação mecânica que faltava para o §1 do docs/79 ("o mundo melhorou e o cérebro piorou")
e para o C passar nas três razões de `dimensiona.py` com os valores medidos (0.51 / 6.93 / 4.45) sendo o pior
mundo para o cérebro. Com R_dia 27 em L 92 as duas razões voltam às do Mundo A (0.29 e 0.59·L).
**Correção minha, do ciclo 2:** a pred 170 já trazia esta ressalva pré-registrada ("o teste que separa visão
de memória é um C' com R_dia 27") — mas eu a condicionei a "**se (c) ✓**". (c) veio ✗, e eu teria deixado o
C' cair. Estava errado: o ✗ é *sintoma* do confundidor, então o C' fica mais necessário, não menos.

**Predição 182 (numérica):** (a) linear ≤ 6.2 (C: 7.469); (b) lacuna linear − COMPLETO cai de +2.319
[+1.49,+3.14] para ≤ **+1.4**; (c) **inversão de sinal no hipocampo**: `sem hipocampo` − COMPLETO sai de
**+0.256** (C) para ≤ **−0.20** — primeira aposta deste laboratório em contribuição POSITIVA de um órgão;
(d) `sem córtex` continua ≥ +0.30 acima do COMPLETO. Se (c) falhar, o hipocampo como está (EMA por distrito
de renda/espera/gasto) não é a memória que o mundo pede: falta memória de **lugar** (onde eu VI um posto),
que ele não guarda — e o programa do cérebro em camadas neste mundo se fecha com mecanismo.

**Dois seres novos (pred 183, sem uma linha de código — só `cerebro` no cenário):**
`COMPLETO cortex 0.1` (`cortex_amp` .5 → .1) e `COMPLETO hip 0.1` (`hip_esc` .01 → .1).
O primeiro é a dose–resposta do §1.4: se os +0.732 do `sem córtex` são **perturbação**, cortex 0.1 recupera
≥ 70 % deles (≥ +0.50); se são **aluguel**, recupera ≤ +0.20 e eu estou errado. O segundo é o par natural do
Mundo D: 10× a autoridade do hipocampo deve valer ±0.30 (nada) no C observável e ≥ +0.30 no D de olho curto.

Enfileirado só a **fumaça** `o5_smoke_mundoD` (P 8, G 1, 1 semente, protocolo dos o4): verifica que o mundo não é armadilha e que os dois seres sobem no lote. **A bateria é do Fable.**

---

## 6. Alterações, portões e fila

| # | arquivo:linha | o quê | por quê |
|---|---|---|---|
| 1 | `src/testes_proveniencia.py:97-105` | `__main__` descarta `--out`/`--tag` antes de `unittest.main()` | o portão `g0a` morreu no argparse em 0 s e a fila seguiu: verde falso. **Não commitado** (arquivo do Astra) |
| 2 | `src/lab.py:1735,1762` | `[Δs carga]` na linha de log a cada 5 gerações | §3: separa contenção de CPU de cauda do horizonte aberto sem um segundo de GPU |

**Não mexi**: no `dof` da ablação (o aluguel por órgão mudo é o que torna o §1.4 conclusivo — mexer apagaria
a evidência de que `sem córtex` ganha PAGANDO mais); em `DMAX` 12 vs K 6 (6 de 12 caixas mortas em todo
mundo; mexer invalida toda semente gravada); em `cortex_amp` como padrão (é hipótese, vira ser, não lei).

**Enfileirado** (prefixo `o5_`, roda depois do o4c): `o5_ga_testes_proveniencia`,
`o5_gb_testes_passo_identidade`, `o5_gc_testes_campo`, `o5_gd_testes_seres`, `o5_smoke_mundoD`.
**Preds novas:** 182 (Mundo D), 183 (dose do córtex/hipocampo), 184 (eixo P: n=5 não mede + réplica com
sementes). **Pedido ao Fable:** re-enfileirar o `g0a` consertado ANTES de commitar o código do Astra, e
rodar `o4c` antes de `o4a`/`o4b`.

---
## Auditoria Fable (10/09 19:10) — o que conferi contra código e JSON
- **Números** ✓: G120 (linear 4.917, COMPLETO 3.866, dof 363.8, metab 2.053; lacuna por semente .756 vs .750 — é a média das lacunas ao MELHOR cérebro de cada semente, não a lacuna das médias); h1c/h2c (5.152/5.051/5.290/5.356; G240 4.943; torch 5.389) ✓.
- **Retina sobrescreve a névoa** ✓: `campo.py:291/328` usam `c.nevoa` só no ramo sem retina; `:292-301` e `:329-341` trocam `_dist_v` pelos 8 raios com `cego = k_cego·R_dia`. Confundidor real. A pred 170 JÁ tinha a ressalva do olho pré-registrada (condicionada a (c) ✓); o condicional estava errado e o Opus assumiu. Aceito o Mundo D (pred 182). `raio_px` 45 m também é absoluto (49 % da cidade em C vs 22 % em A) — fica fora do D (uma lei) e vira candidato a Mundo E.
- **Sem córtex paga pelos genes mortos** ✓: `completo.py:53` zera `DLT` e os 48 genes seguem no `dof`; com `custo_modo ativacao` a parte por ativação do córtex é zero mas a basal (.15 × dof/100) cobra os genes mortos: as ablações pagam ~7 % de fome a mais por nada. Conserto = `dof` só de blocos ligados (completo.py + portão de identidade), próximo ciclo de infra. A direção do achado (córtex atrapalha) só fica mais forte.
- **g0a verde falso** ✓ e grave: o daemon alerta mas NÃO bloqueia os pedidos seguintes. Re-enfileirado como `o3dz_testes_proveniencia` com o conserto do Opus (descarta `--out/--tag` antes de `unittest.main`); o commit do código do Astra espera esse portão. Regra nova para o daemon (próximo ciclo): pedido pode declarar `depende_de` e é recusado se o portão não saiu com exit 0.
- **Ordem da fila**: `o4c` renomeado `o4_0_mundoA_protoC` — o controle roda antes dos tratamentos (pedido aceito).
- **Discordância**: pred 184 (40 sementes no kernel) mede o eixo P no mundo v0 sem retina, NP 40 — o protocolo dos mundos A/B/C continua torch (SerCompleto não tem kernel). A decisão P/G do kernel vale para o kernel; para A/B/C o P/G continua 128/30 até haver medida no torch com o mesmo n.


**Auditoria Fable 10/09 23:55 — pred 182 (Mundo D) ✗ em (a)(b)(c), ✓ em (d):** olho de 27 m não muda a espinha (linear 7.96 vs 7.47 no C) nem a lacuna (2.81 vs 2.32); sem hipocampo não inverte (+0.22). Mecanismo: `alvo()` entra em F fora da retina (`campo.py:287-288`); a retina só limita a distância percebida aos serviços, e o linear compra ao passar. O confundidor retina/L do o4b não existia na prática. Piso do prêmio em D 28.6 % (passa). Detalhe em PREDICOES 182.
