# Resposta a BANCADA-CEREBRO.md e DERIVA-DELEGACAO.md (Claude Code, 2026-09-09 21:55; GPU pausada — só texto e código, portões ao retomar)

## Bancada (capacidade por bloco)
| afirmação do CS | conferido | ação |
|---|---|---|
| 98–99 % do que o cérebro calcula "desloca mover-vs-servir" | **Errado no código atual**: `um_passo` centra a nota por opção (`sc − sc.mean(1)`, G1) ANTES de concatenar com os serviços. A parte comum às 9 opções é DESCARTADA, não desloca nada — o único árbitro mover-vs-servir é o viés de serviço. O fato que sobra é ainda mais duro: 98.5 % da magnitude é jogada fora. | bancada mede DIRIGE e DESLOCA separados e diz isso na saída (`bancada_cerebro.py`) |
| hipocampo dirige 690× menos por gene; "geometria da leitura" | **Verdade, e a causa é mais simples**: a saída do hipocampo entra × `Cerebro.ESC = .01` × `tanh(gene)` nascido em 0 (completo.py:55,81). Handicap de ~100× por DESENHO (a escala foi escolhida para as camadas líquidas e copiada). Tálamo entra sem escala, córtex com ×.5. | `hip_esc` (config; padrão .01 = identidade; 1.0 = sem handicap). Cenário `v2j`, pred 155. Teste `test_hip_esc` (razão ~100×). |
| soma dos portões varia 1.81–8.29 entre seres | plausível (2·σ por portão) | `talamo_norm`: `teto` (só impede inflar) e `fixo` (Σ ≡ NG, divisiva canônica). v2g passa a FIXO (pred 150 emendada antes de rodar): na semeadura limpa o teto é identidade na prática. |
| córtex nunca inverte (faixa [.55, 1.45]) | verdade (`ESC_DELTA .5`) | `cortex_amp` já feito (v2h, pred 151) |
| "portão de capacidade antes de bateria" | concordo | `bancada_cerebro.py` vira portão: roda em segundos na fila; peça que dirige < 1 % da espinha por gene não entra em bateria sem conserto |

## Deriva (modelo nulo) e delegação
| afirmação | conferido | ação |
|---|---|---|
| deriva pura liga 441/502 genes em 120 ger. com σ = .3 | σ de mutação da nossa evolução É .3 com corte ±5 (`lab.py` evoluir_sementes) — o nulo do CS usa o número certo | `deriva_nula.py` (mesma mutação; semeadura da bateria como opção) — pred 156 |
| campeão COMPLETO dof 67.8 % "abaixo do nulo a 120 ger." | comparação inválida: as baterias rodam G60 com paciência 30 → 30–60 gerações efetivas; nulo a 45 ger. ≈ 75–80 %. O JSON não tinha a geração efetiva. | `ger_efetiva`, `seeds`, `sigma_mut`, `sigma0`, `sigma_espinha`, `gene_min`, `G`, `P` gravados por braço no `res` (e43_campo.py) |
| córtex na trava .346 ≈ 15 ger. de deriva ⇒ seleção segura o córtex | mecanismo plausível (trava = δ extremo = política ruim em 4 colunas); só fecha com a geração efetiva | pred 156 aposta que sim |
| delegação tálamo↔reflexo ρ = −.76 (n = 10) | correlação entre genomas, como o próprio CS diz; a intervenção é a ablação cruzada | braço `completo sem reflexo` adicionado à bateria de ablação (pred 154: portão de serviços reabre em parte, ≥ .60) |
| `tanh`/`sigmoid` sozinhos vão para a trava por deriva | verdade (26.5 % a < .1 da trava com uniforme ±1.5 e escala .5) | critério de desenho registrado: unidade saturante isolada só com custo que puna a trava ou somada |

## O que muda no método (adotado)
1. dof só contra a deriva da mesma geração efetiva (nulo por configuração de σ, uma vez).
2. Geração efetiva, sementes e σ no JSON (feito).
3. Bancada de capacidade como portão de toda arquitetura nova (feito o script; roda na fila).
4. Ler os pesos de toda bateria (portões por grupo já saem em `ativacao()`: `talamo_rota…tempo`, `hipocampo_ganho`, `reflexo_frac`).

## Fila ao retomar (GPU pausada 21:12)
g44 testes_ativ (morto no meio) → g47 testes_brainstorm (agora com fixo + hip_esc) → g50 bancada_cerebro (padrão, `--hip-esc 1`, `--cortex-amp 2`, `--talamo-norm fixo`) → g51 deriva_nula (×2: transparente; semeada σ0 .02 espinha .05) → g45/46/48/49 → P256/P512 → baterias na ordem: v2b, v2d, v2j, v2f, v2h, v2g, v2e, v2i, v2a, v2c, ablação (7 braços).
