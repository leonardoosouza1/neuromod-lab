# Portão de mundo na pista — seis intervenções, nenhuma cria prêmio, e o prêmio está em outro lugar

Figura: `portao-mundo-pista.png`. Fontes: `laps_gen*.jsonl` das famílias `u1v_{ctrl,hip}`,
`u10b_hip`, `u11_d03_ctrl`, `u11_d06_ctrl`, `u11b_r10_ctrl`, `u9_{free,log-fixed}` — 3
sementes por família (031/077/113), 40 seres, última geração de cada corrida.

O `RETROSPECTIVE-RESPONSE` acertou em levantar a pergunta do prêmio antes de gastar mais
GPU. Os seis controles que rodaram respondem — e a resposta muda o alvo.

---

## 1. Seis intervenções de mundo, nenhuma passa o portão

O portão registrado é `r = t2/t1 ≤ 0.97` medido por setor no **controle**: se a segunda
passagem não pode ser mais rápida para quem não tem memória, não há o que a memória ganhe.

| intervenção | r mediano | seres com 2+ voltas | veredito |
|---|---|---|---|
| base (controle) | 0.9951 | 116 | recusado |
| olho 10 m (`--retina-range 10`) | 0.9953 | 86 | recusado |
| dropout de sensor 0.3 | 0.9952 | 106 | recusado |
| dropout de sensor 0.6 | 1.0000 | 51 | recusado |
| banco τ livre | 1.0000 | 87 | recusado |
| banco τ log-fixo | 1.0000 | 45 | recusado |

**Nenhuma chega perto.** E o ponto que mais importa: as duas intervenções desenhadas
justamente para tornar o mundo *não observável* — encurtar o olho de 60 para 10 m e apagar
30 % dos sensores — mudaram o `r` em **0.0002 e 0.0001**. Esconder informação não criou
prêmio para a memória.

O `dropout 0.6` é um negativo com mecanismo claro: corta a folga pela metade (7.4 % contra
15.1 %), as voltas medianas de 3 para 1, e só 51 de 120 seres completam duas voltas.
**Mundo mais difícil, não mais aprendível** — tirar informação seleciona robustez, não
memória.

## 2. Mas a pista tem prêmio: 15 %, e a métrica primária vê 0.49 %

Medi a **folga própria** de cada ser: a soma dos seus melhores tempos por setor, tomados
entre as suas próprias voltas, contra a sua melhor volta real. É a "volta ideal" daquele
motorista, e captura consistência sem misturar seres.

```
controle de base:  folga própria mediana  15.1 %   IC95 [14.4, 17.1]   (n = 116 seres)
o que r = t2/t1 vê:                         0.49 %
razão:                                        31×
```

**O mundo não é sem prêmio — a métrica é.** Há 15 % de volta em cima da mesa, e a pergunta
"a memória paga?" estava sendo feita através de um número cuja faixa é 0.5 %. É a mesma
classe de erro que `mortos em 10 dias` no táxi (§4.2 da retrospectiva), diagnosticada em uma
tarde em vez de oitenta baterias.

**Ressalva honesta:** a volta ideal própria é um **limite superior**. Os melhores setores
podem não ser simultaneamente alcançáveis — ser rápido num setor compromete a entrada do
seguinte, e telemetria de automobilismo trata a "volta teórica" exatamente assim. A ressalva
vale igual para todos os braços, então a comparação entre braços continua válida; o valor
absoluto de 15 % é teto, não promessa.

## 3. Correção à recomendação que eu ia fazer

O passo óbvio seria trocar a métrica primária para consistência. **Fui medir antes de
recomendar, e não funciona:**

| métrica | prêmio | DP entre sementes (pareada) | prêmio/DP | MDE n=3 | n p/ ver 1/3 |
|---|---|---|---|---|---|
| consistência (folga própria) | 15.13 pp | 4.63 pp | **3.3** | 14.33 pp | 9 |
| `r = t2/t1` (atual) | 0.49 % | 0.12 % | **4.0** | 0.38 % | 7 |

A consistência tem **31× mais faixa** que o `r` — e **~37× mais ruído**. A razão
prêmio/ruído fica em 3.3 contra 4.0, ou seja **ligeiramente pior**. Trocar a métrica não
conserta a régua.

**O que aperta é n = 3.** E há evidência direta disso: na consistência, a diferença
hipocampo − controle **troca de sinal entre sementes** — +4.2, +0.1, −5.0 pp nas sementes
031, 077, 113. Com três sementes isso é ruído puro, qualquer que seja a métrica.

Nenhum sinal de que o hipocampo capture a folga: `u1v_hip` 14.2 % contra 15.1 % do controle;
`u10b_hip` 15.0 % contra 15.1 %.

---

## 4. O que eu faria, em ordem

1. **n = 8 sementes, mesmas 15 gerações.** É o conserto mais barato e o único que torna as
   duas métricas utilizáveis: 2.7× o custo do que acabou de rodar, e leva o MDE da
   consistência de 14.3 pp para ~5 pp. Sem isso, nenhuma das duas métricas decide nada.
2. **Trocar o portão de controle por portão de oráculo.** O portão de hoje pergunta se a
   *segunda volta do controle* é mais rápida — mas a única memória intravida do controle é o
   banco de τ, então `r ≈ 1.00` é o valor esperado, e não é evidência sobre o mundo. O teste
   certo é um **teto**: um braço que recebe o índice do setor de graça, como entrada
   perfeita. Se nem o oráculo bate o controle, não há memória que ajude e o mundo é recusado
   de verdade. Se o oráculo ganha, o prêmio existe e a pergunta passa a ser se a evolução o
   encontra — que é a pergunta da tese.
3. **Parar de procurar o mundo que precisa de memória por subtração.** Seis intervenções que
   *removem* informação falharam, e há mecanismo: informação ausente seleciona robustez.
   O que cria prêmio para memória não é informação escondida, é **informação que só chega
   depois da decisão que precisava dela** — por exemplo aderência do setor sentida apenas
   dentro dele, com a frenagem tendo de começar antes de entrar. Aí lembrar é a única saída,
   e a primeira volta *tem* de ser mais lenta que a segunda. É uma mudança de uma lei no
   mundo, não de um hiperparâmetro do cérebro.
4. **Registrar a folga própria no ledger ao lado do `r`**, como prêmio declarado do mundo.
   Sai de graça dos `laps_gen*.jsonl` que já estão sendo escritos.
