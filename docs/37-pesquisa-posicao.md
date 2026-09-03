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

**Multi-timescale RL no cérebro** (Masset, Tano, Kim, Malik, Pouget, Uchida —
bioRxiv 2023, Nature 642:682, jun 2025): cada neurônio de dopamina tem SEU
fator de desconto (propriedade da célula, correlacionada entre tarefas;
população 0.56 ± 0.21 s⁻¹); cada um sozinho é exponencial, o desconto
hiperbólico do animal EMERGE da diversidade da população; a população de τ
é uma transformada de Laplace invertível → dá pra decodificar QUANDO a
recompensa vem e QUANTO vale, separados (um τ só confunde os dois);
agentes multi-τ acertam 94 % vs 83 % em tarefas ramificadas por pesar
curto/longo conforme o contexto.

**O que isso muda pra nós:** confirma pelo lado biológico o `Banco de τ`
(ter escalas variadas foi selecionado 40× vs 5.3× — doc 31) e dá o MOTIVO:
não é memória, é decodificação de tempo-até-o-evento. Predição 30 (E29b):
se a reação paga, os τ evoluídos das 2 espécies DIVERGEM (razão ≥ 3× em ≥
3/5 sementes) — sede e fome vivem em escalas diferentes (tanque cai em ~200
passos, fome em ~600), e a população precisa de um τ por escala pra
"decodificar" cada urgência. Se convergirem pro mesmo τ, a persistência é
genérica e um só integrador bastava.

### E28 honesto — enxuto (32 genes) vs direto (44): o PISO DE RUÍDO do honesto

| | fit | mortos | por semente (fit) |
|---|---|---|---|
| direto 44 genes | 6.90 | 0.35 | 6.24 7.45 7.18 7.27 6.41 |
| enxuto 32 genes (mesma função) | 6.43 | 0.34 | 5.77 6.88 5.86 6.61 7.02 |

Mesma política, mesma avaliação, só o gerador aleatório muda de forma
(W com 32 colunas em vez de 44) → 0.47 de fit de diferença. Isso é a
régua: **no honesto, diferença < 0.5 fit ou < 0.03 mortos é ruído.**
Reavaliando com a régua: E23 (3 termos = direto) é EMPATE dentro do ruído
(a conclusão "3 termos bastam" fica, a de "melhor" não existe); E20 corpo
fala −1.1 = 2× ruído, real; E24 Noite24 panes −49 % é outra métrica, fica.
Predição 21 (enxuto ≥ direto) não confirmada; tirar os 12 genes mortos não
muda nada, como era de esperar de genes que não entram na conta.

### E29a resultado (2026-09-03, triagem n=3, cidades 1000+): log é MUITO pior

| política | fit | mortos | entregas |
|---|---|---|---|
| direto (linear) | 4.85 | 0.60 | 9.4 |
| noite24 (1 produto) | 5.36 | 0.51 | 10.0 |
| **log (lei de potência)** | **2.19** | **0.81** | 6.7 |

Predição 26 refutada com folga (não é ruído: 3/3 sementes, −2.7 fit). O
mecanismo é geométrico, não químico: `log(x+ε)−log ε` com ε=0.05 tem
inclinação 20 perto de zero e ~1 perto de 1. Pra SENTIR magnitude (Weber–
Fechner) isso é ótimo; pra NAVEGAR é péssimo — a escolha do vizinho compara
`d_alvo` de nós adjacentes, que diferem por um passo em dezenas; no log, ao
longe, todos os vizinhos parecem iguais ("achata o longe") e o argmax vira
ruído das outras features. Resultado: entregas 9.4 → 6.7, e sem entregar não
há dinheiro nem comida (mortos 0.81). A lei da mistura tem multiplicação e
divisão, sim — mas a razão útil no táxi é entre NECESSIDADE e DISTÂNCIA
(Noite24: tanque × d_posto), não o log de cada sinal sozinho. Isso fecha
a pergunta "lei de potência ajuda?": não. A não-linearidade que paga é o
produto com portão → E29b (reações), já na fila.

**E29c (seguimento mecânico, na fila): log SÓ no corpo.** Se o log matou por
achatar o longe, o teste limpo é aplicá-lo só aos 9 sinais internos
(tanque, fome, fadiga, pneu, temperatura, óleo, dinheiro, reserva, dano) e
deixar as distâncias lineares. **Predição 31 (antes de rodar; triagem):**
log-corpo ≈ direto (fit 4.85 ± 0.5, mortos 0.60 ± 0.05) — a escala do
sinal é absorvida pelo gene `w` (regra 15), Weber–Fechner não acrescenta
informação que o gene linear não alcance. Se ficar MELHOR (mortos ≤ 0.52):
o tanque-quase-vazio "gritar" 20× mais alto compra reabastecer a tempo, e
o portão do Noite24 era um substituto disso.

Cidades 2000+ (mesma triagem): direto 2.66 / 0.66 · noite24 2.50 / 0.64 ·
**log 0.72 / 0.86**. A segunda metade da predição 26 ("razões adimensionais
perdem menos ao trocar de cidade: ≤ 30 % vs 45 %") também cai: o log perde
73 % de fit (2.19 → 0.72) contra 45 % do linear (4.85 → 2.66). Faz sentido
pelo mesmo mecanismo: em cidades maiores o "longe" é mais longe, e o
achatamento piora. E29a encerrado: log/lei de potência não entra no lab.

### E29b resultado (2026-09-03, triagem n=3) — reações: o melhor do pacote até hoje

| política | 1000+ fit / mortos | 2000+ fit / mortos | panes | fome fim |
|---|---|---|---|---|
| direto (linear) | 4.85 / 0.60 | 2.66 / 0.66 | 8.4 | 85 |
| noite24 (1 produto) | 5.36 / 0.51 | 2.50 / 0.64 | 8.2 | 80 |
| **reações (sede, fome; portão; τ)** | **7.08 / 0.31** | **4.36 / 0.46** | 5.8 | 70 |

Mortos por semente 1000+: .40 .27 .26 (direto: .60 .51 .67) — as três
sementes das reações ficam abaixo da MELHOR do direto. Predição 27 (mortos
≤ 0.32, fit ≥ 6.6) bate na triagem; vale como afirmação só depois do
honesto (na fila, 5 sementes).

**Os genes que a evolução escolheu (3/3 sementes):**

| semente | τ sede | τ fome | w sede | w fome | portão θ |
|---|---|---|---|---|---|
| 0 | 1.1 | 5.0 | +4.81 | +0.43 | 0.93 |
| 1 | 1.1 | 3.3 | +3.04 | +1.82 | 0.88 |
| 2 | 2.6 | 1.3 | +1.13 | +0.79 | 0.87 |

Leitura: **portão 0.87–0.93** — a reação só liga quando `1 − tanque/cap`
passa de ~0.9, isto é, tanque abaixo de ~10 %. **τ da sede ≈ 1** — a
espécie NÃO persiste; é instantânea. **w sede grande e positivo** — no
código o termo é `−w·a·d_posto`, então +w = "quanto mais perto do posto,
melhor" com força 3–5 (o gene linear de d_posto no direto fica ~0.5–1).
Conclusão mecânica: o que paga não é a persistência química (predição 27
errou o MOTIVO) nem a "mistura" — é um **reflexo de emergência com limiar
alto**: abaixo de 10 % de tanque, esquece tudo e vai ao posto. É o mesmo
portão que o Noite24 aproximava com o produto suave (tanque × d_posto), só
que agora com o joelho no lugar certo e ganho 5×. Fome: τ 3–5 e w menor —
segunda faca, mais fraca.

Predição 29 ("w NEGATIVO em ≥ 4/5"): **errei a letra** — escrevi o sinal
contra a convenção do código (o `−` já está no termo); o mecanismo previsto
(sede empurra PRA o posto) bateu 3/3. Fica registrado como erro de
redação, não como acerto. Predição 30 (τ divergem ≥ 3×): 2/3 na triagem,
mas no sentido oposto ao imaginado — não é "um τ por escala de urgência",
é "sede instantânea, fome com 3–5 passos de memória"; julgo no honesto.

**E29d (ablações do mecanismo, na fila atrás do honesto; triagem):**
(a) *reflexo puro* — τ cravado em 1, portão livre; (b) *reações sem portão*
— θ cravado em 0, reação sempre ligada e proporcional. **Predição 32:**
reflexo puro ≈ reações (fit ≥ 6.6, mortos ≤ 0.35): a persistência não
conta. **Predição 33:** sem portão cai pro nível do Noite24 ou abaixo
(mortos ≥ 0.45): o que paga é o JOELHO em ~10 % de tanque, não a
multiplicação em si. Se (b) ficar igual ao completo: o portão era
decoração e a evolução só usou o ganho 5×.

### E28b — a régua do honesto, com 15 sementes da mesma função

Três medidas do MESMO cérebro (direto 44 genes, sementes 0–4; enxuto 32
genes, sementes 0–4; direto sementes 5–9): 6.90/0.35 · 6.43/0.34 · 6.55/0.40.

| | média (15 sementes) | desvio por semente | erro-padrão (n=5) | diferença mínima detectável (2·EP·√2) |
|---|---|---|---|---|
| fit | **6.63** | 0.52 | 0.23 | **0.65** |
| mortos | **0.36** | 0.067 | 0.030 | **0.085** |

**Régua (vale daqui em diante):** no honesto com 5 sementes, só conta
diferença ≥ 0.65 de fit ou ≥ 0.085 de mortos (≈ 8.5 pp). E o baseline
direto passa a ser citado como **6.63 / 0.36**, não 6.90 / 0.35.

Reavaliando o que já foi dito com a régua:
- E23 mínimo 3 termos (6.91/0.34): empate — "bastam", não "melhor". ✓ como estava.
- E20 corpo-fala (5.83/0.36): −0.8 de fit vs 6.63 → real por pouco; mortalidade igual.
- **E24 Noite24 honesto (6.66/0.32): fit e mortos DENTRO do ruído** — o
  "mortos −3 pp" que registrei era ruído; o que sobra do E24 é panes −49 %
  (8.1 → 4.0), outra métrica, provavelmente real (efeito 2×) mas sem régua
  própria ainda.
- E29b (triagem 0.31 vs 0.60): 29 pp, 3× a régua — se o honesto repetir
  metade disso, é o maior efeito do pacote.

**E29c resultado (triagem n=3): log-corpo 4.67 / 0.63 vs direto 4.85 /
0.60 — igual.** Predição 31 confirmada. Fecha o mecanismo do E29a por
dissociação: log nas distâncias mata (2.19/0.81), log no corpo não muda
nada. A escala do sinal interno é absorvida pelo gene `w` (regra 15);
"tanque quase vazio gritar 20× mais alto" não compra reabastecer a tempo —
o que compra é o JOELHO (portão ~0.9 do E29b), que é outra coisa: não é
mudar a escala do sinal, é mudar QUANDO ele entra na conta.

### E29b HONESTO (R=16, 5 sementes, cidades 1000+) — o efeito encolhe 5×, a estrutura fica

| | fit | mortos | panes | fome fim | idas ao posto |
|---|---|---|---|---|---|
| direto (15 sementes, régua) | 6.63 | 0.36 | ~8.1 | 73 | 3.9 |
| **reações** | **6.97** | **0.30** [.29 .26 .30 .43 .21] | **5.2** | 65 | 5.0 |

Contra a régua do E28b: mortos −6.6 pp (t = −1.6) e fit +0.34 (t = +1.3)
— **abaixo do detectável** (8.5 pp / 0.65). O −29 pp da triagem virou
−6.6 pp no honesto: replicação > σ, de novo. O que é claro: **panes −36 %**
(8.1 → 5.2), mesmo efeito do Noite24 (−49 %), e come mais (fome fim 73 →
65, posto 3.9 → 5.0). Predição 27 bate na letra (0.30 ≤ 0.32, 6.97 ≥ 6.6)
mas a comparação com o baseline não passa da régua — fica como TENDÊNCIA.
Mais 5 sementes (5–9) na fila: com 10, a régua cai pra ~6 pp e decide.

**Genes no honesto (5 sementes):**

| s | τ sede | τ fome | w sede | w fome | portão |
|---|---|---|---|---|---|
| 0 | 7.5 | 39.9 | +4.04 | −0.19 | 0.90 |
| 1 | 1.0 | 11.7 | +4.30 | −0.79 | 0.87 |
| 2 | 1.6 | 1.5 | +2.60 | −0.86 | 0.85 |
| 3 | 134.0 | 2.3 | +0.10 | +1.76 | 0.98 |
| 4 | 6.1 | 4.2 | +3.58 | −0.42 | 0.80 |

A ESTRUTURA replica: portão 0.80–0.98 em 5/5, w sede +2.6..+4.3 em 4/5.
A semente 3 é a exceção — não montou o reflexo da sede (w 0.10, τ 134,
portão 0.98 = nunca liga) e é a que mais morre (0.43 vs 0.21–0.30 das
outras). Correlação dentro do experimento, não prova; mas aponta o mesmo
que o E29d vai testar por ablação. Predição 30 (τ divergem ≥ 3×): 3/5,
e sem padrão de escala — τ da sede vai de 1 a 7.5 nas que usam o reflexo;
a persistência é livre, o que é fixo é o JOELHO.

**Régua das panes (mesma função, honesto):** direto 7.9 · direto s5–9 8.1 ·
enxuto 8.3 → espalhamento 0.4. Panes é a métrica mais estável do lab (o
oposto de mortos). Com ela, o que já é afirmação no honesto: **Noite24 4.0
(−50 %), reações 5.2 (−36 %), mínimo-3 6.6 (−18 %)** — toda forma de
"tanque × distância" (produto suave, portão duro, ou só 3 termos) corta as
panes; a diferença entre elas está DENTRO do ruído de mortos. A pergunta
do dia ("a lei tem multiplicação — isso nos ajuda?") tem resposta medida:
ajuda na pane (metade), não muda a morte além da régua — porque a morte
tem 2.ª causa (fome) que o produto tanque × posto não toca.

**E29e (na fila; triagem): portão POR ESPÉCIE.** No E29b o portão é um só
(0.85–0.98) — pra `fome/100` isso é "só liga com fome > 85", quando o dano
(FOME_CRIT 90) já está batendo. Com um portão por espécie a fome pode
ligar em ~0.6. Verificado: genes 0 == Reativo bit a bit; θ iguais == E29b
bit a bit; sem sync. **Predição 34:** portão da fome evoluído ≤ 0.7 em
≥ 2/3 sementes E fome-no-fim ≤ 60 (vs 65–70) com mortos ≤ 0.28 na triagem
(vs 0.31 do E29b). Se o portão da fome também for pra ~0.9: a fome não é
resolvida por reflexo de distância porque a comida é rara (6 nós) e o
táxi precisa PLANEJAR o desvio, não reagir — e o próximo passo é comida
como parada no caminho (rota), não como reflexo.

### E29d resultado (triagem n=3, 1000+) — ablação: o portão é o mecanismo

| braço | fit | mortos | panes | fome fim |
|---|---|---|---|---|
| direto (referência) | 4.85 | 0.60 | 8.4 | 85 |
| reações completo | 7.08 | 0.31 | 5.8 | 70 |
| reflexo puro (τ=1, portão livre) | 5.53 | 0.40 [.58 .21 .41] | 6.0 | 73 |
| **reações sem portão (θ=0)** | **3.46** | **0.71** | 7.5 | 89 |

**Predição 33 confirmada com folga:** sem o joelho, a reação sempre ligada
fica PIOR que não ter reação (0.71 vs 0.60): o termo `−w·c·d_posto`
proporcional puxa o táxi pro posto o tempo inteiro, ele orbita o posto,
entrega menos (8.0 vs 9.4), fica sem dinheiro e morre de fome (89). É a
mesma doença dos 5 produtos do E17 — multiplicação sem portão é órbita.
O que salva não é multiplicar, é multiplicar SÓ quando o tanque cai
abaixo de ~10 %.

**Predição 32 (reflexo puro ≈ reações) não decidida:** 0.40 vs 0.31, mas as
sementes do reflexo espalham .21–.58 (n=3, regra 13). Panes iguais (6.0 vs
5.8) — o reflexo instantâneo já corta as panes; o que a persistência
poderia acrescentar é na morte. Reflexo puro no honesto na fila.
**Predição 35 (antes de rodar):** reflexo puro honesto fica em 0.30 ± 0.06
de mortos (= reações): persistência não conta, o E29b é um reflexo de
limiar e ponto. Se ≥ 0.36: a espécie lenta compra alguma coisa (o que,
exatamente, o E29e com dois portões vai dizer).

**E29b honesto, cidades 2000+ (5 sementes): 4.34 / 0.42 [.37 .41 .35 .59
.39], panes 7.7** vs baseline pacote direto 3.77 / 0.47. Seis cidades:
**reações 5.66 / 0.36 vs pacote 5.34 / 0.41.** Direção igual nos dois
conjuntos (+0.34 e +0.57 de fit; −6.6 e −5 pp de mortos); cada um sozinho
fica abaixo da régua (0.65 / 8.5 pp). A semente 3 — a que não montou o
reflexo da sede — é a pior nos dois conjuntos (0.43 e 0.59): a estrutura
prevê a morte dentro do experimento. Decisão fica com as sementes 5–9
(10 sementes em 1000+, régua ~6 pp).

### E29b com 10 sementes — AFIRMAÇÃO: o reflexo de emergência mata menos

Sementes 5–9: 7.13 / 0.27 [.38 .12 .33 .17 .32], panes 6.3. Juntando 0–9:

| | mortos (10 sem.) | fit (10 sem.) | panes |
|---|---|---|---|
| direto (15 sementes) | 0.36 | 6.63 | 7.9–8.3 |
| **reações** | **0.28** (sd .095) | 7.05 (sd .80) | 5.2 / 6.3 |
| diferença, não pareada | **−8.2 pp, t = −2.4** | +0.43, t = 1.5 | −30 % |
| diferença pareada por semente (0–9) | **−9.3 pp, t = −3.3, 9/10 sementes** | +0.32, t = 1.2, 6/10 | |

Mortalidade passa a régua (n=10 → ~6 pp): **−8 a −9 pp, 9 de 10 sementes
morrem menos**. Fit: tendência (+0.3–0.4), não afirmação. Panes: −30 %,
claro. Predição 27 confirmada no que importa (mortos), errada no MOTIVO
(não é persistência — é o joelho; E29d).

Em português: dar ao táxi UM reflexo — "abaixo de 10 % de tanque, larga
tudo e vai ao posto" — com o limiar e o ganho evoluídos (7 genes) tira
8 de cada 100 mortes e um terço das panes. É o primeiro mecanismo do
pacote de dentes que passa a régua honesta, e é o mais barato: sem
espécie lenta, sem produto geral, sem log. A trajetória do dia:
triagem −29 pp → 5 sementes −6.6 pp → 10 sementes −8.2 pp. O honesto
com 5 tinha subestimado; a triagem tinha inflado 3×.

### E29e resultado (triagem n=3): dois portões NÃO ajudam — a fome não é reflexo

| | fit | mortos | fome fim | panes |
|---|---|---|---|---|
| reações, 1 portão | 7.08 | 0.31 | 70 | 5.8 |
| reações, portão por espécie | 5.78 | 0.37 [.34 .28 .49] | 73 | 5.5 |

Genes: portão da fome 0.60 / 0.93 / 0.97 (1/3 abriu cedo); w da fome
−0.21 / −0.28 / +0.29 (≈ 0 ou com sinal que AFASTA da comida — a reação
da fome fica desligada ou vira ruído). Predição 34 refutada; cláusula
pré-registrada vale: **a fome não se resolve por reflexo de distância.**
Mecanismo provável: comida em 6 nós de ~250 é rara demais pra "vai pra
comida quando a fome sobe" — o reflexo tira o táxi da rota e ele perde
entregas (fit 5.78 vs 7.08) sem chegar a comer mais (fome fim 73 vs 70).
Tanque é reflexo porque posto é denso (8 nós) e pane é morte imediata;
fome é ROTA — precisa de planejamento do desvio (parar pra comer no
caminho da entrega), não de reação. Próximo passo: autópsia de quem
morre de fome (onde está, quanto dinheiro tem, a que distância da comida
morre, se está com passageiro) antes de desenhar qualquer mecanismo.

### E29d reflexo puro HONESTO (5 sementes): 7.22 / 0.31 [.53 .27 .27 .21 .26], panes 6.3
≈ reações (7.05 / 0.28 em 10 sementes). **Predição 35 confirmada: a
persistência (τ) não conta.** O E29b é um reflexo de limiar: "tanque < ~10 %
→ posto", 5 genes bastam (w, portão, ganho de serviço). A semente 0 (0.53)
repete o padrão da s3 do E29b: quando a evolução não monta o reflexo, a
mortalidade volta ao nível do direto.

### Autópsia (2026-09-03) — quem morre, como, e a intervenção "come forçado"
Campeões honestos rodados em 192 vidas (3 cidades × 64), estado no instante da morte:

| | reações s0 | direto s5 |
|---|---|---|
| mortos | 0.33 | 0.47 |
| morre com fome ≥ 90 | 65 % | 71 % |
| morre com tanque vazio | **0 %** | 2 % |
| dia da morte (mediana) | 3.3 | 3.6 |
| dinheiro ao morrer (mediana) | 56 | 29 |
| distância à comida ao morrer | 3 nós | 3 nós |
| com passageiro a bordo | 76 % | 79 % |
| oportunidades reais de comer faminto (parado em nó com comida, fome ≥ 70), por vida | mortos 4.7 / vivos 10.1 | mortos 8.2 / vivos 13.0 |
| … das quais comeu | 1.1 / 3.0 | 1.2 / 2.7 |
| "comer" vence o argmax quando faminto sobre comida | 40 % (sem pax) / 56 % (com) | 29 % / 42 % |

O reflexo do tanque apagou a morte por pane (2 % → 0 %) e a sangria de
dinheiro (29 → 56). O que sobra: morrer com fome 100, dinheiro no bolso, a
3 nós da comida, trabalhando. A decisão de comer é uma MOEDA (vence 30–56 %
quando deveria vencer 100 %): o placar de serviço `necessidade × gene +
viés` compete passo a passo com o movimento, e o viés é UM só pra 5
serviços — não dá pra afinar "comer" sem mexer em "posto".

**Intervenção (sem evoluir):** forçar "come se fome ≥ θ e há comida aqui":

| | sem força | θ = 70 | θ = 50 |
|---|---|---|---|
| reações s0 | 0.33 | 0.32 | 0.31 |
| direto s5 | 0.47 | 0.38 | 0.40 |

No direto a decisão vale 7–9 pp; nas reações, quase nada — e os mortos
continuam com fome 100 E tanque ~6 E 27–35 % morrendo "sem causa única".
Leitura: a vida é um POOL drenado por várias fontes ao mesmo tempo (fome
0.15/passo, rodar ferido, calor, furo); "fome ≥ 90 ao morrer" não prova
que a fome matou. Próximo passo obrigatório: decompor o dreno de vida por
fonte para os mortos, antes de desenhar mecanismo de comida.

**E30 (na fila; triagem): viés POR SERVIÇO.** A autópsia mostrou que
"comer" vence o argmax só 30–56 % das vezes quando deveria vencer sempre, e
que os 5 serviços dividem UM viés. Quatro genes a mais (viés próprio de
posto, comida, descanso, oficina) — genes 0 == base bit a bit, sem sync.
**Predição 36 (antes de rodar):** reações + viés5 ≤ 0.26 de mortos na
triagem (vs 0.31) e fome-no-fim ≤ 62 (vs 70); direto + viés5 ≤ 0.52 (vs
0.60). Se nada mudar: o problema não é afinar o placar — é que "comer"
compete com "andar" TODO passo (argmax único), e o caminho é decisão em
duas etapas (primeiro "paro aqui?", depois "pra onde vou").

**E30 resultado (triagem n=3): viés por serviço PIORA.** direto+viés5 4.50 /
0.57 (direto 4.85 / 0.60); reações+viés5 4.62 / 0.53 (reações 7.08 / 0.31),
panes 8.9 (vs 5.8), idas ao posto 6–7 (vs 5). Predição 36 refutada com
folga. Quatro genes de viés destroem a vantagem do reflexo: a evolução usa
o viés pra ligar serviço "sempre" (sobre-serve, entrega 9.5 vs 11.3) e o
espaço maior atrasa a busca em 40 gerações. Vale a cláusula: **afinar o
placar não é o caminho; "comer" compete com "andar" a cada passo num
argmax único**. E a autópsia por fonte (abaixo) mostra que o problema
nem é comida.

### Autópsia por fonte e por cidade (2026-09-03) — quem mata é a PANE, e a geografia manda

Campeão das reações (s0), 192 vidas, dreno de vida decomposto por fonte:

| | mortos | vivos |
|---|---|---|
| dreno por fome | 31 (23 %) | 16 |
| dreno por avarias | 108 (77 %) | 121 |
| … das quais pane (6 cada) | 75 (12.5 panes/vida) | 56 (9.4) |
| … calor | 38 | 60 |
| idas à oficina (reparo) | 3.4 | 8.7 |
| panes à noite | 37 % (noite = 33 % do dia) | |

"Morre com fome 100" era a última gota: **77 % do dreno é avaria, e a
avaria é PANE** — mesmo com o reflexo (8–12 panes por vida). Pane não é
noturna (37 % vs 33 % de noite): é proporcional ao rodar. Forçar
"oficina se vida < 50" não muda (0.33 → 0.29) e não sobe as idas dos
mortos (3.4 → 3.5): eles não ESTÃO em nó com oficina quando precisam.

Por cidade (mesmo cérebro):

| cidade | mortos | panes/vida | d_posto média / máx (saltos) | entregas |
|---|---|---|---|---|
| 1001 | **0.17** | 8.6 | 2.2 / **4** | 14.4 |
| 1000 | 0.42 | 12.5 | 2.7 / **7** | 11.2 |
| 1002 | 0.39 | 10.1 | 3.6 / **8** | 9.2 |

A mortalidade acompanha a distância máxima ao posto. O reflexo dispara a
~10 % de tanque — a 4 saltos do posto chega; a 7–8 não. **O limiar certo
depende de onde o posto está**: "abaixo de X → posto" com X crescendo com
d_posto. Isso é o produto tanque × d_posto do Noite24 posto no lugar
certo: dentro do PORTÃO, não no ganho.

**E32 (na fila; triagem): portão por distância** — θ_ef = θ − β·d_posto/8,
1 gene (β = softplus), β→0 == reações bit a bit (verificado), sem sync.
**Predição 37:** β evoluído > 0.3 em ≥ 2/3 sementes; panes ≤ 4.5 (vs 5.8)
e mortos ≤ 0.26 (vs 0.31) na triagem; nas cidades 2000+ o ganho é maior
(mapas com posto mais longe). Se β → 0: a evolução prefere aceitar panes
a gastar entregas com desvios longos — e o preço da pane (6 de vida) é
que está barato demais (lei da moeda cruzada: E33 = D_PANE maior).

**E33 (na fila atrás do E32; triagem): a pane fica cara** — D_PANE 6 → 12 e
20, com o reflexo (E29b). Testa a lei da moeda cruzada no preço da pane.
**Predição 38 (antes de rodar):** com pane a 12, o portão evoluído cai
(≤ 0.85 em ≥ 2/3 sementes, vs 0.87–0.93) e as panes caem ≤ 4.0 (vs 5.8):
o comportamento se adapta ao preço. Mortos: se ≤ 0.31, a adaptação paga o
preço; se ≥ 0.40, a pane cara só mata mais rápido do que o reflexo consegue
evitar — e o gargalo é geometria (E32), não preço.

**E32 v1 resultado (triagem): 4.26 / 0.64 — e a culpa é minha.** Genes: w da
sede −0.08 / −0.05 / −0.29 (3/3): a evolução DESLIGOU o reflexo. Mecanismo:
β = softplus(gene) nasce em 0.69 com gene 0 → o portão abre pra toda a
população desde a geração 0 → quem tem |w| grande orbita e morre primeiro
→ w vai a zero antes de β conseguir encolher → sem reflexo, volta ao nível
do direto (0.60). Erro de parametrização (regra 15, escala do gene, agora
na direção do "nascimento"): **todo gene novo tem de nascer DESLIGADO
(igual ao pai) — a evolução liga se pagar.** Corrigido: β = softplus(gene
− 4) (gene 0 → 0.018), verificado quase idêntico ao reações no perito.
E32b refeito na fila. A predição 37 vale pro E32b.

### E33 resultado (triagem n=3): a pane cara muda o comportamento, não a morte

| custo da pane (vida) | fit | mortos | panes/vida | dano por pane (custo × panes) | entregas | fome fim |
|---|---|---|---|---|---|---|
| 6 (E29b) | 7.08 | 0.31 | 5.8 | 35 | 11.3 | 70 |
| 12 | 6.17 | 0.42 | 2.9 | 35 | 9.9 | 73 |
| 20 | 5.45 | 0.58 | 1.8 | 36 | 8.8 | 82 |

Predição 38: a adaptação existe e é forte (panes ≤ 4.0 ✓, portões abaixo),
mas mortos ≥ 0.40 ✗ → vale a cláusula: a pane cara mata mais do que o
reflexo evita. O achado que não estava previsto: **o orçamento de dano por
pane é CONSTANTE (35–36 de vida por vida)** em três preços diferentes. A
evolução ajusta o número de panes até que o dano marginal iguale o custo
marginal em entregas perdidas — e paga a pane cara com entregas (11.3 →
8.8), dinheiro e comida (fome fim 70 → 82). É o mesmo princípio do
"orçamento" do EXP10/E13: o ser não minimiza pane, minimiza o total. Mudar
o preço no mundo não compra sobrevivência; o que sobra como alavanca é a
GEOMETRIA (E32b: portão que sabe onde está o posto).

Portões evoluídos: custo 6 → 0.87–0.93; custo 12 → 0.50 / 0.84 / 0.86;
custo 20 → 0.63 / 0.79 / 0.76 (cláusula 1 da predição 38 ✓: o joelho desce
quando a pane encarece — o reflexo dispara com 20–40 % de tanque em vez de
10 %). O preço muda ONDE o reflexo dispara; não muda quanta vida sobra.

**E34 (na fila atrás do E32b; triagem): geometria direta — +2 postos.** As
cidades têm 26 nós e 3 postos; acrescento 2 postos nos nós mais longe (em
saltos) dos existentes (wrapper no gerador; lab.py intocado; comida segue
o posto). **Predição 39 (antes de rodar):** com d_posto máx ≤ 4 em toda
cidade, reações ≤ 0.22 de mortos (vs 0.31) e panes ≤ 4.0; direto ≤ 0.50
(vs 0.60). Se as reações NÃO melhorarem: o orçamento de pane é
comportamental (E33), não geométrico, e a autópsia por cidade era
correlação com outra coisa (tamanho das viagens, por exemplo).

**E32b resultado (β nasce desligado; triagem n=3): 5.51 / 0.61 [.38 .63
.82], panes 6.3.** Genes: β 0.52 / 0.74 / 0.31 (a evolução LIGOU o portão
por distância em 3/3 — predição 37, cláusula do β, ✓) mas w da sede caiu
pra 0.89 / −0.07 / 1.74 (vs 2.6–4.3 no reações) e o resultado é pior que
o reflexo fixo em fit, mortos e panes (predição 37 ✗). Mecanismo, agora
de desenho e não de parametrização: **o portão depende da distância que a
própria ação reduz.** Longe do posto o portão abre (θ − β·d), o táxi vai
ao posto, chega perto, o portão fecha, ele volta à entrega, se afasta, o
portão abre de novo — oscilação na fronteira, sem histerese. O reflexo
fixo não tem isso: o tanque só desce até abastecer. Linha encerrada; se
voltar, volta com HISTERESE (portão que, uma vez aberto, só fecha ao
abastecer) — e isso é exatamente uma espécie lenta com τ, que o E29d
disse que não paga. A geometria fica com o E34 (mundo).

### E34 resultado (triagem n=3): o reflexo VALE dois postos

| | 3 postos (padrão) | 5 postos (+2 nos nós mais longe) |
|---|---|---|
| direto | 4.85 / 0.60 / panes 8.4 | **6.87 / 0.37 / panes 5.6** |
| reações | 7.08 / 0.31 / panes 5.8 | 7.22 / 0.30 / panes 4.8 |

Predição 39: direto ≤ 0.50 ✓ (com folga: −23 pp); reações ≤ 0.22 ✗
(0.30, igual). **Pro cérebro sem reflexo a geografia é a alavanca; pro
cérebro com reflexo, mais posto não muda nada** — o reflexo já resolveu o
que dois postos resolvem. Vale a cláusula pré-registrada: o que sobra nas
reações (30 %) é orçamento comportamental (E33), não geometria; a
correlação por cidade da autópsia (0.17 vs 0.42) era com outra coisa
(tamanho das viagens / estrutura), não com d_posto por si. Honesto do E34
na fila (dois braços, 5 sementes) — se confirmar, "reflexo ≡ 2 postos" vira
afirmação: 7 genes compram a mesma sobrevivência que 67 % mais infraestrutura.

### Autópsia: o táxi passa no posto e não enche

Campeão das reações (s0), oportunidades = parado num posto ABERTO com
tanque < 50 %: mortos 3.0 por vida, abasteceram em 1.2; vivos 6.9 / 3.6.
Em ~60 % das chances de encher o tanque, o táxi segue viagem — porque o
MESMO portão (0.9) governa "desviar pro posto" e "abastecer estando no
posto": ele só enche com tanque < 10 %, mesmo parado na bomba. Panes no
meio da rua: 0 % (a pane acontece ao chegar no nó). A cidade 1000 (5
postos) mata 0.59 com d_posto média 1.7 — não é distância; é não encher
quando passa.

**E35 (na fila; triagem): portão separado pra abastecer.** θ_s =
sigmoid(g_θ + g_extra), gene extra 0 → θ_s = θ (nasce igual ao pai,
verificado bit a bit; sem sync). **Predição 40 (antes de rodar):** θ_s
evoluído ≤ 0.6 em ≥ 2/3 sementes (enche com < 40–60 % de tanque quando
já está no posto) enquanto θ do desvio fica ≥ 0.8; panes ≤ 3.5 (vs 5.8) e
mortos ≤ 0.24 (vs 0.31). Se θ_s ficar em 0.9: encher cedo custa mais (3 de
dinheiro por parada? tempo?) do que a pane — e o orçamento de pane do E33
é mesmo a resposta racional do ser.

**E34 honesto, braço 1 (direto, +2 postos; 5 sementes): 7.86 / 0.23 [.22
.31 .29 .16 .18], panes 5.5, fome fim 56, entregas 12.2** — contra 6.63 /
0.36 / 8.1 com 3 postos. −13 pp de mortos e +1.2 de fit: bem acima da
régua (8.5 pp / 0.65). Dois postos a mais são, pro cérebro linear, o maior
efeito do pacote inteiro — maior que o reflexo (−8 pp). Braço das reações
rodando; a comparação decide se "reflexo ≡ 2 postos" ou se os dois somam.

### E34 HONESTO completo (5 sementes, cidades 1000+): postos e reflexo SOMAM

| | 3 postos | 5 postos (+2) |
|---|---|---|
| direto | 6.63 / 0.36 / panes 8.1 (15 sem.) | **7.86 / 0.23 / 5.5** |
| reações (reflexo) | 7.05 / 0.28 / 5.2–6.3 (10 sem.) | **8.49 / 0.18 / 3.9** [.21 .20 .18 .17 .15] |

A triagem (n=3) dizia "mais posto não muda nada no cérebro com reflexo"
(0.31 → 0.30). O honesto diz o contrário: 0.28 → 0.18 (−10 pp, acima da
régua). E o reflexo em cima dos postos: 0.23 → 0.18 (−5 pp, 4/5 sementes,
fit +0.63 — na régua, tendência). Predição 39 no honesto: ✓ nos dois braços.
Correção da conclusão da triagem: **não é "reflexo ≡ 2 postos"; é "postos
e reflexo somam"** — a triagem inverteu o sinal pela 8.ª vez hoje (regra
13 vale pra tudo, não só pra mortalidade pequena).

Estado da arte do programa (cidades 1000+, honesto): **8.49 de fit, 18
mortos por 100, 3.9 panes** — metade da mortalidade do pacote de dentes
original (0.35) com 7 genes de corpo e 2 postos a mais na cidade. Panes
3.9 vs 8.1 = −52 %.

### Regra 18 — o que a triagem PODE dizer (balanço de 2026-09-03)
Hoje a triagem (P=1024, G=40, R=8, 3 sementes) inverteu ou inflou o sinal
em: E19/E20 (pacote), E21 (atenção), E23 (mínimo 5), E27 (pena), E29b
(−29 pp virou −8), E34 (reações "não muda" virou −10 pp) — e acertou só
os desastres (log 0.81, sem portão 0.71, deserto 0.93, E30, E32). Regra:
**triagem serve pra DESCARTAR (deserto, órbita, colapso — efeito ≥ 20 pp
e 3/3 sementes no mesmo sentido); nunca pra afirmar direção fina.** Tudo
que passar da triagem vai pro honesto ANTES de virar frase no doc, e a
frase da triagem é escrita já como "provisório". Custo: 11 min por braço
— mais barato que 8 correções por dia.

### E35 resultado (triagem): 4.63 / 0.60, panes 9.0 — e o diagnóstico é MONTAGEM, não mecanismo
Genes: portão de abastecer foi a 1.00 (nunca) em 2/3; w da sede −0.18 /
+5.00 / +0.02 — o reflexo não se montou em 2/3. Terceira vez hoje que
"reações + 1 gene neutro" (E30, E32b, E35) volta ao nível do direto: com
NP maior a evolução de 40 gerações não consegue MONTAR o reflexo (nem no
honesto ele monta sempre: s3 do E29b, s0 do E29d). Esses três resultados
não refutam os mecanismos — refutam o protocolo. **E36: evolução SEMEADA.**
`evoluir_sementes(W0=…)`: a população nasce do campeão das reações (5
sementes do honesto), genes novos em 0 (desligados, regra 17), ruído
σ = 0.2. Testa o INCREMENTO. Verificado: perito bit a bit (lab.py mudou),
testes ok, 1 geração semeada mantém genes e fitness do campeão.

Braços (triagem, semeados do campeão da mesma semente): reações + portão
de abastecer (E35), reações + viés por serviço (E30), reações + 2 portões
(E29e), e **controle: reações semeadas de si mesmas**. **Predição 41
(antes de rodar):** controle ≥ 6.8 / ≤ 0.33 (o campeão sobrevive à
semeadura); E35 semeado: portão de abastecer < θ em ≥ 2/3 e panes ≤ 4.5 —
o mecanismo era bom e a montagem que falhava; E30 semeado ≈ controle (viés
não ajuda nem atrapalha); E29e semeado: portão da fome ≥ 0.85 (fome não é
reflexo, agora com teste justo). Se o E35 semeado continuar ≈ controle: o
portão único é mesmo o ótimo e encher cedo custa entregas.

**E34 honesto, cidades 2000+ (reações + 2 postos, 5 sementes): 6.12 / 0.29
[.33 .33 .27 .32 .22], panes 3.6.** Seis cidades: **7.31 / 0.235** — contra
5.34 / 0.41 do pacote original (direto, 3 postos) e 5.66 / 0.36 das
reações com 3 postos. Metade dos mortos do baseline de 6 cidades. Panes
3.6–3.9 nos dois conjuntos (era 8): o reflexo + 2 postos corta a pane
pela metade em qualquer mapa.

### E36 resultado (triagem, semeado do campeão honesto): os "desastres" eram montagem

| braço (semeado) | fit | mortos | panes | fome fim |
|---|---|---|---|---|
| controle (reações semeadas de si) | 7.80 | 0.15 | 4.3 | 57 |
| + portão de abastecer (E35) | **8.20** | 0.16 | **3.3** | 53 |
| + 2 portões (E29e) | 8.13 | 0.15 | 3.8 | 54 |
| + viés por serviço (E30) | 8.05 | 0.20 | 3.8 | 59 |

Predição 41: controle ✓ (7.80 / 0.15); E35 semeado panes ≤ 4.5 ✓ (3.3,
−23 % vs controle); E30 ≈ controle ✓; E29e: o portão da fome DESCEU (0.43 /
0.81 / 0.49) mas w da fome ficou ≈ 0 (−0.52 / −0.05 / −0.06) — abre o
portão e não usa; "fome não é reflexo" fica. Do zero em 40 gerações, os
mesmos três desenhos davam 0.53–0.64 de mortos: **era falha de montagem do
reflexo com NP maior, não refutação dos mecanismos** (E30, E32b e E35
ficam reclassificados como "protocolo").

Achado colateral e grande: **o controle semeado (60 + 40 gerações) faz
0.15 de mortos, contra 0.28 do campeão de que nasceu** (avaliação triagem
R=8 vs honesto R=16, então não é comparação exata, mas 13 pp não é R).
O campeão do honesto não está convergido em 60 gerações. Isso muda o
protocolo: **evolução CUMULATIVA** — cada experimento novo nasce do
melhor anterior (como na vida), e compara com o controle semeado do mesmo
pai. Honesto semeado (controle vs abastecer, 5 sementes) na fila.
Correção de fila: os 4 braços gravaram no mesmo JSON (tag igual) — os
genes do controle/abastecer/viés se perderam (números estão nos logs);
honesto relançado com tags distintas.

### 9.2 Por que "um gene a mais" quebrou a montagem — o custo da complexidade (lido 2026-09-03)
**Orr, "Adaptation and the cost of complexity", Evolution 54:13 (2000):** no
modelo geométrico de Fisher, a taxa de adaptação cai pelo menos como
**1/n**, n = número de caracteres independentes, com mutações do mesmo
tamanho fenotípico. Organismo mais complexo adapta mais devagar — e é isso
que o E30/E32/E35 mostraram do zero: com NP 51 → 52–55, as 40 gerações da
triagem que bastavam pra montar o reflexo deixam de bastar (e no honesto de
60 já falhava 1 em 5). **Welch & Waxman, "Modularity and the cost of
complexity", Evolution 57:1723 (2003):** modularidade (mutações que mexem
em poucos caracteres) alivia o custo — no nosso caso, nascer do campeão com
o gene novo em zero é modularidade imposta pelo protocolo: a mutação só
precisa achar UMA dimensão nova, as outras 51 já estão no lugar. Literatura
de evolução aberta (Artificial Life, número especial 2024; "Tokyo OEE"
tipos 2–3: evolução da evolvabilidade, transições maiores) chama isso de
"stepping stones": o próximo degrau só é alcançável de cima do anterior.

Regra 19 (derivada): **variante de arquitetura só se testa SEMEADA do
melhor pai, com controle semeado** — comparar do-zero-contra-do-zero mede
o custo da complexidade (1/n), não o mecanismo. Corolário honesto: as
"refutações" E30, E32b, E35 do-zero medem exatamente isso e ficam no doc
como o que são.
Fontes: https://academic.oup.com/evolut/article-abstract/54/1/13/6758049 ·
https://academic.oup.com/evolut/article/57/8/1723/6755709 ·
https://dx.doi.org/10.1162/artl_e_00445

**E37 (na fila atrás do E36h; honesto, cumulativo): melhor mundo (+2
postos) × melhor pai (campeão do E34, 8.49 / 0.18) × portão de abastecer,
com controle semeado do mesmo pai.** **Predição 42 (antes de rodar):**
controle semeado ≤ 0.15 de mortos (continua melhorando sobre o pai, como
no E36); abastecer semeado: panes ≤ 3.0 (vs ~3.9) e mortos ≤ controle −
0.02; se mortos ≥ controle + 0.03: encher cedo custa entregas/dinheiro e o
portão único do reflexo é o ótimo também no mundo denso.

### E36 HONESTO semeado (5 sementes, 3 postos): abastecer não paga; continuar evoluindo paga

| | fit | mortos | panes | fome fim |
|---|---|---|---|---|
| pai (E29b honesto, 60 ger.) | 6.97 | 0.30 [.29 .26 .30 .43 .21] | 5.2 | 65 |
| **controle semeado (+60 ger.)** | **8.07** | **0.18** [.18 .09 .13 .35 .17] | 4.5 | 61 |
| + portão de abastecer semeado | 8.09 | 0.16 [.13 .13 .21 .17 .15] | 4.8 | 53 |

Portão de abastecer vs controle: −2 pp, +0.3 panes, fit igual → **neutro**
(a triagem semeada dizia panes 3.3 vs 4.3; não replicou — regra 18 vale
até pra triagem semeada). Predição 41, cláusula do E35: ✗.

O que fica: **o pai + 60 gerações vai de 0.30 → 0.18 e 6.97 → 8.07** sem
mudar nada de arquitetura ou mundo. Sessenta gerações não convergem; mais
sessenta valem tanto quanto dois postos (E34: 0.28 → 0.18). A semente 3 —
a linhagem que nunca montou o reflexo — continua a pior (0.43 → 0.35): a
linhagem não descobre o reflexo nem com 60 gerações a mais em cima do
próprio campeão. Montagem é evento raro; depois de montado, refina rápido.

Estado da arte no mundo de 3 postos passa a **8.07 / 0.18** (cumulativo,
120 gerações). Protocolo daqui em diante: evolução cumulativa + controle
semeado; e "gerações" entram como variável declarada em toda comparação.

Genes do honesto semeado: controle mantém o reflexo (w 3.0–5.0, portão
0.81–0.89) em 4/5, s3 segue sem (w −0.19, portão 0.99). No braço com
portão de abastecer, o portão extra ficou ABAIXO do de desvio em 2/5 (0.51
e 0.57; "enche com meio tanque se já está no posto") e igual nas outras —
usado às vezes, sem ganho medível. Anedota de 1 semente: a linhagem s3
MONTOU o reflexo no braço com o gene extra (w +2.33, portão 0.73, mortos
0.35 → 0.17) — um gene neutro a mais mudou a trajetória da mutação o
bastante pra achar o degrau. Vale registrar, não vale afirmar.

**E37 honesto, braço 1 (controle cumulativo: campeão do E34 + 60 gerações,
mundo com +2 postos; 5 sementes): 9.40 / 0.14 [.19 .14 .12 .10 .13],
panes 2.8, fome fim 50, entregas 13.3.** Contra o pai (E34, 8.49 / 0.18 /
3.9): +0.9 de fit, −4 pp, −28 % de panes — o mesmo salto do E36 (continuar
evoluindo paga). Predição 42, cláusula do controle (≤ 0.15): ✓. Estado da
arte: **9.40 / 0.14 / 2.8 panes** (cidades 1000+, 120 gerações, 5 postos).
