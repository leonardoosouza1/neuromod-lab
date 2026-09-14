# 94 — Auditoria do achado da poda (material recebido do Colab, 14/09/2026 09:06)

Leonardo trouxe a pasta `new-universe-e-neuromodlab/` (versão Colab do lab, 13/09) com um
achado novo: **poda supera mutação livre** como operador de busca. O material foi copiado
como recebido: `docs/93-poda-colab-recebido.md` (o doc 16 de lá), `colab/pruning/`
(`poda2.py`, `taxi_np.py`, `resultados/*.jsonl`, CLAUDE/README de lá). A pasta de origem
não é repositório git.

## 1. Recomputado do jsonl bruto (`colab/pruning/resultados/poda2.jsonl`, 40 linhas, 20 sementes × 2 modos)

| | gerar | podar | podar − gerar (pareado) | t | p (bicaudal, 19 gl) | vitórias |
|---|---|---|---|---|---|---|
| fitness de treino | 9,04 ± 0,71 | 10,54 ± 1,18 | **+1,50 ± 0,32** | 4,67 | **1,7 × 10⁻⁴** | 18/20 |
| entregas em 5 cidades novas | 13,76 ± 2,59 | 15,38 ± 2,39 | +1,62 ± 0,84 | 1,93 | 0,068 | 12/20 |

Poda melhor em **57 das 60 gerações** (média entre sementes); esparsidade final **0,34**.

> **CORREÇÃO 14/09 12:42 (revisão do Astra, conferida por mim — `docs/97`).** Tratar 57/60 como 57
> confirmações é errado: gerações sucessivas compartilham população, elite e histórico, logo não são
> independentes. O que a curva mostra é que a vantagem não é artefato do ponto de parada — não que seja
> significativa 57 vezes. Duas outras correções ao que está acima: (1) a comparação `gerar` × `podar`
> muda DUAS variáveis (σ 0,30 → 0,15 **e** a máscara), e o controle que isola o σ (`gerar_fino`, que
> existe em `poda2.py:21`) nunca foi rodado nas 20 sementes — **sem ele não se pode afirmar que a poda
> vence**; (2) `taxi_np.py:126` atualiza o nó na chegada ANTES de a ação ser aplicada (`:157`), então no
> tique de chegada o índice escolhido olhando o nó A é aplicado aos vizinhos do nó B — o "núcleo
> convergente" de features fica suspenso até o conserto. Detalhe e reprodução em `docs/97`.
Núcleo convergente reproduzido: `d_alvo` mantido em 20/20, cinco features descartadas em 20/20.

**Correções ao doc recebido:** (1) o p do treino é 1,7e-4, não "< 0,00001" — o efeito continua
claro (t 4,67), só o número estava exagerado; (2) o p da generalização recomputado é 0,068
(o doc diz 0,053) — mesma leitura: no limiar, **não afirmar**. Verificado: `esparsidade`,
`hist`, `mask` e `teste` no jsonl batem com as tabelas do doc.

**Ressalvas (do próprio doc, confirmadas no código):** um domínio (táxi numpy de 24 nós),
arquitetura reativa de 24 parâmetros, p_off/p_on a olho, `poda2.py` grava em `/tmp`
(fora da política de armazenamento — não rodar como está; se for reproduzir aqui, `--out`
em `/media/llm-data`).

## 2. Por que importa para o programa da mosca (docs/95)

O mecanismo proposto no doc 16 §5 — *desligar uma conexão é um sinal de seleção discreto e
atribuível; mexer um peso é difuso* — é exatamente a aposta de usar o conectoma da mosca
sem gerar nada: o mapa já existe, a busca vira **escolher** (que grupos recebem cada sentido,
que grupos lêem cada comando, que neurônios ficam). `src/flybrain/selection.py` implementa o
mesmo operador (`prune_step`: nasce denso, desliga p 5 %, religa p 1,5 %) sobre 138 639
neurônios em vez de 24 pesos. Predições 186–187 no `PREDICOES.md`.
