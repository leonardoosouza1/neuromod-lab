# Onde o laboratório está travado — diagnóstico de 2026-09-08

Você pediu as lacunas. Observabilidade e otimização são duas delas e estão
abaixo, mas nenhuma é a principal. A principal é do **mundo**, e explica de uma
vez o cérebro que não paga, o hipocampo decorativo e o "canhão para o que não
precisa".

---

## 1. O gargalo: o ser é ONISCIENTE

Em `campo.py`, `obs()` chama `_perto_todos(s.pos)`, que **varre todos os pontos
de cada tipo de serviço no mapa inteiro** e devolve a distância exata ao mais
próximo. Não há raio de visão. A cada tick, de qualquer ponto de um campo de
200×200, o ser sabe exatamente a que distância está o posto, a comida, a água,
a oficina e o descanso mais próximos — e sabe a distância de cada uma das 9
opções de movimento a cada um deles. Os passageiros idem (`alvo()` devolve o
mais próximo).

Nesse regime, a política ótima **é** um gradiente descendente de um passo sobre
números que o mundo entrega prontos. Isto é: o mundo já resolveu o problema
espacial; sobrou escolher o coeficiente. É exatamente o que a evolução acha —
e é por isso que:

- o cérebro completo empata com o linear (0.64 vs 0.63) e 300 gerações não
  mudam;
- o **hipocampo** (memória de lugar) fica com 70–90 % dos genes acima de 0.5 e
  **+2 pp** de efeito: não há o que lembrar, a informação chega de graça a cada
  tick;
- o **córtex** (política por distrito) quase não paga: o distrito não carrega
  informação que a distância já não dê;
- com λ = 0.3 a evolução larga 352 de 355 genes: correto — nenhuma peça tem
  função **neste** mundo.

E vocês **já provaram isso**, em outro repositório, meses atrás: em
`neuromod/`, `new/`, `novo/` está registrado como teorema + medição —
*"memória é inútil em MDP totalmente observável"*. O mundo-táxi é um MDP
totalmente observável. O resultado do E54 não é um resultado sobre cérebros; é
o corolário empírico daquele teorema.

**Consequência para a meta.** "Cérebros pequenos que alocam peso conforme o
mundo pede" não pode ser observado num mundo que não pede nada. O canhão não é
grande demais — o alvo é que está a um metro. Antes de mexer no cérebro, o
mundo precisa **esconder**, não só cobrar. Vocês já fizeram *cobrar* (λ, E55) e
*diferenciar* (distritos, E56). Falta o terceiro eixo.

### O experimento (E63 "névoa") — implementado e com portão passado

Patch de 4 linhas em `campo.py`: a distância percebida a um serviço **satura**
num raio `nevoa`; além dele o gradiente some (mover-se na direção de um posto
invisível não muda a nota). A distância verdadeira continua valendo para a
física (serviço por contato, raio 6; reboque da pane) — névoa é percepção, não
teleporte. `auton` e `e_risco` passam a ler a distância **percebida**, senão
vazam a resposta.

- `nevoa=inf` (padrão) é **idêntico bit a bit** ao código de hoje — portão
  rodado em CPU aqui, 2 braços × 2 sementes, todas as 17 medidas iguais.
- Régua para escolher o raio, medida no mundo distinto L=200 (256 posições,
  4 mapas): distância ao posto mais próximo tem percentis 10/25/50/75/90 =
  **8.9 / 15.4 / 26.5 / 43.8 / 61.2**. Logo `nevoa` 40 / 25 / 15 = posto
  visível ~70 % / ~50 % / ~25 % do tempo. Escada honesta, não chute.

Com névoa, cada peça do cérebro passa a ter uma função **nomeável antes de
rodar**: hipocampo = onde eu vi um posto neste distrito; córtex = neste
distrito compensa procurar, naquele não; tálamo = quando a luz acende, olhar
para o canal certo; lenta = integrar avistamentos.

---

## 2. Alocar peso conforme a necessidade: hoje o mecanismo só sabe PODAR

A meta é o ser **alocar** genes conforme o mundo cobra. O mecanismo atual não
consegue expressar isso, por duas razões de construção:

**(a) O genoma nasce inteiro.** Toda arquitetura nasce com os 460 genes (em
zero, transparente) e λ só **remove**. Não há como um gene *aparecer* porque
passou a fazer falta. Alocação exige **complexificação**: começar na espinha e
aceitar um gene novo apenas quando a mutação que o liga paga o próprio
metabolismo — que é literalmente a sua Lei do Metabolismo usada como critério
de aceitação, não como imposto de fundo.

**(b) O custo é um degrau, o benefício é contínuo.** `dof_de()` conta
`|w| > gene_min` (0.5). Um gene que liga aos poucos **paga o imposto inteiro no
instante em que cruza 0.5**, quando o benefício dele ainda é quase zero. Isso é
um vale de aptidão construído pelo próprio contador: a evolução nunca vê o
degrau valer a pena. Trocar por custo suave (λ·Σ w²/(w²+w₀²), que tende ao
mesmo AIC quando os pesos são grandes, mas é diferenciável na subida) remove o
vale sem mudar a lei. **Isso pode ser a causa do "nada paga em λ ≥ 0.3", e é
barato de testar.**

---

## 3. Otimização — o que está frouxo na busca

Lendo `evoluir_sementes()`:

| hoje | problema | conserto |
|---|---|---|
| seleção por truncamento (elite 15 %) + mutação gaussiana σ=0.3 fixa, **sem crossover, sem torneio, sem niching** | paisagem bimodal (N4: 1/3 das sementes acha a bacia boa) e monocultura; o `diversidade` já é registrado nos snapshots mas não realimenta nada | fitness sharing / niching — o `iara-swarm` já tem um motor testado com isso, é reúso e não código novo |
| σ=0.3 **igual para todo gene**, clamp ±5 igual para todo gene | é por isso que existe "escala 1 vs escala 3": o gene de risco precisa valer ~12 e o clamp corta em 5, então a escala vira parâmetro de mão. E foi por isso que a semeadura afogou a espinha | σ por bloco, auto-adaptativo (o próprio genoma carrega log σ). Some a escolha manual de escala |
| semeadura `w = base; w += randn*sigma0` — o ruído cai **também sobre a espinha copiada** | é exatamente o modo de falha que custou E54–E57 ("semeado contaminado") | ruído só nos genes novos; espinha com σ menor |
| fitness escalar (`bemestar` = soma ponderada de 5 termos) | a "pedra" (viver parado) e o "dirigir menos" do E61d são ótimos legítimos dessa soma. O critério `entregas ≥ 15` é um remendo **por fora** da seleção | multi-objetivo (NSGA-II) em (sobreviver, entregar): a pedra e o trabalhador ficam em pontos diferentes da fronteira **por construção**, e a fronteira é a métrica de "juízo" que falta na pergunta aberta 4 |

---

## 4. Observabilidade — o que eu construo sem GPU

Você tem 50 pastas de run e nenhum índice; o JSON guarda por semente só `fit` e
`mortos` (todo o resto é média, então panes/entregas **não podem** entrar em
teste pareado); e a autópsia de campeão é feita à mão, como no E61d.

1. **`indice.parquet` + painel único** sobre `universe-runs/neuromod-lab-taxi/`:
   uma linha por (bateria, braço, semente) com config, medidas, veredito e o
   link para a predição do ledger. Responde "onde ficou o número X" em segundos.
2. **Por-semente para todas as medidas** — três linhas em `e43_campo.py`
   (`med[k+'_por_semente']`). Sem isso metade da régua pareada fica inacessível.
3. **Autópsia automática**: gene → nome (`NOMES_F` / `nomes_genes()`), quais
   entraram, com que sinal, e a correlação de cada unidade com cada sentido —
   o que você fez à mão para achar `M[risco, d_posto] < 0`.
4. **EEG do ser**: série temporal de corpo/decisão de um campeão, já existe em
   pedaços (`diag_oraculo`, `retrato_*`) e nunca virou instrumento fixo.

---

## 5. O que aconteceu enquanto eu escrevia isto (12:53)

O honesto de 10 dias fechou e **a predição 88 deu ✗**: em 10 dias o
bilinear-risco morre igual ao linear (0.97 vs 0.97) e o só-camadas corta as
panes **parando** (1.0 pane, fome 89). O 0.46 de 5 dias era "dirigir menos" —
exatamente a ressalva que estava registrada. Isso muda duas coisas neste
documento, e para melhor:

- O item 1 fica **mais** forte, não menos: a única coisa que o cérebro grande
  conseguiu fazer com as próprias peças foi degenerada (parar). Num mundo que
  entrega todas as distâncias, "não se mover" é a política mais barata que
  sobrevive ao horizonte — e nenhuma peça é necessária para não se mover.
- Sua correção (`riqueza` = bemestar + renda/300, e 15 dias) ataca o item 3,
  linha da fitness escalar. **Mas continua sendo uma soma ponderada**: qualquer
  peso escolhido antes tem um ótimo degenerado do outro lado. Se `renda/300`
  for pouco, a pedra volta; se for muito, o ser dirige até morrer de fome. O
  conserto estrutural é a fronteira de Pareto em (sobreviver, renda): a pedra e
  o trabalhador viram **pontos diferentes da fronteira**, você escolhe depois
  de ver, e a fronteira é a métrica de juízo que falta na pergunta aberta 4.
  A soma serve para rodar amanhã; a fronteira serve para não voltar a esse
  problema.

Por isso a fila do E63 já vem com `--fitness riqueza --dias 15`: a névoa tem de
ser testada em cima da régua nova, não em cima da pedra.

---

## 6. Ordem que eu proponho

1. **E63 névoa** (patch pronto, portão passado, fila escrita) — é o teste de se existe mundo
   onde uma peça paga. Sem isso, todo trabalho de arquitetura mede o teto do
   mundo, não o do cérebro.
2. **Custo suave** (item 2b) — barato, e pode desbloquear o λ.
3. **Observabilidade** (item 4) — eu faço em paralelo, sem GPU.
4. **σ por bloco + multi-objetivo** — depois que a névoa disser se há sinal.
5. **Complexificação** — só faz sentido depois de existir um mundo que pede.

---

## 7. Pré-registro — E63 névoa (registrado 2026-09-08, antes de rodar)

**Pergunta.** Existe algum nível de cegueira em que uma peça do cérebro paga o
próprio metabolismo?

**Mundo e protocolo.** distinto pobre · L=200 · **15 dias** · `--fitness riqueza`
· guincho 10 + 5 L · `NM_RISCO=1` · P=1024 · G=120 · R=8 · sementes 0–4 ·
4 níveis de névoa (inf / 40 / 25 / 15 → posto visível 100 / ~70 / ~50 / ~25 %
do tempo, percentis medidos, não chutados) · braços: linear, bilinear-risco
esc 3, só-camadas, COMPLETO.

**Portões.** `--perito` na GPU antes da 1ª etapa; identidade `nevoa=inf` vs HEAD
**já passou** (CPU, 17 medidas × 2 braços × 2 sementes, bit a bit).

**Predições.**

| # | afirmação | critério | aposta |
|---|---|---|---|
| a | névoa piora todo mundo | mortalidade cresce monotonicamente em inf → 40 → 25 → 15 no braço linear | ✓ |
| b | **a névoa é o mundo onde a memória paga** | em nevoa ≤ 25, só-camadas/COMPLETO batem o linear por ≥ 10 pp **pareado por semente** com `ent ≥ 15` (não é pedra) | ✓ |
| c | e paga com custo de gene | em nevoa 25 com λ=0.3, o `dof` sobrevivente é ≥ 30 (hoje: 3 de 355) e concentra no bloco de memória | ✓ |
| d | o hipocampo deixa de ser decoração | ablação do hipocampo no campeão de nevoa 25 piora ≥ 10 pp (hoje: +2 pp) | ✓ |

**Cláusula de escape.** Se (b) der ✗ com névoa 15 e mortalidade ≥ 0.95 em todos,
o mundo virou impossível em vez de difícil — o diagnóstico é `ent` do braço
linear: se caiu a zero, refazer com névoa 40/60 antes de concluir qualquer coisa
sobre peças.

**Como isto morre.** Se em nenhum nível de névoa nenhuma peça bater o linear
pareado, então a tese "o mundo é que não pede" está refutada **para este eixo**,
e o problema é da arquitetura de memória — o que joga a aposta para o Minecraft
(`mc-farol`), onde a observação é parcial por construção.

**Confusão conhecida (declarada antes).** Saturar a distância em `nevoa`
**também comprime a escala** do sentido: com névoa 15 as distâncias vivem em
[0,15] em vez de [0,280], e o peso efetivo do bloco de direção muda junto.
Portanto a comparação válida é **entre arquiteturas dentro de um mesmo nível de
névoa** (é a comparação que interessa). A escada de névoa serve para achar o
regime, não para medir "quanto o mundo ficou difícil".

**Custo.** 5 etapas × 4 braços × 120 gerações × R=8 em 15 dias. Na GPU, pelos
tempos do E60 (1389 s para o COMPLETO em 120 ger., 10 dias, R=4), estimo
**8–14 h para a fila inteira** — vale rodar `e63c_nevoa25` (a etapa que decide
(b)) primeiro, sozinha, ~2–3 h.
