# 53 — Agentes criam cenários e políticas; o simulador julga (receita Navier–Stokes, em casa, com Claude)

**OK do Leonardo (2026-09-08 22:40):** "achei legal a ideia de agents criarem as coisas e devemos fazer o que você
pontuou; via parâmetro algo melhor para criar os cenários, cidade e entre outros."

## O que copiamos da OpenAI e o que não
| Peça deles | Aqui |
|---|---|
| 10.000 agentes em grupos isolados | 3–4 grupos × 2 agentes **Sonnet** (`claude -p`, assinatura), ≤ 10 por rodada (handbook 91; nunca Fable) |
| Codex consolida ideias entre grupos | 1 **Opus** por rodada lê resultados + diários, extrai 3 insights, realoca tarefas |
| Lean checa cada passo | simulador determinístico na fila `nmd` + régua pareada + **predição escrita pelo agente antes de rodar** |
| Euler antes de Navier–Stokes | escada: cenário base → cidade (E70) → escasso → competição |
| humano escolhe problema, realoca, confere o enunciado | Leonardo escolhe o degrau, veta, decide o que é "natureza" e o que é "muleta" |
| internet em cache | docs 44–53, PREDICOES.md, acervo, achados 84 e 95 |

Lição central: a tese é nossa, a moagem é dos agentes, o juiz é obrigatório. Sem juiz, N agentes = N rascunhos.

## Contrato: `cenario.json` (v0)
Tudo que hoje é constante espalhada vira parâmetro num arquivo que um agente consegue escrever e o simulador lê:
```json
{"nome": "centro-caro-periferia-vazia", "predicao": "linear morre >= .85; completo <= .70 porque ...",
 "mundo": {"L": 200, "dias": 10, "regua": "riqueza", "K": 6, "ruas": {"dentro": 1, "fora": 3}, "nevoa": null,
           "precos": {"amp": 0.5, "periodo": 3}},
 "distritos": {"centro":      {"pmul": 2.0, "aliq": .35, "alug": 2.5, "dem": 2.0, "dens": [1.0, 1.5, 1.0, 0.5, 1.0]},
               "industrial":  {"pmul": 0.6, "aliq": .10, "alug": 0.8, "dem": 0.7, "dens": [2.5, 0.0, 1.0, 0.0, 2.0]},
               "residencial": {"pmul": 1.0, "aliq": .15, "alug": 1.0, "dem": 1.0, "dens": [0.0, 2.0, 1.5, 2.0, 0.0]},
               "periferia":   {"pmul": 0.5, "aliq": .00, "alug": 0.8, "dem": 0.3, "dens": [0.5, 0.5, 0.5, 0.5, 0.0]}},
 "passageiros": {"npx": 12, "respawn": 20, "pax_cidade": true, "ponto": 0, "tarifa_base": 3, "tarifa_km": .25},
 "corpo": {"dinh0": 10, "fome_passo": .32, "kcal_pane": 8, "guincho": 0, "fuel_pos_pane": 15},
 "bracos": ["linear", "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)"], "protocolo": {"P": 1024, "G": 120, "paciencia": 40, "R": 4, "seeds": [0,1,2,3,4]}}
```
`dens` = multiplicador de densidade por serviço (posto, comida, água, descanso, oficina). O loader (`e43_campo --cenario`)
aplica em `CfgCampo` e em `gerar_mapa(perfis=...)`; tudo que o cenário não define fica no default (identidade preservada).
Um cenário sem `predicao` é recusado pelo orquestrador.

## Rodada (3–5 por noite)
1. **Grupos** (isolados, cada um com uma tarefa imposta): G1 "cenário em que ESPERAR/ESCOLHER LUGAR vale mais que rodar"; G2 "política explícita
   (Python vetorizado, `politica(obs) -> esc`) que sobrevive 10 dias no cenário base" — a prova por construção; G3 "cenário MÍNIMO que
   separa completo de linear por ≥ 10 pp". Cada agente recebe o contexto, a API e devolve `cenario.json` / `politica.py` + predição.
2. **Juiz**: fila `nmd`, um item por vez (~10 min por cenário de 4 braços; ~1 min por política). Régua pareada; controle linear sempre.
3. **Consolidação** (Opus): o que matou cada tentativa, que truque de um grupo serve para outro, 3 insights, realocação.
4. **Diário** por grupo em `docs/agentes/<rodada>/<grupo>.md`; ledger PREDICOES recebe uma linha por item julgado.

## Guardas
- **Banda do controle (regra desde a rodada 1):** um cenário só é válido se o linear (controle) ficar com mortos entre **0.40 e 0.80**. Abaixo
  disso o mundo é fácil demais; acima, a régua crava no teto e não separa nada (na rodada 1, 'ímã no centro' deu 1.00 em todos e a
  cidade com 12 passageiros deu 0.91–0.95 em todos). Tabela de calibração medida: passageiro perto (npx 12) → linear 0.83 / 18 entregas;
  cidade npx 12 → 0.93 / 11; cidade npx 5 + respawn 80 + periferia .05 → 1.00 / 3. A alavanca é a DENSIDADE (npx 20–40 na cidade).
- Agente não avalia o próprio resultado; só o simulador. Cenário "fácil demais" é pego pelo controle linear (se o linear já
  resolve, o cenário não separa nada). Política que lê estado proibido (posição do passageiro além do sentido) é recusada pela API.
- Sem GPU fora da fila. Sem Fable. Contar agentes antes de disparar.

## Ordem de implementação
1. `gerar_mapa(perfis=...)` + `--cenario` no e43 (identidade: cenário = defaults → bit-igual). **(em andamento)**
2. `scripts/agentes/rodada.py`: monta prompts, chama `claude -p --model sonnet`, coleta JSON/py, enfileira, espera, chama Opus.
3. Primeiro degrau (pred 98): "existe política explícita com mortos ≤ 0.50 em 10 dias no cenário base?" Se ✗ com mecanismo, o
   mundo é insolúvel e o farol vira prioridade; se ✓, a política vira semente da evolução (o Euler do nosso N–S).
