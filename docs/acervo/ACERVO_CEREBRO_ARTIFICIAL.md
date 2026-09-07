# ACERVO DE CONTEXTO — Arquitetura Cognitiva Bio-Inspirada
### Neurociência computacional · Plasticidade e seleção · Evolução e comportamento · CS/Matemática · Diagnóstico das ideias do time

> Uso: colar/referenciar em `CLAUDE.md` do projeto. Cada seção tem: o fato biológico → o modelo computacional → o análogo em ML → o que isso implica para a nossa arquitetura. Marcadores: **[R]** resultado reportado na literatura · **[E]** estimativa/opinião · **[?]** controverso/evidência fraca.
> Data de compilação: set/2026. Clássicos são estáveis; itens 2025–2026 estão marcados.

---

## 0. Sumário executivo

1. **A descoberta empírica do time — "neurônios são alocados por necessidade e depois o cérebro seleciona" — é o princípio mais bem estabelecido do neurodesenvolvimento**: *superprodução → competição dependente de atividade → estabilização seletiva / eliminação*. Nomes: Theory of Neuronal Group Selection / Neural Darwinism (Edelman 1987), Estabilização Seletiva de Sinapses (Changeux & Danchin 1976), poda sináptica do desenvolvimento (Huttenlocher 1979; Rakic 1986), alocação de engramas por excitabilidade (Josselyn & Frankland). Em ML o análogo direto é **Dynamic Sparse Training** (SET 2018, RigL 2020: grow-by-gradient / prune-by-magnitude), a **Lottery Ticket Hypothesis** (Frankle & Carbin 2019) e **"train large, then compress"** (Li et al. 2020). Você não inventou o princípio; a novidade possível está em **como** aloca (sob demanda, guiado por sinal de necessidade/surpresa, em rede stateful contínua) — ver §5.

2. **O cérebro é uma máquina de roteamento e gating multi-escala, não um MLP grande.** Tálamo = roteador/gate contextual; PFC = controlador hierárquico com gating dopaminérgico; hipocampo = memória episódica rápida com pattern separation; gânglios da base = seleção de ação por RPE; cerebelo = forward models esparsos; neuromoduladores = sinais globais de incerteza/ganho que reescrevem parâmetros efetivos. Cada um tem modelo computacional maduro (PBWM, CLS, TEM, TD-learning, Marr-Albus, adaptive gain) — §1.

3. **O estado da arte de ML convergiu (2024–2026) para exatamente os temas do time**: memória que aprende em tempo de teste (Titans, jan/2025), memória multi-frequência (Nested Learning / HOPE, NeurIPS 2025), MoE com roteamento esparso e balanceamento sem loss auxiliar (DeepSeek-V3), redes contínuas CfC/LTC (Hasani/Lechner) em produção (Liquid AI), híbridos SSM+attention (Hymba, Jamba). Isso é bom (validação de direção) e ruim (competição) — §4 e §5.

4. **Onde a evidência é fraca**: plausibilidade biológica de backprop **[?]**, Free Energy Principle como teoria testável **[?]**, IIT **[?]**, benefício de SNNs fora de hardware neuromórfico **[?]**, e — crucial — **arquiteturas "cérebro completo" (Spaun, Leabra, ACT-R, HTM) nunca escalaram para competir com deep learning em tarefas abertas**. A lição histórica é: módulos bio-inspirados vencem quando **um** princípio é isolado e escalado (attention, sparsity, replay), e perdem quando se tenta copiar a anatomia inteira — §6.

5. **Recomendação central [E]**: tratar a anatomia como *fonte de hipóteses de design*, não como *especificação*. Priorizar os componentes com melhor razão evidência/risco (§9): (a) memória episódica externa com replay (CLS); (b) roteamento esparso top-k com balanceamento; (c) multi-timescale explícito (constantes de tempo hierárquicas / CMS); (d) neuromodulação como modulação de ganho/LR; (e) grow-then-prune com sinal de necessidade. Medir sempre contra um baseline Transformer/Mamba de mesmo FLOPs.

---

## 1. Mapa: estrutura cerebral → função → modelo computacional → análogo ML → implicação

| Estrutura | Função computacional | Modelo canônico | Análogo em ML | Implicação p/ nossa arquitetura |
|---|---|---|---|---|
| **Tálamo** (relé de 1ª ordem + núcleos de ordem superior: pulvinar, MD; núcleo reticular TRN) | Único portão de entrada sensorial ao córtex; **gating atencional** (TRN = "spotlight" de Crick 1984); loops tálamo-corticais; MD como **controlador de contexto** que seleciona qual rede cortical PFC está ativa (Halassa, Nature 2017/2020); pulvinar sincroniza áreas corticais (Saalmann 2012) | Sherman & Guillery: drivers vs moduladores; Wang & Halassa 2021 (arXiv 2104.01474): tálamo resolve credit assignment contextual; modelos de inibição seletiva (McCreesh & Cortés 2022) | Router de MoE; gating multiplicativo; attention bottleneck; "difference engine" entre predição e input (CTNN, Remmelzwaal 2019) | O tálamo **não armazena**; ele **seleciona e amplifica**. Nosso roteador stateful = tálamo. Regra de design: roteador com pouca capacidade de memória própria, alta capacidade de gating; sinal de contexto vindo do PFC (top-down). |
| **Córtex pré-frontal** (dlPFC, vmPFC, OFC, ACC) | Working memory ativa (persistent activity), controle executivo, seleção de regra/tarefa, meta-aprendizado, hierarquia **rostro-caudal** (regras abstratas → concretas; Badre 2008, Koechlin 2003) | **PBWM** (O'Reilly & Frank 2006): dopamina dos gânglios da base atua como *gate* de atualização da WM (equivalente a LSTM gates aprendidos por RL); **PFC como meta-RL** (Wang et al., Nat Neurosci 2018): RNN pré-frontal aprende algoritmo de RL nas ativações, dopamina treina os pesos lentamente | Gated RNN/LSTM, controladores hierárquicos (Options, FeUdal Networks), meta-RL (RL², MAML), "slow weights treinam fast dynamics" | Controle hierárquico multi-timescale do time = hierarquia rostro-caudal. Regra: níveis mais abstratos atualizam mais devagar e enviam *contexto*, não *conteúdo*. |
| **Hipocampo** (DG → CA3 → CA1; córtex entorrinal) | Memória episódica one-shot; **pattern separation** (giro dentado, ~1–2% ativo, expansão 1:5–10 do EC); **pattern completion** (CA3 recorrente = autoassociador); place/grid cells; **replay** durante sono/repouso; consolidação para neocórtex | **CLS** (McClelland, McNaughton & O'Reilly 1995): hipocampo = aprendizado rápido/esparso, neocórtex = lento/distribuído; replay intercalado evita esquecimento catastrófico. **TEM** (Whittington 2020): fatoriza estrutura (grid) × conteúdo. **Successor Representation** (Stachenfeld 2017): place cells = SR, grid = autovetores. Hopfield para CA3 | Memória externa (NTM/DNC), retrieval (RETRO, RAG), **Hopfield moderno** (Ramsauer 2020), experience replay, episodic control (Blundell 2016, NEC), Titans (memória neural em tempo de teste) | Nosso módulo hipocampal deve ser: escrita one-shot esparsa, leitura por completação, e um **processo offline de replay** que treina os módulos lentos. Sem replay, CLS não funciona. |
| **Gânglios da base + dopamina (VTA/SNc)** | Seleção de ação (desinibição), aprendizado por reforço; dopamina fásica = **RPE** (Schultz, Dayan & Montague 1997); codificação distribucional (Dabney et al., Nature 2020) | TD-learning; actor-critic (striatum = crítico/ator, D1 go / D2 no-go, Frank 2005); distributional RL | RL, actor-critic, gating aprendido por RL (PBWM) | O sinal que **gate**ia o PFC e que **modula** plasticidade (3-factor) vem daqui. Em ML: um crítico que emite RPE usado como fator de modulação de aprendizado e de roteamento. |
| **Cerebelo** | Forward models / predição sensório-motora, aprendizado supervisionado por erro (fibras trepadeiras), timing sub-segundo | **Marr-Albus-Ito**: expansão esparsa (células granulares ~50 bilhões, 4 entradas cada) + aprendizado no Purkinje; Kawato: modelos internos | Expansão esparsa aleatória + readout linear (reservoir/ELM), modelos de mundo locais | Padrão "expansão aleatória esparsa + readout treinado" é barato e robusto para predição de erro; ótimo para o readout assíncrono. |
| **Neuromodulação** (DA, 5-HT, NA/locus coeruleus, ACh) | Sinais **globais, lentos, de baixa dimensão** que mudam ganho, LR, exploração e constantes de tempo de circuitos inteiros | **Doya 2002** "Metalearning and neuromodulation": DA = TD error, 5-HT = fator de desconto γ, NA = temperatura/exploração (β), ACh = learning rate α. **Yu & Dayan 2005**: ACh = incerteza esperada, NA = incerteza inesperada. **Aston-Jones & Cohen 2005**: LC adaptive gain (fásico = exploit, tônico = explore) | Hypernetworks, FiLM/conditional scaling, temperatura adaptativa, LR adaptativo por surpresa, modulação de ganho (gain = 1/σ) | **Neuromodulação como transformação de parâmetro** do time = exatamente Doya/hypernetwork. Regra: poucos escalares globais (4–8), atualizados lentamente, que reescalam ganho/LR/γ/temperatura de módulos. Não faça o modulador emitir vetores grandes. |
| **Coluna cortical / microcircuito canônico** | Unidade repetida (~100 µm minicoluna, ~10⁴ neurônios); camadas: L4 entrada, L2/3 feedforward, L5/6 feedback e saída subcortical | **Predictive coding** (Rao & Ballard 1999; Bastos 2012 canonical microcircuit): erros sobem (gamma), predições descem (beta/alpha). **Thousand Brains** (Hawkins 2019): cada coluna aprende modelos completos com reference frames, voto entre colunas | Autoencoders hierárquicos com erro de predição, PC networks (Millidge, Song 2020), Perceiver/RIMs como colunas independentes que votam | Se usarmos módulos repetidos, dê a cada um seu próprio erro de predição local (loss local) — isso é o que permite treino sem backprop global e assincronia. |
| **Oscilações / sincronia** (theta 4–8 Hz, gamma 30–90 Hz, alpha/beta) | Multiplexação temporal, binding, **communication through coherence** (Fries 2005), theta-gamma coupling como "slots" de WM (Lisman & Jensen 2013) | Osciladores acoplados (Kuramoto), binding por sincronia (von der Malsburg) | Phase-coded routing (pouco explorado), positional encodings rotacionais, clocks multi-frequência | Sincronia é a solução biológica para *readout assíncrono*: módulos "publicam" em fases. Vale como inspiração para o clock hierárquico do time. |
| **Global Workspace** | Broadcast serial de conteúdo selecionado para todos os módulos (Baars 1988; Dehaene & Changeux) | Global Neuronal Workspace; **Global Latent Workspace** (VanRullen & Kanai 2021): espaço latente compartilhado com tradução entre módulos | **Goyal & Bengio "Coordination among neural modules through a shared global workspace"** (ICLR 2022): RIMs + workspace limitado; Perceiver (latent bottleneck) | O gargalo (workspace pequeno, competição para escrever) é o que dá generalização composicional. Nosso "tálamo" pode ser fisicamente esse workspace. |
| **Multi-timescale intrínseco** | Constantes de tempo neuronais crescem com a hierarquia (sensorial ~50–100 ms → PFC ~300+ ms; Murray et al., Nat Neurosci 2014); janelas de integração temporal aninhadas (Hasson 2008) | Redes com τ heterogêneo; **LTC/CfC** (Hasani 2021; Hasani & Lechner 2022, Nat Mach Intell): τ dependente do input; NCP (Lechner 2020) | SSMs (S4/Mamba com decaimentos por canal), CMS do Nested Learning (2025), hierarchical RNNs (Clockwork RNN, Koutník 2014) | Já é o núcleo do time. Ver §5 para posicionamento. |

---

## 2. Desenvolvimento, plasticidade, seleção e alocação — contexto da descoberta

### 2.1 Fatos biológicos [R]
- **Superprodução**: o cérebro fetal produz ~2× os neurônios que sobrevivem; ~50% morrem por apoptose (competição por fatores neurotróficos — hipótese neurotrófica, Levi-Montalcini/Oppenheim). Sinapses: pico em ~1–2 anos no córtex visual, ~3–5 anos no PFC; **perda de ~40–50% até a adolescência** (Huttenlocher 1979, 1990; Rakic 1986 "concurrent overproduction").
- **Seleção por atividade**: "neurons that fire together wire together" (Hebb 1949) + "out of sync, lose your link"; **Changeux & Danchin 1976** "estabilização seletiva" — a atividade *estabiliza* sinapses existentes, não cria as corretas. **Edelman 1987 (TNGS)**: repertório primário (genético, superproduzido) → repertório secundário (selecionado por experiência) → reentrada (loops recíprocos) para integração. Períodos críticos são janelas de alta plasticidade fechadas por maturação de interneurônios PV e freios moleculares (Hensch 2005).
- **Alocação de engramas**: neurônios com maior excitabilidade/CREB no momento do evento **vencem a competição** e são recrutados (Han et al. 2007; Josselyn & Frankland 2015; "memory allocation" review, Nat Rev Neurosci). Alocação é **competitiva e probabilística**, não endereçada; engramas de eventos próximos no tempo se sobrepõem (linking).
- **Neurogênese adulta** (giro dentado): neurônios novos são hiperplásticos, recrutados por aprendizado; os não integrados morrem; neurogênese alta **facilita esquecimento** de memórias antigas (Akers et al., Science 2014) — trade-off estabilidade/plasticidade literal.
- **Homeostase**: escala sináptica multiplicativa mantém taxa de disparo alvo (Turrigiano 1998); metaplasticidade (Abraham & Bear) — a história de atividade muda o limiar de plasticidade (BCM).

### 2.2 Regras de plasticidade (fórmulas)
- **Hebb**: Δw_ij = η · x_i · y_j (instável sem normalização).
- **Oja** (Hebb normalizado → PCA): Δw = η · y · (x − y·w).
- **BCM** (Bienenstock, Cooper & Munro 1982): Δw = η · x · y · (y − θ_M), θ_M = ⟨y²⟩ (limiar deslizante → estabilidade + seletividade).
- **STDP** (Bi & Poo 1998): Δw = A₊·exp(−Δt/τ₊) se pré antes de pós (Δt>0); −A₋·exp(Δt/τ₋) caso contrário. τ ≈ 20 ms.
- **Homeostase / synaptic scaling**: w_i ← w_i · (r_target / ⟨r⟩)^κ, aplicado lentamente (horas).
- **Three-factor rule** (Frémaux & Gerstner 2016; Gerstner et al. 2018): 
  de_ij/dt = −e_ij/τ_e + f(pré_i, pós_j)  [eligibility trace, Hebbiano]
  Δw_ij = η · M(t) · e_ij  [M = neuromodulador: RPE, surpresa, novidade]
  → o traço local "propõe", o sinal global "aprova". **Isso é a ponte formal entre Hebb e RL** e a base biológica do seu "alocar, depois selecionar" no nível sináptico.
- **e-prop** (Bellec et al., Nat Commun 2020): aproximação de BPTT em SNNs recorrentes com traços de elegibilidade locais + sinal de aprendizado top-down; desempenho próximo de BPTT em TIMIT/Atari. Estrutura idêntica à 3-factor.
- **Deep Rewiring** (Bellec, Kappel, Maass 2018): pesos como variáveis com sinal; conexões negativas são "dormentes", re-sorteadas aleatoriamente → plasticidade estrutural como amostragem Bayesiana (Kappel 2015 "synaptic sampling").

### 2.3 Análogos em ML e o que a evidência diz sobre "overprovision → prune"
| Método | Mecanismo | Evidência [R] |
|---|---|---|
| **Lottery Ticket** (Frankle & Carbin 2019) | Rede densa contém sub-rede esparsa que treina até a mesma acurácia *se* iniciada nos pesos originais | Vale para redes pequenas; para grandes, precisa "rewind" para iteração k>0 (Frankle 2020). Treinar a sub-rede do zero com init aleatória **falha** → o supertreino faz a seleção. |
| **SET** (Mocanu, Nat Commun 2018) | Poda por magnitude + regrowth aleatório a cada época, esparsidade fixa | Iguala denso em MLPs/CNNs com 1–10% dos pesos. |
| **RigL** (Evci et al., ICML 2020) | Poda por magnitude + **regrowth por gradiente** (conexões com maior |∂L/∂w| entre as inativas) | Iguala/supera denso em ImageNet a 80–90% esparsidade com mesmo FLOPs de treino; supera SET e static sparse. **Análogo direto de "alocar por necessidade (gradiente) e depois selecionar (magnitude)".** |
| **MEST / Top-KAST / GraNet** | Variações (grow by momentum, gradual pruning durante treino) | Marginalmente melhores em cenários específicos. |
| **"Train large, then compress"** (Li, Wallace et al., ICML 2020) | Para orçamento fixo de compute, treinar modelo maior por menos passos e podar/quantizar supera treinar modelo pequeno até convergir | Confirmado em Transformers de NLP. Minitron (NVIDIA 2024) confirma em LLMs 8–15B. |
| **Progressive Nets** (Rusu 2016), **DEN** (Yoon 2018), **PackNet**, **CPG** | Continual learning por expansão de capacidade + congelamento/poda | Zero esquecimento, mas capacidade cresce linearmente com tarefas — "alocar sob demanda" sem "selecionar" explode. |
| **Neurogenesis Deep Learning** (Draelos et al. 2017) | Adiciona neurônios quando erro de reconstrução sobe; replay intrínseco | Prova de conceito em MNIST; não escalou. |
| **DPAP** (Han, Shen, Zeng et al., TPAMI 2024) | Poda adaptativa inspirada em espinhas dendríticas: "use it or lose it, gradually decay", sem pré-treino/retreino, em ANNs e SNNs | Compressão extrema com desempenho mantido em benchmarks pequenos/neuromórficos. |
| **Growing via gradient descent** (Radhakrishnan et al., Proc R Soc A, jul/2025) | Tamanho da rede como variável otimizada pelo mesmo GD (peso auxiliar ou máscara de controlador) | Redes pequenas crescem até o necessário; escala não demonstrada. |
| **Growth/prune alternado em neuroevolução** (Singh, Lyu, Desell, EvoApps 2026) | Fases alternadas de crescimento e poda em EXAMM | Melhora a busca de arquiteturas RNN em séries temporais. |
| **MoE expert allocation** | Roteador aloca tokens a experts; risco de *routing collapse* (poucos experts dominam) | Soluções: aux load-balancing loss (Switch, Fedus 2021), noisy top-k (Shazeer 2017), expert-choice routing (Zhou 2022), **auxiliary-loss-free balancing por bias dinâmico** (DeepSeek-V3, 2024), capacity factor, z-loss. |

**Conclusão [R+E]**: "overprovision → select" é comprovadamente superior a "treinar no tamanho final" **quando há sinal de seleção informativo (gradiente/atividade/magnitude) e um período de treino/consolidação após a seleção**. Seleção sem retreino degrada (Minitron, pruning one-shot). O ponto genuinamente aberto — e onde o time pode contribuir — é **alocação *online* guiada por necessidade (surpresa/erro/incerteza) em redes stateful de tempo contínuo**, com seleção posterior por uso, sem ciclos de treino separados. Isso está pouco explorado além de DEN/Draelos/DPAP, todos em escala pequena.

---

## 3. Evolução e comportamento

### 3.1 Evolução do cérebro [R]
- **Custo energético** (Attwell & Laughlin 2001; Lennie 2003): cérebro humano ~20 W, 2% da massa, 20% do metabolismo basal; sinalização (potenciais de ação + sinapses) consome a maior parte. Lennie: o orçamento permite **≈1% dos neurônios corticais ativos a qualquer instante** → esparsidade de ativação é imposição energética, não escolha. Levy & Baxter 1996: código ótimo energeticamente é esparso (fração de ativação ~ 1–10%).
- **Expensive tissue hypothesis** (Aiello & Wheeler 1995): cérebro grande trocado por intestino menor/dieta rica. **Social brain** (Dunbar 1992): tamanho do neocórtex ∝ tamanho do grupo **[?]** (correlação contestada).
- **Herculano-Houzel**: leis de escala neuronal diferem por ordem; primatas escalam linearmente (neurônios ∝ massa) — humanos têm ~86 bilhões de neurônios, ~16 bi no córtex, ~69 bi no cerebelo. Densidade importa mais que massa.
- **Neocórtex como módulo repetido** (Mountcastle 1978): a mesma coluna canônica replicada; evolução por **duplicação e divergência** de áreas (exaptação) — argumento para arquiteturas com módulos idênticos especializados por dados (MoE, colunas).
- **Inteligência com cérebros pequenos**: abelha (~1 M neurônios) aprende conceitos abstratos (igual/diferente); *Drosophila* (~140k neurônios) — **conectoma completo FlyWire (Nature, out/2024)**, permitindo modelos que preveem comportamento a partir da conectividade (Shiu et al. 2024); polvo (~500 M, 2/3 nos braços — controle distribuído); corvídeos rivalizam primatas com pallium denso. **Lição**: capacidade cognitiva depende de arquitetura e densidade, não só de contagem de parâmetros.
- **Evolução como meta-aprendizado**: genoma (~GB) não codifica sinapses (~10¹⁴); codifica *regras de desenvolvimento e plasticidade* — "genomic bottleneck" (Zador 2019). Argumento forte para: aprender regras de plasticidade/crescimento, não pesos (Najarro & Risi 2020 "Meta-learning through Hebbian plasticity in random networks"; Pedersen & Risi 2021; NCA de Mordvintsev 2020; HyperNCA, Najarro 2022).

### 3.2 Comportamento e cognição [R]/[?]
- **Inato vs aprendido**: core knowledge (Spelke): objetos, agentes, número, espaço — priors que aparecem antes da experiência. "Child as hacker" (Rule, Tenenbaum, Piantadosi 2020): aprendizado como síntese de programas.
- **Curiosidade intrínseca**: recompensa = erro de predição (Schmidhuber 1991), **progresso de aprendizado** (Oudeyer 2007 — mais robusto: evita "noisy TV"), ICM (Pathak 2017), RND (Burda 2018). Para o time: **progresso de aprendizado é também o melhor sinal de "necessidade" para alocar capacidade** [E].
- **Homeostase/alostase** (Sterling 2012): o cérebro regula *antecipadamente*; emoções como estados neuromodulatórios que reconfiguram políticas (Damasio somatic marker; LeDoux). Em ML: drives internos como variáveis de estado que modulam recompensa e ganho.
- **Cérebro bayesiano / inferência ativa / Free Energy Principle** (Friston 2010) **[?]**: unifica percepção e ação como minimização de surpresa variacional. Predictive coding é bem suportado; FEP como *teoria* é criticado por ser não-falseável (Colombo & Wright 2021) e por resultados empíricos mistos. Use predictive coding, cite FEP com cautela.
- **Dual process** (Kahneman): System 1 rápido/paralelo, System 2 lento/serial. Bengio "consciousness prior" (2017) e "System 2 deep learning" (NeurIPS 2019): gargalo de atenção de baixa dimensão sobre variáveis esparsas e composicionais → GFlowNets, RIMs. Nosso workspace/tálamo é System 2.
- **Períodos críticos** (Hensch 2005): plasticidade alta cedo, fechamento por maturação inibitória. Em ML: **critical learning periods em redes profundas** (Achille, Rovere, Soatto, ICLR 2019) — déficits no início do treino são permanentes; a "informação de Fisher" cresce e depois cai. Argumento para agendar alocação (crescimento) cedo e seleção (poda) depois.

### 3.3 Evolução computacional [R]
- **Neuroevolução**: NEAT (Stanley 2002 — cresce topologia, speciation protege inovação; *alocar por necessidade* em nível de grafo), HyperNEAT (codificação indireta via CPPN), OpenAI-ES (Salimans 2017 — competitivo com RL em Atari/MuJoCo com paralelismo massivo), CMA-ES (padrão para ≤10³ parâmetros).
- **Quality-Diversity**: MAP-Elites (Mouret & Clune 2015), POET (Wang, Lehman, Clune, Stanley 2019 — co-evolução de ambientes e agentes, open-endedness). Evolução de regras de plasticidade (Soltoggio, Stanley, Risi 2018 review; Najarro & Risi 2020: rede com pesos aleatórios + regras Hebbianas evoluídas resolve quadrúpede com dano).
- **NCA** (Mordvintsev 2020): desenvolvimento como regra local iterada; auto-reparo. **HyperNCA** (Najarro 2022): NCA cresce os pesos de uma rede de política.
- **Lição**: evolução é boa para *descobrir regras* (plasticidade, crescimento, topologia) e ruim para *otimizar pesos* em escala. Use ES/QD para meta-parâmetros do seu sistema (τ, regras de alocação, limiares de poda), GD para pesos.

---

## 4. CS e matemática fundamentais (com fórmulas)

### 4.1 Informação e inferência
- **Information Bottleneck** (Tishby 1999; Tishby & Zaslavsky 2015): min_p(t|x) I(X;T) − β·I(T;Y). Representações boas comprimem X mantendo Y. Controverso como explicação de deep learning (Saxe et al. 2018) **[?]**, mas útil como objetivo de design para o workspace/gargalo.
- **Rate-distortion, MDL, Kolmogorov, Solomonoff/AIXI** (Hutter): inteligência = compressão + previsão; base teórica para "surpresa" como sinal.
- **ELBO / free energy variacional**: F = E_q[log q(z) − log p(x,z)] ≥ −log p(x). Predictive coding é descida de gradiente em F com Gaussianas (Bogacz 2017 tutorial).

### 4.2 Sistemas dinâmicos e memória associativa
- **Hopfield clássico**: E = −½ Σ w_ij s_i s_j; capacidade ≈ 0,14 N padrões.
- **Hopfield moderno / Dense Associative Memory** (Krotov & Hopfield 2016; **Ramsauer et al. 2020 "Hopfield Networks is All You Need"**): E(ξ) = −lse(β, Xᵀξ) + ½ξᵀξ + const; update ξ_new = X·softmax(β·Xᵀξ) ≡ **attention**; capacidade exponencial em d; convergência em 1 passo. → CA3 = Hopfield moderno; attention = recuperação associativa.
- **Neural ODE** (Chen 2018): dh/dt = f(h,t;θ). **LTC** (Hasani 2021): dh/dt = −[1/τ + f(h,x;θ)]·h + f(h,x;θ)·A — constante de tempo efetiva τ_sys = τ/(1+τ·f) depende do input (**isso é neuromodulação de τ**). **CfC** (Hasani & Lechner 2022): solução fechada aproximada h(t) = σ(−f(x,h)·t)⊙g(x,h) + [1−σ(−f·t)]⊙h(x,h) — sem solver ODE, 1–5 ordens de grandeza mais rápido; **NCP** (Lechner 2020): 19 neurônios dirigem carro com esparsidade conectômica de C. elegans.
- **Reservoir computing / echo state property** (Jaeger 2001; Maass LSM 2002): raio espectral ρ(W) < 1 para memória desvanecente; melhor computação perto de ρ≈1 (**edge of chaos**, Bertschinger & Natschläger 2004; Langton 1990). **Criticalidade neural** (Beggs & Plenz 2003: avalanches com expoente −3/2) **[?]** quanto à função.
- **Kuramoto**: dθ_i/dt = ω_i + (K/N)Σ sin(θ_j − θ_i) — sincronização emerge acima de K_c; modelo mínimo de binding/coherence.
- **Estabilidade**: para redes contínuas treinadas por BPTT, exploding/vanishing gradients ↔ autovalores do Jacobiano; LTC/CfC têm limites provados de estabilidade (τ_sys ∈ [τ/(1+τW_max), τ]).

### 4.3 Grafos, esparsidade e roteamento
- **Small-world** (Watts & Strogatz 1998): alto clustering + caminho curto; cérebros são small-world com **rich-club** de hubs (van den Heuvel & Sporns 2011) e módulos hierárquicos (Bullmore & Sporns 2009). Custo de fiação ~ 60% do volume; "wiring economy" prevê a organização.
- **Sparse coding** (Olshausen & Field 1996): min ||x − Da||² + λ||a||₁ → filtros tipo V1. **k-WTA** e **top-k gating** são aproximações duras.
- **MoE routing** (Shazeer 2017; Switch, Fedus 2021): g = softmax(top-k(W_r·x + ε)); loss auxiliar L_bal = α·N·Σ_i f_i·P_i (f = fração de tokens ao expert i, P = prob média). **DeepSeek-V3 (2024)**: sem loss auxiliar — bias b_i por expert somado ao score só para a *seleção*, ajustado ±γ conforme sobrecarga; evita o trade-off perda×balanceamento. **Expert-choice** (Zhou 2022): experts escolhem tokens (capacidade garantida). **Hash routing** (Roller 2021): determinístico, surpreendentemente competitivo — baseline obrigatório.
- **Routing collapse**: causas — feedback positivo (expert bom recebe mais dados, fica melhor), gradiente esparso para experts pouco usados. Diagnóstico: entropia da distribuição de uso, coeficiente de variação da carga.

### 4.4 Aprendizado
- **TD / RPE**: δ_t = r_t + γ·V(s_{t+1}) − V(s_t); ΔV(s_t) = α·δ_t. Dopamina fásica ≈ δ_t **[R, um dos resultados mais replicados da neurociência]**. Distributional (Dabney 2020): neurônios DA têm pontos de reversão distintos → codificam quantis.
- **Alternativas ao backprop** (todas [R] em escala pequena/média, [?] em escala LLM): feedback alignment (Lillicrap 2016; pesos de feedback aleatórios fixos funcionam em MLPs, falham em convnets profundas), target propagation, **predictive coding ≈ backprop** (Whittington & Bogacz 2017; Millidge, Song 2020/2022: PC com "fixed prediction assumption" reproduz gradientes exatos), **equilibrium propagation** (Scellier & Bengio 2017), **forward-forward** (Hinton 2022: goodness local por camada, positivo vs negativo — funciona em MNIST/CIFAR, não escalou), e-prop, local losses (Nøkland 2019). **Estado honesto**: nada substitui backprop em performance; PC e e-prop são os mais promissores para hardware/assincronia.
- **Meta-learning**: MAML (Finn 2017), learned optimizers (VeLO, Metz 2022). **Fast weights**: Schmidhuber 1992; Ba et al. 2016; **linear transformers = fast weight programmers** (Schlag, Irie, Schmidhuber 2021) — attention sem softmax é regra Hebbiana externa (W ← W + v·kᵀ). DeltaNet / Gated DeltaNet (2024) usam regra delta (Widrow-Hoff) → "Hopfield que aprende em tempo de teste".
- **Memória em tempo de teste (2025–2026)**: **Titans** (Behrouz et al., jan/2025, arXiv 2501.00663): memória = MLP profundo atualizado por GD em tempo de inferência com **surpresa** (gradiente da loss) e momentum + esquecimento adaptativo; >2M tokens de contexto; supera Mamba-2/Gated DeltaNet/Transformer++ em LM e BABILong [R]. Reimplementação independente (Di Nepi et al., out/2025, arXiv 2510.09551) confirma que o módulo de memória ajuda, mas o ganho geral **não é consistente** por causa do chunking [R]. **MIRAS** (Behrouz 2025): todo modelo de sequência = memória associativa com 4 escolhas (arquitetura da memória, viés atencional/loss, retenção, otimizador). **Nested Learning / HOPE** (Behrouz & Mirrokni, NeurIPS 2025, nov/2025): arquitetura = pilha de problemas de otimização aninhados com **frequências de atualização distintas**; **Continuum Memory System** substitui o FFN por módulos que atualizam em frequências diferentes (multi-timescale explícito); HOPE supera Transformers/Samba/Titans em LM, NIAH e continual learning [R, ainda em escala pequena/média].
- **Continual learning**: EWC (Kirkpatrick 2017: penalidade Fisher), Synaptic Intelligence (Zenke 2017), replay (gerativo ou buffer) continua sendo o mais robusto [R]; revisões 2024–2025 (Wang et al. TPAMI 2024) confirmam que **replay + expansão modular** dominam. "Modular Memory is the Key to Continual Learning Agents" (Dorovatas et al., mar/2026, arXiv 2603.01761, posição de 20+ autores da área): memória modular e separação de escalas temporais como caminho.
- **World models**: Ha & Schmidhuber 2018; **Dreamer v3** (Hafner 2023, Nature 2025): um conjunto de hiperparâmetros, 150+ tarefas, primeiro a coletar diamante no Minecraft sem dados humanos [R]. **JEPA** (LeCun 2022 "A Path Towards Autonomous Machine Intelligence"): arquitetura cognitiva com configurador, percepção, modelo de mundo, custo (intrínseco + treinado), ator, memória de curto prazo — **é o "cérebro modular" mais influente da década e mapeia 1:1 em anatomia** (configurador ≈ PFC/tálamo, custo intrínseco ≈ amígdala/hipotálamo, memória ≈ hipocampo). I-JEPA/V-JEPA 2 (2024–2025) são os únicos módulos realmente treinados.
- **Memória externa**: NTM (2014), DNC (Graves, Nature 2016 — endereçamento por conteúdo + temporal link matrix), Memorizing Transformers (2022, kNN sobre KV antigos), RETRO (2022), Recurrent Memory Transformer (Bulatov 2022–2024).

### 4.5 Neuromórfico / SNN [R]
- LIF: τ·dV/dt = −(V − V_rest) + R·I; spike se V>θ, reset. Treino: surrogate gradients (Neftci 2019), e-prop, ANN→SNN conversion.
- Hardware: Intel **Loihi 2** (Hala Point 2024: 1,15 bi neurônios, ~20 pJ/op sináptica), SpiNNaker2, IBM NorthPole. Vantagem energética real apenas com **esparsidade temporal alta e hardware event-driven**; em GPU, SNNs são mais lentas e menos precisas que ANNs equivalentes **[R]**. **Recomendação [E]**: não usar spikes na arquitetura principal; usar *esparsidade de ativação* e *eventos* (readout assíncrono) que capturam o benefício sem o custo de treino.

### 4.6 Escala e leis
- Scaling laws (Kaplan 2020; **Chinchilla** Hoffmann 2022: tokens ≈ 20× parâmetros). **Bitter lesson** (Sutton 2019): métodos gerais que escalam com compute vencem priors humanos. **Contra-evidência 2024–2026**: priors *estruturais* que também escalam (attention é um prior; esparsidade MoE é um prior; multi-timescale em SSMs é um prior) venceram; priors *rígidos* (anatomia fixa, regras Hebbianas puras) perderam. **Um resultado de jun/2026 [R]**: RNNs inicializadas com conectividade e geometria cortical real do MICrONS (~12k neurônios do córtex visual de camundongo, Shakiba et al., arXiv 2606.14975) superam baselines em 3 tarefas de decisão — priors conectômicos ajudam em escala pequena. Escala grande: aberto.
- Leis de potência em cérebros: número de neurônios ∝ massa^(1,0) em primatas, ^(0,6–0,7) em roedores (Herculano-Houzel); comprimento total de axônios cresce mais devagar que neurônios → **esparsidade de conectividade cresce com escala** (cada neurônio ~10⁴ sinapses independente do tamanho do cérebro) — argumento para *esparsidade de conexão fixa por unidade*, como em NCP/RigL.

---

## 5. Diagnóstico das ideias do time

Formato: (1) já existe · (2) parcialmente novo · (3) aparenta inédito/pouco explorado · (4) resultados de trabalhos similares · (5) armadilhas.

### 5.1 Roteador esparso *stateful* baseado em CfC
1. **Existe**: MoE routers (stateless, por token) — Switch/Mixtral/DeepSeek. Roteadores com estado: **Mixture of Recurrent Experts**, SwitchHead, "MoE with recurrent gating" (poucos, pequenos). CfC/LTC como controlador (Hasani; Liquid AI LFMs 2024–2026 em produção como *backbone*, não como roteador). Tálamo como roteador contextual (Halassa; Wang & Halassa 2021) é a inspiração biológica explícita.
2. **Parcialmente novo**: usar uma rede de tempo contínuo com τ dependente do input **como o próprio roteador**, de modo que a decisão de roteamento tem memória e dinâmica própria (o "tálamo" mantém contexto entre tokens/eventos).
3. **Inédito/pouco explorado**: roteamento **em tempo contínuo com decisões assíncronas** (o roteador não decide a cada token, decide quando sua dinâmica cruza limiar) — não encontrei trabalho equivalente. Combinar isso com balanceamento de carga é território aberto.
4. **Resultados similares**: roteadores stateless funcionam em escala; roteadores com estado historicamente sofrem de **instabilidade** (o estado amplifica collapse). NCP/CfC mostram que 10–50 neurônios contínuos controlam bem sistemas de baixa dimensão — o roteador não precisa ser grande.
5. **Armadilhas**: routing collapse acelerado pelo estado (feedback positivo temporal); não-diferenciabilidade da seleção (use straight-through, Gumbel-top-k ou expert-choice); τ pequenos → roteador vira stateless caro; τ grandes → lento demais para reagir. **Baseline obrigatório**: hash routing e top-k stateless com mesma capacidade. Métrica: entropia de uso, CV de carga, e *quanto do ganho vem do estado* (ablação com τ→0).

### 5.2 Neuromodulação como transformação de parâmetro
1. **Existe**: Doya 2002 (DA/5-HT/NA/ACh ↔ δ/γ/β/α) é literalmente "neuromodulador = hiperparâmetro do RL"; hypernetworks (Ha 2016), FiLM (Perez 2018), **Neuromodulated networks** (Miconi et al. ICLR 2019 "Backpropamine": plasticidade Hebbiana modulada por sinal aprendido; Beaulieu et al. 2020 ANML: uma rede modula ativações de outra para continual learning), Vecoven 2020 "Introducing neuromodulation in deep neural networks to learn adaptive behaviours". Adaptive gain (Aston-Jones) = temperatura/ganho de softmax.
2. **Parcialmente novo**: aplicar a modulação a parâmetros *dinâmicos* da CfC (τ, A, ganhos) em vez de a pesos ou ativações — isso muda a *escala temporal* do módulo, que é o que NA/ACh fazem biologicamente e que nenhum dos trabalhos acima faz explicitamente.
3. **Inédito**: modulador de baixa dimensão (4–8 escalares) com dinâmica lenta própria, treinado por sinal de incerteza (esperada vs inesperada, Yu & Dayan) e usado para reconfigurar **simultaneamente** roteamento, LR local e τ. Pouco explorado.
4. **Resultados**: Backpropamine/ANML mostram ganhos em few-shot e continual learning em escala pequena [R]; em escala LLM, modulação tipo FiLM/adapters funciona, modulação de LR por surpresa é o que Titans faz (e funciona) [R].
5. **Armadilhas**: modulador de alta dimensão vira "segunda rede" e perde a interpretabilidade/estabilidade; modular τ pode violar limites de estabilidade da LTC — mantenha τ_mod ∈ [τ_min, τ_max] com sigmoide; acoplamento modulador↔módulo pode oscilar (loop de ganho) — modulador deve ser **mais lento** que qualquer módulo modulado (separação de escalas, princípio de perturbação singular).

### 5.3 Controle hierárquico multi-timescale
1. **Existe**: Clockwork RNN (2014), HM-RNN (Chung 2017), FeUdal Networks (Vezhnevets 2017: manager em escala lenta, worker rápido), Options/HRL, constantes de tempo hierárquicas do córtex (Murray 2014), SSMs com decaimento por canal, **Nested Learning/CMS (NeurIPS 2025)** — memória como espectro de frequências de atualização.
2. **Parcialmente novo**: CMS é sobre *frequência de atualização de pesos*; o time usa *constantes de tempo de ativação* (CfC) hierárquicas — são complementares e ninguém combinou os dois explicitamente.
3. **Inédito**: hierarquia onde o nível superior modula os τ do inferior (5.2 + 5.3) e onde o readout é assíncrono (5.4).
4. **Resultados**: FeUdal/Options funcionam mas são difíceis de treinar; HOPE mostra ganhos em LM e continual learning [R]; multi-τ em SSMs é o que faz Mamba funcionar em long-range [R].
5. **Armadilhas**: escolher τ à mão vs aprender (aprender τ tende a colapsar para um valor — use inicialização log-uniforme e regularização de diversidade); credit assignment através de níveis lentos (gradientes fracos — use losses locais por nível); avaliar em tarefas que realmente exigem múltiplas escalas (§8).

### 5.4 Integração contínua com readout assíncrono
1. **Existe**: event-based/asynchronous computing em neuromórfico; Adaptive Computation Time (Graves 2016), PonderNet (2021); "Spiking readout"; Liquid Time-constant com saída por amostragem irregular (Hasani; Neural CDE, Kidger 2020 — entradas irregulares).
2. **Parcialmente novo**: readout disparado por evento interno (limiar de confiança/surpresa) em vez de por relógio ou por token.
3. **Inédito**: sistema multi-módulo onde cada módulo publica assincronamente em um workspace quando sua dinâmica interna atinge critério — é a versão "event-driven" do Global Workspace. Não encontrei implementação em ML de escala.
4. **Resultados**: ACT/PonderNet funcionam mas a economia de compute é modesta; Neural CDE lida bem com dados irregulares [R].
5. **Armadilhas**: treinar limiares de disparo (não-diferenciável — surrogate ou REINFORCE); batching em GPU odeia assincronia (perda de eficiência prática — mitigar com "bucketing" de eventos ou simulação síncrona com máscara); métricas devem incluir *compute real gasto*, não só acurácia.

### 5.5 Módulos tálamo / PFC / hipocampo (arquitetura modular anatômica)
1. **Existe**: PBWM/Leabra (O'Reilly), Spaun (Eliasmith 2012: 2,5 M neurônios, 8 tarefas), JEPA (LeCun 2022), Goyal & Bengio global workspace, RIMs (Goyal 2019), CLS com replay (muitos), Titans (memória ≈ hipocampo), MERLIN (Wayne 2018: memória + RL), Kanerva Machine, **Complementary Learning Systems em deep RL** (Kumaran, Hassabis, McClelland 2016 update).
2. **Parcialmente novo**: a composição específica (roteador CfC + modulador + hierarquia multi-τ + memória episódica) — cada peça existe; o *sistema* não.
3. **Inédito**: depende de §5.1–5.4.
4. **Resultados de "cérebros completos"**: ver §6 — todos demonstraram *capacidade cognitiva ampla em escala pequena* e **nenhum escalou** para competir em tarefas abertas. RIMs/GW mostram ganhos de generalização OOD em tarefas sintéticas [R]. JEPA só tem os módulos de percepção treinados.
5. **Armadilhas**: (a) **fidelidade anatômica como objetivo** — mata projetos; a anatomia deve ser hipótese, não requisito; (b) módulos sem loss própria não aprendem seu papel — o "hipocampo" vira mais um bloco; (c) sem replay, CLS não funciona; (d) interfaces entre módulos precisam de gargalo (workspace pequeno) ou vira um monólito; (e) medir cada módulo isoladamente (ablation) — se remover o "tálamo" não piora, ele não é um tálamo.

### 5.6 Alocação de neurônios por demanda seguida de seleção
1. **Existe**: §2 inteira — Edelman, Changeux, Huttenlocher (biologia); RigL/SET, Lottery Ticket, DEN, Draelos, DPAP, NEAT, "growing via GD" 2025 (ML).
2. **Parcialmente novo**: alocação guiada por *necessidade* medida como surpresa/progresso de aprendizado (Oudeyer) ou incerteza (Yu & Dayan), em vez de gradiente (RigL) ou erro de reconstrução (Draelos).
3. **Inédito/pouco explorado**: alocação **online em rede contínua stateful**, com seleção por *uso* (traço de atividade + 3-factor) em vez de magnitude, e um período de "consolidação" análogo a replay antes da poda. Combinado com roteamento (5.1): **alocar experts/unidades quando a carga de um expert ou a surpresa de um input excede limiar** → é um MoE que cresce e depois se poda. Não encontrei isso em escala.
4. **Resultados**: RigL iguala denso a 90% esparsidade [R]; DEN/Progressive zero-forgetting mas crescem sem limite [R]; DPAP comprime sem retreino em pequeno [R]; Minitron confirma que seleção precisa de consolidação [R]. **Tudo em escala ≤ ResNet/ImageNet ou LLM 8B com destilação.**
5. **Armadilhas**: (a) alocar por surpresa cai no "noisy TV" — use progresso de aprendizado; (b) poda por uso pune unidades raras-mas-críticas (tail) — proteja por importância (Fisher/gradiente) além de uso; (c) novos neurônios com init aleatória perturbam a rede (Net2Net resolve com init preservadora de função); (d) alocação sem teto → estabelecer orçamento (energia) explícito: **restrição de custo é o que força seleção** — na biologia é ATP; em ML deve ser um termo de custo por parâmetro ativo/FLOP na loss.

---

## 6. Arquiteturas cognitivas prévias e lições

| Sistema | O que é | Resultado | Lição |
|---|---|---|---|
| **Spaun / Nengo / NEF** (Eliasmith 2012–) | 2,5 M neurônios spiking, anatomia (V1→IT, PFC, BG, tálamo, motor), 8 tarefas com o mesmo modelo; Spaun 2.0 (2019) mais tarefas | Primeiro "cérebro" funcional multi-tarefa; ~lento, não aprende novas tarefas sozinho | Anatomia funcional é implementável; **escala e aprendizado aberto não vêm de graça** |
| **Leabra / Emergent / PBWM** (O'Reilly) | Framework biologicamente plausível (Hebb + erro, inibição k-WTA, PBWM para WM); "Leabra Vision" | Explica muitos dados cognitivos; nunca competitivo em benchmarks de ML | Ótimo *gerador de hipóteses* (gating por DA, k-WTA); não é backbone |
| **ACT-R / Soar / Sigma / CLARION** | Arquiteturas cognitivas simbólicas/híbridas (memória declarativa, procedural, chunking) | Modelam comportamento humano (tempos de reação, erros); zero aprendizado perceptual | Estrutura "módulos + buffers + workspace" é robusta; conteúdo deve ser aprendido |
| **HTM / Thousand Brains** (Numenta) | Colunas com sparse distributed representations, sequence memory, reference frames; Thousand Brains Project (código aberto 2024–) | Bom em anomalia em séries temporais; não competitivo em visão/linguagem | SDRs (~2% ativos) são robustos e baratos; voto entre colunas é uma ideia boa não escalada |
| **Blue Brain / Human Brain Project** | Simulação biofísica de microcoluna de rato (Markram 2015), atlas | Ciência valiosa; **nenhuma função cognitiva emergiu**; críticas duras (Frégnac 2017 "Big data and the industrialization of neuroscience") | Detalhe biofísico ≠ função. Não copie canais iônicos; copie princípios computacionais |
| **RIMs / Global Workspace agents** (Goyal, Bengio 2019–2022) | Módulos recorrentes independentes competindo por atenção a um workspace pequeno | Melhor OOD/transfer em tarefas sintéticas e Atari; não adotado em escala | Gargalo + competição = generalização composicional; custo: treino difícil |
| **DNC / MERLIN / Kanerva** | Memória externa endereçável | DNC resolve grafos/bAbI; MERLIN resolve tarefas de memória em 3D | Memória externa funciona, mas foi *superada por attention longa* — até Titans trazê-la de volta como pesos |
| **JEPA (LeCun 2022)** | Blueprint modular (configurador, percepção, world model, custo, ator, memória) | Só percepção (I-JEPA, V-JEPA 2) treinada até agora | Blueprint correto ≠ sistema; cada módulo é um projeto de anos |
| **Titans / MIRAS / HOPE** (Google, 2025) | Memória neural em tempo de teste; multi-frequência | Ganhos em LM/long-context [R]; reprodução independente mostra ganhos inconsistentes [R] | A direção "memória que aprende + multi-timescale" está validada; detalhes (chunking) importam |
| **Hymba** (NVIDIA 2024), **Jamba**, **Zamba** | Híbridos attention (recall preciso) + SSM (resumo eficiente) em paralelo, com "meta tokens" aprendidos | Hymba-1.5B supera Llama-3.2-3B com 11× menos cache [R] | "Dois sistemas de memória em paralelo" (≈ hipocampo + córtex) é o híbrido que venceu em 2024–2025 |
| **Liquid Foundation Models** (Liquid AI 2024–2026) | LTC/CfC-derivados como backbone de LLM/VLM em edge | Competitivos em 1–3B com pegada de memória menor [R, self-reported] | CfC escala; o gargalo é kernel/hardware, não a matemática |

**Síntese [E]**: os vencedores isolaram *um* princípio biológico e o tornaram um operador diferenciável que escala (attention ≈ associative recall; sparsity/MoE ≈ energia; SSM decay ≈ multi-τ; test-time memory ≈ hipocampo). Os perdedores tentaram reproduzir a *anatomia inteira* de uma vez. Nossa estratégia deve ser **modular na engenharia, incremental na validação**: cada módulo entra só depois de provar ganho isolado.

---

## 7. Armadilhas transversais
1. **Routing collapse** (§4.3) — monitorar entropia; usar aux-loss-free bias (DeepSeek-V3) ou expert-choice.
2. **Instabilidade de redes contínuas** — respeitar limites de τ; gradient clipping; CfC em vez de ODE-solver; inicializar próximo do regime estável (ρ<1) e deixar aprender para a borda.
3. **Esquecimento catastrófico** — replay é obrigatório (CLS); EWC sozinho não basta em sequências longas de tarefas [R].
4. **Noisy TV / curiosidade patológica** — usar progresso de aprendizado, não erro bruto.
5. **Modularidade cosmética** — se ablation não muda resultado, o módulo é decorativo.
6. **Baselines fracos** — todo componente bio-inspirado comparado a Transformer/Mamba de **mesmos FLOPs e dados**; a maior parte da literatura bio-inspirada falha aqui.
7. **Assincronia vs GPU** — o hardware é síncrono; simular assincronia com máscaras e medir compute *efetivo*.
8. **Escala** — resultados em MNIST/CIFAR/gridworld não transferem; planejar desde o início uma escada de escala (§9).
9. **Fidelidade biológica como métrica** — Brain-Score é interessante, mas otimizar para ele não melhora tarefas.
10. **Autoengano terminológico** — chamar um gate de "tálamo" não o torna um; documentar em cada módulo *qual princípio computacional* está sendo testado e qual seria a evidência de que funciona.

---

## 8. Benchmarks recomendados (por hipótese)
| Hipótese | Benchmark |
|---|---|
| Multi-timescale / long-range | Long Range Arena; BABILong; NIAH multi-escala; Copy/Recall com distratores; sequências com estrutura hierárquica sintética (Dyck, hierarchical grammar) |
| Memória episódica / CLS | Split-CIFAR/TinyImageNet class-incremental; CLEAR; Continual World; **Avalanche** (biblioteca); Memory Maze (Pasukonis 2022) |
| Roteamento / modularidade | Compositional generalization (SCAN, COGS, gSCAN); Sort-of-CLEVR; ARC-AGI-2 (dureza máxima); OOD em MiniGrid/BabyAI |
| Controle hierárquico / RL | Crafter (score + achievements), NetHack Learning Environment, Procgen (generalização), Meta-World (multi-task), bsuite (diagnóstico: memória, exploração, crédito) |
| Curiosidade / alocação sob demanda | Montezuma's Revenge, MiniGrid sparse, Crafter sem recompensa extrínseca |
| Eficiência / assincronia | FLOPs efetivos por token/decisão; energia estimada; latência p50/p99 em stream |
| Alinhamento neural (secundário) | Brain-Score; predição de neurônios do MICrONS/Allen |

---

## 9. Roadmap de experimentos (ordem por razão evidência/risco) [E]
**Fase 0 — Baselines e harness (1–2 semanas)**: Transformer pequeno, Mamba, MoE stateless top-k, hash routing; mesmo orçamento de FLOPs; harness com LRA-lite, BABILong-lite, Split-CIFAR, MiniGrid. Logging de entropia de roteamento, uso por unidade, τ efetivos, compute real.

**Fase 1 — Memória episódica + replay (CLS)**: módulo Hopfield moderno / Titans-like com escrita esparsa; replay offline treinando o backbone lento. Critério: reduzir esquecimento em class-incremental ≥ EWC e ≈ replay clássico com menos buffer.

**Fase 2 — Roteador CfC stateful**: substituir gate do MoE por CfC de 16–64 unidades; ablação τ→0. Critério: ≥ top-k stateless em compositional generalization sem collapse (CV de carga < 0,3).

**Fase 3 — Multi-timescale hierárquico**: 3 níveis de τ (log-uniforme), nível superior envia contexto ao roteador. Critério: ganho em LRA/estrutura hierárquica vs τ único de mesma capacidade.

**Fase 4 — Neuromodulador de baixa dimensão**: 4–8 escalares (surpresa esperada/inesperada, RPE, progresso) modulando LR local, temperatura do roteador e τ. Critério: adaptação mais rápida a mudança de distribuição (task switch) sem perda em regime estável.

**Fase 5 — Alocação sob demanda + seleção**: crescer experts/unidades quando progresso de aprendizado estagna e carga/surpresa excede limiar; consolidar (replay); podar por uso×importância com orçamento de custo. Critério: acurácia por parâmetro ativo ≥ RigL/denso em continual learning; capacidade final ≤ 1,5× do necessário.

**Fase 6 — Readout assíncrono**: disparo por limiar de confiança; medir compute efetivo. Critério: −30% compute a acurácia igual.

**Fase 7 — Escada de escala**: 10M → 100M → 1B parâmetros em LM/RL, mantendo apenas os módulos que sobreviveram às fases 1–6.

### Restrições de design a usar como "leis"
- Esparsidade de ativação alvo 1–5% (Lennie; SDRs de Numenta ~2%); esparsidade de conexão fixa por unidade (~fan-in constante).
- Razão excitação/inibição ~80/20 e inibição como normalização/k-WTA (não precisa de neurônios inibitórios explícitos; use divisive normalization).
- Separação de escalas: cada nível ≥ 3–10× mais lento que o inferior; modulador mais lento que tudo.
- 3-factor: toda plasticidade local = traço Hebbiano × sinal global.
- Orçamento energético explícito na loss (custo por parâmetro ativo/FLOP) — é o que torna a seleção necessária.
- Períodos críticos: fase de crescimento cedo, seleção depois; não intercalar caoticamente.

---

## 10. Linha do tempo 2023–2026 (o que "saiu")
- **2023**: Dreamer v3 (Hafner); Mamba (Gu & Dao, dez) — SSM seletivo com decaimento dependente de input; Forward-Forward avaliações mostram limites; Mixtral 8×7B (dez).
- **2024**: DeepSeek-V2/V3 (aux-loss-free load balancing, MLA); Hymba (NVIDIA, nov) híbrido attn+SSM; Minitron (NVIDIA, ago) poda+destilação; FlyWire conectoma completo da Drosophila (Nature, out); Hala Point Loihi 2 (abr); DPAP (TPAMI); Gated DeltaNet; Liquid AI LFM 1.0 (set); revisões de continual learning (Wang et al. TPAMI); Akers/neurogênese & esquecimento consolidado em revisões.
- **2025**: **Titans** (jan) e **MIRAS**; Dreamer v3 na Nature (abr); Growing networks via GD (Proc R Soc A, jul); RAC — poda calibrada com CoT preserva raciocínio (set); Titans Revisited — reprodução crítica (out); **Nested Learning / HOPE / CMS** (NeurIPS, nov); DeepSeek-V3.x/R1 consolidam MoE esparso como padrão; Liquid AI LFM2 (jul).
- **2026**: "Modular Memory is the Key to Continual Learning Agents" (mar, posição coletiva); Deterministic Differentiable Structured Pruning (mar); Homeostase growth/prune em neuroevolução (EvoApps, jan); ACE-SQL/Qwen3 (jun); **MICrONS-constrained RNNs** superam baselines (jun, arXiv 2606.14975); S2TE topologia scale-free em SNNs (Machine Learning, mar).

---

## 11. Bibliografia (seleção; links para busca)
**Neurociência**: Sherman & Guillery, *Exploring the Thalamus* (MIT 2006/2009) · Halassa & Sherman 2019 Neuron "Thalamocortical circuit motifs" · Wang & Halassa 2021 arXiv:2104.01474 · O'Reilly & Frank 2006 Neural Comput (PBWM) · Wang et al. 2018 Nat Neurosci "Prefrontal cortex as a meta-RL system" · Badre 2008 TICS · McClelland, McNaughton, O'Reilly 1995 Psych Rev (CLS); Kumaran et al. 2016 TICS · Whittington et al. 2020 Cell (TEM) · Stachenfeld et al. 2017 Nat Neurosci (SR) · Schultz, Dayan, Montague 1997 Science · Dabney et al. 2020 Nature (distributional DA) · Marr 1969 / Albus 1971 · Doya 2002 Neural Netw "Metalearning and neuromodulation" · Yu & Dayan 2005 Neuron · Aston-Jones & Cohen 2005 Annu Rev Neurosci · Rao & Ballard 1999 Nat Neurosci · Bastos et al. 2012 Neuron · Hawkins 2021 *A Thousand Brains* · Fries 2005/2015 · Lisman & Jensen 2013 · Baars 1988; Dehaene & Changeux 2011 · VanRullen & Kanai 2021 TINS · Murray et al. 2014 Nat Neurosci · Edelman 1987 *Neural Darwinism* · Changeux & Danchin 1976 Nature · Huttenlocher 1979/1990 · Rakic et al. 1986 Science · Josselyn & Frankland 2018 Science "Memory allocation" · Akers et al. 2014 Science · Turrigiano 1998 Nature · Bienenstock, Cooper, Munro 1982 · Bi & Poo 1998 · Frémaux & Gerstner 2016 Front Neural Circuits; Gerstner et al. 2018 · Bellec et al. 2020 Nat Commun (e-prop) · Bellec, Kappel, Maass 2018 ICLR (Deep Rewiring) · Hensch 2005 Nat Rev Neurosci · Attwell & Laughlin 2001 · Lennie 2003 Curr Biol · Levy & Baxter 1996 · Herculano-Houzel 2012 PNAS · Zador 2019 Nat Commun (genomic bottleneck) · Dorkenwald et al. 2024 Nature (FlyWire) · Shakiba et al. 2026 arXiv:2606.14975.
**ML**: Frankle & Carbin 2019 (LTH) · Mocanu 2018 Nat Commun (SET) · Evci 2020 ICML (RigL) · Li et al. 2020 ICML (train large then compress) · Rusu 2016; Yoon 2018 (DEN) · Draelos 2017 · Han/Shen/Zeng TPAMI 2024 (DPAP, arXiv:2211.12714) · Radhakrishnan 2025 Proc R Soc A · Shazeer 2017; Fedus 2021 (Switch); Zhou 2022 (expert-choice); Roller 2021 (hash); DeepSeek-V3 2024 · Goyal et al. 2019 (RIMs); Goyal et al. 2022 ICLR (global workspace) · Hasani 2021 AAAI (LTC); Hasani & Lechner 2022 Nat Mach Intell (CfC); Lechner 2020 Nat Mach Intell (NCP) · Gu & Dao 2023 (Mamba) · Ramsauer 2020 · Krotov & Hopfield 2016 · Schlag, Irie, Schmidhuber 2021 (linear transformers = FWP) · Behrouz 2025 arXiv:2501.00663 (Titans); MIRAS 2025; Behrouz & Mirrokni NeurIPS 2025 (Nested Learning) · Di Nepi 2025 arXiv:2510.09551 · Dong et al. 2024 (Hymba) · Miconi 2019 ICLR (Backpropamine); Beaulieu 2020 (ANML) · Lillicrap 2016 (FA); Whittington & Bogacz 2017; Millidge 2020; Scellier & Bengio 2017; Hinton 2022 (FF) · Kirkpatrick 2017 (EWC); Zenke 2017 (SI); Wang et al. TPAMI 2024 (CL survey); Dorovatas et al. 2026 arXiv:2603.01761 · Hafner 2023/2025 (Dreamer v3) · LeCun 2022 (JEPA position paper) · Graves 2016 Nature (DNC) · Oudeyer 2007; Pathak 2017; Burda 2018 · Achille, Rovere, Soatto 2019 ICLR (critical periods) · Stanley 2002 (NEAT); Salimans 2017 (ES); Mouret & Clune 2015; Wang et al. 2019 (POET); Najarro & Risi 2020; Mordvintsev 2020 (NCA) · Eliasmith 2012 Science (Spaun) · Neftci 2019 (surrogate gradients) · Kaplan 2020; Hoffmann 2022 · Sutton 2019 "The Bitter Lesson".
