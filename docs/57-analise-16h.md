# Análise das últimas horas — 2026-09-09, 17h

Cobre: laço de agentes até L16, bateria da retina (e74, pred 138), `mundo_vivo_v1`
parcial (e75, pred 142) e os instrumentos que entraram com F1–F4.

---

## 1. O platô rompeu — e não foi pelo motivo previsto

Lotes 8–11 ficaram em 0.556–0.566. De L12 em diante: **0.534 → 0.534 → 0.516 → 0.490 →
0.487**. São 7 pp abaixo do platô que eu tinha diagnosticado, e a coincidência temporal é
com o commit `bfd4416` (KCAL_PANE corrigido para 8 no juiz).

**Mas a predição que eu registrei falhou.** Eu previ que, com a pane cobrada, panes/dia
passaria a correlacionar com mortalidade (Spearman ≤ −0.4). Medido:

| | n | panes/dia | corridas/dia | abast/dia |
|---|---|---|---|---|
| lotes 1–11 | 78 | **+0.26** | −0.84 | −0.81 |
| lotes 12–16 | 39 | **+0.33** | −0.37 | −0.29 |

A correlação da pane **não** virou negativa; ficou mais positiva. E as 6 melhores ainda
quebram 6.24 vezes por vida (era 6.89). **Predição ✗, com mecanismo:** cobrar caloria pela
pane (KCAL_PANE) não é o mesmo que cobrar a pane — o guincho continua entregando o ser
**no posto**, o que resolve o problema de navegação de graça. Enquanto o socorro levar ao
destino certo, quebrar continua sendo uma forma barata de chegar lá. É o N15 outra vez,
numa terceira roupa: o subsídio agora não é combustível nem dinheiro, **é transporte**.

Teste barato que decide: deixar o guincho no **local da pane** em vez de no posto. Se
panes/dia finalmente correlacionar, o subsídio era o táxi grátis.

**O que de fato mudou de L12 a L16:** corridas/dia perdeu força como discriminador
(−0.84 → −0.37) e **`n_come` assumiu** (−0.55 bruto, −0.49 por dia). O eixo saiu de
"fazer mais corridas" para "comer direito" — coerente com a causa de morte, que nas 8
melhores é fome 50 % contra dano 39 %.

## 2. Retina (e74, pred 138): a leitura está certa, a conclusão de fundo não está provada

Análise pareada por semente, n=5:

| contraste | efeito | IC95 | p |
|---|---|---|---|
| linear: sem → com retina | +2.5 pp | [−2.1, +7.2] | 0.20 |
| COMPLETO: sem → com retina | −2.7 pp | [−8.5, +3.1] | 0.27 |
| COMPLETO − linear, **sem** retina | +5.0 pp | [−1.4, +11.3] | 0.097 |
| COMPLETO − linear, **com** retina | −0.3 pp | [−2.9, +2.3] | 0.78 |
| **interação** | +5.2 pp | [−0.9, +11.3] | 0.075 |

**Nenhum intervalo exclui zero.** O menor efeito detectável deste desenho a n=5 é
**8.5 pp** no contraste simples e **8.2 pp** na interação — e os efeitos observados são de
5 pp. O experimento foi desenhado com potência abaixo do efeito que procurava.

Portanto: "a retina não piora a evolução" está **sustentado** (o linear não piorou de
forma detectável, e é um resultado negativo legítimo). Mas "o COMPLETO vai melhor sem
retina" **não está estabelecido** — é 5 pp com p=0.097. Sugiro não fechar essa parte no
ledger; ou re-rodar com n=10, que baixa o detectável para ~5 pp.

Custo de fechar direito: as duas células levaram 796 s e 461 s com n=5. Ir a n=10 custa
~21 min de GPU. É barato para não gravar um achado que o próprio dado não sustenta.

## 3. O confundidor que ameaça o experimento principal

O `dof_bloco` entrou (I1a) e já mostrou seu valor — mas revelou um problema de desenho:

| | dof | rap | len | hip | cor | tal | ref |
|---|---|---|---|---|---|---|---|
| sem retina | 334 | 25 % | 37 % | 25 % | 9 % | 3 % | 1 % |
| com retina | 498 | 27 % | 40 % | 24 % | 6 % | 2 % | 1 % |

A retina acrescentou **+164 genes ligados** — e a composição ficou praticamente igual.
A razão é mecânica: mais sentidos ⇒ `NF` maior ⇒ as matrizes `hipM`/`hipP` e as camadas
genéricas crescem ⇒ mais genes cruzam o limiar **na mesma densidade**. Não é o mundo
pedindo mais cérebro; é o genoma ficando maior.

**Duas consequências práticas:**

1. **`NP` não está no JSON** (nem `ativacao_bloco`, nem `dispositivo` — três campos que a
   spec §2.2 pede). Sem `NP` não dá para reportar densidade (`dof/NP`), que é a única
   forma comparável. São três linhas.
2. **O cruzamento do dia 4 está mal desenhado como está.** Se o fator "mundo" for
   *retina ligada vs desligada*, `NP` muda entre as células e `dof` deixa de ser
   comparável — e a interação apareceria por artefato. **Correção:** manter a retina
   ligada nas quatro células e variar só o **alcance** (`R_dia` grande = praticamente
   onisciente vs `R_dia` = 25). Mesmos sentidos, mesmo `NP`, mesma dimensão de genoma;
   muda só a informação disponível. É exatamente o que a névoa fazia — e é por isso que
   ela continua sendo o instrumento certo para o experimento principal, mesmo com a
   retina existindo.

Observação lateral que vale registrar: **62–67 % dos genes ligados estão em `rap`+`len`**
(as camadas genéricas), contra 24–25 % no hipocampo e 1 % no reflexo. A evolução prefere
capacidade genérica a órgão nomeado — o que é consistente com "as peças são decoração" e
sugere que a próxima ablação interessante é *das camadas genéricas*, não dos órgãos.

## 4. F1 funciona: a régua sem teto está entregando

`mundo_vivo_v1` (parcial: linear fechado, COMPLETO na geração 15) num mundo com retina,
guincho pago (10) e `fuel_pos_pane` 5:

```
mortos 1.00 [1.0, 1.0, 1.0, 1.0, 1.0]      <- a régua velha diz "nada aconteceu"
t_vida  média 4.23 d  mediana 3.59  p10 1.72  p90 7.30  frac_teto 0.00
fit     4.59 [4.71, 4.33, 4.44, 4.94, 4.51]
```

Mortalidade saturada em 1.00 — nenhuma informação — e ao mesmo tempo o tempo de vida
varia de 1.7 a 7.3 dias entre os indivíduos, com coeficiente de variação estimado em
~0.5 (o critério de aceite que escrevi era ≥ 0.15). **É a demonstração de que a régua
sem teto resolve o problema que travou o E62**: o mundo pode ser tão brutal quanto você
quiser, que ela continua ordenando. `frac_teto = 0.00` confirma que o horizonte de 30
dias não está amarrando.

Com isso, o veto que eu tinha colocado sobre rodar em mundos onde todos morrem **cai** —
desde que a régua seja `vida`.

## 5. O portão pegou um erro real

`g15_testes_retina` falhou com exit 1 e o commit `c4f6d94` mostra o motivo: as colunas do
corpo estavam deslocadas em 2 (a retina entrou antes de `demanda`/`espera`). Um sentido
lido na posição errada é o tipo de bug que produz meses de resultado limpo e errado —
foi o portão de identidade que o pegou, em 13 segundos, antes de qualquer bateria.
Vale dizer isso em voz alta porque é o argumento a favor de manter a disciplina quando
ela parecer burocracia.

---

## 6. O que eu faria a seguir, em ordem

1. **Três linhas**: `NP`, `ativacao_bloco` e `dispositivo` no JSON (spec §2.2). Sem `NP`
   nenhuma leitura de `dof` entre mundos diferentes é válida.
2. **Re-rodar a pred 138 com n=10** (~21 min) ou marcar no ledger que a parte
   "COMPLETO sem retina" ficou indeterminada por potência.
3. **Testar o guincho-táxi**: largar o ser no local da pane. Decide se o resíduo de
   subsídio é transporte.
4. **Redesenhar o cruzamento** com retina ligada nas quatro células e `R_dia` como fator
   (§3), 8 sementes.
5. **Ablação das camadas genéricas** (`rap`+`len`), que concentram dois terços dos genes
   ligados e nunca foram alvo de ablação isolada.
