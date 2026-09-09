# Um mundo de verdade — física, luz, corpo e morte sem amaciar

Leonardo, 2026-09-09: *"como realmente fazer um mundo de verdade, física, dia e noite, o
ser ver também se fosse possível... para que o mundo seja mais hostil e o ser precise
evoluir. Eu sei que vai ter muitas mortes e não tem problema. Vejo que o Claude Code
tenta amenizar para salvar e não evoluir."*

O diagnóstico está certo. Este documento explica **por que** o reflexo de amaciar
aparece, qual é a única maneira de endurecer sem cegar a medição, e como seria o mundo
se ele obedecesse a leis em vez de a remendos.

---

## 1. Por que o copiloto amacia (é a régua, não a coragem)

A seleção natural não opera sobre mortalidade absoluta; opera sobre **variância de
aptidão**. É o teorema fundamental de Fisher: a taxa de adaptação é proporcional à
variância genética aditiva em aptidão. Se todo mundo morre no dia 6, a variância é zero
e a evolução para — não porque o mundo é duro, mas porque o mundo deixou de **ordenar**
os indivíduos.

Com "sobreviveu 10 dias?" como medida, existem dois tetos e a faixa útil entre eles é
estreita:

- mundo fácil → todos vivem → variância zero → nada é selecionado (foi a "pedra")
- mundo duro → todos morrem → variância zero → nada é selecionado (é o E62 a 15 dias)

Todo endurecimento honesto empurra para o segundo teto, o número piora, e o reflexo
é recuar. **A saída não é amaciar o mundo: é trocar a régua por uma que não sature.**
Isso é o item IV abaixo, e é pré-requisito de todo o resto — sem ele, cada peça nova de
hostilidade vai parecer um retrocesso.

## 2. A lei que falta: conservação e irreversibilidade

Olhe a lista de exploits que vocês taparam à mão: a **pedra** (ficar parado 10 dias com
20 de nascença), o **guincho-subsídio** (N15: a pane devolvia 15 L de graça), o
**hormônio-desconto** (N19: modulação que baratear física vira multiplicador saturado),
o **degrau** (N14). São quatro remendos com a mesma raiz: *no mundo de vocês, existe
ação sem custo e existe tempo sem consequência.*

Mundos reais não precisam de anti-exploit porque duas coisas são verdadeiras neles:
**energia se conserva** (nada é de graça; toda vantagem sai do orçamento de alguém) e
**o tempo é irreversível** (parado também envelhece). Um mundo com essas duas leis mata
a pedra e o guincho-subsídio sozinho, sem cláusula especial — e, o que importa mais,
**mata também os exploits que vocês ainda não descobriram**.

Esse é o critério de projeto que eu proporia para tudo o que vier: *não adicione uma
regra; adicione uma conservação.*

---

## 3. As peças, em ordem de retorno científico

### I. Visão de verdade — uma retina, não um oráculo

Hoje `obs()` chama `_perto_todos()`, que varre o mapa inteiro e devolve a distância
exata ao posto, comida, água, oficina e descanso mais próximos, a cada tick, de qualquer
ponto, para cada uma das 9 opções de movimento. O ser é onisciente; a névoa (E63) é um
remendo desse sintoma. A peça de verdade é uma **retina**:

- **K raios** num campo de visão de abertura θ, orientado pela direção da cabeça
- cada raio devolve **distância ao primeiro obstáculo** e **um rótulo de tipo**
- **oclusão**: prédio na frente esconde o posto atrás (o campo 128×128 de custo que já
  existe serve de mapa de oclusão — é um `gather` ao longo do raio, barato na GPU)
- **alcance limitado pela luz**: de dia R_dia, de noite R_noite ≪ R_dia. A noite deixa
  de ser "o posto fecha" e passa a ser **cegueira**
- **resolução cai com a distância**: o rótulo longe vem ruidoso (ângulo sólido menor)

O que isso cria, de graça e sem cláusula: **memória vira necessária** (você viu o posto
há 200 ticks e agora não vê); **atenção vira necessária** (não dá para olhar para todo
lado — para onde apontar a cabeça é uma decisão); **a noite vira perigosa de verdade**;
e **mapa mental** passa a ser uma função com valor mensurável. É o mundo pedindo
exatamente as peças que hoje são decoração.

**E o sensor custa energia.** Isto é biologia estabelecida: tecido sensorial é caro, e o
custo energético da visão é um limitador real do projeto de olhos em animais (Niven &
Laughlin, *J. Exp. Biol.* 2008; Laughlin sobre energia como restrição do processamento
sensorial). Se cada raio e cada bit de resolução custarem caloria, **quanto enxergar
vira um gene** — e a sua tese ("aloca conforme o mundo pede") passa a valer também para
o sensor, não só para o cérebro. Num mundo aberto e claro, a evolução deve largar a
retina; num mundo ocluído e noturno, deve pagar por ela. Esse é um cruzamento tão bom
quanto o do dia 4.

### II. Uma moeda só: energia, com eficiências

Hoje gasolina, fome, água, fadiga e calor são acumuladores separados com taxas fixadas à
mão (`fuel_passo .15`, `fome_passo .32`, `agua_passo .08`...). Cinco parâmetros
independentes é onde exploits nascem, porque não há nada que os obrigue a fechar conta.

Física: **um orçamento de energia** com conversões explícitas. Comida → reserva calórica
com eficiência η₁; reserva → trabalho metabólico com η₂; trabalho mecânico do veículo →
combustível com η₃; e **calor é o resíduo de toda conversão** (é o que a segunda lei diz)
— então dirigir forte aquece, e aquecer obriga a beber. As taxas deixam de ser cinco
números arbitrários e viram **três eficiências** com significado, o que reduz a
superfície de calibração e faz o calor emergir em vez de ser um acumulador à parte.

### III. Metabolismo com lei de escala — λ deixa de ser parâmetro solto

A "Lei do Metabolismo" de vocês (met = σ²(1+2·dof) = AIC) é uma analogia estatística. A
versão física é mais forte e dá **um valor** em vez de uma varredura:

- taxa metabólica basal escala com a massa como **M^0,75** (lei de Kleiber), não
  linearmente — a estrutura tem retorno decrescente, e isso muda a forma do custo
- **tecido neural é desproporcionalmente caro**: no humano o cérebro é ~2 % da massa e
  ~20 % do metabolismo basal, e a hipótese do tecido caro (Aiello & Wheeler, 1995) diz
  que esse custo é pago cortando outro tecido — não é grátis em lugar nenhum
- dentro do cérebro, a conta é dominada pela **sinalização**: correntes pós-sinápticas e
  potenciais de ação (Attwell & Laughlin, 2001) — ou seja, o custo é do gene *que
  dispara*, não do gene *que existe*

Essa última linha muda o desenho do experimento: hoje `dof_de` conta genes com |w| >
0.5 — cobra por **ter**. A versão física cobra por **usar**: custo ∝ ativação média do
gene ao longo da vida. Um gene que só dispara na emergência é quase de graça; um gene
sempre ligado é caro. Isso é ao mesmo tempo mais realista e mais favorável à sua tese —
é assim que um reflexo raro sobrevive ao custo e um córtex sempre-ligado não.

### IV. Morte sem horizonte — a régua que não satura *(pré-requisito)*

Troque "sobreviveu 10 dias?" por **risco contínuo com vida ilimitada**: a cada tick o
ser morre com probabilidade h(estado), e a aptidão é **tempo de vida** (ou trabalho
acumulado ao longo da vida). Não há teto e não há piso: por mais brutal que o mundo
fique, uns duram 4 dias e outros 11, e a ordenação sobrevive. Fisher fica satisfeito.

Isto é o que permite fazer tudo o que você quer sem nunca mais amaciar. Custa pouco:
o `T` fixo do laço vira um `while` com máscara de vivos que já existe, e a aptidão passa
a somar `t_vida` — que o `campo.py` **já acumula** (`s.t_vida += vivo`).

### V. Seleção mole: reprodução e capacidade de suporte

O passo seguinte, e o que transforma "simulação de sobrevivência" em **evolução de
verdade**: o ser gasta energia para se reproduzir, e o mundo tem capacidade de suporte
(postos, comida e passageiros finitos). Com população regulada pelo ambiente, a seleção
é **mole** no sentido de Wallace (1975): o que decide não é passar de um limiar
absoluto, é ser melhor que os vizinhos. **Hostilidade nunca zera o gradiente** — só troca
quem se reproduz. É a resposta definitiva ao problema do item 1.

### VI. Regime não estacionário — estações, clima, escassez

Vocês já mediram (N19) que hormônio/neuromodulação **não paga sem regime que mude**, e
concluíram corretamente: "próxima chance honesta: mundo com REGIME que exige trocar de
política". Então ponha o regime: estação seca (água escassa, calor alto), inverno
(consumo maior, dia curto), greve de combustível, feriado (demanda alta). Não como
evento aleatório, mas como **ciclo com fase aprendível** — porque é isso que separa
"reagir" de "prever", e prever é a função que a memória de longo prazo teria.

### VII. Outros seres — Rainha Vermelha

Passageiros e postos disputados por N seres coevoluindo. A dificuldade deixa de ser um
parâmetro que você calibra e passa a ser **endógena**: fica exatamente tão difícil quanto
a população é competente. Nunca satura, nunca precisa de recalibração, e é o único
desenho em que "mais inteligente" tem valor ilimitado. Vocês já têm `iara-swarm` e o doc
23 (superorganismo) — a peça que falta é disputa por recurso finito no mesmo mapa.

---

## 4. O que cada lei mata

| exploit / remendo de hoje | a lei que o elimina sozinho |
|---|---|
| pedra (ficar parado sobrevive) | metabolismo basal + envelhecimento (III, IV): parado consome e envelhece |
| guincho-subsídio (N15) | conservação de energia (II): o combustível do guincho sai do caixa de alguém |
| hormônio-desconto (N19) | eficiências explícitas (II): não existe conversão > 1 |
| degrau da mortalidade (N14) | vida ilimitada + seleção mole (IV, V) |
| onisciência (achado 84 / névoa) | retina com oclusão e luz (I) |
| "peça sem custo é decoração" | custo por ativação, não por existência (III) |

## 5. Como isto encaixa no programa de 5 dias

Não substitui — **o item IV entra antes, e é barato.** A régua sem teto vale para tudo
que já está na fila: o cruzamento do dia 4 fica muito mais sensível medindo tempo de vida
do que mortalidade binária, porque a variância volta.

Ordem que eu proporia: **IV (régua sem teto) → I (retina) → III (custo por ativação) →
VI (regime) → V (reprodução) → VII (competição) → II (energia unificada, que é
refatoração e pode vir por último)**. Cada uma com portão de identidade: parâmetro novo
com valor padrão que reproduz o mundo atual bit a bit, como foi feito com `nevoa=inf`.

## 6. O que eu faço além de código

Comparado a um copiloto de código, o que muda é o que posso trazer de fora do
repositório e o que posso fazer com os números depois que eles existem:

- **Revisão de literatura com fontes verificáveis** para as cinco perguntas abertas do
  projeto — evolvabilidade de função de dois sinais (epistasia, paisagens NK, redes
  neutras, variação genética críptica), custo metabólico como seletor de módulos,
  protocolo correto de ablação (knock-out de nascença vs no campeão), métricas de
  aptidão em vida artificial que não saturam, e trilhos de pré-registro. Marcando
  [R] reportado / [E] opinião / [?] controverso e **traduzindo cada achado em mudança
  concreta de experimento**, não em resumo.
- **Desenho estatístico**: potência antes de rodar, fatorial em vez de escada, régua
  pareada, e o cálculo de quantas sementes um efeito exige (já em `analise_campo.py`).
- **Física e biologia do modelo**: as leis de escala, orçamentos energéticos e
  restrições sensoriais deste documento — é daí que vêm valores com significado em vez
  de parâmetros varridos.
- **Figuras de publicação e o artigo**: o laboratório tem seis resultados fechados e
  nenhum texto; isso é trabalho de dias, não de semanas.
- **Instrumentação**: o `dof_por_bloco`, o EEG do ser (série temporal de corpo e decisão),
  o atlas das ~70 pastas de run num índice consultável. Nada disso é difícil; é que
  nunca teve dono.
- **Auditoria adversarial dos próprios resultados** — foi assim que apareceram a
  onisciência, o N15 de volta pela porta dos juízes e o platô que era das alavancas.

O que eu **não** devo fazer é escolher a hipótese. As boas vieram de você: *"me cheira a
bug"* (o guincho era subsídio), *"faça o mundo cobrar"* (E56), e agora *"pare de
amaciar"* — que é o melhor palpite de método desta semana.
