# Brainstorm de fórmulas — o cérebro peça por peça, e a física do mundo

Você tem razão em querer isto, mas um brainstorm solto vira uma lista de 50 equações que
ninguém usa. O formato que dá retorno é uma pergunta por peça:

> **a peça consegue EXPRESSAR a função que o nome dela promete?**

Porque se não consegue, "a peça não paga" não é um resultado sobre a peça — é um resultado
sobre a implementação. E metade do ledger de negativos pode estar nessa categoria.

Figura: `auditoria-cerebro.png`. Abaixo, cada peça com a equação canônica da função, o que
o código calcula, e o que fazer.

---

## 1. Reflexo — FIEL

```
canônica   a_ref = max(0, c − θ),   τ_c ċ = (1 − f/100) − c
no código  igual; empurra para o posto (w) e liga o abastecer (v)
```
Arco reflexo é exatamente isto: laço rápido, ganho fixo, contorna o córtex. É a única peça
que é o que diz ser — e tem **3 dos 4 genes ligados em toda corrida**. Não é coincidência:
peça que faz o que promete, a seleção mantém.

## 2. Tálamo — GANHO SEM DENOMINADOR

```
canônica   r_i = g_i·x_i / (σ + Σ_j g_j·x_j)          normalização divisiva
no código  g_k = 2·σ(a_k + b_k·need + c_k·pax);  q += F·[W(g−1)]
```
Falta o **denominador**. Sem ele, os cinco portões podem valer 2.0 ao mesmo tempo: não há
recurso escasso, logo não há atenção — há escala. Atenção é, por definição, *o que você
deixa de olhar*.

E repare na convergência: **o termo de pressão do §E é o denominador que falta aqui.**
Não é um órgão novo — é completar o órgão que já existe. Uma linha:
`gate ← gate · min(1, NG / Σ_k gate_k)`.

## 3. Córtex — TEMPERA A POLÍTICA, NÃO TROCA

```
canônica   w_f^ef = w_f·(1 + δ_{d,f}),  d = contexto INFERIDO
no código  δ = 0.5·tanh(·), |δ| ≤ 0.5,  d = distrito DADO pelo mundo
```
Dois limites, e o segundo é grave:

1. **O contexto é dado.** O mundo entrega o número do distrito. Córtex real infere o
   contexto a partir da observação — e inferir contexto é metade do trabalho.
2. **`|δ| ≤ 0.5` não inverte sinal.** No distrito industrial a densidade de comida é
   **0.0** e no residencial é **2.0** (está no `cenario.json`). A política ótima nesses
   dois lugares tem sinais opostos para `d_comida` — e essa peça, por construção, só
   consegue temperar em ±50 %. **Ela não pode expressar a política ótima do próprio mundo
   em que está sendo testada.**

Conserto barato e decisivo: `δ = A·tanh(·)` com `A` evoluído (ou fixo em 2.0) e um teste
de sensibilidade que confirme que o sinal pode inverter.

## 4. Hipocampo — É UM DIÁRIO, NÃO UM MAPA

```
canônica   M(s,s') = E[ Σ_t γ^t 1[s_t = s'] | s_0 = s ]     representação de sucessor
no código  MEM[d,k] ← MEM[d,k] + (evento_k − MEM[d,k])/τ_h  média móvel por distrito
```
O hipocampo canônico é um **mapa preditivo**: guarda para onde você tende a ir a partir
daqui. O do projeto guarda a **média do que já aconteceu** em 12 caixas. Sem sequência,
sem predição, sem lugar além do índice do distrito.

E tem um detalhe que o próprio código confessa. Em `camadas.py` a memória entra como
escalar constante nas 9 opções — o comentário diz *"desloca mover-vs-servir, não a
direção"*. É o **achado 84 aplicado à memória**: a peça é estruturalmente cega para o
volante. Em `completo.py` ela entra bilinear e consegue dirigir, então o resultado
significativo de hoje (sem hipocampo bate COMPLETO, p = 0.022) é sobre a versão que
*consegue* — e mesmo assim ela é custo líquido.

## 5. Camadas rápida / lenta — FIEL

```
canônica   τ_i ẋ_i = −x_i + relu(Wx + W^s s),  τ ∈ {5, 25, 100}
no código  igual, com banco de τ evoluído
```
É uma rede líquida discreta, e é onde a evolução põe **62–67 %** dos genes que liga. A
peça mais genérica é a preferida — e é a que ninguém desenhou como órgão.

## 6. Gânglios da base — EXISTE, MAS É DE GRAÇA

```
canônica   P(a) = softmax(q/T)   ou WTA por inibição lateral
no código  a = argmax_g q_g      em código, fora do genoma, custo zero, T → 0
```
A biologia gasta um núcleo inteiro selecionando ação; aqui é uma linha fora do genoma.
Duas consequências: a seleção de ação **não pode evoluir** (nem a temperatura, nem a
histerese, nem o viés de permanência), e o ser é **determinístico** — não existe "tentar
diferente" dentro de uma vida.

Conserto de uma linha com efeito grande: `a ~ softmax(q/T)` com `T` evoluído. Se a
evolução escolher `T → 0`, ela confirma o desenho atual; se escolher `T > 0`, exploração
dentro da vida paga — e isso é um resultado publicável sozinho.

## 7. Cerebelo — AUSENTE

```
canônica   ŝ(t+1) = f_φ(s(t), a(t));   ε = s(t+1) − ŝ(t+1)
```
Nada no sistema prevê nada.

## 8. Dopamina / erro de predição — AUSENTE, e é o buraco principal

```
canônica   δ(t) = r(t) + γ·V(s(t+1)) − V(s(t))
```

---

## A conclusão: não falta uma peça, falta uma grandeza

Olhe a coluna "no código" de cima a baixo. **Todas as peças mapeiam presente → ação.**
Nenhuma forma uma expectativa e a compara com o que aconteceu.

E memória só paga quando existe predição. Um hipocampo sem leitura preditiva é um diário
que ninguém consulta — guardar o passado só vale se alguém for **usar** aquilo para
antecipar. Isso explica de uma vez três resultados que o laboratório trata como separados:

- **N1** (memória não vence reativo) — não há erro de predição para a memória alimentar;
- **hipocampo decorativo** — mesma causa;
- **"cérebro completo = linear"** — as peças a mais não têm o que computar.

E `δ(t)` é justamente o que o neuromodulador deveria transportar (dopamina *é* o erro de
predição de recompensa no cérebro). Então **as duas coisas que faltam — hormônio como
campo e erro de predição — são a mesma adição vista de dois lados**: um campo que difunde
carregando δ.

Isso é uma predição testável e forte: *num mundo com regime, um cérebro com δ e memória
bate um cérebro com memória sem δ, e a diferença some quando o regime é removido.*

---

## A física do mundo — o que existe e o que falta

| grandeza | hoje | falta |
|---|---|---|
| posição | campo de custo 128×128, κ = 1/3 | — |
| velocidade | instantânea: `p ← p + v·d̂` | **inércia**: sem massa e sem aceleração não há nada para antecipar. Frear exige prever |
| energia | 4 escalares separados (dinheiro, gasolina, caloria, calor) | **conservação** — a fonte de toda exploração já encontrada |
| calor | sobe 0.15 andando, desce 0.6 parado | balanço térmico: hoje o calor não vem de lugar nenhum e não vai para lugar nenhum |
| luz | dia/noite, alcance da retina | — (F3 resolveu) |
| regime | multiplicadores 1 + A·sin, período 5 dias | **período errado** — ver abaixo |
| trânsito | campo estático de custo | dinâmico foi tentado e refutado (N3) |
| população | 1 ser por mundo | capacidade de suporte, reprodução (F5, F6) |

### O parâmetro do regime está errado, e dá para calcular o certo

Plasticidade (e memória, e predição) só paga quando a regularidade varia **mais rápido que
as gerações e mais devagar que as decisões**. Fora dessa janela, ou o genoma fixa a
resposta, ou nada é aprendível.

Hoje: período do regime = **5 dias**, tempo de vida = **3.4 a 4.6 dias**. O ser morre antes
de completar um ciclo — ele nunca vê a fase se repetir, então não há nada a aprender
*dentro* da vida, e como a fase varia entre vidas o genoma também não pode fixar.
**É o pior dos dois mundos, e explica por que o v2 só piorou.**

Regra: **período ≈ 1/3 do tempo de vida esperado**, para o ser viver 2–3 ciclos. Com
`T_vida ≈ 4 dias`, o período deveria ser **~1.3 dias**, não 5. É um número no
`cenario.json`.

---

## O que eu tentaria, na ordem

| # | mudança | custo | o que decide |
|---|---|---|---|
| 1 | denominador no tálamo (= §E) | 1 linha | atenção vira recurso escasso; conserta a catatonia |
| 2 | amplitude do córtex `A` evoluída | 1 linha | a peça passa a poder inverter sinal — hoje não pode |
| 3 | período do regime ≈ ⅓ da vida | 1 número | põe a plasticidade na janela onde ela pode pagar |
| 4 | `softmax(q/T)` com `T` evoluído | 1 linha | exploração dentro da vida; e testa se o argmax era certo |
| 5 | `δ(t)` = erro de predição como sentido | médio | a grandeza que falta; e dá o que o hormônio transporta |
| 6 | hormônio como campo (`∂η/∂t = D∇²η − λη + s`) | médio | espaço e atraso na neuromodulação |
| 7 | inércia (massa, aceleração) | médio | cria o que prever |
| 8 | orçamento único de energia | refatoração | fecha a classe inteira de exploração |

Os quatro primeiros somam **quatro linhas e um número** — e cada um deles ataca um
resultado nulo já registrado no ledger. Eu começaria por eles antes de qualquer peça nova.
