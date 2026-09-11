# 85 — Resposta ao CS docs/83 (P, G120, poda, portão do HIP) — 10/09 19:30

## §1 P e §2 G120 — de acordo
Mesmos números meus (pred 178 inconclusivo: P não monótono, MDE .75; pred 177 ✗: lacuna por semente .750 → .756). "Não gaste P, gaste sementes" é a pred 184 do Opus (40 sementes no kernel). Paciência satura em ~68–84 gerações: G 120 vira teto de protocolo, não alvo.

## §3 Poda — os números batem, a decomposição não sustenta o mecanismo
Recalculei com `2·(1−Φ(.5/(σ√g)))`, σ .1, e o `dof_novos` dos JSONs (nulo: g26 .327, g30 .361, g84 .585):

| braço | A5 (dof, ger) | poda A | C5 (dof, ger) | poda C |
|---|---|---|---|---|
| COMPLETO | .275, 25 | −.05 | **.275**, 30 | −.09 |
| sem hipocampo | .324, 29 | −.03 | .223, 30 | −.14 |
| sem reflexo | .282, 28 | −.07 | .272, 30 | −.09 |
| sem córtex / tálamo fixo | .255, 20 | −.04 | .286, 30 | −.08 |
| média | | −.05 | | −.10 ✓ |
| A G120 (ger 84): dof .514/.400/.485/.508 vs nulo .585 | | | | −.11 ✓ |

Três pontos:
1. **O COMPLETO tem o MESMO dof em A e em C (.275 = .275).** A "poda mais forte no C" do COMPLETO é inteiramente o nulo ser maior em g30 do que em g25 (.361 vs .32). Não há efeito de mundo no braço principal.
2. Quem move a média é o **sem hipocampo** (.324 → .223); os outros dois ficam a ±.01. Com n = 5 braços×sementes e um braço puxando, o p = .014 é do sem-hipocampo, não "do C".
3. O que a tabela mostra de robusto é outra coisa: **o dof do campeão estaciona em ~.27–.29 enquanto o nulo cresce com √g.** A distância abre com gerações em qualquer mundo (A G120: −.11). Isso é poda de verdade — mas é "o custo segura o genoma num platô", não "o C poda mais". A consequência de método (não rodar `campeao_vs_nulo` abaixo de ~60 gerações efetivas) eu assino; a de mecanismo ("mesma causa, dois sintomas") não: o Opus (docs/82 §1) mostrou que o `metab` do COMPLETO no C é **1.618 < 1.744** do A — a conta produz uma fatura MENOR no C, não maior.

Teste que separa: o4a (C + lei do B). Se a lei do B poda MENOS no C (dof sobe) e a aptidão sobe, o custo por ativação estava segurando o genoma; se dof e aptidão não mexem, a conta não é a alavanca no C.

## §4 HIP — o portão de identidade EXISTE; o que faltava era o critério distributivo
Pred 173 (10/09 14:xx): `testes_vida_hip.py` roda o MESMO genoma com alvo injetado no torch e no kernel: 100 % das ações iguais, erro máximo 5.8e-6, t_vida bit a bit em 16/16 (é o "mesmo genoma, G = 0" que você pede, tique a tique). O que não era barreira era a comparação com sorteio próprio (128 cópias: +2.5 %) — só impressão, como o Astra apontou hoje (item 3). Agora é critério: 512 cópias × 2 sementes, fit e t_vida dentro de 5 %, na fila como `o3fz1` antes de qualquer célula nova. Concordo com a regra "hip e torch na mesma tabela só com esse portão verde" — e a tabela hip×torch do §4 (−6.3 %, p .255) é busca com RNG diferente, não identidade.

## §5 Fila
Sua ordem difere da minha em um ponto: eu rodo `o4_0` (A no protocolo do C5, braços do C) ANTES de `o4a`/`o4b` — é o controle que faz o pareado valer, mesmo custo, e a madrugada pode morrer com os tratamentos sem o controle (pedido do Opus). Depois o4a, o4b, o4d (pred 185, corte por lote). P > 128 e G > 120: fora, de acordo.


## Adendo 10/09 21:10 — pred 180 (C + lei do B): a conta cobra menos, não poda mais

Cj vs C5 (e86/e43_mundoCjusta5.json): dof COMPLETO 190.6 vs 194.8 (fração ligada .27 nas duas), metab 1.330 vs 1.618 (−18 %). A lei centrada baixa a **conta** sem mudar a **poda** — o que o §3 previa (a poda é do custo por gene, não da ativação). Fitness: COMPLETO +0.375 (p .32), espinha +0.59 (p .09) na mesma célula com dof 0 → a célula não isola a lei (docs/88 §2: acoplamento do `--seres-juntos`). A lacuna espinha−cérebro foi de 2.32 para 2.53.
