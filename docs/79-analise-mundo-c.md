# Mundo C: o mundo melhorou e o cérebro piorou

Figura: `mundo-c.png`. Três resultados novos: `e79/e43_mundoC5.json` (6 574 s),
`e78/e43_P256sig01retina.json` (z5) e `e83/e43_torchP256.json`. A fila está com um pedido
(`zzz_A_G120_corte05`) e o daemon parou de novo.

---

## 1. A lacuna triplicou

Vantagem da espinha sobre o COMPLETO, pareada por semente:

| mundo | lacuna | IC95 | % da espinha |
|---|---|---|---|
| A (conta por ativação) | +0.861 | [+0.32, +1.40] | 17 % |
| B (conta justa) | +0.496 | [+0.04, +0.95] | 10 % |
| **C (dimensionado)** | **+2.319** | [+1.49, +3.14] | **31 %** |

Todos os quatro braços com cérebro perdem no C com p ≤ 0.007. O Mundo C é, de longe, o
mundo em que o cérebro vai pior — e a pred 170 cita o meu doc 70 §3.1 como motivo para
construí-lo. **A consequência que eu previa (dar chance às peças que dependem de repetição)
não aconteceu.**

## 2. Mas o mundo ficou muito melhor como mundo

O que o dimensionamento prometia, ele entregou:

| | Mundo A | Mundo C | |
|---|---|---|---|
| entregas por dia | 2.84 | 6.22 | **2.2×** |
| receita | 116.0 | 236.1 | 2.0× |
| tempo de vida | 4.59 d | 6.68 d | 1.5× |
| dinheiro final | **−14.7** | **+21.5** | de dívida para lucro |

A cidade menor (L 200 → 92) fez o que eu disse que faria: o ser trabalha o dobro por dia,
vive mais, e **deixa de viver endividado**. Isso muda a natureza econômica do mundo — pela
primeira vez o taxista fecha no azul.

## 3. Por que isso pode ter PIORADO para o cérebro — mecanismo com predição

O Mundo C usa a conta do **Mundo A**: custo por ativação 0.3 + basal 0.15. E o ser do C é
**2.2× mais ativo por dia**. Um cérebro cobrado por ativação paga **por ativação** — logo o
mesmo genoma de ~195 genes custa mais no C do que no A, na proporção da atividade.

Ou seja: o dimensionamento amplificou exatamente o custo que o Mundo B foi desenhado para
consertar. Isso é testável em uma célula.

> **Predição:** o Mundo C com a lei do Mundo B (`ativ_centrada`) deve dar um ganho **maior**
> que o +0.36 d que o B deu sobre o A no COMPLETO — porque a atividade é 2.2× maior e o
> desconto se aplica a cada ativação. Se der ganho **menor**, a hipótese cai e o problema
> não é a conta.

Essa é a bateria de maior informação por segundo que existe agora, e é uma célula.

## 4. Mas não dá para atribuir nada ao dimensionamento

O `mundoC_cidade_da_vida` mudou **seis coisas de uma vez** em relação ao A:

```
L         200  -> 92          motor       (padrão) -> torch
R         (padrão) -> 4       obs_rapido  (padrão) -> True
T_evo/T_aval -> 7200          corte_vivos (padrão) -> 0.05
```

A regra da casa — uma feature por commit, com portão de identidade — vale para o código e
**não foi aplicada ao cenário**. Com seis mudanças simultâneas, nem "o dimensionamento
piorou para o cérebro" nem o contrário está demonstrado: `R 4` sozinho muda a régua,
`obs_rapido` muda o que o ser percebe, e o motor torch é outro simulador.

O conserto é barato e vale mais que a próxima bateria: **`cenario.json` também precisa de
portão de identidade e de uma mudança por célula.** Um C que só muda `L` custa o mesmo e
responde a pergunta.

## 5. Tirar o córtex ajuda — e não é contagem de genes

No Mundo C, contra o COMPLETO (pareado, n = 5):

| braço | diferença | p | genes ligados |
|---|---|---|---|
| **sem córtex** | **+0.732** | 0.075 | **203** (COMPLETO tem 195) |
| sem hipocampo | +0.256 | 0.289 | 158 |
| sem reflexo | +0.244 | 0.495 | 193 |

O braço sem córtex é o melhor cérebro do Mundo C **tendo mais genes ligados que o
COMPLETO**. Então o ganho não vem de economizar metabolismo: o córtex **atrapalha
ativamente**. Casa com a auditoria peça por peça: com `|δ| ≤ 0.5` ele só consegue perturbar
a política, nunca invertê-la — e perturbar custa.

Com p = 0.075 e n = 5 é sugestão forte, não resultado. Merece ser braço próprio na próxima
bateria, nos três mundos.

## 6. O z5 resolveu a dúvida que eu levantei — no sentido contrário

Eu pedi uma réplica limpa porque suspeitei que a comparação do `corte_vivos` misturasse
modos de campeão. O z5 (`ultimo`, sem corte, com retina) devolveu:

```
P256sig01  [5.167 5.747 5.667 5.222 4.987]
z5         [5.167 5.747 5.667 5.222 4.987]     idênticos bit a bit
```

`campeao: None` e `campeao: 'ultimo'` são o mesmo caminho. **A comparação já estava limpa e
o confundidor que eu apontei não existia.** Consequência: o efeito do corte continua sendo
**uma** medição, não duas — aptidão −0.138 (p = 0.34), DP 0.331 → 0.131 (razão 0.156,
p = 0.099). Ainda vale a segunda amostra, com sementes novas e não com célula nova.

## 7. Estado das ferramentas

- Os `h1b` **passaram** do erro de retina (o `NM_RETINA: "0"` funcionou) e param num novo:
  `vida_hip.py:36 → RuntimeError: expected scalar type Float but found Long`. Algum tensor
  passado ao kernel (`st`, `_cfg_f(cfg)` ou `cfg_i`) está em inteiro. É bug de uma linha.
- `e43_torchP256`: linear com NP 40 (sem retina), fit 5.389, DP 0.284, 728 s. Não é
  comparável com as células de NP 57 — genoma diferente.

## 8. Fila que eu rodaria

1. **Mundo C com a lei do Mundo B.** Uma célula, predição escrita acima, e é o único
   experimento que separa "a conta é o problema" de "o mundo é o problema".
2. **A política que só fica parada, no Mundo C.** Uma chamada de `medidas`. No C o ser
   trabalha 2.2× mais; se ficar parado *ainda* render perto do campeão linear, o problema
   não é dimensionamento nem conta — é o desenho do prêmio.
3. **Um Mundo C que só muda `L`**, com portão de identidade no cenário.
4. `sem córtex` como braço permanente nos três mundos.
5. O G 120 depois disso, não antes.
