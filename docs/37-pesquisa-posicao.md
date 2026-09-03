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

## 4. Primeira destilação simbólica (2026-09-03) — negativa com mecanismo

`src/destilar.py`: ranqueia os termos da política do campeão por |peso| ×
desvio da feature numa vida, poda para k termos e VERIFICA rodando a
política podada (128 réplicas × 3 cidades).

| k termos (de 26 de movimento) | fit | mortos | campeão |
|---|---|---|---|
| 5 | 4.48 | 0.61 | 6.94 / 0.30 |
| 10 | 4.88 | 0.53 | |
| 15 | 5.89 | 0.43 | |

**A política evoluída não é esparsa.** Zerar os termos "pequenos" quebra a
política porque os pesos são co-adaptados (o mesmo mecanismo do N9): a
equação curta que descreve o campeão não existe por poda — precisa de
RE-AJUSTE (aprender uma política de k termos que imite as decisões do
campeão, e verificar). É o que a destilação simbólica de 2025 (SPID) faz de
fato: regressão, não poda. Fica como E23. A frase em português que a poda
produz ("prefiro o vizinho com +2.1·distância ao destino +1.2·hora +3.0·tanque
−4.9·dinheiro −3.4·temperatura") é uma DESCRIÇÃO, não uma equação
verificada — e a diferença entre as duas é exatamente a diferença entre
falar sobre matemática e falar matemática.

## 5. E23 — a equação mínima que sobrevive (predição antes de rodar)
Em vez de podar o campeão, EVOLUIR a política com só k termos permitidos
(`src/minimo.py`: os outros são cancelados; com todos permitidos é bit-igual
ao Reativo). A equação de k termos que sair é verificada por construção —
o fitness dela é o fitness.
16. Triagem (pena 5): `mínimo 10` ≥ 85 % do direto; `mínimo 5` (destino,
    posto, comida, tanque, fome) ≥ 70 %; `mínimo 3` < 60 %. Se o mínimo-5
    ficar ≥ 85 %: o táxi "fala" em 5 termos e o resto da política é ruído
    co-adaptado. Mortalidade: mínimo-5 ≤ direto + 0.10.

### E23 triagem (R=8, G=40, 3 sementes) — a predição 16 inverteu

| política | termos de movimento | fit | mortos | panes |
|---|---|---|---|---|
| direto (Reativo) | 26 | 4.85 | 0.60 | 8.4 |
| mínimo 10 | 10 | 6.67 | 0.36 | 8.0 |
| mínimo 5 (destino, posto, comida, tanque, fome) | 5 | 6.39 | 0.35 | 7.4 |
| **mínimo 3 (destino, posto, tanque)** | 3 | **6.42** | **0.35** | 6.8 |

Menos termos, MELHOR: com 40 gerações e 32 vidas por genoma, a política de 3
termos chega onde o cérebro completo só chega com 60 gerações e 64 vidas
(honesto do direto: 6.90 / 0.35). Mecanismo: a busca — 44 genes co-adaptados
demoram a se organizar; 3 + 6 genes se organizam em 40 gerações. É o oposto
da poda (doc 37 §4): tirar termos DEPOIS quebra; evoluir SEM eles funciona.
A equação de 3 termos é verificada por construção e cabe numa frase: "vou
na direção do destino, na direção do posto, tanto mais quanto menos tanque
tenho; uso o serviço cuja necessidade × peso vencer."

**Predição 19 (antes de rodar, honesto R=16, 5 sementes):** mínimo 3 e mínimo
5 ficam ≥ direto (6.90 / 0.35): fit ≥ 6.7 e mortos ≤ 0.35 com ≥ 3/5 sementes
≤ 0.35. Se o direto passar os mínimos no honesto (≥ +0.8): a vantagem era só
velocidade de busca (útil mesmo assim: triagem em 3 termos). Se os mínimos
continuarem ≥ direto: os outros 23 termos são ruído co-adaptado e o táxi
FALA em 3 termos.

## 6. Fundamentos clássicos e o que dizem dos nossos desertos (2026-09-03, tarde)

**Hinton & Nowlan 1987 — como o aprendizado guia a evolução (efeito Baldwin).**
Numa paisagem "agulha no palheiro" (20 genes têm de acertar todos), a
evolução pura não acha (fitness ≈ 1); com aprendizado em vida (genes "?" que
o indivíduo ajusta tentando), a paisagem fica suave e a evolução acha
(≈ 11.6 em 50 gerações). Condição: o aprendizado tem de conseguir CHEGAR à
solução dentro da vida. **Nosso E22 falhou exatamente nessa condição**: a
regra de plasticidade só dispara depois da primeira refeição, e a primeira
refeição não acontece na vida — o "?" nunca vira "1". Baldwin exige que a
exploração em vida seja barata: E25 (infância individual) é isso.

**Zador 2019 — a crítica do aprendizado puro e o gargalo genômico.** Quase
todo comportamento animal é INATO: o genoma é pequeno demais pra escrever o
cérebro, então codifica regras de ligação que passam por um gargalo — e esse
gargalo é um regularizador. Receptor e hormônio vêm juntos no genoma.
**Nosso E20 encontrou isso na prática**: código herdado dos dois lados
funciona; aprender o código do zero não. A leitura certa não é "falhou", é
"a biologia também não faz assim". Desenho que decorre: herdar o
dicionário mínimo (fome→comida, sede→posto) e deixar a evolução refinar —
o que o E20 triagem 3 já mostrou que funciona.

**Doya 2002 — neuromodulação como meta-aprendizado.** Dopamina = erro de
predição de recompensa; serotonina = fator de desconto (horizonte);
noradrenalina = temperatura (exploração); acetilcolina = taxa de
aprendizado. Os hormônios modulam os PARÂMETROS DO APRENDIZADO, não a
física. **É a regra 16 dita por outro caminho**: as nossas glândulas
mexeram em consumo e velocidade (preço), e a seleção as usou como
desconto. O lugar certo do hormônio é: quanto explorar, quão longe olhar,
quão rápido aprender. Isso só faz sentido com aprendizado em vida (E22/E25)
— sem ele, hormônio não tem o que modular.

**Sterling 2012 — alostase: regulação preditiva.** O cérebro não corrige
erros, ANTECIPA necessidades e prepara o corpo antes. Vantagens: erros
menores, capacidades casadas, reservas menores, erros lembrados. **Nosso τ
das glândulas era a metade disso** (memória, não antecipação). Antecipar
exige um sinal do futuro — o relógio (noite chegando) é o candidato óbvio,
e é onde a hora, que nunca convergiu como feature, pode entrar como
ANTECIPAÇÃO no corpo (hormônio que sobe antes da noite) e não como sinal
cru no cérebro.

**Kirby / Ren et al. 2020 — aprendizado iterado.** Línguas ficam
composicionais e aprendíveis quando passam por gerações de aprendizes que
têm de reaprendê-las de pouco input (o gargalo de transmissão); resetar o
receptor periodicamente cria a pressão por códigos aprendíveis. **Nossos
hormônios nunca passaram por isso**: o cérebro de cada geração nasce com o
gene, não aprende o código do pai. Desenho que decorre (E26, "transmissão
cultural"): o filho nasce com o corpo do genoma mas o receptor (Gserv)
aprende EM VIDA observando... não há pai no táxi. A versão honesta pro nosso
mundo: o receptor é aprendido em vida (E22/E25) e só os aprendizes que
aprenderam rápido se reproduzem — a pressão de aprendibilidade vem da
morte, não de um professor. Se E25 mostrar que aprender em vida funciona
com infância, a próxima é medir se o código que a evolução herda fica MAIS
simples quando o receptor é aprendido (o efeito Kirby).

**Síntese:** os quatro desertos que vimos (seleção, currículo, receptor,
plasticidade) são o mesmo fenômeno com quatro caras — uma paisagem
agulha-no-palheiro onde nem a evolução nem o aprendizado alcançam a agulha
dentro do orçamento. Os clássicos dão três saídas, e as três já estão em
teste ou desenhadas: aprendizado em vida barato (Baldwin → E25), código
inato mínimo (Zador → E20 triagem 3), hormônio modulando aprendizado e não
física (Doya → regra 16 + E22). A quarta (Kirby) é a que ainda não tem
experimento.

### Fontes desta seção
- https://www.cs.toronto.edu/~hinton/absps/evolution.htm · https://arxiv.org/abs/2409.15609 · https://arxiv.org/abs/1702.08411
- https://www.nature.com/articles/s41467-019-11786-6 · https://www.pnas.org/doi/10.1073/pnas.2409160121
- https://pubmed.ncbi.nlm.nih.gov/12371507/ · https://arxiv.org/pdf/2111.00134
- https://pubmed.ncbi.nlm.nih.gov/21684297/ · https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.1052998
- https://arxiv.org/abs/2002.01365 · https://arxiv.org/pdf/2409.02645 · https://www.pnas.org/doi/abs/10.1073/pnas.2509739123

## 7. Matemática vem do corpo (Lakoff & Núñez, 2000) — e o que isso diz do lab

"Where Mathematics Comes From": a matemática não é descoberta num céu
platônico nem inventada do nada — é construída por **metáforas de
fundamento** que projetam experiências corporais (juntar objetos, andar num
caminho, encher um recipiente) em conceitos abstratos (adição, reta
numérica, conjunto). Bebês já "subitizam" (contam até 3 sem contar). A
matemática é humana porque tem corpo.

O que isso diz do nosso projeto, com franqueza:
1. **As nossas leis vieram do corpo.** A lei da poupança (doc 26) nasceu de
   tanque, gordura e noite; a lei da moeda cruzada (EXP10, N16, N19) de
   reboque, dinheiro e calorias; a regra da seleção cega (regra 14) de
   mortes que ninguém via. Nenhuma foi derivada primeiro e testada depois —
   foram sentidas no custo e depois escritas. É Lakoff & Núñez ao pé da
   letra: a fórmula é a metáfora de fundamento tornada precisa.
2. **"Fazer a rede falar matemática" tem duas metades, e só uma é
   tradução.** A metade de tradução (frase ↔ Lean, política ↔ equação) já
   existe na literatura e no lab. A metade que falta é a metáfora: a rede
   precisa ter EXPERIÊNCIA do que a fórmula descreve pra que a fórmula
   signifique algo pra ela. O E23 é o primeiro passo nessa direção: a
   equação de 3 termos não foi imposta — foi a que sobreviveu, e por isso
   "quer dizer" destino, posto e tanque.
3. **A comunicação matemática ↔ PT-BR passa pelo corpo do leitor.** Uma
   frase como "vou pro posto tanto mais quanto menos tanque tenho" é
   compreendida porque o leitor tem tanque (ou fome). Documentar as leis com
   a metáfora corporal ao lado da fórmula (como as "Aulas" fazem) não é
   didática — é o mecanismo pelo qual a matemática é entendida.

Fonte: https://en.wikipedia.org/wiki/Where_Mathematics_Comes_From ·
https://www.americanscientist.org/article/embodied-mathematics

## 8. E29a — o cérebro em log (Leonardo, café com leite: "a lei tem multiplicação e divisão")
Toda lei de mistura é produto/razão (`Pe = vL/D`, `k[A][B]`, `L²/D`); o
Reativo só soma. `ReativoLog` (`src/quimico.py`): as features de distância e
estado entram como `log(x + ε)` — a mesma soma de pesos vira **lei de
potência** (`exp(score) = Π xᵢ^wᵢ`), que expressa tanque × distância,
necessidade / custo, sem gene extra (NP = 44). Verificado: sem NaN, sem sync
(o primeiro rascunho criava um tensor no laço — pego pelo detector).

**Predição 26 (antes de rodar; triagem, depois honesto):** `log` ≥ `noite24`
em mortos (≤ 0.35 no honesto) e ≥ `direto` em fit, sem gene extra; em
cidades 2000+ perde MENOS que o linear (razões são adimensionais: queda
≤ 30 % vs 45 % do direto). Se `log` ≈ `direto`: a não-linearidade que vale
é o PORTÃO (só quando o tanque baixa), não a multiplicação em geral — e o
E29b (reações espécie × sinal com portão) é o próximo.

### E23 honesto (R=16, 5 sementes) — a equação de 3 termos empata com o cérebro completo

| política | termos | fit | mortos | por semente (mortos) |
|---|---|---|---|---|
| direto (Reativo, 44 genes) | 26 | 6.90 | 0.35 | .30 .38 .38 .39 .32 |
| **mínimo 3 (destino, posto, tanque)** | 3 | **6.91** | **0.34** | .35 .30 .31 .39 .34 |
| mínimo 5 (+ comida, fome) | 5 | 5.89 | 0.39 | .47 .43 .37 .30 .36 |

Predição 19: mínimo 3 ✓ (≥ direto nos dois eixos); mínimo 5 ✗ (os termos
de comida e fome no MOVIMENTO atrapalham — puxam o táxi pra órbita, o mesmo
mecanismo dos 5 produtos do E17). A vantagem da triagem era velocidade de
busca; no honesto o resultado é **empate com 3 termos**: os outros 23 são
ruído co-adaptado que a evolução carrega sem usar.

Em português, a política inteira que sobrevive tanto quanto o cérebro
completo: *"vou na direção do destino; vou na direção do posto; quanto
menos tanque, mais forte; uso o serviço cuja necessidade × peso vencer o
movimento."* Verificada por construção — é a primeira frase do lab que é
matemática de verdade, não descrição.

## 9. E29b — reações (desenho, roda se o E29a não bastar)
A imagem do Leonardo ("líquidos com intensidade molecular; misturados viram
outra coisa") em mecanismo: **lei de ação das massas**. K espécies lentas
`c_k` (τ próprio, alimentadas pelos sinais do corpo, como as glândulas do
E16/E20) e termos de reação `c_k · x_j` só nos pares que a física sugere —
necessidade × distância ao serviço — com **portão** (o produto só liga acima
de um limiar, o que o E17/E23 mostraram que evita a órbita). Genes: τ_k,
entradas de cada espécie, e um peso por par (≤ 10). Nada de canal que mexa
em preço de física (regra 16).

**Predições (antes de rodar):** 27. com 2 espécies (sede = 1−tanque lenta,
fome lenta) e portão em 0.5, mortos ≤ Noite24 (0.32) com fit ≥ 6.6 — a
espécie lenta dá PERSISTÊNCIA à urgência (a fome continua "mandando" por τ
passos depois do pico, que é o que o Leonardo apontou: "só pensa em comer
quando está com fome"); 28. τ evoluído das espécies > 20 passos em ≥ 3/5
sementes (persistência é usada); se τ → 1: a persistência não paga e o
produto instantâneo (Noite24) já é o teto.

### E27 — pena de morte proporcional (morrer cedo custa mais): NULO na triagem

| braço | pena fixa | pena proporcional 2·(1−t/T) |
|---|---|---|
| direto | 4.85 / mortos 0.60 | 5.55 / 0.48 |
| noite24 | 5.36 / 0.51 | 5.28 / 0.56 |

Sinal inverte entre as duas arquiteturas (n=3) → regra 13: nulo. Mecanismo
que explica o nulo: quem morre no pacote morre por volta do dia 3.5 de 5,
então o fator médio é 2·(1−0.7) ≈ 0.6 — a pena proporcional só ENCOLHEU a
pena em ~40 % pra quase todo mundo; não abriu gradiente novo entre "morreu
cedo" e "morreu tarde" porque quase ninguém morre cedo. Predição 20 não
confirmada. Não sobe pro honesto; a avaliação fica com pena fixa 5.

### 9.1 O que a literatura já sabe de "reação química como computação" (lido 2026-09-03)
**Neural CRNs** (Nandi, Ellis et al., arXiv 2409.00034 / ACS Synth Bio 2025):
neurônio = concentração que EVOLUI no tempo (não camada estática); a
multiplicação é reação catalítica `P + Z → Z + P + Z` (dz/dt = θ·z, ação das
massas — exatamente o "×" da lei que o Leonardo apontou); não-linearidade
= amortecimento quadrático `θx − αz²`, nunca trimolecular (lifting implícito
no lugar); sinal negativo exige dual-rail (X⁺, X⁻) e isso EXPLODE o
circuito; aprendizado = espécies adjuntas (erro) + espécies-gradiente
`dg/dt = a·z` + realimentação negativa nos parâmetros; relógio de 2 fases
separa "computar" de "aprender"; regressor linear em 15 espécies / 13
reações (mais compacto que emular camadas). Limite deles: relógio
oscilatório amplifica ruído.

**Tradução pro E29b:** (a) nossas espécies `c_k` com τ próprio são
exatamente concentrações que evoluem; (b) a reação `c_k · d_p` é a
catalítica deles — sem dual-rail porque distância e necessidade são
positivas por construção (o sinal fica no gene `w`); (c) o portão `relu(c −
θ)` é a "classificação por limiar φ" deles; (d) o que ELES não têm e nós
temos: seleção por sobrevivência no lugar do adjunto — o gradiente vem da
morte, não da espécie A±. Predição extra 29: se a reação paga, `w` evoluído
tem sinal NEGATIVO em ≥ 4/5 sementes (sede empurra PRA o posto — reduzir
distância), não positivo.
