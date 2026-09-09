# Resposta ao EQUACOES-NEUROMOD.md (Claude Code, 2026-09-09 21:05)

Auditoria item a item contra o código em `src/campo.py` / `src/completo.py` (commit 07a53f7 + este).

| # (CS §8) | afirmação do CS | conferido no código | ação |
|---|---|---|---|
| 1 | `λ_b` existe e não foi ligado no v2 | Verdade com um detalhe: B1 (`custo_basal`) foi implementado DEPOIS do v2 rodar (pred 143); v2 não tinha o campo. | `v2b_ativ_basal.json` (basal .15) já está na fila (pred 146). |
| 2 | `Σ‖a_b‖ ≤ B` falta | **Existe**: §E orçamento (`orcamento_ativ`, `_fator_orc` em `Cerebro`/`SerCompleto`, testes `testes_orcamento*.py`), commit 08dfcf1. | `v2d_orcamento.json` (B = 1.0) na fila (pred 147). Documento do CS está atrasado aqui. |
| 3 | `m(t)` entra só na fome (`campo.py:351`) | **Verdade** — única linha onde `metab` toca o corpo. | Implementado `custo_canais`: ('fome',) padrão = identidade; ('fome','agua','calor') = água ×m, calor +calor_sobe·(m−1)/tique. Cenário `v2e_canais.json`, pred 148, teste `test_custo_canais`. |
| 4 | hormônio como campo `∂η/∂t` | falta mesmo | ideia original do Leonardo; projeto médio, decisão dele. |
| 5 | `Ė` orçamento único de energia | falta mesmo (= F7 da spec) | refatoração; espera decisão. O princípio "não adicione regra, adicione conservação" está certo e fica registrado como critério. |
| 6 | reprodução no episódio (F5) falta | **Existe**: `reproducao` (res > limiar → filho, conservação), régua `filhos`, `testes_reproducao.py`. Nenhum cenário usa ainda. | ligar quando F6 (multi-ser) existir; sem multi-ser o filho não nasce no mundo, só conta. |

Constantes da §3 conferem com o código (fuel .15, água .08, fome .32, calor .15/.6).

## Onde discordo do mecanismo

"O custo do cérebro e o custo de existir são indistinguíveis pela seleção porque entram no mesmo canal." A seleção nunca vê canal —
vê aptidão. Um gene é mantido se seu benefício marginal em aptidão paga seu custo marginal; isso é igual se o custo entra pela fome,
pela água ou pelo calor. O que o canal muda é o **preço em aptidão por unidade de m**: fome é o canal mais caro (77/dia, 55–60 % do
dano), água é barato (2 dias de reserva) e calor só cobra quando passa de 60/80. Logo, espalhar em três canais BARATEIA o cérebro na
média e muda a forma do preço, não a "distinguibilidade". A aposta 148 é que isso não move o resultado do v2b em mais de 3 pp — a
alavanca continua sendo λ (quanto custa um gene) e não o canal.

O número "m ≈ 2.05" vale só para `custo_modo='existencia'` com dof 350. No v2 (`ativacao`), m = 1 + λ·Σ n_b·min(1, ativ_b/ativ_ref)/100
— com ativação parcial fica bem abaixo; e sob semeadura limpa (σ0 .02) o dof efetivo é pequeno. "Preço brutal ou zero" descreve o modo
existência, não o v2.

"O ser é determinístico" — correto (argmax, sem sorteio). A exploração é a mutação entre gerações; dentro do episódio não há "tentar
diferente". Concordo que vale um teste de decisão estocástica (softmax com temperatura como gene), depois das baterias atuais.

## Estado da fila (sequencial, 1 processo na GPU)
Portões g33–g46 → células P 256/512/1024 (pred 145) → s1 v2a, s2 v2b (=item 1), s3 v2c, s4 v2d (=item 2), s5 ablação camadas, s6 v2e (=item 3).
