# 37 — Onde o projeto está diante das pesquisas recentes (2026-09-03)

Pergunta do Leonardo: o que foi descoberto e não foi usado (ou não teve uso
prático)? Se matemática é uma língua, como falamos ela, como fazer uma rede
falar ela, como criar comunicação entre matemática e PT-BR?

## 1. As frentes e onde estamos

### Neuromodulação em RL (o que a literatura chama de "cortisol/dopamina do agente")
Linha: Vecoven et al. 2020 (neuromodulação em redes profundas), "Lifelong RL
via Neuromodulation" (2024) — noradrenalina como incerteza inesperada mapeada
na temperatura de exploração; dopamina/serotonina/acetilcolina como
hiperparâmetros modulados. **Descoberto e pouco usado:** a ideia é sólida e
antiga (Doya 2002), mas quase ninguém a usa em produção porque o ganho só
aparece quando o ambiente muda de regime — em benchmarks estáticos ela vira
um hiperparâmetro a mais. **Nós:** foi exatamente o que vimos no E16: sem
regime real o hormônio é desligado; com "regime" ele virou desconto de
física (N19). A literatura modula a POLÍTICA (exploração, taxa de
aprendizado); nós deixamos o hormônio tocar em PREÇO de física — erro nosso
que a regra 16 fecha.

### RL homeostático e interocepção (o corpo como fonte do valor)
Linha: Keramati & Gutkin 2014 (eLife) — recompensa = redução do desvio de
pontos de ajuste internos; "Interoceptive Mixture of Experts" e "Interoceptive
Behavior Switching" (2023, controle contínuo com troca de política pelo estado
interno); meta-RL em regulação homeostática (2025); acoplamento homeostático
pró-social (2025); **"Interoceptive Attention as Dynamic Homeostatic
Prioritization" (ago/2026)**: um agente com 4 necessidades num gridworld que
redireciona um orçamento fixo de precisão para a necessidade mais urgente
**dobrou a sobrevivência** (0.41 vs 0.20) e aprendeu a dinâmica do canal
atendido 2× mais rápido. **Descoberto e pouco usado:** RL homeostático tem 12
anos e quase nenhum uso prático — os benchmarks não têm corpo. **Nós:** o
táxi É um agente homeostático (tanque, fome, cansaço, calor, vida, dinheiro)
e o nosso gargalo de hoje é exatamente o deles: escolher qual necessidade
manda. O E21 (atenção interoceptiva) é o teste direto desse achado de 2026.

### Co-evolução corpo–cérebro e vida artificial aberta
Linha: survey "Embodied Co-Design for Rapidly Evolving Agents" (dez/2025:
quatro famílias — bi-nível, nível único, generativa, aberta); **"Evolutionary
Brain-Body Co-Optimization Consistently Fails to Select for Morphological
Potential" (2025)**: mapearam 1,3 milhão de corpos e mostraram que a
evolução conjunta descarta corpos promissores porque um corpo novo com
cérebro velho parece ruim — subvaloriza o "potencial morfológico". **Nós:**
é o nosso N1/N9 (co-adaptação: alavanca nova × pesos evoluídos) e explica
por que o gene de timing (E14a) e as glândulas (E16) morriam ao nascer. A
resposta deles e a nossa convergem: proteger o novo até o parceiro se
adaptar (currículo, infância) — só que no E20 nem isso bastou para uma
"palavra" emergir.

### Comunicação emergente (dois sistemas que aprendem a falar)
Linha: jogos de Lewis (dois agentes têm de combinar um protocolo), "Emergent
Communication: Generalization and Overfitting in Lewis Games" (2022),
populações que se encontram (2025). **Achado sóbrio da área:**
composicionalidade e código NÃO emergem só por gargalo, população ou
memória curta — precisam de pressão específica (aprendizado iterado,
tarefa que exige o código). **Nós:** o E20 reproduziu isso com honestidade:
gargalo de 2 hormônios transmite (código herdado = mesma mortalidade), mas o
código não nasce do zero em 40 gerações, nem com infância protegida. A
biologia herda receptor e hormônio juntos; a nossa versão que funciona faz o
mesmo.

### Plasticidade evoluída (aprender em vida sem gradiente)
Linha: Najarro & Risi 2020 (só regras hebbianas evoluídas; o quadrúpede se
adapta a dano de corpo nunca visto), HyperNCA (2022), redes que se
auto-montam (2023). **Descoberto e pouco usado** fora de robótica
evolutiva. **Nós:** temos o SerSono (E9b) aprendendo a lei do radiador
dormindo, e a dopamina do cérebro-por-órgãos como portão de plasticidade —
é a peça que ainda não entrou no táxi com corpo. Candidato forte: o
"cérebro surdo" do E20 aprenderia a ouvir EM VIDA (regra hebbiana entre
hormônio e serviço, gateada por recompensa), em vez de por seleção.

### Matemática como língua
Linha 2025–2026: autoformalização (PT/EN → Lean 4) explodiu — FormalVerse
(367 mil exemplos verificados), StepfunFormalizer, Numina-Lean-Agent,
LeanMarathon (formalização longa), ProofBridge (embeddings conjuntos de prova
em linguagem natural e prova formal), MathForm (recuperação + refinamento
guiado por verificação), FormalRx (falhas semânticas). E o caminho inverso —
redes que ESCREVEM equações: regressão simbólica neural (SPID, set/2025:
destila políticas de RL em equações; "universal neural symbolic regression",
Nature Comms 2025; redes informadas por simetria, 2026).

## 2. Como "falar" matemática — o que eu acho

Matemática é uma língua com três registros, e cada um tem uma ponte com o
português:

1. **Fórmula ↔ frase.** Autoformalização faz PT-BR → Lean; a volta
   (informalização) é o LLM explicando a fórmula. A ponte de verdade é a
   **verificação**: a frase em PT-BR está certa se a formalização compila e
   prova. É o que os sistemas de 2026 fazem, e é o que já fazemos na mão
   nas "Aulas" (custo → derivada zero → lei → frase).
2. **Dado ↔ lei.** Uma rede "fala" matemática quando o que ela aprendeu
   pode ser destilado numa equação curta que prevê tão bem quanto ela
   (SPID, regressão simbólica). Já fizemos isso duas vezes: E5 (a lei
   Δfuel = −2.101·custo saiu dos pesos) e a lei da poupança (doc 26). O
   que falta é fazer de rotina: **todo campeão passa por destilação
   simbólica**, e a equação vira a explicação em PT-BR.
3. **Corpo ↔ cérebro.** É a mesma pergunta em outra escala: o hormônio é
   uma "palavra" de um vocabulário pequeno; o cérebro precisa de um
   dicionário. O E20 mostrou que o dicionário não nasce sozinho — tem de
   ser herdado ou aprendido em vida com um professor (recompensa).

**Proposta concreta (barata):** um passo de "tradução" no fim de toda
bateria: (a) regressão simbólica do campeão (política → equação com ≤ 5
termos), (b) a equação em PT-BR gerada por LLM, (c) a frase re-formalizada
e checada contra a política (previsão de mortos/entregas dentro de ±10 %).
Se fecha, temos a comunicação matemática ↔ PT-BR verificada, não só bonita.

## 3. O que está descoberto e nós ainda não usamos (ordem de valor)
1. **Atenção interoceptiva** (2026) — E21, rodando.
2. **Plasticidade em vida gateada por recompensa** (Najarro & Risi) para o
   cérebro aprender a ouvir hormônios sem seleção.
3. **Destilação simbólica de políticas** (SPID 2025) como rotina de
   explicação.
4. **Proteger o potencial** na co-evolução (2025): avaliar corpo novo com
   cérebro re-adaptado, não com o velho — o nosso "avaliar com vidas
   suficientes" (regra 14) mais "deixar o parceiro se adaptar".
5. **Meta-RL homeostático** (2025): a política aprende o ponto de ajuste, não
   só a ação — é o "τ e limiar como genes" que ainda não testamos.

## Fontes
- https://arxiv.org/html/2408.08446v1 · https://pmc.ncbi.nlm.nih.gov/articles/PMC6984695/
- https://elifesciences.org/articles/04811 · https://ieeexplore.ieee.org/document/10191925/ · https://arxiv.org/html/2608.04232 · https://arxiv.org/pdf/2506.12894 · https://2025.ccneuro.org/abstract_pdf/Yoshida_2025_Meta-Reinforcement_Learning_Homeostatic_Regulation.pdf
- https://arxiv.org/pdf/2512.04770 · https://arxiv.org/pdf/2508.17464 · https://arxiv.org/pdf/2502.04809
- https://openreview.net/pdf?id=rqLgeQWCXZ9 · https://arxiv.org/pdf/2209.15342 · https://link.springer.com/chapter/10.1007/978-3-031-97557-8_19 · https://arxiv.org/pdf/2403.14427
- https://arxiv.org/abs/2007.02686 · https://arxiv.org/html/2406.09787
- https://arxiv.org/abs/2608.14221 · https://arxiv.org/pdf/2606.05400 · https://arxiv.org/pdf/2510.15681 · https://arxiv.org/pdf/2607.04655 · https://arxiv.org/pdf/2607.07779
- https://openreview.net/forum?id=xLycLWUMas · https://www.nature.com/articles/s41467-025-61575-7 · https://arxiv.org/abs/2601.21720
