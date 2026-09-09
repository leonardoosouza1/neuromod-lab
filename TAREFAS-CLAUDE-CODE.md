# Tarefas — rodada de correções (2026-09-09, 20h)

Documento para o implementador. Baseado nas corridas e75 (`mundo_vivo_v1`), e76
(`mundo_vivo_v2`) e e77 (`v1_sigma02`), analisadas com régua pareada por semente.
Complementa `ESPECIFICACAO-MUNDO-VIVO.md` (contratos e algoritmos) — aqui estão só as
**correções que a evidência nova exige**, em ordem.

---

## §A. O que a evidência diz agora

Aptidão da régua `vida`, diferenças **pareadas por semente** (`fit_por_semente`):

### A1. Tirar o hipocampo melhora o cérebro completo — e isso é significativo

Juntando as duas réplicas de v1 (e75 + e77, n=10):

| contraste | efeito | IC95 | p |
|---|---|---|---|
| **sem hipocampo − COMPLETO** | **+0.410** | **[+0.073, +0.747]** | **0.022** |
| sem hipocampo − linear | +0.214 | [−0.081, +0.509] | 0.135 |
| COMPLETO − linear | −0.196 | [−0.533, +0.141] | 0.221 |

Leitura: **o hipocampo é custo líquido dentro do cérebro completo**, e o cérebro completo
— com ou sem ele — **não bate a espinha linear**. É a quinta vez que uma peça nomeada
aparece como custo.

Ressalva declarada: as duas réplicas diferem em σ (0.2 na e77), então agrupar assume que o
contraste é estável em σ. Os dois valores separados foram +0.484 e +0.335 — mesmo sinal e
mesma ordem, o que sustenta o agrupamento, mas não é uma réplica pura.

### A2. A n=5 esse resultado não existia — e o de e75 quase virou achado falso

Isolados: e75 dava `sem hipocampo − linear = +0.398` (p=0.132) e e77 dava **+0.030**
(p=0.821). A vantagem de +0.35 d que parecia clara na e75 sumiu na réplica. Só o contraste
contra o COMPLETO sobreviveu, e **só apareceu a n=10**.

**Consequência operacional: n=5 não é protocolo, é triagem.** Nenhuma conclusão de
arquitetura deve ser registrada no ledger com n=5.

### A3. O custo por ativação quebrou o experimento — três arquiteturas viraram a mesma

Em v2 (λ=0.3, `custo_modo=ativacao`, regime ligado):

| contraste | efeito | IC95 | p |
|---|---|---|---|
| COMPLETO − linear | **−0.416** | [−0.567, −0.265] | **0.002** |
| sem hipocampo − linear | −0.416 | [−0.636, −0.197] | 0.006 |
| sem hipocampo − COMPLETO | **−0.000** | [−0.272, +0.271] | 0.997 |

Os dois braços com cérebro ficaram **exatamente iguais entre si** e significativamente
piores que o linear. E o comportamento: corridas por vida caíram para **1.1** (COMPLETO),
**1.5** (sem hip) e **2.7** (só camadas), contra **5.6** do linear — que tem `dof 0` e
portanto **não paga custo nenhum**.

A assinatura é inequívoca: um custo que só cobra por agir tem um atrator em **não agir**,
e todas as arquiteturas caem nele. Isso é a "pedra" reaparecendo por dentro do
metabolismo, e enquanto existir **nenhuma comparação de arquitetura sob custo tem
sentido** — o custo apaga a diferença entre elas.

O erro é da especificação (minha), não da implementação. A física não é essa: o
metabolismo basal é pago em repouso — é esse o ponto da hipótese do tecido caro.

---

## §B. Tarefas, em ordem

### B1. `λ_basal` no custo de gene *(bloqueia todo o resto)*

**Arquivo:** `src/campo.py` (`dof_de` / aplicação do `metab`), `src/e43_campo.py`,
`cenarios/*.json`.

**Mudança:**
```
custo = lambda_basal * dof_existencia(W)  +  lambda_ativ * ativacao_media(W, F)
```
- `cfg.custo_basal` (novo, padrão **0.0** = comportamento de hoje)
- `cfg.custo_gene` continua sendo o λ de ativação quando `custo_modo='ativacao'`
- primeira tentativa de proporção: `custo_basal : custo_gene` = **1 : 2**

**Portão:** `custo_basal=0.0` reproduz o resultado atual bit a bit.

**Teste** (`src/testes_ativ.py`): `test_basal_impede_catatonia` — um genoma com muitos
genes ligados e ativação zero deve pagar **mais** que um genoma vazio. Hoje paga igual.

**Critério de aceite:** refazendo v2 com `custo_basal>0`, o COMPLETO faz **ent ≥ 5** (o
patamar do linear) em vez de 1.1.

**Predição a registrar:** com basal ligado, o contraste `sem hipocampo − COMPLETO` volta
a ser positivo (o hipocampo passa a pagar aluguel), e as três arquiteturas deixam de ser
idênticas entre si (|diferença| ≥ 0.2 em pelo menos um par).

### B2. Refazer o v2 mudando **um** fator por vez

O v2 ligou λ, `custo_modo` e `regime` juntos — nada é atribuível. Três cenários, cada um
mudando uma coisa em relação ao v1:

```
v2a  = v1 + custo_gene 0.3 (custo_modo existencia)
v2b  = v1 + custo_gene 0.3 (custo_modo ativacao + custo_basal 0.15)
v2c  = v1 + regime
```
Sem isso, o −53 % de corridas do **linear** em v2 (11.9 → 5.6) fica sem dono: pode ser o
regime endurecendo o mundo de verdade, pode ser assimetria de Jensen (a média do
desempenho não é o desempenho na média mesmo com multiplicador de média 1.0). O
`test_regime_ciclo` verifica a média do multiplicador, não o efeito — são coisas
diferentes.

### B3. Instrumentos que ainda faltam e travam o desfecho principal

Todos já estão em `ESPECIFICACAO-MUNDO-VIVO.md §2.2` e continuam ausentes do JSON:

| campo | por que trava |
|---|---|
| `ativacao_bloco` | **`dof_bloco` não serve como desfecho.** Controle interno na e75: o braço `sem hipocampo` zera o ganho do bloco (`completo.py:54`) e mesmo assim tem **131** genes `hip` acima do limiar, contra **117** do COMPLETO funcional. O bloco que não faz nada tem mais genes que o que funciona — sem seleção, a deriva enche. `dof` mede peso grande, não capacidade usada. |
| `NP` | sem ele, `dof` não é comparável entre mundos com números de sentidos diferentes (a retina somou +164 genes ligados só por aumentar `NF`) |
| hash do cenário | resolve o §B5 |
| `t_vida_por_semente` | hoje `t_vida` vem só agregado; a régua pareada precisa do vetor. E `fit` na régua `vida` é composto (`t_vida/240 + w_trab·rec/300`) — **reportar os dois separados**, senão "viveu mais" e "trabalhou mais" ficam indistinguíveis |
| `dispositivo` | GPU/torch/hip-cuda; aritmética difere entre dispositivos |

### B4. Protocolo: n=10 é o mínimo, e testar se sai de graça

**Mudança de protocolo:** `--seeds 0..9` como padrão das baterias de arquitetura; n=5 fica
como triagem, e triagem não fecha predição no ledger.

**Antes disso, o teste que decide se é de graça** (4 células, um braço, mesmas sementes):
`P ∈ {128, 256, 512, 1024}` medindo a qualidade do campeão.

Motivo: 68 % da variância é da evolução e só cai com sementes (medido: DP de avaliação
0.0147 contra DP total 0.0258). Custo ∝ P·G·R·n, então cortar P de 512 para 128 e R de 4
para 2 paga **20 sementes pelo mesmo tempo de GPU** — o menor efeito detectável vai de
8.5 pp para 3.4 pp.

**A ressalva é obrigatória:** cortar P pode penalizar mais o braço de genoma grande
(COMPLETO ~500 genes contra 57 do linear) e enviesar justamente a comparação de interesse.
Se a qualidade do campeão for plana de 128 para cima **nos dois braços**, corte; se cair
só no COMPLETO, mantenha P e aumente sementes gastando mais GPU.

### B5. Uma fonte de verdade para a configuração do mundo

Hoje a config existe em **três** lugares: os defaults de `e43_campo.py`, o namespace de
`politica_util.py:34` e o `cenario.json`. Foi assim que os juízes de política rodaram com
`guincho=0` enquanto as baterias rodavam com `guincho=10` — as duas trilhas produziram
meses de números que **não são comparáveis entre si**, e não havia como perceber porque a
config não vai no resultado.

1. `cenario.json` passa a ser a única forma de configurar; os defaults dos scripts viram
   "carregue o cenário base".
2. O cenário **inteiro** vai dentro do JSON de resultado, com um hash.
3. O índice (`docs/agentes/indice_corridas.csv`, 453 linhas de 84 arquivos) é regenerado
   ao fim de cada corrida.

Deriva de esquema medida no índice: `fitness` ausente em **302 das 453** linhas,
`dof_bloco` em 7, `t_vida` em 13.

### B6. Ablação das camadas genéricas (a que nunca foi feita)

`dof_bloco` mostra que **62–67 % dos genes ligados estão em `rap`+`len`** (camadas
genéricas), contra ~24 % no hipocampo e 1 % no reflexo. A evolução prefere capacidade
genérica a órgão nomeado. As ablações até hoje foram todas de órgão nomeado.

Rodar: `sem rapida`, `sem lenta`, `sem rapida+lenta`, contra COMPLETO e linear, n=10, no
v1. E pela regra N5 (uso ≠ contribuição, quatro aparições), fazer **knock-out de nascença**
(evoluir sem a peça), não só no campeão.

---

## §C. O que NÃO fazer

1. **Não registrar conclusão de arquitetura com n=5.** A e77 mostrou uma vantagem de
   +0.35 d virar +0.02 d na réplica.
2. **Não usar `dof_bloco` como desfecho** enquanto `ativacao_bloco` não existir — o bloco
   desligado tem mais genes que o ligado.
3. **Não comparar `dof` entre mundos com sensores diferentes** sem `NP`.
4. **Não amaciar o mundo** se a mortalidade saturar: a régua `vida` já resolve isso —
   está validada (em e75 a mortalidade é 1.00 em todas as sementes e o tempo de vida ainda
   varia de p10 1.72 a p90 7.30 dias, `frac_teto` 0.00).
5. **Não mudar dois fatores no mesmo cenário** (foi o que inutilizou o v2).

---

## §D. Ordem sugerida

```
[ ] B1  lambda_basal + teste + portao                    bloqueia o resto
[ ] B3  ativacao_bloco, NP, hash, t_vida_por_semente     ~25 linhas
[ ] B4a teste de P (4 celulas, 1 braco)                  decide o orcamento
[ ] B2  v2a / v2b / v2c, um fator cada                   torna o v2 interpretavel
[ ] B4b n=10 como padrao das baterias de arquitetura
[ ] B5  cenario unico + hash + indice
[ ] B6  ablacao das camadas genericas, n=10, de nascenca
```
