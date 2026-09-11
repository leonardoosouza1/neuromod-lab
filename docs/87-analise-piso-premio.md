# O piso do prêmio — a medida que explica todos os nulos

Figura: `piso-do-premio.png`. Fontes: `e85/julga_parada_{A,B,C}.json`,
`e85/julga_semficar*.json`, `e86/e43_mundoCjusta5.json`. O teste que eu pedi ontem custou
segundos e é, disparado, o resultado mais importante que este laboratório produziu.

---

## 1. Uma política que não faz NADA sobrevive 95 % do que o campeão sobrevive

`politicas/parada.py`: nunca move, nunca come, nunca abastece, zero entregas.

| mundo | campeão linear | política parada | ganho do campeão |
|---|---|---|---|
| A | 3.865 d | 3.664 d | **+0.20 d (5.2 %)** |
| B | 3.865 d | 3.664 d | **+0.20 d (5.2 %)** |
| C | 5.088 d | 3.667 d | **+1.42 d (27.9 %)** |

**Nos mundos A e B, 94.8 % da sobrevivência do campeão vem de graça.** Todo o trabalho —
11.2 entregas, 2.2 abastecimentos, 4.2 refeições, uma vida inteira dirigindo — compra
0.20 dia.

E a comparação com a terceira política fecha o diagnóstico: `linear_sem_ficar` com genoma
degenerado, que **anda o tempo todo sem direção**, vive **1.46 d** — muito pior que ficar
parado. Ou seja o mundo pune com força a ação sem rumo e premia com quase nada a ação com
rumo. A distância entre "não fazer nada" e "fazer certo" (0.201 d) é **11 vezes menor**
que a distância entre "não fazer nada" e "fazer errado" (2.205 d).

### Por que isto explica a história inteira de nulos

O prêmio disponível acima do piso, em porcentagem da medida, contra o ruído entre sementes
(DP/média do braço linear na bateria):

| mundo | prêmio | ruído | |
|---|---|---|---|
| A | 5.2 % | 8.7 % | **ruído > prêmio** |
| B | 5.2 % | 8.7 % | **ruído > prêmio** |
| C | **27.9 %** | 9.6 % | prêmio 2.9× o ruído |

**Em A e B o sinal inteiro cabe dentro do ruído.** Nenhum tamanho de população, nenhum
número de gerações e nenhuma arquitetura pode ser detectado num experimento cujo efeito
máximo possível é menor que o desvio padrão. Isso reconcilia tudo o que medimos esta
semana: a saturação da régua, o degrau do N14, P não fazer nada, G não fazer nada, e o
cérebro completo empatar com a espinha em bateria após bateria.

### O Mundo C não foi um fracasso — foi o conserto

Ontem eu li o Mundo C pelo eixo errado. Ele **multiplicou o prêmio por 5.4×** (5.2 % →
27.9 %) e é o primeiro mundo em que o prêmio é maior que o ruído. A lacuna espinha–cérebro
aumentou lá justamente porque **passou a existir alguma coisa para perder**. As duas
leituras são a mesma: em A quase não há mérito a distribuir, então todo mundo empata perto
do piso; em C há, e o cérebro perde a disputa.

### A medida seguinte, e é uma chamada de `julga_politica`

Se o piso vale 94.8 % do campeão linear em A, e na bateria o COMPLETO faz 82.7 % do linear
(4.115 contra 4.976), então **o cérebro completo pode estar abaixo do piso** — pior que
ficar parado. Não afirmo isso: os dois números vêm de protocolos diferentes (o juiz de
`julga_politica` usa cópias e semente próprias). Mas é uma comparação de um comando:

> rodar `julga_politica.py --politica parada.py` contra o **campeão COMPLETO**, no mesmo
> protocolo, nos três mundos. Se o COMPLETO ficar abaixo da parada, esse é o número mais
> importante que o projeto já produziu, e reescreve a interpretação de todas as ablações.

## 2. O Mundo C justa não pode ser interpretado — o controle falhou

O cenário é limpo: `mundoC_conta_justa` difere de `mundoC_cidade_da_vida` em **um campo**
(`corpo.ativ_centrada`) mais o nome. Mas o controle falhou em execução.

```
A → B    espinha (dof 0):  +0.0000   [0. 0. 0. 0. 0.]        ger. efetivas  30 = 30
C → Cj   espinha (dof 0):  +0.5884   [−0.24 1.05 1.19 0.11 0.83]  ger. efetivas  30 ≠ 26
```

A espinha tem `dof` 0 — nenhum gene sujeito ao imposto — então a lei da conta **não pode**
tocá-la, e no par A→B ela não tocou, em cinco sementes, exatamente zero. No par C→Cj ela
se moveu **+0.59 d, mais que o +0.375 que a célula estava tentando medir**.

**Causa encontrada:** `ger_efetiva` 30 no C contra 26 no Cj. O `corte_vivos = 0.05` do
Mundo C é uma parada antecipada **dependente dos dados**; durante a evolução a população do
braço linear contém genomas com genes ligados (a deriva os liga), esses pagam o imposto, a
lei muda a trajetória da busca, e o corte dispara em geração diferente. O campeão terminar
com `dof` 0 descreve o ponto final, não prova que a busca foi a mesma. Em A→B não havia
`corte_vivos`, e por isso o controle passou.

**Regra:** `corte_vivos` não pode estar ligado numa célula que compara duas leis — ou as
duas células têm de ser casadas em `ger_efetiva`.

### O que fica da minha predição

Nada. Eu previ (doc 79) que o ganho da lei justa seria **maior** no C que no A, porque a
atividade é 2.2× maior e o desconto se aplica por ativação. O número saiu +0.375 contra
+0.360 — diferença de **+0.015 com p = 0.97**, que é um empate, e vem de uma célula cujo
controle falhou. **A predição não foi confirmada: ela não foi testada.** Registro como
inconclusiva, não como ✓.

Se ela for testada direito e continuar empatando, o mecanismo cai — e a conclusão passa a
ser que o benefício da conta justa **não** escala com a atividade, o que seria informativo
por si.

## 3. Sem córtex, de novo, e agora com o maior ganho

No Mundo C justa contra o Mundo C (mesma ressalva de controle):

| braço | C | C justa | ganho | p |
|---|---|---|---|---|
| **sem córtex** | 5.882 | **6.799** | **+0.917** | **0.017** |
| sem reflexo | 5.394 | 6.022 | +0.627 | 0.172 |
| COMPLETO | 5.150 | 5.525 | +0.375 | 0.323 |
| sem hipocampo | 5.406 | 5.658 | +0.252 | 0.381 |

`sem córtex` é o melhor cérebro nos dois mundos e o que mais ganha com a lei justa. Terceira
aparição do mesmo padrão. Já passou de sugestão: **o córtex, como está implementado, é um
custo líquido.**

---

## 4. O que eu rodaria agora

1. **`julga_politica --politica parada.py` contra o campeão COMPLETO**, três mundos. Uma
   chamada, e responde se os cérebros deste laboratório são melhores que não fazer nada.
2. **Repetir C → C justa com `corte_vivos = 0`**, para que o controle da espinha volte a
   valer. Sem isso a pred 180 fica inconclusiva no ledger.
3. **Piso do prêmio como portão de mundo.** Todo cenário novo deveria declarar, antes de
   qualquer bateria, o par (prêmio acima do piso, ruído entre sementes). Cenário com
   prêmio < ruído é recusado — teria poupado a maior parte das baterias de A e B.
4. `sem córtex` como braço permanente, e uma bateria só dele contra o COMPLETO no Mundo C
   com n = 8.
5. O Mundo D (`mundoD_olho_proporcional`, na fila) só depois que o piso dele for medido.
