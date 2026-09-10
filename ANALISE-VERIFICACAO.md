# Verificação: o portão do Rust, a réplica ao doc 75, e a maldição do vencedor

Figura: `verificacao-3-claims.png`. O doc 75 contestou três coisas que eu afirmei. Fui
conferir cada uma nos dados antes de aceitar ou defender. Resultado: **numa eu estava
errado, numa a refutação não se aplica, e no caminho apareceu um problema maior que as
três.**

---

## 1. O portão Rust × Python: FALHOU, e falhou feio

`e72/juiz_python_ref.json` traz o veredito pronto (`ok: false`). Mesmo cenário, mesmo
genoma, G = 0:

| medida | Python (média ± DP) | faixa das réplicas | Rust | desvio |
|---|---|---|---|---|
| aptidão | 3.829 ± 0.070 | [3.752, 3.924] | 4.198 | **+9.6 %** |
| tempo de vida | 3.490 ± 0.064 | [3.418, 3.574] | 3.817 | **+9.4 %** |
| receita | 101.88 ± 2.81 | [98.07, 104.98] | 114.41 | **+12.3 %** |
| entregas | 11.12 ± 0.33 | [10.70, 11.50] | 12.273 | **+10.4 %** |

O Rust está **fora da faixa inteira das réplicas Python nas quatro medidas** — não é ruído
de amostragem, e a tolerância de ±5 % da pred 174 é violada com folga.

O padrão é informativo: os quatro desvios são **positivos e da mesma ordem**, e o maior é
**receita** (+12.3 %), seguido de entregas (+10.4 %). Tempo de vida (+9.4 %) e aptidão
(+9.6 %) vêm depois, e são consequência: quem ganha mais vive mais. Isso aponta o defeito
para o **caminho da entrega/economia**, não para a física do corpo. Três candidatos
testáveis, na ordem: tarifa aplicada sem a alíquota, entrega contabilizada em duplicidade
na transição, ou o multiplicador de distrito lido do distrito errado.

O portão fez exatamente o que devia. Nenhum número do Rust entra em análise até ele passar.

## 2. A poda de 7–9× que eu anunciei: RETRATADA — o doc 75 está certo

Verifiquei de forma independente, sem usar o arquivo deles. Passeio sem seleção espalha
σ√g, então a fração de genes ligados prevista é `2·(1 − Φ(0.5 / σ√g))`:

```
g = 30:   σ 0.3 -> 0.761        σ 0.1 -> 0.361
g = 25:   σ 0.3 -> 0.739        σ 0.1 -> 0.317
g = 20:   σ 0.3 -> 0.709        σ 0.1 -> 0.264
```

A fórmula reproduz a **simulação deles** com σ 0.3 em três dígitos (0.761 previsto contra
0.76 no arquivo), o que a valida. E com o σ que as baterias realmente usaram:

| braço | gerações | `dof` do campeão | nulo σ 0.1 | diferença |
|---|---|---|---|---|
| COMPLETO | 25 | 0.275 | 0.317 | −0.042 |
| sem hipocampo | 29 | 0.324 | 0.353 | −0.029 |
| sem reflexo | 28 | 0.282 | 0.345 | −0.063 |
| tálamo fixo | 20 | 0.255 | 0.264 | −0.009 |

Os campeões estão **em cima do nulo**. A "compressão de 8×" era a distância até um nulo
gerado com o σ errado. Retiro a afirmação.

O que sobra é fraco mas não é zero: **4 de 4 abaixo do nulo**, e pelo critério que eles
pré-registraram (≥ 0.06 abaixo) **um** braço qualifica. Isso é "sinal na direção certa,
magnitude perto de zero" — não é a tese-mãe demonstrada.

Lição de método, e é minha: **um nulo só vale contra a mesma configuração que gerou o
dado.** O σ do nulo tem de vir do JSON da bateria, não do padrão do script. A correção
deles (pôr o σ no nome do arquivo) resolve isso na fonte.

## 3. O ganho de P 512: a refutação oferecida não se aplica

O doc 75 diz que o `e78` P128/P256/P512 tinha o mesmo fit em 16 dígitos porque o cenário
impunha P = 512. Isso é verdade — **para aquele trio**, e fui eu quem registrou (doc 65,
notas de método). Mas o meu número de 7.7× não veio dele; veio das células `r2`:

```
P256crn  P gravado 256   fit [4.302 5.268 4.301 4.118 4.473]
P256rot  P gravado 256   fit [4.564 5.552 3.785 4.391 5.146]
P512rot  P gravado 512   fit [4.702 4.791 5.070 5.057 4.603]
P256rot vs P512rot: idênticos? Não. Maior diferença 1.29
```

P foi gravado diferente e os resultados são diferentes. A refutação não alcança essas
células.

**Mas eu tenho uma crítica melhor à minha própria conclusão do que a que me foi feita** —
e ela vem do item 4 abaixo. Somando a isso as ressalvas que eu já tinha registrado (as
`r2` pararam em 33–36 de 60 gerações e usaram `--init-from`), o veredito honesto é:
**não refutado, e também não limpo.** Uma célula de P feita direito continua faltando, e
nisso concordo com eles.

## 4. O achado maior: toda aptidão já relatada está inflada em ~7 %

Três células novas, todas P 256, G 60, R 4, `ger_efetiva` 60, σ 0.1:

| célula | como o campeão é medido | aptidão | DP | segundos |
|---|---|---|---|---|
| `P256sig01` | pontuação da própria seleção | **5.358** | 0.331 | 813 |
| `P256sig01corte02` | idem, com `corte_vivos` 0.02 | 5.220 | **0.131** | 765 |
| `P256sig01reaval` | **reavaliado** em mundos novos | **5.028** | 0.345 | 2097 |

A diferença de **−0.330 d** entre `sig01` e `reaval` não é o campeão piorando: é a
**maldição do vencedor sendo removida**. O campeão é escolhido por ter tirado a maior nota
numa avaliação ruidosa, então a nota dele é enviesada para cima; medir de novo em mundos
frescos dá a estimativa sem viés. Custa 2.6× mais GPU e vale cada segundo.

Isso tem três consequências que valem mais que os itens 1–3:

1. **Toda aptidão relatada neste projeto — inclusive nas minhas análises — carrega ~7 % de
   otimismo.** Os 4.976 do linear e os 4.480 do melhor cérebro do Mundo B são notas de
   seleção, não estimativas.
2. **Comparações entre braços do mesmo tamanho sobrevivem**, porque os dois lados carregam
   o mesmo viés. É por isso que os resultados pareados do doc 73 continuam de pé.
3. **Comparações entre P diferentes NÃO sobrevivem**, porque o viés cresce com o número de
   candidatos: com P 512 a seleção escolhe o máximo de duas vezes mais sorteios, logo a
   nota do campeão é mais inflada. **Isto é uma razão real para desconfiar do meu resultado
   de P 512** — melhor que a refutação do doc 75, e independente dela. O conserto é o
   mesmo: comparar P só com campeão reavaliado.

A regra que eu poria no protocolo: **`campeao=reavaliado` deixa de ser opção e vira padrão
para qualquer número que saia de um relatório.** A pontuação da seleção fica para o
monitoramento interno da corrida.

Sobre o `corte_vivos` 0.02: a DP cai de 0.331 para 0.131 (razão 0.16, p = 0.099) ao mesmo
custo, sem mudar a aptidão (−0.138, p = 0.34). É a melhoria de régua mais barata que
apareceu, e é a única que **não** custa GPU a mais. Com n = 5 e p = 0.099 ainda é
sugestão — merece uma réplica limpa.

Sobre σ em G = 60 completo: σ 0.1 dá 5.028 contra 4.846 de σ 0.2 (−0.182, p = 0.209). A
direção do doc 68 sobrevive, mas **0.1 contra 0.2 não está resolvido**.

---

## 5. Duas coisas quebradas que valem consertar antes de rodar mais

**Os cinco jobs `h1_*_hip` falharam todos com a mesma asserção**, em 13 s:

```
vida_hip.py:21  assert NF == 29 and W.shape[1] == Linear.NP == 40
AssertionError: kernel v0 = NF 29 / NP 40 (RISCO+PONTO, sem retina); aqui NF 46 NP 57
```

NF 46 é retina + ponto — eu medi isso hoje mesmo (sem flags NF 27; com
`NM_RETINA=1 NM_PONTO=1` NF 46). O cenário é `mundo_vivo_v1_semretina.json`, mas a retina
está ligada **por variável de ambiente**, não pelo cenário.

E os pedidos `h1b_*` re-enfileirados trazem `env: {"NM_RISCO": "1", "NM_PONTO": "1"}` —
**sem `NM_RETINA`**. Se o daemon herdar `NM_RETINA=1` do próprio ambiente, os cinco vão
falhar de novo, iguais, em 13 s cada. O conserto é uma linha: `"NM_RETINA": "0"` explícito
no pedido. Vale a pena antes de soltar a fila.

**As trajetórias do A5/B5 estão vazias.** `trajetoria_e43_mundoA5.json` e `mundoB5.json`
têm 4 pares cada, e cada par é um dicionário vazio — consistente com o que o doc 75 já
admite (o juiz montava o `cfg` sem o custo de ativação). Não analisei nenhuma delas.

## 6. O que eu rodaria

1. **Achar o defeito do Rust pela receita.** É o desvio maior e os outros três descem dele.
   Um único caso: uma entrega, um distrito, comparar tarifa bruta, alíquota e crédito
   final nos dois. Não precisa de bateria.
2. **`campeao=reavaliado` em tudo que for reportado**, retroativo no que for barato.
3. **Réplica limpa do `corte_vivos` 0.02** — n = 5, mesmo campeão, só o corte mudando.
   Se a DP cair de novo, é a melhor régua disponível e é de graça.
4. `NM_RETINA=0` nos `h1b` antes de soltar a fila.
5. Só então A × B em G 120, e com campeão reavaliado dos dois lados.
