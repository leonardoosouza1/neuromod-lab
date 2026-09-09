# Quantos seres? — e o que mais consertar

Resposta à pergunta "realmente precisamos de muitos seres?", medida nos dados que já
existem, mais três achados novos das corridas e75/e76. 2026-09-09, 21h.

---

## 1. "Seres" são três coisas diferentes, e só uma delas importa para a régua

O projeto usa a mesma palavra para três papéis, e é daí que vem a confusão:

| papel | parâmetro | o que compra | como escala |
|---|---|---|---|
| **candidatos** | `P` (população) | largura da busca genética | qualidade do campeão, com retorno decrescente |
| **vidas do mesmo genoma** | `R` × cópias × mapas | precisão da medida daquele genoma | ruído de avaliação, cai com 1/√(R·cópias) |
| **repetições do experimento** | sementes | precisão da **comparação entre braços** | a régua honesta, cai com 1/√n |

Sua proposta — "poucos seres, muitas sementes" — mistura os três, mas **aponta para o
lugar certo**, e dá para provar com os dados.

## 2. A decomposição: 68 % da variância só some com sementes

Aproveitei uma coincidência do desenho de vocês: **as políticas explícitas são
determinísticas**. Julgar a mesma política em sementes diferentes mede ruído de
avaliação puro, sem evolução no meio. Já um campeão evoluído carrega os dois.

| fonte | DP mediana | como reduzir |
|---|---|---|
| avaliação (política fixa, 72 medições) | **0.0147** | mais cópias/mapas/R — barato |
| total (campeão evoluído, 76 medições) | **0.0258** | — |
| **evolução** (subtraindo em quadratura) | **0.0212** | **só com mais sementes** |

**A evolução responde por 68 % da variância.** Nenhuma quantidade de cópias, réplicas ou
população reduz esses 68 % — só repetir a evolução inteira com outra semente.

E isso explica uma assimetria que o projeto não estava vendo: as duas trilhas têm
resoluções muito diferentes.

| trilha | DP entre sementes | IC95 da média a n=5 |
|---|---|---|
| política (agentes) | 0.0147 | **± 1.3 pp** |
| evolução (baterias) | 0.0262 | **± 2.3 pp** |

O laço de agentes enxerga efeitos quase duas vezes menores que as baterias. Conclusões
tiradas do lado evolutivo são bem mais fracas do que parecem quando colocadas ao lado das
do laço — e foi exatamente isso que aconteceu com a pred 138 (§4 do doc 57).

## 3. O que o mesmo tempo de GPU compra

A bateria da retina custou 796 s com P=512, G=60, R=4, 5 sementes, e detecta **8.5 pp**.
Custo ∝ P·G·R·n. Cortando P para 128 e R para 2, o mesmo tempo paga **20 sementes**:

| configuração | custo relativo | menor efeito detectável |
|---|---|---|
| P=512, R=4, 5 sementes (hoje) | 1.0 | 8.5 pp |
| P=128, R=2, 20 sementes | 1.0 | **3.4 pp** |
| P=128, R=2, 40 sementes | 2.0 | 2.4 pp |

**Mesma GPU, o dobro e meio de resolução** — e passa a enxergar a faixa de 3–5 pp onde
quase todos os efeitos deste projeto vivem.

**A ressalva honesta, e é a única coisa que falta testar.** Cortar `P` pode penalizar
mais o braço de genoma grande (o COMPLETO tem ~500 genes contra 57 do linear), e isso
enviesaria justamente a comparação que interessa. A regra 4 do README de vocês já avisa
na direção oposta ("réplicas antes de população"). Então o teste é obrigatório e é
pequeno: **um braço, P ∈ {128, 256, 512, 1024}, mesmas sementes, medir a qualidade do
campeão.** Se for plano de 128 para cima, corte P para sempre e quadruplique as sementes.
Quatro células. É o melhor retorno por GPU disponível hoje no projeto.

## 4. Três achados novos das corridas de hoje

### 4a. Tirar o hipocampo MELHORA — e o bloco desligado tem mais genes que o ligado

`mundo_vivo_v1` (e75, retina + guincho 10 + régua `vida`), régua de tempo de vida:

| braço | t_vida | corridas | dof |
|---|---|---|---|
| linear | 4.23 d | 11.9 | 0 |
| COMPLETO | 4.12 d | 12.7 | 476 |
| **completo sem hipocampo** | **4.58 d** | **13.6** | 555 |

O braço **sem** hipocampo vive 11 % mais que o completo e 8 % mais que o linear. Com
n=5 e a régua de vida ainda não dá para cravar significância — mas a direção é clara e é
a quarta vez que uma peça nomeada aparece como custo líquido.

E aqui está o controle acidental que vale mais que o resultado. Em `completo.py:54`,
`sem hipocampo` zera o **ganho** do bloco: os genes continuam no genoma, sem efeito
nenhum. Mesmo assim:

- COMPLETO (hipocampo funcionando): **117** genes do bloco `hip` com |w| > 0.5
- sem hipocampo (ganho = 0, genes inertes): **131**

**O bloco que não faz nada tem 12 % mais genes "ligados" que o bloco que funciona.** Sem
seleção puxando, a deriva enche o espaço livremente. Isso prova, com um controle interno,
que `dof` e `dof_bloco` **não medem capacidade usada — medem peso grande**. Toda leitura
de "quantos genes o mundo pediu" feita com esse instrumento está contaminada por deriva,
e o experimento principal do dia 4 daria um falso positivo com ele.

O conserto é o `ativacao_bloco` que a spec §3-F2 pede e que ainda não está no JSON: gene
que dispara conta, gene que só existe não conta. **Até ele existir, eu não usaria
`dof_bloco` como desfecho** — só como descritivo.

### 4b. Custo por ativação empurra para a catatonia

`mundo_vivo_v2` (e76) ligou três coisas de uma vez: λ=0.3, `custo_modo=ativacao` e o
regime. O COMPLETO desabou de 12.7 para **1.1 corrida por vida** (−91 %), com panes 0.7 e
p10–p90 de tempo de vida comprimido em 1.96–3.84 (todo mundo morrendo do mesmo jeito). O
linear, que tem `dof 0` e portanto **não paga custo nenhum**, caiu bem menos (11.9 → 5.6).

Como três fatores mudaram juntos, não dá para atribuir — mas o mecanismo é previsível e
eu errei ao especificar F2 sem ele: **custo puramente por ativação torna o cérebro grátis
enquanto não é usado.** O ótimo passa a ser ter muito tecido e não usar — ou congelar. É
a "pedra" de volta, agora por dentro do metabolismo.

A física não funciona assim: o metabolismo basal é pago em repouso, e é exatamente esse o
ponto da hipótese do tecido caro (o cérebro consome ~20 % do basal humano **em repouso**).
**Correção da spec F2:**

```
custo = λ_basal · dof_existencia  +  λ_ativ · ativacao
```

Com `λ_basal > 0`, parar de agir não escapa da conta. Sugiro `λ_basal : λ_ativ` de 1:2
como primeira tentativa (é a ordem de grandeza do repouso vs sinalização no córtex).
Teste de um fator só: v2 mudando **apenas** `custo_modo`, sem regime.

### 4c. O regime endureceu o mundo para todos

Ainda em v2, o linear caiu de 11.9 para 5.6 corridas. Como a média do multiplicador ao
longo do ciclo deve ser 1.0 (o `test_regime_ciclo` da spec verifica isso), uma queda de
53 % no linear sugere que **o regime não está neutro em média na prática** — provavelmente
porque o ser não consegue aproveitar as fases boas tão bem quanto sofre nas ruins
(assimetria de Jensen: a média do desempenho não é o desempenho na média). Isso não é bug,
é um efeito real e interessante — mas precisa ser medido e declarado, senão vira
"dificuldade escondida" e contamina toda comparação feita em v2.

## 5. Sobre "está tudo disperso" — o diagnóstico concreto

Você está certo, e dá para apontar exatamente onde. Montei um índice de todas as corridas
(`indice_corridas.csv`, **453 linhas de 84 arquivos em 26 pastas**). O que ele mostra:

- **A configuração do mundo mora em três lugares.** Os defaults de `e43_campo.py`, o
  namespace de `politica_util.py:34` e o `cenario.json`. Foi por isso que os juízes
  rodaram com `guincho=0` enquanto as baterias rodavam com `guincho=10` — meses de
  resultados das duas trilhas que **não são comparáveis entre si**, e ninguém tinha como
  ver isso porque a config não está no resultado.
- **Deriva de esquema.** `fitness` está ausente em 302 das 453 linhas; `dof_bloco` em
  7; `t_vida` em 13. Metade das perguntas retrospectivas é arqueologia.
- **Sementes desiguais:** 140 medições com 3 sementes, 65 com 5, 18 com 1.

**O conserto não é reescrever nada.** É uma regra e um arquivo:

1. **Uma fonte de verdade**: o `cenario.json` é a única forma de configurar o mundo; os
   defaults dos scripts passam a ser "carregue um cenário". Duas linhas em cada entrada.
2. **O cenário inteiro vai dentro do resultado**, com um hash. Aí "esta corrida e aquela
   são comparáveis?" vira comparar dois hashes, não ler dois commits.
3. **O índice regenerado a cada corrida** (o `indice_corridas.csv` que já está aí).
   Qualquer pergunta retrospectiva vira uma consulta de uma linha.

Isso é meia hora de trabalho e é o que impede que o próximo `guincho=0` fique seis meses
escondido.

## 6. Sugestões de instrumentação — o que medir que hoje não é medido

Em ordem de valor por linha de código:

1. **`ativacao_bloco`** (§4a) — sem ele o desfecho principal é inválido.
2. **`NP` e o hash do cenário** no JSON — sem `NP`, `dof` não é comparável entre mundos.
3. **Variância explicada por fonte**, gravada na própria bateria: com `R ≥ 2` dá para
   separar ruído de avaliação de ruído de evolução **dentro** de cada corrida, e imprimir
   "esta bateria detecta X pp" no fim. O laboratório passa a saber o que consegue ver
   antes de interpretar.
4. **Trajetória de convergência por semente** (o log já imprime "melhor por semente" a
   cada 5 gerações; basta gravar no JSON). Com isso dá para responder se `P` está
   amarrando: se as 5 sementes convergem para o mesmo valor cedo, a busca não é o
   gargalo e cortar `P` é seguro — que é a ressalva do §3.
5. **Espectro de deriva**: distribuição de |w| por bloco, não só a contagem acima do
   limiar. O controle do §4a apareceu por acaso; com o histograma ele apareceria sempre.
6. **Causa de morte por semente** (já existe agregada) — para saber se as sementes morrem
   do mesmo jeito ou se a média está juntando dois regimes diferentes.

## 7. O que eu faria nesta ordem

1. Teste de `P` (4 células, um braço) — decide se a régua fica 2,5× mais fina de graça.
2. `ativacao_bloco` + `NP` + hash do cenário no JSON (~20 linhas).
3. `λ_basal` no custo (§4b) e re-rodar o v2 mudando **um** fator.
4. Re-rodar `mundo_vivo_v1` com 20 sementes — com a régua nova a n=20, os 0.46 d do
   "sem hipocampo" ou viram achado ou morrem.
5. Unificar a configuração num só lugar (§5).
