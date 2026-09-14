# Retrospectiva 08–12/09 — o que este programa mediu, o que retratou, e a regra que faltava

Figura: `retrospectiva.png`. Escrito para três leitores: o Leonardo, o codex que está
chegando, e eu mesmo no próximo ciclo.

---

## 0. Para quem chega agora

O programa investiga se **pressão de sobrevivência seleciona inteligência**: um ser com
corpo (combustível, fome, água, vida, dinheiro) vive num mundo simulado e um cérebro
pequeno é evoluído por algoritmo genético para sobreviver. A tese-mãe é que sobrevivência é
um **seletor**, não um gerador: peça de cérebro só vira função quando o mundo cobra e
quando ela custa algo.

Dois laboratórios, dois ledgers:

| onde | mundo | motor | ledger |
|---|---|---|---|
| `neuromod-lab/` | táxi numa cidade contínua | Python/torch + kernel HIP | `PREDICOES.md` — 155 entradas, 122 ✓ / 140 ✗ |
| `Universe/crates/taxi-world/` + `src/bin/gpu_evolve` | pista, voltas, hipocampo por setor | Rust/HIP | `docs/PREDICOES-CEREBRO.md` — 9 entradas (U1…U10) |

A regra da casa que vale mais que tudo: **predição escrita antes de rodar, e negativo com
mecanismo conta como resultado.** É por causa dela que esta retrospectiva pode existir.

---

## 1. O achado que reorganiza tudo

Auditei os **16 contrastes** que este programa mediu desde 08/09, calculando para cada um o
efeito observado e o **menor efeito detectável (MDE)** do protocolo que o mediu (poder 80 %,
α .05 bilateral, pareado por semente, n = 5).

**Cinco de dezesseis eram detectáveis. A razão mediana efeito/MDE é 0.55.**

Onze contrastes estavam abaixo da diagonal: **o protocolo não os detectaria nem se o efeito
fosse exatamente do tamanho observado.** Isso inclui quase todo experimento de arquitetura
— hipocampo, córtex, tálamo, jardim comum, P, G. Eles não são resultados nulos sobre o
cérebro; são **não-medições**.

### A causa

Uma política que não faz nada (`politicas/parada.py`: nunca move, nunca come, nunca
abastece) sobrevive:

| mundo | campeão linear | parada | prêmio | ruído entre sementes |
|---|---|---|---|---|
| A | 3.865 d | 3.664 d | **5.2 %** | 8.7 % |
| B | 3.865 d | 3.664 d | **5.2 %** | 8.7 % |
| C | 5.088 d | 3.667 d | 27.9 % | 9.6 % |
| D | 5.14 d | 3.67 d | 28.6 % | 8.5 % |

**Nos mundos A e B, onde a maior parte das baterias rodou, 94.8 % da sobrevivência do
campeão vem de graça e o prêmio inteiro cabe dentro do ruído.** Nenhuma arquitetura pode
ser distinguida num experimento assim, e não é questão de rodar mais.

### O número mais duro do programa

Medido em `e85/julga_parada_COMPLETO_A.json`, mesmo protocolo do piso:

```
Mundo A:  COMPLETO 3.389 d   <   parada 3.664 d      (e o COMPLETO faz 10.8 entregas)
Mundo B:  COMPLETO 3.866 d   >   parada 3.664 d      (+0.20)
Mundo C:  COMPLETO 4.286 d   >   parada 3.667 d      (+0.62, mas a espinha faz 5.088)
```

**O cérebro de 460 genes, no mundo onde o programa passou a maior parte do tempo, é pior
que uma pedra** — e não por não trabalhar: ele entrega 10.8 corridas. A conta metabólica
consome mais do que o trabalho rende. Isso não invalida o cérebro; invalida o mundo A como
instrumento, e reinterpreta todas as ablações feitas nele.

### O portão que saiu disso

Adotado em 11/09 (`docs/89-portao-de-mundo.md`): **cenário só ganha bateria se o prêmio
acima da parada for ≥ 2× o ruído entre sementes.** A e B são recusados retroativamente; C e
D passam. Custa uma chamada de `julga_politica` e teria poupado a maior parte de 80
baterias.

---

## 2. O que está estabelecido

Efeitos que superam o MDE do próprio protocolo (IC95, n = 5 pareado):

| resultado | efeito | IC95 |
|---|---|---|
| mundo C − mundo A, medido na espinha | **+50.1 %** | [24.6, 75.7] |
| espinha − COMPLETO no mundo C | **+31.0 %** | [20.0, 42.1] |
| espinha − COMPLETO no mundo A | **+17.3 %** | [6.4, 28.2] |
| sem córtex − COMPLETO no mundo C justa | **+15.8 %** | [5.6, 26.0] |
| σ de mutação 0.05 contra 0.3 | **+15.2 %** | [6.1, 24.3] |

Mais dois resultados que não entram nessa tabela por serem de outro tipo:

- **Poda por custo de manutenção**: com o nulo da deriva no σ certo, 8 de 8 braços ficam
  abaixo do nulo em condições com ≥ 60 gerações efetivas (−0.07 a −0.19 em fração de
  genoma), passando o critério de 0.06 pré-registrado. **A tese-mãe tem apoio, na
  magnitude certa** — e o instrumento não tem poder abaixo de ~60 gerações, o que explica
  por que ela parecia ausente antes.
- **`sem córtex` bate o COMPLETO em três aparições independentes** (C: +0.73 com *mais*
  genes ligados; C justa: +0.92, p = 0.017). Não é economia de genes: o córtex, como está
  implementado (`|δ| ≤ 0.5`, só tempera a política, nunca inverte sinal), é **custo
  líquido**.

E a leitura que amarra tudo: **os maiores efeitos deste programa são todos sobre o mundo,
não sobre o cérebro.** Mudar o mundo move a medida em 50 %; a melhor peça de cérebro nunca
moveu mais de 16 %, e sempre para cima quando removida.

---

## 3. O que foi retratado

Cinco retratações minhas em cinco dias, e três do lado do implementador. A lista importa
mais que o embaraço, porque cada uma nomeia uma classe de erro.

| afirmação | de quem | por que caiu |
|---|---|---|
| "P 512 vale 7.7× de poder por segundo" | minha | a varredura limpa (HIP, G 60, só P mudando) não mostra efeito nenhum; meu número veio de células truncadas em 33–36 gerações com `--init-from` |
| "o custo de gene poda 7–9× abaixo da deriva" | minha | o nulo usado tinha σ 0.3; as baterias evoluíram com σ 0.1. Com o nulo certo os campeões ficam *em cima* do nulo |
| "toda aptidão relatada está inflada ~7 %" | minha | o número relatado já é fora da amostra (`medidas()` roda em mapas de teste 1000–1002); `reavaliado` é regra de *escolha*, não de medição |
| "as trajetórias A5/B5 estão vazias" | minha | meu `print` filtrava listas, e todos os campos são listas |
| "a razão é 7×" (piso do prêmio) | minha | 0.201 contra 2.205 dá 11× |
| pred 145: P 512 melhora | deles | o cenário sobrescrevia `--P`; as três células rodaram com o mesmo P |
| pred 166: campeão reavaliado melhora | deles | reavaliar escolhe um genoma pior (−0.33 d, 5/5 sementes) |
| pred 180: lei justa rende mais no C | deles (meu mecanismo) | o controle falhou: a espinha, com `dof` 0, moveu +0.59 d |

---

## 4. A taxonomia de armadilha — a parte que vale levar para o Universe

Seis classes, cada uma com instância real e o teste que a pega. **Codex: este é o
checklist.**

### 4.1 Handicap em código confundido com biologia
O hipocampo tinha `HESC = 0.01` — saída multiplicada por 1/100 — e todas as conclusões de
"o hipocampo não paga" foram tiradas com a memória abaixada 100×. O córtex tem `|δ| ≤ 0.5`,
logo **não pode** inverter a política, num mundo cuja política ótima inverte de sinal entre
distritos. No Universe, o braço `--hipocampo-setor` rodava com `--hip-p 1.0 --hip-sigma 0.2`:
todo filho não-elite levava chute σ 0.2 em cada um dos 29 genes, toda geração — carga
mutacional que o controle não pagava.
**Teste:** antes de interpretar um nulo, leia as constantes de escala e a taxa de mutação
do braço. Se o braço e o controle não têm a mesma carga, o nulo é sobre o encanamento.

### 4.2 Instrumento sem poder
`campeao_vs_nulo` não detecta nada abaixo de ~60 gerações efetivas, porque o nulo da deriva
cresce mais rápido que o `dof` do campeão. No Universe, o `u1v` mediu +0.16 % com
**MDE de 2.3 %** — precisaria de ~1 000 sementes.
**Teste:** calcule o MDE do protocolo *antes* de enfileirar. Se o efeito esperado for menor
que o MDE, a bateria mede ruído.

### 4.3 Referência com configuração diferente do dado
O nulo da deriva foi gerado com σ 0.3 e comparado com baterias de σ 0.1.
**Teste:** todo parâmetro da referência vem do JSON do dado, nunca do padrão do script.

### 4.4 Mudança em pacote
`mundoC_cidade_da_vida` mudou seis coisas de uma vez (L, R, T, corte, motor, obs_rapido).
A regra "uma feature por commit" existia para o código e não valia para o cenário.
**Teste:** um campo por célula, `cenario_hash` e `config_hash` no JSON de resultado.

### 4.5 Controle assumido em vez de verificado
A espinha tem `dof` 0, então a lei da conta **não pode** tocá-la. No par A→B ela deu
exatamente `0.0000` em cinco sementes — controle passou. No par C→C justa deu **+0.59 d**,
maior que o efeito medido, porque `corte_vivos = 0.05` é parada antecipada dependente dos
dados e a busca divergiu (`ger_efetiva` 30 contra 26).
**Teste:** o controle é uma asserção, não uma expectativa. Se ele se move, a célula não
pode ser lida — mesmo que o cenário difira em um campo só.

### 4.6 Interpretar um número sem ler a linha que o produz
Duas das cinco retratações minhas vêm daqui: o σ do nulo e o que `medidas()` recebe.
**Teste:** antes de interpretar qualquer quantidade relatada, leia o trecho que a calcula.
Não a documentação, não o nome do campo.

---

## 5. O Universe está repetindo o padrão — e ainda dá tempo

O mundo de pista é melhor engenharia: Rust, testes de identidade (`tests/identity.rs`,
`gate_tick_zero.rs`), juiz separado (`judge.rs`), traço (`trace.rs`), e o ledger novo já
nasce com aposta declarada. Mas as duas primeiras entradas repetem exatamente as classes
4.1 e 4.2:

- **U1 (hipocampo por setor paga na volta 2): ✗ nulo** com efeito +0.16 % contra MDE 2.3 %.
  Isso não é um nulo sobre memória — é a mesma não-medição das baterias de A e B, e está no
  ponto mais baixo do painel *a*.
- **U2 (a memória não custa a volta 1): ✗ regride** −18/−28/−11 %, com o mecanismo
  corretamente identificado como carga mutacional + trim de freio constante. O `u10b` já
  corrige para `--hip-p 0.3 --hip-sigma 0.1`.

**O que falta, e é a lição transferível:** o mundo de pista **não tem piso do prêmio
medido**. Ninguém sabe quanto de volta/tempo um ser que não faz nada — não acelera, ou
acelera reto — consegue. Sem esse número, `lap2/lap1` e `≥2V/gen` podem estar na mesma
situação de `mortos em 10 dias`: métricas cujo prêmio disponível é menor que o ruído.

O táxi levou 80 baterias e quatro dias para descobrir isso. O Universe pode descobrir em
duas chamadas.

---

## 6. Ordem que eu daria

1. **Piso do prêmio do mundo de pista.** Três políticas triviais (não acelera; acelera reto
   sem volante; volante fixo) contra o campeão, no mesmo juiz. Uma tarde de CPU.
2. **MDE do protocolo de voltas** no n que couber, declarado *antes* do U1 completo. Se o
   MDE ficar acima do efeito que o PRD espera, mudar a métrica ou o n — não rodar.
3. **U1 com 60 gerações e a correção de mutação** (`u10b`), só depois de 1 e 2.
4. **`sem córtex` como braço permanente** no táxi, n = 8 — três aparições independentes já
   pedem isso.
5. **Portões de identidade do Rust e do HIP.** O do Rust falhou em 9–12 % nas quatro
   medidas; o do HIP nunca foi feito, e HIP e torch já aparecem juntos em análises.

---

## 7. Os dois números para a parede

> **94.8 %** da sobrevivência do campeão nos mundos A e B vem de não fazer nada.
>
> **5 de 16** contrastes medidos neste programa tinham régua para serem medidos.

Nenhum dos dois é sobre cérebro. Os dois são sobre a medida — e é por isso que o programa
avançou mais nos últimos dois dias, quando passou a medir a medida, do que nos oitenta
experimentos anteriores.
