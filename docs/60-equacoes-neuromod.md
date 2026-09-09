# As equações do neuromod-lab

Você está certo em não querer uma equação só. Corpo e cérebro são sistemas **diferentes**,
com escalas de tempo diferentes, acoplados por **poucas variáveis** — e é isso que dá para
escrever com precisão, porque o código já é essa estrutura, só que espalhada.

Cada equação abaixo tem o ponto no código e um estado: **existe e está certa**, **existe
mas está errada**, **falta**. Figura: `equacoes-neuromod.png`.

---

## 1. As cinco escalas de tempo

| escala | duração | quem vive nela |
|---|---|---|
| tique | 1 passo | mundo, corpo, decisão do cérebro |
| ~1 a 160 tiques | banco de τ | estados internos rápido/lento |
| dia | 240 tiques | ciclo de luz, aluguel, preços |
| episódio | até a morte | vida, `T_vida`, aptidão |
| geração | 1 população | seleção, mutação |

Um sistema é "diferente" do outro exatamente quando vive em outra escala. Corpo e cérebro
compartilham a escala do tique, e é por isso que o acoplamento entre eles é o lugar
sensível — os dois se atualizam ao mesmo tempo, todo passo.

## 2. Mundo (tique)

```
p(t+1) = p(t) + v · d̂_a(t) / κ(p)          κ = 1 na rua, 3 fora
π_k(t) = π_k⁰ · μ_distrito · [1 + A·sin(2πt/T + φ_k)]
```
A rua não é um grafo: é um **campo de custo** amostrado em 128×128. Isso é o que permite
gradiente contínuo em vez de busca em nós — e é o que torna a retina possível.

## 3. Corpo (tique) — oito estados, uma morte

```
ḟ = −c_f κ ω m(t)·[andando] + ℓ·[abastece]      gasolina   c_f = 0.15
ḣ = +c_h · m(t)                                  fome       c_h = 0.32/tique = 77/dia
ẇ = −c_w − c_w^calor·[θ > 60]                    água       c_w = 0.08
θ̇ = +c_θ κ·[andando] − c_θ⁻·[parado]             calor      sobe 0.15 / desce 0.6
Ḋ = τ_via μ (1−α)·[entrega] − Σ π_k q_k − aluguel/240
V̇ = −dano(h, w, θ, D)                            morte: V ≤ 0
```

**A vida é o integrador.** É ela que faz o corpo ser *um* sistema em vez de oito escalares
correndo em paralelo: todos os déficits desaguam nela, e é ela que fecha o episódio.

## 4. O acoplamento — e é aqui que está o problema

São só **duas** variáveis ligando corpo e cérebro:

**Corpo → cérebro (interocepção).** Os sentidos do corpo entram em `s` e o cérebro lê o
próprio estado. Largura: 16 dos 27 sentidos.

**Cérebro → corpo (a conta).**
```
m(t) = 1 + λ_b · dof(W)/100 + λ_a · ‖ativ‖/100         campo.py:478-491
```
e o `m(t)` entra **em um único lugar**: `ḣ = c_h · m(t)`. Ou seja, **o cérebro paga
exclusivamente em fome.** Não paga em gasolina, não paga em calor, não paga em água.

Isso é uma escolha de modelagem que nunca foi discutida, e tem duas consequências:

1. Com `λ = 0.3` e `dof ≈ 350`, `m ≈ 2.05` — o cérebro **dobra** a taxa de fome. Não é um
   custo marginal, é uma conta que compete com o metabolismo inteiro do corpo. Explica por
   que a evolução larga 352 de 355 genes: o preço é brutal ou é zero, não há meio-termo.
2. Como o canal é o mesmo da morte dominante (fome é 55–60 do dano total), **o custo do
   cérebro e o custo de existir são indistinguíveis pela seleção**. Ela não consegue
   separar "meu cérebro é caro" de "eu tenho fome".

**O `λ_b` (basal) já existe no código** (`campo.py:479`) — e não foi ligado no cenário v2.
A catatonia do v2 não foi falta de implementação, foi um campo de configuração em zero.

## 5. Cérebro (tique a ~160 tiques)

```
s_gj(t) = Φ_j(W, b, g)                            27 sentidos × 9 opções
τ_i ẋ_i = −x_i + σ(W^xx x + W^xs s)               camadas rápida/lenta, banco de τ
q_g(t)  = Σ_j w_j s_gj + extra(x, s; W)
a(t)    = argmax_g q_g
```

Duas observações que o código revela e que não estão em nenhum documento:

- **O ser é determinístico.** Dado `(W, mundo, semente)` não há um único sorteio na
  decisão. Toda a variabilidade vem do mundo. Isso é bom para reprodutibilidade e é
  provavelmente ruim para exploração: não existe "tentar algo diferente".
- **A equação de `x` é uma rede líquida discreta** — e é onde estão 62–67 % dos genes
  ligados, contra 24 % no hipocampo e 1 % no reflexo. A evolução escolhe a parte líquida.

**O que falta no cérebro (as duas bolinhas vermelhas):**

```
Σ_b ‖a_b(t)‖ ≤ B                                  vínculo global (o termo de pressão)
∂η/∂t = D∇²η − λ_η η + s_glândula(x,t)            neuromodulador como campo
```

Sem o primeiro, os blocos **somam** em vez de competir — não existe "atenção" no sentido
de recurso escasso. Sem o segundo, o hormônio é escalar, global e instantâneo, e por isso
nunca teve nada a fazer que um peso fixo não fizesse (é a raiz do N19).

## 6. Vida (episódio) e evolução (geração)

```
T_vida = min{ t : V(t) ≤ 0 }
aptidão = T_vida/240 + w·renda/300                 régua `vida`, validada
F(W)    = (1/R) Σ_r fit(W, ξ_r)
W' = W_elite + σ·ε,  ε ~ N(0, I)                   σ fixa, corte ±5, sem crossover
```

A régua `vida` está validada: mortalidade 1.00 em todas as sementes e o tempo de vida
ainda separando de 1.7 a 7.3 dias. A evolução é o elo mais fraco: 68 % da variância vem
dela, e σ fixa com corte em ±5 é o operador mais simples possível.

E falta uma equação estrutural: **reprodução dentro do episódio** (F5). Hoje a seleção
acontece *fora* do mundo — um processo externo lê a aptidão e escreve a próxima geração.
Num mundo com reprodução, a seleção seria uma equação do próprio mundo, e a dificuldade
viraria endógena (seleção mole: a hostilidade nunca zera o gradiente, só troca quem se
reproduz).

---

## 7. A equação que falta de verdade

```
Ė = η_a·q_alim + τ_via  −  c_f·d  −  P_cérebro  −  Θ  −  aluguel
    ↑ comida   ↑ renda    ↑ andar   ↑ pensar     ↑ calor
```

Hoje **dinheiro, gasolina, caloria e calor são quatro escalares separados**, com câmbio
definido caso a caso: gasolina compra-se com dinheiro a `π`, comida vira caloria a uma
taxa, calor não vira nada, a pane devolve combustível de graça.

Olhe a lista de explorações que o laboratório já encontrou e o padrão é único — **toda
uma delas mora numa dessas conversões**:

| exploração | conversão vazando |
|---|---|
| N15 — subsídio vira renda | pane → combustível grátis |
| guincho-táxi | pane → transporte grátis |
| N19 — almoço grátis | hormônio → desconto de física |
| a pedra | tempo → nada (parar não custa) |
| catatonia do v2 | não agir → cérebro grátis |

Não são cinco bugs. É **um** buraco aparecendo em cinco lugares: não há grandeza
conservada. Cada vez que se tapa um, a evolução acha o próximo — e ela vai continuar
achando, porque procurar isso é literalmente o trabalho dela.

Com um orçamento único de energia e as conversões viradas **eficiências** (`η_a`, `η_f`,
`η_θ` ∈ (0,1]), a classe inteira fecha de uma vez, inclusive os buracos que ainda não
foram descobertos. É a diferença entre um mundo com regras e um mundo com física — e é o
critério que eu proporia daqui pra frente: **não adicione uma regra, adicione uma
conservação.**

---

## 8. Ordem de implementação

| # | equação | estado | custo |
|---|---|---|---|
| 1 | ligar `λ_b` nos cenários com custo | **já existe no código** | 1 campo de config |
| 2 | `Σ‖a_b‖ ≤ B` — vínculo global | falta | ~1 linha no `extra()` |
| 3 | `m(t)` em mais de um canal (não só fome) | errada | pequeno |
| 4 | `∂η/∂t` — hormônio como campo | falta | médio |
| 5 | `Ė` — orçamento único de energia | falta | refatoração |
| 6 | reprodução no episódio (F5) | falta | grande |

Os três primeiros somam poucas linhas e atacam problemas que estão travando o experimento
**agora**. O 5 é o que muda a natureza do laboratório.
