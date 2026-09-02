# 30 — Glândulas evolutivas: hormônios sem nome (E16, 2026-09-02)

**Leonardo:** *"Preços são hormônios: alto = estresse, baixo = tranquilidade;
hormônio não é controlado pelo cérebro, o corpo ajuda; precisa do reverso
(dopamina). E estresse deve EMERGIR, não ser roteirizado."*

## 1. O princípio: o hormônio é do CORPO

Tudo o que o lab chamou de "neuromodulação" até aqui (EXP10, doc 07) era um
**gatilho no cérebro**: o próprio controlador lia um sinal e mexia no próprio
ganho. O E16 inverte a posse.

- `h` (K integradores com vazamento) mora no **`Lote`** — o corpo — e é
  atualizado dentro de `passo()`, junto com fome, fadiga e temperatura.
- Os **genes** (τ, pesos de entrada `a`, pesos de saída `b`) vêm do genoma da
  arquitetura e são copiados pro corpo no `reset()`.
- O cérebro **só sente** `h` (features `h_gl0`/`h_gl1`, ex-`e16_a/e16_b`) e é
  **modulado** por ele. Não escreve em `h`. A única coisa que o cérebro decide
  e que muda `h` é **descansar** — e mesmo isso é fisiologia, não controle: o
  sono corta `h` pela metade.
- **Ninguém dá nome às glândulas.** Não existe "cortisol" nem "dopamina" no
  código: existem K integradores idênticos. Quem vira o quê é decidido pela
  seleção, e a etiqueta só é colada **depois**, por
  `src/analise_glandulas.py`, a partir da correlação medida e do sinal dos
  ganhos.

## 2. O desenho

```
h_k ← h_k·(1 − 1/τ_k) + (1/τ_k)·Σ_i a_ki·x_i^déficit + γ_ev·Σ_j a_kj·x_j^evento
                                                       clamp em [0, H_MAX]
ganho_j = 1 + Σ_k b_kj·h_k                             clamp por canal
custo   = κ_h·Σ_k h_k   por passo, gordura primeiro (com perda), depois tanque
sono (descanso): h ← h/2
```

**Entradas (10)** — 6 déficits (tônicos, contínuos) e 4 eventos do passo
**anterior** (fásicos, impulsos):

| déficit | evento de ganho |
|---|---|
| `1 − fuel/cap` · `fome/100` · `fad/100` | `entregou` |
| `1 − vida/100` · `temp/120` · `dinh < 2` | `abasteceu` · `consertou` · `descansou` |

**Saídas (5 canais)** — `necessidade`, `exploração`, `metabolismo`, `sono`,
`velocidade`.

**Duas escolhas de escala que não estavam no rascunho do doc 28** (§3), ambas
pela **regra 15** ("gene novo precisa ter escala comparável aos pesos com que
compete" — o gene de timing O(1) do ReativoHora era inerte por construção):

1. **Déficit entra normalizado por 1/τ, evento não.** Com a fórmula literal
   `h ← h − h/τ + Σa·x`, um déficit constante de 0.5 com `a=1` e `τ=200` dá
   regime permanente `h* = 100` — satura em `H_MAX` no primeiro segundo de
   vida e τ vira amplitude, não memória. Normalizado, `h* = Σ a·x` e τ governa
   **só a memória**: amplitude e constante de tempo viram genes independentes.
   O evento continua sendo um chute de `γ_ev·a` que decai em τ — que é o que
   permite uma glândula **fásica** (dopamina) existir.
2. **τ log-uniforme em [10, 2000] passos** via `τ = 10·200^σ(gene)`. Gene 0 →
   141 passos (0.6 dia); a mutação σ=0.3 com clamp ±5 alcança as duas pontas.

**Limites (N9 / regra 5: "mecanismo novo × peso evoluído = co-adaptação;
LIMITAR a alavanca")**: `H_MAX = 2`, `GL_ESCALA_B = 0.25`, e um clamp por
canal — metabolismo e velocidade em [0.70, 1.30], sono em [0.50, 2.0],
necessidade em [0.25, 2.5], exploração em [0, 3]. O EXP10 já mostrou que
ganho 0.5–1.0 ajuda e 8.0 destrói; o clamp é o que impede a evolução de
descobrir o 8.0.

**κ_h = 0.25 por unidade de h, por passo, sempre — inclusive parado.** É o
detalhe que faz o **timing** valer: o benefício de um ganho só aparece
andando (ou dormindo, ou servindo), mas a conta chega todo passo. Um hormônio
cronicamente alto perde; um que sobe na hora certa ganha. Sem isso o E16 seria
um botão de desconto, não uma glândula.

## 3. O que é aplicado onde (e o que NÃO é — honestidade primeiro)

Regra de convivência do doc 28 §2: o E16 só pode editar os seus blocos
`# [E16 ...]` em `lab.py`. Dois dos cinco canais entram exatamente onde
deviam; um entra **pela metade**; um é opt-in; um fica **calculado e não
aplicado**.

| canal | onde entra | estado |
|---|---|---|
| **necessidade** | `SerGlandular.extra_serv`: `ss += (ganho−1)·svn·W` ⇒ total `svn·W·ganho` | **multiplicativo, completo** (EXP10: multiplicativo bate aditivo 16/16) |
| **sono** | bloco 2 do `passo()`, como a *diferença* `−(30/peso)·(ganho−1)` sobre a recuperação que já saiu | **completo** (equivalente a `30·ganho/peso`, a menos dos clamps de borda) |
| **metabolismo** | bloco 2, como a diferença `−cuf·c.fuel·an·(ganho·regime − 1)` | **parcial: só o TANQUE.** Pneu, óleo e calor usam `cuf` mais abaixo, fora do bloco |
| **exploração** | `SerGlandular.decidir`, ruído Gumbel escalado por `ganho` | **opt-in** (`expl_on=False` por default — o `ReativoRuido` do E14g já perdeu; diversidade sozinha não basta) |
| **velocidade** | — | **calculado (`m.mult[:,4]`), NÃO aplicado** |

### As 3 linhas fora do bloco que precisariam mudar

Se o dono do `lab.py` quiser os cinco canais completos, são estas três (números
de linha do estado atual do arquivo):

```
557:  m.fad = torch.where(o3, (m.fad-30./peso).clamp(min=0), m.fad)
      ->    (m.fad - 30.*m.mult[:,3]/peso)                       # sono, direto
635:  cuf = cuf*peso*saude
      ->  cuf = cuf*peso*saude*m.mult[:,2]                       # metabolismo pleno
677:  m.rest = torch.where(an, (cu*m.vel()*peso*saude).round()...)
      ->                  (cu*m.vel()*peso*saude*m.mult[:,4])    # velocidade
```

A 557 eu **emulo** exatamente no meu bloco (a diferença aditiva compõe com o
que já saiu); a 635 eu emulo **só para o combustível**; a 677 não tem como
emular — `m.rest` é escrito depois do meu último bloco.

### Por que não rebindei `peso`/`saude` (a saída "esperta" que eu recusei)

`peso` e `saude` são variáveis **locais** de `passo()` definidas antes do meu
bloco, então eu *poderia* multiplicá-las e a modulação chegaria em `cuf` e em
`m.rest` sem tocar em linha nenhuma. Recusei porque a física sai errada e a
seleção acharia o buraco: `cuf ∝ peso·saude` e `rest ∝ peso·saude` com o
**mesmo** fator, então qualquer redução faria o ser **gastar menos E andar
mais rápido E aquecer menos** — almoço grátis, com o κ_h como único freio. Em
particular o calor: o N13 mostrou que **100% das avarias deste mundo são
superaquecimento**; um canal que baixa `cuf` corta o único eixo perigoso do
mundo de graça. O canal de metabolismo aplicado só ao tanque não tem esse
buraco: economizar combustível não compra imunidade térmica.

Fica declarado como **limitação conhecida**: o canal de metabolismo do E16 é
"quanto o motor bebe", não "quanto o corpo inteiro consome"; e o único
trade-off real dele é o κ_h. A versão honesta — o hormônio que **troca**
consumo por tempo (economizar ⇒ andar devagar) — exige a linha 677 e é o
primeiro pedido do E16 pro dono do `lab.py`.

## 4. Predições (ANTES de rodar)

**Procedência, exata:** as cinco predições e o negativo (a) estão no **doc 28
§3, escrito antes de existir uma linha de código do E16** — são elas que valem
como pré-registro. O texto desta seção foi redigido **depois** da 1ª rodada da
fase a (a que tinha o bug do regime, §6), então os detalhes que eu acrescentei
aqui — os valores de `GL_ESCALA_B` da predição 3 e os negativos (b), (c) e (d)
— **não são pré-registro**, são hipóteses informadas por aquela rodada.
Declarado pra não inflar o placar: nenhuma predição foi *alterada*, mas três
dos quatro negativos foram *escritos sabendo* que a 1ª rodada tinha ido mal.

1. **τ das duas glândulas diferem por mais de 3×.** Mecanismo: uma alimentada
   por déficit (tônica, precisa integrar) e outra por evento (fásica, precisa
   decair) têm ótimos de memória diferentes por construção. τ pode ir de 10 a
   2000 passos (0.04 a 8.3 dias).
2. **Papéis opostos:** uma correlaciona com déficit e **reduz** gasto/esforço
   (estresse-like); a outra correlaciona com evento de ganho e **aumenta**
   esforço (dopamina-like). O reverso que o Leonardo pediu não é escrito em
   lugar nenhum — as duas glândulas são idênticas no código.
3. **U invertido na escala dos ganhos** (`GL_ESCALA_B` em 0.10 / 0.25 / 1.00 /
   4.00): pico no meio, colapso em 4.00. É a replicação do achado do EXP10
   (0.5–1.0 ajuda, 8.0 destrói) num mundo com corpo de verdade.
4. **O sono passa a pagar.** No E13 dormir era inerte (N17: sono em bloco não
   reduz mortalidade) e caro (E13j: `sono_come=5` custa fitness). Com `h ← h/2`
   no descanso, dormir vira **manutenção**: quem acumulou hormônio tem motivo
   fisiológico pra parar. Predição: no braço `sono5`, glândulas > reativo, e a
   diferença é maior do que no mundo sem `sono_come`.
5. **Com regime variável, glândulas > reativo** — e a diferença é maior do que
   no mundo estacionário. É a Tese do Corpo: modulação só paga quando existem
   estados lentos acoplados cujos ótimos **variam**. Sem regime o ótimo é fixo
   e um peso constante já o expressa (E2: aumentar o mundo não faz a
   neuromodulação emergir; o que move o teto é o acoplamento).

**Negativos possíveis, declarados antes:**

- **(a) As duas viram a mesma coisa** — este mundo só precisa de um eixo. Seria
  o resultado do doc 28 §3, e o braço `K=1` é o controle que o mede: se K=1 ≈
  K=2, a segunda glândula é decoração.
- **(b) As duas ficam inertes** (`h ≈ 0` ou `b ≈ 0`): κ_h = 0.25 é caro demais,
  ou os canais que sobraram (tanque + sono + necessidade) são fracos demais
  para pagar por um hormônio. Diagnóstico: `h_medio` e `ganho_medio` na
  telemetria.
- **(c) `h` cravado em `H_MAX`**: virou botão de desconto, não glândula —
  κ_h barato demais ou o clamp do canal frouxo demais.
- **(d) A avaliação não enxerga** (regra 14): com R=4 e sem pena, 5 pontos de
  mortalidade afogam. A validação rápida abaixo é R=4, 1 semente e G=10 —
  **não decide nada**, só diz se o mecanismo anda.

## 5. Validação rápida (G=10, P=512, T_evo=600, 1 semente, R=4, aval 1200 em 1000+)

Orçamento do doc 28 §2: fumaça + **uma** evolução curta. **Isto não é
bateria.** Fitness tem ±1.5 entre sementes e mortalidade ±8 pp (regra 13);
aqui n=1. Pior: `T_evo=600` = **2.5 dias**, e a regra 11 diz que a 2.5 dias a
seleção **não vê a morte** (o perito morre depois do dia 3). Toda leitura de
mortalidade abaixo é decorativa. O que vale é o **mecanismo**.

| braço | fit | ent | mortos | panes | quente | posto | res~ | custo de h | glând. ativas |
|---|---|---|---|---|---|---|---|---|---|
| reativo (referência) | **2.82** | 6.5 | .27 | 6.2 | 3.3 | 12.5 | 37.7 | – | – |
| glândula K=2 | 1.74 | 4.5 | .29 | 5.4 | 2.2 | 9.5 | 15.2 | 68.5 | **1 de 2** |
| glândula K=1 | 2.85 | 5.8 | .25 | 5.3 | 2.8 | 8.9 | 35.0 | 0.3 | **0 de 1** |
| reativo regime (referência) | **2.38** | 6.3 | .34 | 6.4 | 4.0 | 10.3 | 30.9 | – | – |
| glândula K=2 regime | 1.83 | 4.7 | .31 | 5.8 | 2.6 | 7.4 | 8.2 | 79.7 | **1 de 2** |
| glândula K=2 κ=0.05 | 0.77 | 5.5 | .71 | 10.3 | 3.6 | 9.7 | 18.9 | 11.0 | **1 de 2** |

### 5.1 As predições, uma a uma

1. **τ diferem > 3×: NÃO TESTÁVEL.** Nunca houve duas glândulas ligadas ao
   mesmo tempo. O τ de uma glândula com `h ≈ 0` é um gene que deriva sem
   pressão — comparar τ de glândula morta seria fabricar confirmação (foi
   literalmente o primeiro output do `analise_glandulas.py`, e o script foi
   corrigido pra recusar).
2. **Papéis opostos: NÃO no mesmo indivíduo — SIM entre indivíduos.** Cada
   campeão acende **uma** glândula, e o papel dela muda com o mundo:
   - `K=2` → **ESTRESSE-like**: sobe com `def_fome` (+0.53) e **reduz o
     metabolismo** (b = −0.39 ⇒ ganho médio 0.915, 8.5% menos combustível
     queimado). É exatamente o que o Leonardo pediu que emergisse, e não está
     escrito em lugar nenhum: as K glândulas são idênticas no código.
   - `K=2 regime` → **SACIEDADE-like**, o reverso: sobe com o **evento**
     `ev_abasteceu` (+1.80) e aumenta a manutenção (necessidade +0.32, sono
     +0.33 ⇒ ganho 1.10 nos dois). "Abasteci, agora me cuido."
   - `κ=0.05` → também dirigida por `ev_abasteceu` (+1.92), mas com os `b`
     aplicados ≈ 0: liga o hormônio e não usa.
3. **U invertido na escala dos ganhos: NÃO RODADO** (fase b não coube no
   orçamento de GPU). Comando pronto: `python src/e16_glandulas.py --fase b`.
4. **O sono passa a pagar: parcialmente, e não em fitness.** O sono é o
   mecanismo mais *usado* de todos: nos dois braços com glândula ativa ele
   removeu **1/3 (91.8 de 277) e 1/4 (89.0 de 365) de todo o hormônio
   produzido na vida**. Ou seja: dormir virou, de fato, a manutenção
   endócrina. Mas isso não virou fitness — e o braço `κ=0.05`, que quase não
   dorme (sono limpou 0.5), é o que mais morre (0.81). Fase c (`--fase c`,
   `sono_come=5`) não rodou.
5. **Com regime variável, glândulas > reativo: NÃO.** O regime **funciona**
   (o braço de referência cai 2.82 → 2.38, e as avarias por calor sobem 3.3 →
   4.0), mas a glândula continua atrás (1.83 vs 2.38). A distância até a
   referência até **encolhe** com o regime (−1.08 → −0.55), que é a direção
   que a Tese do Corpo prevê — só que partindo de um déficit, não de um
   empate. Com n=1 isso é sugestão, não resultado.

### 5.2 O negativo, com o mecanismo

**As glândulas perdem em todas as condições, e a conta é aritmética.** A
glândula ativa custa **68–80 de combustível por vida** (`κ_h·Σh` = 0.25 ×
0.23 × 1200 ≈ 69, bate) e o que ela compra com isso é 8.5% de desconto no
tanque. O preço é pago em **gordura primeiro**: a reserva média desaba de
37.7 para 15.2 (e para 8.2 com regime). **O hormônio come exatamente a
poupança que o E13 levou uma bateria inteira pra fazer existir.** O ser vira
um táxi mais econômico e mais pobre: queima menos (panes 6.2 → 5.4, calor
3.3 → 2.2, posto 12.5 → 9.5) e entrega 30% menos (6.5 → 4.5).

Três causas, em ordem de tamanho, e nenhuma delas é "a modulação não serve":

1. **O repertório modulável que sobrou é fino.** Dos 5 canais, 2 estão
   aplicados de verdade (necessidade, sono), 1 pela metade (metabolismo, só
   o tanque) e **2 são genes à deriva** (exploração desligada por default,
   velocidade não aplicada — §3). São **40% dos genes de saída sem efeito
   nenhum**, competindo por seleção com os que mordem — a regra 15 no limite
   (gene cuja escala de efeito é exatamente ZERO).
   E o canal que mais importaria neste mundo — o calor, 100% das avarias
   segundo N13 — está fora do alcance do meu bloco por construção.
2. **A seleção não convergiu.** O `K=2` tem 32 genes a mais que a referência
   e 10 gerações; a curva de treino dele ainda estava subindo no fim
   (0.05 → 2.90 contra 0.13 → 3.83 da referência). O controle que mostra isso
   é o **`K=1`: com só 16 genes extras a evolução conseguiu DESLIGAR a
   glândula** (h = 0.001, custo 0.3) e empatou com a referência (2.85 vs
   2.82). Ou seja, quando dá tempo de convergir, a resposta da seleção neste
   mundo é *"não quero hormônio"* — não *"o hormônio me atrapalha"*.
3. **κ_h = 0.25 não é o vilão.** Baratear o hormônio 5× (κ=0.05) dá o **pior**
   braço de todos (0.77, mortos 0.71): com o hormônio barato o ser sustenta
   `h` e distorce a política sem pagar por isso, e morre. E o treino desse
   braço é o **melhor** de todos (hist até 3.88) contra o pior teste — o
   sintoma clássico da regra 11 (treino de 2.5 dias não vê a morte que
   acontece no dia 4). Preço baixo demais é pior que preço alto demais.

**O que isto contribui pro programa:** é o E2 outra vez, num mundo com corpo
de verdade. *Aumentar o mundo (regime oculto) não faz a neuromodulação
emergir; o que move o teto é o ACOPLAMENTO corpo→computação e o repertório
modulável.* O E16 mediu isso pela primeira vez com um acoplamento
**contável**: 2.5 canais de 5. A predição que fica pro E16b é direta — **o
ganho da glândula deve crescer com o número de canais realmente aplicados**,
e a próxima medida vale mais que qualquer ajuste de κ_h.

### 5.3 O que emergiu sem roteiro (o positivo, pequeno)

- **Estresse emergiu** no braço `K=2`: uma glândula que sobe com a fome e
  desliga o motor. Ninguém escreveu "estresse".
- **O reverso emergiu** no braço com regime: uma glândula que sobe com o
  **evento de ganho** (abasteceu) e aumenta a manutenção.
- **A retificação criou um terceiro modo que eu não desenhei.** Com `h` preso
  em [0, H_MAX], um peso **negativo** num déficit faz a glândula subir quando
  o déficit **some**. Quase todos os campeões usam isso (`def_fuel −1.76`,
  `ev_consertou −1.71`, `def_calor −1.53`): a glândula vira um **detector de
  "está tudo bem"** sem precisar de nenhum gene de evento. O "reverso" que o
  Leonardo pediu tem, neste desenho, dois caminhos — e o segundo é de graça.
- **A correlação mentiu e os genes contaram a verdade.** A glândula do `K=2`
  correlaciona +0.52 com `descansou` — mas o gene de `ev_descansou` nem está
  entre os quatro maiores. Ela é dirigida por `def_fome` e pela ausência de
  calor/pane; o `descansou` é *consequência*. É a regra 6 ("toda vitória tem
  uma história prevista e uma real") aplicada a um hormônio, e por isso a
  análise final lê **gene e correlação juntos**.

## 6. Contratos e portão

- `cfg.glandulas=False` ⇒ **identidade bit-exata**: nada é alocado no `Lote`,
  nada roda em `passo()`, as features ficam `zeros_like`. Portão do perito
  `ent 7.9740 / av_fuel 25.1302` intacto (`src/testes_e16.py` teste 1).
- **Genes zerados ⇒ o Reativo é reproduzido bit a bit** com as glândulas
  LIGADAS (teste 2): `h=0` ⇒ ganhos 1 ⇒ todos os deltas do bloco são
  exatamente `0.0`. É o que garante que a glândula é um acréscimo, não um
  mundo novo.
- O bloco do `Lote.__init__` **não consome o Generator `g`**: ligar as
  glândulas não desloca nenhum sorteio do mundo (`s.perda` continua idêntico).
- O ruído de exploração usa um **gerador próprio** (`s.gexp`), nunca `m.gsim`:
  os braços continuam pareados no mesmo mundo sorteado.
- Zero sync no laço quente: as correlações saem de somas acumuladas
  (`Σh`, `Σh²`, `Σx`, `Σx²`, `Σhx`) e só viram Pearson no fim, na análise.

### Dois erros meus, pegos e consertados (pra não repetir)

1. **O regime nasceu dentro do `if c.glandulas`** — então o braço `reativo
   regime` rodava no mundo SEM regime e saiu **bit a bit igual** ao `reativo`
   (fit 2.820 nos dois, até a 3ª casa). A comparação inteira teria sido
   placebo. O que pegou foi o número idêntico demais. O regime agora é do
   MUNDO: vale pra todo braço, e `testes_e16` + uma checagem direta provam que
   ele muda o Reativo (ent 0.2396 → 0.2708, panes 4.56 → 3.60).
2. **A primeira versão do `analise_glandulas.py` fabricava confirmação.** Ela
   contava uma glândula desligada como "um papel distinto" e imprimia
   "PREDIÇÃO 2 CONFIRMA" em 3 de 3 braços; e somava os 5 canais no "esforço
   líquido" incluindo os 2 que não estão aplicados. Corrigido: glândula com
   `h ≈ 0` é **inerte** e não entra em predição nenhuma; os genes dos canais
   não aplicados saem marcados com `*` e ficam fora de qualquer soma.

## 7. Arquivos

| arquivo | o quê |
|---|---|
| `src/lab.py` blocos `# [E16 ...]` | Cfg (flags), `Lote.__init__` (estado), `obs()` (2 features), 2 blocos em `passo()` |
| `src/glandulas.py` | `SerGlandular` (genes, τ, ganho de necessidade, exploração), `ser_glandular(K)`, `ler_genes` |
| `src/e16_glandulas.py` | runner: fases a (braços), b (U invertido), c (sono paga?) |
| `src/analise_glandulas.py` | roda o campeão, mede correlação e **só então** dá nome |
| `src/testes_e16.py` | identidade, genes zero, [0,H_MAX], custo, sono limpa, multiplicativo |
