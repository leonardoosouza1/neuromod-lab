# 16 — PRD: Sistema Endócrino v2 (auto-regulação do cérebro do táxi)

**Status:** v2.1 — revisada por avaliador adversarial em 2026-08-31; 5 achados
CRÍTICOS incorporados (ver §11). Aguardando gates G2 antes de bateria.
**Baseado em:** brief de restrições (docs 01–15) + resultado parcial da bateria
base (s0/s1, Colab T4) + revisão adversarial.

---

## 1. O que a bateria base já nos disse (s0/s1, P=8192, G=100)

| arq | teste s0 | teste s1 | treino s0 | treino s1 |
|---|---|---|---|---|
| reativo | **16.26** | **16.83** | 7.56 | 7.83 |
| banco EMA | 16.09 | 15.95 | 7.84 | 7.82 |
| corpo | 15.10 | 14.83 | **7.86** | **8.17** |
| diádica | 14.19 | 14.27 | 7.66 | 7.38 |
| híbrido | 14.15 | 15.54 | 7.74 | 7.92 |

1. **Memória não paga no mundo base** — predição confirmada (2/3 sementes).
2. **Ordem INVERTE treino→teste**: memória/corpo vencem no treino e perdem em
   cidade nova — overfit estrutural.
3. **Por que `corpo` falhou**: `serv_need()` já pondera serviço por necessidade.
   Lição: **modular o que a política não expressa, nunca o que ela já expressa.**

## 2. Objetivo da v2 — reformulado após revisão

Dar ao táxi um sistema de auto-regulação interoceptiva (fome→foco, recompensa→
persistência, cansaço→sono) e medir **qual mecanismo paga**, separadamente:

- (a) **estocasticidade** de decisão (ter temperatura);
- (b) **interação instantânea** corpo×decisão (termos bilineares φ×feature);
- (c) **estado lento** (EMAs interoceptivas alimentando as interações);
- (d) **dinâmica hormonal em si** (reserva finita, habituação, burnout).

**Honestidade estrutural (achado crítico do revisor):** com política LINEAR,
"escalar peso multiplicativamente por m" ≡ "somar feature de interação m·x ao
score" — a distinção multiplicativo/aditivo dos docs 03/06 pressupõe
não-linearidade que o táxi não tem. Então o que construímos é uma política
bilinear com estado + dinâmica de reserva — e a escada (§6) atribui o ganho a
cada camada. A proibição real: m NUNCA entra como termo aditivo puro (bias) —
isso sim é reparametrização (06 §2.1).

## 3. Restrições herdadas (violação = bug de método)

- NÃO modular τ de memória (15 §2.1 — redundante com banco de τ).
- Gatilho = σ(w_g·φ) evoluído sobre interocepção; nunca surpresa genérica
  (15 §3), nunca a variável oculta (02 §6.3).
- U invertido: amplitudes partem de ~1.0 e são VARRIDAS (ablação estática §7).
- Reserva finita (03 §2) — só no braço ⑤, com τ's que CABEM no episódio (§5.3).
- Custo metabólico κ_m·⟨m⟩ declarado; pressão exige tensão (05 §5).
- Morte obrigatória: fome=100 por 50 passos consecutivos → colapso terminal
  (contabilizado: zeros até o fim de T — morrer cedo NÃO reduz penalidade §8).
- I8 real: braços pareados por **parâmetros VIVOS** (braço ③ tem os mesmos 46
  vivos que ⑤), não só por NP nominal.
- I4: **≥5 sementes de evolução** (3 era violação do próprio invariante).
- I2/I3: Euler implícito nas ODEs de reserva; τ evoluído em log.
- Moeda cruzada: **não implementada nesta versão** — κ_m debita no fitness
  (mesma moeda). Declarado como limitação; se amplitudes degenerarem em
  política dominada, v2.2 troca κ_m por custo em fuel/tempo.

## 4. Arquitetura

### 4.1 Interocepção φ (10 dims, só estado interno)
fome, fadiga, fuel/cap, pneu, temp, dinheiro, EMA(entregas), EMA(receita),
EMA(avarias), adenosina. **τ das EMAs = 50** (4.6·τ=230 ≤ T_evo — conta do
revisor; 200 não convergia dentro do episódio).

### 4.2 Canais (podados pela revisão)

| canal | gatilho | age em (o que a política NÃO expressa) |
|---|---|---|
| NA (foco) | σ(w₁·φ) | temperatura da decisão T = T₀/(1+a·m) |
| cortisol (defesa) | σ(w₂·φ) | ×(1+b·m) SÓ em custo_rua e congestão (features por-candidato; e_pneu/e_temp são constantes entre candidatos — não mudam ranking, cortadas) |
| DA (persistência) | σ(w₃·φ) | ×(1+c·m) no peso d_alvo |
| adenosina (sono) | acumula acordado; descanso zera | piso da temperatura cresce com m — **predição registrada: amplitude evolui → 0** (canal sem fechamento de laço; a morte dele É o teste de pressão-sem-tensão) |

**5-HT CORTADO** (achado crítico: modulava serviço-vs-entrega, que `serv_need`
já expressa — era o braço `corpo` de novo; e "γ/paciência" não existe numa
política de 1 passo sem função valor).

### 4.3 Decisão estocástica — pré-requisito técnico
`escolha ~ softmax(score/T)` via Gumbel-argmax. **T=0 = argmax literal por
máscara** (sem divisão — sem NaN). **Gerador de RNG SEPARADO do gsim do mundo**
(senão braço estocástico dessincroniza o mundo e o portão G0 falha espúrio).
ODEs de reserva atualizam em `atualizar()`, fora do grafo compilado (contrato
de perf do lab.py).

### 4.4 Genoma e evolução
46 params endócrinos (4×10 gatilhos + amplitudes + T₀). Mutação POR BLOCO
(σ próprio núcleo vs endócrino) — mutação global penaliza o braço com mais
dims vivas (√dims). **Semeadura**: metade da população parte do núcleo reativo
campeão da bateria base + endócrino aleatório (senão amplitudes→0 antes do
gatilho alinhar — vale de fitness, revisor §5.2). Concluir negativo SÓ com
curva de fitness em platô (06 §9).

## 5-pre. Direção do Leonardo (2026-08-31, incorporada): CASA, PICO e CARGA MENTAL

Pedido em linguagem dele: *"horário de pico como horário de trabalho, criar
residência pra ir pra casa e descansar renova as baterias, como uma carga
mental e o táxi é só um corpo usado; no descanso ele se recupera, ajusta a
neuromodulação; o foco é a eficiência do modelo e como os pesos se alocam."*

Mapeamento no design (e por que isso CONSERTA um furo da revisão):

- **Casa**: cada mundo ganha um nó `casa` (sorteado). Só em casa o descanso é
  PROFUNDO: recupera carga mental; o `descanso` de rua continua só baixando
  fadiga. Ir pra casa custa corridas perdidas + combustível — **moeda cruzada
  de verdade** (a limitação declarada no §3 morre aqui: proteção custa em
  moeda diferente).
- **Carga mental** (novo recurso do corpo): esgota com trabalho contínuo
  (déficit lento, tipo adenosina); baixa carga → piso de RUÍDO na decisão
  sobe (erra a escolha). Dormir em casa zera. Isso **fecha o laço da
  adenosina** que o revisor apontou como canal morto (§3.2 da revisão): agora
  existe um caminho causal carga↓ → decisão pior → ir pra casa paga → canal
  selecionável.
- **Horário de pico**: relógio oculto do dia (fase aleatória por mundo);
  pico manhã/tarde = 2-3× passageiros. Trabalhar no pico e descansar no vale
  é a política ótima — mas o relógio é OCULTO: o ser precisa inferir a hora
  pela taxa interna de encontros (interocepção), que é exatamente o que os
  gatilhos hormonais leem. Decisão de TIMING é acionável em 1 salto (ir pra
  casa / trabalhar) — ao contrário do desvio de rota do `ruas`, que morreu
  por ser inacionável (ver PREDICOES §ruas).
- **Eficiência/alocação de pesos**: κ_m (§7-8) + paisagem f(w) por braço +
  M2/M5 — a pergunta "como os pesos se alocam" é respondida pela curvatura
  da paisagem e pela lesão por canal.
- **Cidades maiores**: flag `--n-cidade` implementada (26→52+); entra como
  eixo secundário depois do G2 (mundo maior = rotas longas = pico/casa mais
  caros de alcançar — aumenta o teto do timing).

O mundo `turnos` abaixo é SUBSTITUÍDO por este mundo `cidade` (pico+casa+
carga mental) no G2 em diante; o contraste dia/noite vira o pico/vale.

## 5. Mundo `turnos`

- Regime oculto dia/noite, **período 150** (≥4 ciclos em T_evo=600), **fase
  inicial aleatória por mundo** (senão gatilho vira relógio de contagem).
- **Visão raio-limitada** (obrigatório — com visão global a densidade é
  observável e o teorema do MDP observável mata tudo, 05 §7).
- dia: 2× passageiros; noite: 0.5× passageiros, risco de avaria ×2.
- **Tarifa SEM contraste determinístico** (revisor: tarifa ×0.8/×1.6 tornava
  UMA entrega diagnóstica do regime → gatilho instantâneo basta, canal lento
  vira decoração). Ruído de tarifa por corrida > gap entre regimes: cada
  observação individualmente fraca (02 §7 condição 3).
- Perito recalibrado para turnos ANTES do G2 (perito do base pode reprovar o
  mundo injustamente).

## 6. Escada de braços (G3 — decompõe os 4 mecanismos; era o furo central)

```
① reativo (argmax)                       baseline
② + T fixa evoluída (softmax)            valor da ESTOCASTICIDADE
③ + interações INSTANTÂNEAS σ(w·φ)×feat  valor da EXPRESSIVIDADE bilinear
④ + φ com EMAs lentas (estado, s/ reserva) valor do ESTADO LENTO
⑤ endócrino completo (reserva/burnout)    valor da DINÂMICA HORMONAL EM SI
⑥ endócrino-CEGO (φ embaralhado)          controle G=0 (esperado: PIORA, cf. −21% Universe)
⑦ ORÁCULO-modulado (m = regime verdadeiro) teto REALIZÁVEL da parametrização
```

⑤≈③ ⇒ "interação paga, hormônio não" — resultado igualmente registrável (I6).
⑦ é o teto justo: gap do especialista (G2) é teto frouxo por cima.

## 7. Gates

- **G0 identidade**: todos os braços com amplitudes=0 e T=0 ≡ reativo, spread
  0.000 (portão de 7 braços).
- **G1 fórmula** — EXECUTADO 2026-08-31 (`src/g_formula.py`): P(K) ≡ simulação
  real de EMA em OU (K* e MSE, 3 pontos); persistência do exp08 reproduzida
  EXATA (21.2%, τ*=[2.8,1.2]); linhas de ruído só qualitativas (exp08 não
  documenta σ_s²/ρ₀/R₀; base registrada: 1/0.9/0.1). **Papel rebaixado pela
  revisão: G da filtragem NÃO transfere para decisão ("G não traduz",
  Universe: prometeu 24.2%, entregou 0.94%). G teórico = sanidade matemática,
  nada mais. O teto que vale é o G2 empírico + braço ⑦.**
- **G2 teto empírico + teste de PODER**: especialistas por regime (teto frouxo)
  + oráculo ⑦ (teto justo). Prosseguir SÓ se: ganho do oráculo ≥ 1.5× o desvio
  entre sementes E gap do especialista ≥ 2× o desvio. Senão: engrossar
  contraste do mundo e repetir — não prosseguir no escuro.
- **G3 escada** (§6) com ablação estática ANTES da evolução (§7.1).
- **G4 bateria**: **5 sementes** × R=8 (R maior nos braços estocásticos —
  winner's curse: elite truncada sobre avaliação ruidosa seleciona ruído, Lei
  do Garimpo; olhar treino-vs-teste POR braço), predições registradas antes.

### 7.1 Ablação estática (06 §10 passo 2 — faltava)
m fixo exógeno em níveis {0, .25, .5, 1, 2, 4} sem evolução, medir fitness →
curva U invertido REAL (amplitude evoluída não desenha U; só varredura desenha)
e separa "arquitetura não explora o teto" de "evolução não achou".

## 8. Fitness (fechado, sem ambiguidade)

```
fit = Σ_t∈[0,T] entregas_t − 0.3·avarias_t − κ_m·(1/T)·Σ_t m_total_t
morte no passo t*: entregas/avarias congelam, m conta como m_t* até T
```
κ_m ∈ {0, 0.01, 0.05} → curva custo×competência (E4: preço desloca ótimo;
κ_m=0 é o controle).

## 9. Métricas (06 §7 / 07 §8 — faltavam)

| métrica | pergunta |
|---|---|
| M2 variância do genoma endócrino entre sementes | selecionado ou deriva? |
| M3 **info mútua m ↔ regime oculto** | o hormônio INFERE o regime? (sem isso, vitória de ⑤ é ininterpretável) |
| M5 lesão por canal (zerar um, medir) | atribuição por canal |
| trajetórias inspecionadas (rodar.py `trajetoria`) | reward-hacking? (07 §11) |
| curvas de convergência por braço | platô? (senão "não achou" ≠ "não ajuda") |

## 10. Critério de parada da linha inteira (faltava)

Se no G4: ⑤ ≤ ③ (hormônio não adiciona a interação) **E** ⑦ ≤ ② + ruído
(nem o oráculo paga nesta parametrização) ⇒ encerrar a linha endócrina no
táxi, documentar no 05, voltar para porta de escrita (v3) — não iterar mundo
atrás de p-valor.

## 11. Registro da revisão adversarial (2026-08-31)

Críticos acatados: escada não separava mecanismos (→ braços ③④⑦); 3 sementes
violava I4 (→5); τ's não cabiam em T_evo (→ EMA 50, período 150, reserva
comprimida no ⑤ com 4.6·τ ≤ T); G=19.1% era número emprestado de filtragem
(→ rebaixado; teto = G2+⑦); 5-HT duplicava serv_need (→ cortado). Médios
acatados: RNG separado, T=0 mascarado, adenosina como predição-de-morte,
mutação por bloco, semeadura, poder estatístico no G2, M3/M5, ablação
estática, fitness fechado, perito recalibrado, fase aleatória, tarifa
ruidosa. Efeito realizável esperado (histórico Universe: 4–23% do teto):
com teto empírico X%, esperar 0.04X–0.23X — dimensionar poder para isso.

## 12. Cronograma

| fase | entrega | gate |
|---|---|---|
| F0 | `g_formula.py` ✅ | G1 ✅ (papel rebaixado) |
| F1 | mundo `turnos` + perito recalibrado + especialistas + oráculo ⑦ | G2 (poder) |
| F2 | decisão estocástica + canais + G0 de 7 braços | G0 |
| F3 | ablação estática + mini-bateria local + PREDICOES-V2.md | §7.1 |
| F4 | bateria Colab 5 sementes × {base, turnos} × κ_m | G4 |
