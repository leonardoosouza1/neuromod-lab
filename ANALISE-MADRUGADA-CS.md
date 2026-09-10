# Os resultados da madrugada — a alavanca, o nulo (meu), e a primeira travessia

Figura: `resultados-madrugada.png`. Quatro coisas fecharam. Uma delas contradiz o que eu
recomendei ontem, e três das quatro sugestões de uma linha que eu dei parecem ruins.

---

## 1. A alavanca é σ da mutação, não a população

Cinco células no `e78`, todas 60 gerações, mesmo cenário, mesmas 5 sementes, pareadas
contra o controle `P256R4jan` (P 256, R 4, σ 0.3):

| braço | tempo de vida | Δ vs controle | IC95 | p |
|---|---|---|---|---|
| controle P256 R4 σ 0.3 | 4.52 d | — | — | — |
| + jardim comum | 4.69 d | +0.17 | [−0.50, +0.84] | 0.52 |
| P128 R8 (mesma verba) | 4.83 d | +0.31 | [−0.19, +0.81] | 0.16 |
| **σ 0.05** | 5.21 d | **+0.69** | [+0.28, +1.10] | **0.010** |
| **σ 0.10** | 5.36 d | **+0.84** | [+0.20, +1.47] | **0.022** |

Baixar σ de 0.3 para 0.1 vale **+18.5 %** de tempo de vida. É o maior efeito já medido em
qualquer botão de protocolo neste laboratório, e custa zero — é um número no cenário.
`mundoA` e `mundoB` já foram rodados com σ 0.1, o que foi a decisão certa.

À mesma verba de avaliação (128×8 = 1024 = 256×4), mais réplicas bateu mais população por
+0.31 d (p = 0.16, não significativo). Direção a favor da regra da casa, não contra.

## 2. O jardim comum deu nulo — e a explicação corrige a minha conta

`P256jardim` contra o controle: **+0.17 d, p = 0.52**. A DP entre sementes subiu de 0.209
para 0.348 (razão 2.76, p = 0.35). Nenhum dos dois é significativo. **Negativo.**

E o negativo é legítimo, porque a implementação é a completa: `testes_jardim` mostra
diferença máxima **0.0e+00** entre cópias do mesmo genoma dentro de um bloco, com desvio
114.9 entre blocos. O fluxo é compartilhado, não só o berço — exatamente o portão que eu
pedi, e ele passou.

**Onde eu errei.** Eu calculei "9× menos réplicas" sobre o estágio de julgamento. Mas
`medidas()` já é chamada com `seed=7777` **fixo para todos os braços** (`campo.py:566`,
`e43_campo.py:87`): as 128 cópias de avaliação são as *mesmas* para todo braço, com os
mesmos berços e o mesmo fluxo. **A comparação entre braços já era um jardim comum,
implicitamente, desde sempre.** Minha decomposição de variância estava certa na magnitude
e errada no alvo — aquele ruído já estava controlado onde importa.

O que o `jardim_comum=True` acrescenta é pareamento **dentro da evolução**, e é aí que ele
não pagou. O mecanismo mais provável: sob seleção por truncamento, ruído **independente
entre genomas** se cancela na média ao longo de 60 gerações — o sortudo de uma geração é
reavaliado na seguinte. Ruído **compartilhado** não se cancela: ele vira um viés por
geração, "quem é bom *naquele bloco*". Trocar variância independente por viés correlacionado
não é obviamente um ganho. Isso é um resultado de método e vale registrar como tal.

## 3. Mundo B — a primeira vez que o cérebro passa a espinha

Mundo A e Mundo B diferem por **uma lei só**: em A o cérebro paga pela ativação; em B paga
apenas pelo que **muda a decisão** (`ativ_centrada`). É a distinção dirige-vs-desloca
promovida a regra econômica do mundo.

| braço | Mundo A | Mundo B | B − A | dof A → B |
|---|---|---|---|---|
| linear (espinha) | 4.085 | 4.085 | 0.000 | 0 → 0 |
| **COMPLETO** | 3.575 | **4.141** | **+0.567** | 15 → 9 |
| sem hipocampo | 3.581 | 4.131 | +0.550 | 15 → 9 |
| sem reflexo | 3.583 | 4.169 | +0.585 | 15 → 9 |
| hipocampo ×100 | 3.572 | 4.051 | +0.480 | 9 → 4 |
| córtex amp 2.0 | 3.591 | 3.657 | +0.067 | 9 → 9 |
| tálamo normalizado | 3.744 | 4.048 | +0.304 | 4 → 4 |
| softmax T = 0.3 | 2.788 | 2.882 | +0.094 | 4 → 4 |

No Mundo A o cérebro completo perde da espinha por −0.51. No Mundo B ele **ganha por
+0.06** — e com **menos** genes ligados (15 → 9). O linear é idêntico nos dois mundos, o
que é o controle correto: ele não paga imposto de gene (dof 0), então a lei nova não o
toca. Toda a diferença é dos braços que têm cérebro.

**Isto é fumaça: 1 semente, 25 gerações.** O +0.06 sobre a espinha está muito abaixo do
ruído (DP entre sementes ≈ 0.2–0.35), então "o cérebro ganhou" **não** é uma afirmação
sustentada. O que é grande é o **giro de 0.57 d** entre as duas leis, maior que a DP entre
sementes. É exatamente para isso que a fumaça serve: ela justifica gastar a bateria
completa, e a predição já está escrita (pred 167).

## 4. A trajetória: comportamento muito diferente, desfecho parecido

O `trajetoria.py` mediu o que eu tinha proposto — comparar **decisões**, não desfechos,
em 24 blocos de jardim comum:

```
linear vs COMPLETO          concordância 0.269   1ª divergência: tique 18   vence em 39 % dos blocos
linear vs sem hipocampo     concordância 0.277   1ª divergência: tique 19   vence em 40 % dos blocos
estado do linear na divergência: fome 18, gasolina 76, água 83, dinheiro 13, vida 100
maior diferença de estratégia: FICAR PARADO — 20 % do tempo no linear → 4 % no COMPLETO
```

Três leituras:

1. **Eles concordam em 27 % dos tiques e mesmo assim o desfecho é parecido.** O mapa de
   comportamento para destino é muito degenerado neste mundo — muitas políticas diferentes
   levam ao mesmo fim. Isso é uma propriedade do mundo, não das arquiteturas, e é a razão
   mais provável de tanta bateria dar nulo.
2. **A divergência acontece no tique 18**, com o corpo inteiro (vida 100, gasolina 76) e o
   bolso vazio (dinheiro 13). A decisão que separa as arquiteturas é tomada no começo, sob
   pressão de dinheiro, não de escassez física.
3. **A diferença concreta é ociosidade**: o linear fica parado 20 % do tempo, o COMPLETO 4 %.
   E ainda assim o COMPLETO vence em só 39 % dos blocos — ou seja, neste mundo **ficar
   parado paga**. É o fantasma da "pedra" outra vez, agora medido em fração de tique.

## 5. Três das minhas quatro sugestões parecem ruins

Vale dizer com todas as letras, já que elas foram medidas:

| sugestão minha | resultado na fumaça |
|---|---|
| tálamo normalizado (denominador) | +0.17 no A, −0.09 no B — misto, e o melhor braço do Mundo A |
| córtex amplitude 2.0 (poder inverter sinal) | entregas caem de 11.9 para 6.2 — a política inverte e para de trabalhar |
| softmax T = 0.3 | −1.2 a −1.3 d, o pior braço dos dois mundos |
| hipocampo ×100 | sem efeito no A, −0.09 no B |

O `temp .3` merece uma nota: eu propus **T evoluído**, não T fixo em 0.3, e 0.3 é ruído
demais. Mas a fumaça já mostra que a faixa útil, se existir, é bem menor. O `hip 1.0`
também não sustentou a minha hipótese do handicap de 100× — o que restringe a explicação
ao segundo handicap, o de dados (3.2 de 12 caixas tocadas por vida).

---

## Notas de método achadas na conferência

1. **`e43_P128.json` e `e43_P256.json` gravam `P = 512`** — são anteriores ao conserto do
   `_explicit` e rodaram no P do preset. Os números dos três são idênticos bit a bit.
   Não usar essas duas células em nenhuma comparação de população.
2. **As células `r2` pararam em 33–36 de 60 gerações**, contra 59–60 das novas. A conclusão
   de ontem sobre P512 vem dessas células truncadas e continua válida para a DP entre
   sementes, mas não é comparável em média com as novas.
3. O daemon **parou no meio do `r5_P256_sig01_jardim`**; há 4 pedidos na fila
   (`r5`, `r6_P256_sig01_reaval`, `s1_mundoA`, `s2_mundoB`).

## O que eu rodaria agora

1. **`s2_mundoB` e `s1_mundoA` completos** — 5 sementes, 60 gerações, σ 0.1. É a pred 167 e
   é a única chance real de travessia que apareceu até hoje.
2. **σ como eixo próprio** — 0.05, 0.1, 0.2, 0.3 com n = 5. O efeito é grande e barato, e
   pode não ser monotônico (0.1 bateu 0.05).
3. **Não repetir o jardim comum na evolução.** Ele está medido e deu nulo; se voltar, que
   seja com a hipótese nova (viés por geração), não com a antiga.
