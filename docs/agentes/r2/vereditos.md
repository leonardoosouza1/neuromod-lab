# Rodada 2 — vereditos (consolidador: Fable; juiz: simulador)

| item | previu | mediu | veredito | mecanismo |
|---|---|---|---|---|
| construcao_1 (3 camadas + histerese) | mortos ≤ .5 | 1.00, 1.3 ent, refeições 0, abastecidas 0.1 | ✗ INVÁLIDO | índice de ACOES errado no contrato (culpa minha); a política nunca comprou o que achava que comprava |
| construcao_2 | mortos ≤ .5 | crash `reset(m)` sem W | — | juiz ganhou shim; reenviada (r2_construcao2b) com traço de escolhas |
| lugar_1 (npx 22, respawn 12, contraste 4×) | linear na banda | linear 0.89 / 14.6 ent (outros braços pendentes) | pendente | ainda acima da banda: 22 passageiros repostos rápido não bastam; densidade precisa subir mais |
| lugar_2 (npx 32, respawn 15, rua fora 4) | linear .55–.70, 13–15 ent | pendente | — | — |

## Ajustes para a rodada 3
1. Contrato da API com a tabela EXATA de ações (do código) e aviso explícito do erro anterior.
2. Juiz de política: traço das escolhas nos primeiros 240 ticks (fração ficar/mover/cada serviço + deslocamento por tick) além da autópsia.
3. Calibração: cidade npx 22/respawn 12 → linear 0.89; próximo ponto npx 32 (lugar_2). A banda 0.40–0.80 provavelmente pede npx ≥ 32–40.

## Fechamento r2 (00:45)
| lugar_1 (npx 22, respawn 12, contraste 4×) | linear na banda | linear 0.89, COMPLETO 0.85, bilinear+dem 0.88 | ✗ (fora da banda) | densidade ainda baixa; COMPLETO lidera de leve pela 3ª vez na cidade |
| lugar_2 (npx 32, respawn 15, rua fora 4) | linear .55–.70 | linear 0.96, COMPLETO 0.95 | ✗ (confundido) | mudou rua-fora junto → mais gasolina, panes 7.4; ponto inválido |
| construcao_2b | — | crash de novo (shim com super() não vinculava self) | — | juiz refeito por composição; reenviada (r2_construcao2c) |

Regra nova para os agentes de cenário: **um parâmetro por vez quando o objetivo é calibrar**. Calibração limpa (npx 24/36/48, só isso) roda pelo consolidador (q17, pred 108).
