# A varredura limpa de P, o G120, e a poda que finalmente aparece

Figura: `p-g120-poda.png`. Cinco células `hip`, o `G120juntos`, e os instrumentos do Mundo C.
Uma retratação minha, uma pergunta decisiva respondida, e um resultado que muda o veredito
sobre a tese-mãe.

---

## 1. Terceira retratação: P não faz nada

A célula limpa que faltava existe agora. Kernel HIP, linear NP 40, G 60 com `ger_efetiva`
60 nas cinco, R 4, `campeao=ultimo`, mesmas 5 sementes — só P muda:

| P | aptidão | DP entre sementes | segundos |
|---|---|---|---|
| 128 | 5.152 | 0.322 | 75 |
| 256 | 5.051 | 0.669 | 74 |
| 512 | 5.290 | 0.644 | 86 |
| 1024 | 5.356 | 0.397 | 125 |

Pareado contra P 128: P 256 −0.101 (p = 0.81), P 512 +0.138 (p = 0.75), P 1024 +0.204
(p = 0.37). **Nenhum efeito na aptidão, e a DP não cai** — ela sobe, desce e sobe, sem
tendência (razões de variância p = 0.19 a 0.69).

**Meu "P 512 vale 7.7× de poder por segundo" está refutado.** Ele veio das células `r2`,
que pararam em 33–36 de 60 gerações e usaram `--init-from`; eu já tinha registrado essas
ressalvas e mesmo assim recomendei. A medição limpa manda.

O que sobrevive da análise de perfil: **P é quase de graça no tempo** — 8× de população
custa 1.7× de relógio, exatamente o que se espera de um laço limitado por lançamento de
kernel. Só que não compra precisão nenhuma. A recomendação correta é o contrário da que eu
dei: **não gaste P, gaste sementes.**

E o mesmo vale para gerações: `hipP256G240` parou em `ger_efetiva` **68** de 240 e deu
4.943 contra 5.051 do G 60. **A paciência satura a busca perto de 68 gerações**; pedir 240
não faz nada além de esperar.

## 2. A pergunta decisiva: a lacuna NÃO fecha com gerações

`G120juntos`, mundo A, `ger_efetiva` 84 de 120:

```
G 30  (ger. efetivas 30):  lacuna espinha−COMPLETO  +0.861   [0.58 1.62 0.87 0.61 0.62]
G 120 (ger. efetivas 84):  lacuna                   +1.050   [1.28 0.94 0.73 1.16 1.15]
                                        mudança  +0.190  IC95 [−0.54, +0.91]  p = 0.51
```

Não fecha, e nem piora de forma significativa. **Quatro vezes mais gerações não movem a
travessia.** Somado ao item 1, a conclusão de protocolo é dura e útil: nem população nem
gerações são a alavanca. O que resta é o mundo e a conta.

## 3. A poda aparece — e por dois caminhos independentes

Conferi primeiro se o nulo foi corrigido: a fórmula `2·(1 − Φ(0.5/σ√g))` reproduz o
`dof_ger_nulo` do arquivo do Mundo C dentro de 1.5 gerações. **O σ agora é 0.1, o certo.**

Com esse nulo, e o critério de 0.06 que o doc 75 pré-registrou:

| condição | ger. efetivas | poda média | braços que passam |
|---|---|---|---|
| Mundo A | 26 | −0.036 | **1 de 4** |
| **Mundo C** | 30 | **−0.097** | **4 de 4** |
| **Mundo A, G 120** | 84 | **−0.109** | **4 de 4** |

Dois caminhos diferentes fazem o sinal aparecer:

- **Mais atividade.** Mundo C contra Mundo A, com gerações praticamente iguais (30 contra
  26): a poda mais que dobra, **p = 0.014**. Como as gerações estão casadas, não é
  artefato de tempo de busca.
- **Mais gerações.** O mesmo mundo A a 84 gerações efetivas chega a −0.109.

**Isto reabilita a tese-mãe na magnitude certa.** Não são os 8× que eu anunciei e retirei —
é um efeito de 0.07 a 0.19 em fração de genoma, que passa um critério escrito antes por
outra pessoa, em 8 de 8 braços nas duas condições. O custo de manutenção *está* podando; o
instrumento é que não tinha poder onde estava sendo usado.

E o resultado do Mundo C **sustenta o mecanismo que propus ontem**: no C o ser é 2.2× mais
ativo por dia e a conta é por ativação, então o cérebro paga mais — o que aparece nas duas
pontas ao mesmo tempo, como aptidão pior *e* como poda mais forte. Mesma causa, dois
sintomas.

### Consequência de método

O `campeao_vs_nulo` **não tem poder abaixo de ~60 gerações efetivas**. O nulo da deriva
cresce mais rápido (0.317 → 0.585 entre g 26 e g 84) do que o `dof` do campeão
(0.275 → 0.514), então a distância só abre com o tempo. Toda afirmação de poda precisa
reportar `ger_efetiva`, e rodar o instrumento abaixo de 60 é gastar GPU para medir ruído.

## 4. O kernel HIP: 9.8× mais rápido, e ainda sem portão

`hipP256` e `torchP256` têm o mesmo cenário, P, G, R e NP; o hip **evolui** no kernel novo e
**julga** em torch (`motor_avaliacao: torch`), então o juiz é o mesmo:

```
torch  fit 5.389   t_vida 4.961   ent 14.30   rec 128.5   728 s
hip    fit 5.051   t_vida 4.647   ent 13.65   rec 121.4    74 s
       diferença −6.3 %          −4.5 %      −5.5 %      9.8× mais rápido
```

−0.338 d, IC95 [−1.05, +0.37], p = 0.255 — não significativo com n = 5. Das oito medidas
comparadas, sete ficam dentro de 6 % e uma passa: o dinheiro final, +7.3 % (−13.77 no torch
contra −12.76 no hip). Como o ser fecha no vermelho nos dois, um desvio percentual grande
aí vem de uma base pequena — mas é justamente a medida que mais desviou no portão do Rust
(receita, +12.3 %), então ela merece atenção no portão do HIP. Mas isso é uma comparação de **busca**, não um portão: mede que a
evolução no HIP acha genomas 6 % piores, não que o HIP simule o mesmo mundo.

**O portão de identidade do HIP não foi feito.** O do Rust foi, e falhou em 9–12 %. Enquanto
o HIP não tiver o mesmo teste — mesmo genoma, G = 0, todas as medidas dentro de tolerância
declarada — números de HIP e de torch não devem entrar na mesma tabela. A varredura de P
acima é interna ao HIP, então é válida como está.

Nota boa: o `config_hash` novo apareceu no JSON do HIP. Isso é o que faltava para o portão
de cenário que pedi ontem.

## 5. Fila

Os quatro pedidos que eu sugeri ontem estão enfileirados (`o4a_mundoC_justa`,
`o4b_mundoA_L92`, `o4c_mundoA_protoC`, e `o3e/o3f_julga_parada` nos três mundos). Ordem que
eu daria, com o que aprendi hoje:

1. **`o4a_mundoC_justa`** — a predição do doc 79 ganhou apoio: se a poda mais forte no C vem
   da atividade × conta por ativação, a lei justa deve render mais no C do que rendeu no A.
2. **`o3e/o3f_julga_parada`** nos três mundos — é o teste que diz se o prêmio do mundo está
   quebrado, e custa segundos.
3. **Portão de identidade do HIP** (G = 0, mesmo genoma) antes de qualquer número de HIP
   entrar numa tabela com torch.
4. **`o4b_mundoA_L92`** — o C que só muda `L`, agora com `config_hash` para provar.
5. Nada de P > 128 e nada de G > 120: ambos estão medidos e não pagam.
