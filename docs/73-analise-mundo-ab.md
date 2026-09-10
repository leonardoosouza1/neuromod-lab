# Mundo A × Mundo B com 5 sementes — o que aconteceu, e uma correção minha

Figura: `mundo-a-vs-b.png`. Fontes: `e79/e43_mundoA5.json`, `e79/e43_mundoB5.json`,
`e72/campeao_vs_nulo_e43_mundoA5.json`. Ambas as baterias: P 128, G 30, σ 0.1, 5 sementes,
fitness `vida`, `ger_efetiva` 30 em todas as células.

---

## 0. Correção antes de tudo

Ontem eu reportei a fumaça A/B como **"1 semente, 25 gerações"** e destaquei um giro de
+0.57 d entre as duas leis. Fui conferir os campos: a fumaça rodou com **G = 1 e P = 8**.

Uma geração sobre oito genomas aleatórios não é evidência de nada — nem do giro, nem do
`dof` 15 que eu citei (ele é baixo porque houve uma geração de deriva, não porque a
seleção podou). **O número +0.57 está retirado.** O que segue vem da bateria de verdade,
e felizmente confirma a direção — mas por caminho legítimo e com magnitude diferente.

Isso também anula os "vereditos" que eu dei sobre `córtex amp 2.0`, `softmax T = 0.3` e
`hipocampo ×100`: aqueles braços só existem na fumaça de G = 1. Não sabemos nada sobre
eles.

---

## 1. A lei nova ajuda todo braço que tem cérebro

Mundo A cobra do cérebro pela **ativação**; Mundo B cobra só pelo que **muda a decisão**
(`ativ_centrada`). Diferença pareada por semente, B menos A:

| braço | Mundo A | Mundo B | B − A | IC95 | p |
|---|---|---|---|---|---|
| linear (espinha) | 4.976 | 4.976 | **0.000** | — | — |
| COMPLETO | 4.115 | 4.474 | +0.360 | [−0.24, +0.95] | 0.168 |
| sem hipocampo | 3.967 | 4.196 | +0.229 | [−0.16, +0.62] | 0.177 |
| **sem reflexo** | 3.968 | 4.296 | **+0.328** | [+0.14, +0.51] | **0.008** |
| **tálamo fixo** | 3.874 | 4.480 | **+0.606** | [+0.38, +0.83] | **0.002** |

**4 de 4 braços com cérebro melhoram** (teste de sinal unilateral p = 0.0625), dois com
significância individual. E o linear dá **exatamente 0.000** — que é o controle correto:
ele tem `dof` 0, não paga imposto de gene, então a lei nova não pode tocá-lo. Se ele
tivesse se mexido, a bateria estaria errada.

## 2. A travessia NÃO aconteceu — mas a lacuna caiu 42 %

| | vantagem da espinha sobre o melhor cérebro | IC95 | p |
|---|---|---|---|
| Mundo A | +0.861 | [+0.32, +1.40] | 0.012 |
| Mundo B | **+0.496** | [+0.04, +0.95] | **0.039** |
| encolhimento | −42 % | — | 0.045 |

A espinha continua ganhando, e ainda com significância. O que a lei nova comprou foi
**metade do handicap**, não a ultrapassagem.

Este é o resultado honesto, e ele é bom: é a primeira intervenção do projeto que move a
distância espinha–cérebro de forma medida e significativa, num mundo onde o controle não
se mexe. Mas "o cérebro passou a espinha" segue **falso**.

Nota sobre o tálamo: `tálamo fixo` é o braço que mais ganha com a lei (+0.61) e empata com
o COMPLETO no Mundo B (+0.005, p = 0.98), enquanto no Mundo A ele é pior (−0.24, p = 0.15).
Ou seja: sob contabilidade justa, **desligar a atenção adaptativa deixou de custar caro**.
Com n = 5 isso é sugestão, não resultado — mas casa com o retrato de ontem, onde os
portões do campeão fecham em vez de abrir.

## 3. O custo de gene está podando de verdade — a tese-mãe, medida

O instrumento `campeao_vs_nulo` compara o genoma do campeão com o **nulo da deriva** da
mesma geração:

| braço | gerações que rodou | gerações de deriva pura que dariam o mesmo `dof` | compressão |
|---|---|---|---|
| COMPLETO | 25 | 3.0 | **8×** |
| sem hipocampo | 29 | 3.6 | 8× |
| sem reflexo | 28 | 3.1 | 9× |
| tálamo fixo | 20 | 2.8 | 7× |

O campeão tem o genoma de **três gerações de deriva** depois de rodar **25 a 29**. E a
saturação do córtex é ainda mais extrema: 0.008–0.025 na trava, equivalente a **0.4–1.2
gerações** de deriva.

Isto é a Lei do Metabolismo funcionando como seletor, com o controle certo do lado. Ontem
o mesmo instrumento mostrava o campeão *abaixo* da deriva; agora, com o custo por ativação
ligado, ele está **7 a 9 × abaixo**. É a evidência mais direta que o projeto já produziu
para a tese de que peça só se fixa sob custo.

---

## 4. Ressalvas que limitam tudo acima

1. **G = 30.** A régua honesta da casa é 120. A lacuna está encolhendo com a lei; se ela
   encolhe também com gerações, 30 é cedo demais para declarar que não fecha.
2. **P = 128.** Pelo `e78`, P 512 dá 7.7 × mais poder por segundo de GPU. Rodar a mesma
   comparação em P 512 custa quase o mesmo e mede muito melhor.
3. **R não gravado** nestes JSONs — não dá para reconstruir a verba de avaliação.
4. **Só 5 braços em comum.** Os braços de variação de uma linha só existem na fumaça de
   G = 1.

## 5. Um item que precisa de decisão sua

Existe um **juiz em Rust** novo (`e82/rust_juiz_G0.json`, linear com fit 4.198 no
`mundoA_seres`). A referência Python correspondente (`a9u_juiz_python_ref`) **estava
rodando quando o daemon parou** e não gravou. Sem ela não há comparação: 4.198 não pode ser
confrontado com os 4.976 desta bateria, porque são G e protocolo diferentes.

O portão que isso pede é claro e vale escrever antes de qualquer uso do juiz Rust: **mesmo
cenário, mesmo genoma, G = 0, todas as medidas iguais dentro de tolerância declarada.**
Enquanto ele não passar, nenhum número do Rust entra em análise.

Também: o daemon **recusou** `a9t_vida_hip` por `TORCH_EXTENSIONS_DIR` fora da lista branca.
A recusa está correta — mas se a variável é necessária para compilar extensão, ela precisa
ser adicionada explicitamente à lista, não contornada.

---

## 6. A fila que eu rodaria

O daemon está parado com **17 pedidos** enfileirados, entre eles os quatro instrumentos do
Mundo B (`b1_pareado`, `b2_retrato`, `b3_nulo`, `b4_trajetoria`). Ordem que eu daria:

1. **A × B em G = 120, P = 512, 5 sementes.** É a pergunta que ficou aberta: a lacuna de
   0.496 fecha com gerações? Pelo `e78` isso custa pouco mais que a bateria de hoje e
   mede 3 × melhor. **Esta é a bateria decisiva do projeto neste momento.**
2. `b3_nulo_mundoB` — o campeão do B contra a deriva. Se a compressão de 8 × for maior no
   B que no A, a lei nova não só ajuda o desempenho: ela **aperta a poda**, que é a
   afirmação forte.
3. `b4_trajetoria_mundoB` — a concordância de ação era 27 % no v1. Se a lei nova torna as
   arquiteturas mais distinguíveis, ela sobe ou desce de forma informativa.
4. O portão Rust × Python antes de qualquer outra coisa que use o juiz novo.
