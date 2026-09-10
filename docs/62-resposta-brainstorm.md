# Resposta ao BRAINSTORM-FORMULAS.md (Claude Code, 2026-09-09 21:30)

Auditoria contra `src/completo.py`, `src/campo.py`, `cenarios/base.json` e o resultado P128 (`e78/e43_P128.json`).

| peça (CS) | afirmação | conferido | ação (commit desta noite) |
|---|---|---|---|
| reflexo FIEL | 3/4 genes ligados sempre | ok (retrato_cerebro) | — |
| tálamo sem denominador | `2·σ(a+b·need+c·pax)`, cinco portões podem valer 2.0 juntos | **verdade** (`_gate`, completo.py:63) | `talamo_norm`: gate·min(1, NG/Σgate). Padrão off = identidade. Cenário `v2g`, pred 150. |
| córtex `|δ| ≤ .5`, contexto dado | `ESC_DELTA=.5`, distrito vem de `m.distrito(pos)` | **verdade**; comida industrial 0.0 vs residencial 2.0 confere (`PERFIL`, campo.py:66-67) | `cortex_amp` (padrão .5 = identidade; 2.0 inverte sinal — teste prova `min(1+δ) < 0`). Cenário `v2h`, pred 151. Versão com A evoluído fica para depois do resultado. |
| hipocampo = diário | média móvel por distrito, sem predição | **verdade** | entra no F8 (abaixo) |
| camadas FIEIS | rede líquida discreta, 62–67 % dos genes ligados | ok | ablação B6 mede |
| gânglios = argmax grátis | `tudo.argmax(1)`, campo.py:424 | **verdade** | `temp_decisao`: gumbel-max com T·desvio das notas (gerador próprio `g_dec`: não mexe no sorteio do mundo). Cenário `v2i`, pred 152. |
| cerebelo / dopamina ausentes | nada prevê nada | **verdade** | F8, desenho abaixo |
| regime período 5 d > vida | vida mediana **3.9 d** (linear, P128), p10 1.8, p90 7.8 | **verdade**, o número do CS (3.4–4.6) confere | `v2f`: período 1.3 d, pred 149 |

Bug pego de tabela: o cenário sobrescrevia `--so` (braços) e a célula P128 rodou 3 braços em 50 min em vez de 1. Corrigido
(`--so` explícito vence o cenário); P1024 removido da fila (só roda se 512 > 256 em > 5 %).

## Onde discordo
1. **"Denominador do tálamo = §E, uma linha."** São objetos diferentes: o §E limita a soma das SAÍDAS dos blocos na nota de
   movimento; o denominador limita a soma dos PORTÕES do tálamo. Implementei os dois separados, cada um com seu cenário — se
   forem redundantes, os dados dizem.
2. **Softmax com T.** Exploração dentro da vida só paga se houver aprendizado dentro da vida; hoje só o hipocampo aprende
   (média móvel). Aposta registrada: piora ≥ 5 pp. Se não piorar, o argmax estava travando em empates e T vira gene.
3. **"Atenção conserta a catatonia."** Catatonia do v2 foi custo por ativação sem basal (não agir = grátis) — B1 já cobre; o
   denominador não cobra nada, só redistribui.

## F8 — cerebelo + dopamina (a grandeza que falta: ERRO DE PREDIÇÃO)
Desenho concreto, para OK do Leonardo (muda o genoma: NP, layouts por nome, GRUPOS, contagem de genes):
```
cerebelo   ŝ(t+1) = s(t) + C·[s_5(t), onehot(a_t)_19, 1]      s_5 = (fome, agua, fuel, dinh, calor)   125 genes
           ε(t) = s_5(t+1) − ŝ_5(t+1)  → sentidos erro_fome..erro_calor + surpresa = ‖ε‖ (6 colunas de corpo)
dopamina   V(s) = v·[corpo_16, 1]  (17 genes),  r(t) = Δbem(t) (o bem-estar já calculado em bem_soma)
           δ(t) = r + γ·V(s') − V(s), γ = σ(gene)  (1 gene)  → sentido delta + modula portões (5 genes) e escrita do hipocampo (1 gene)
total      ~155 genes; custo de existência/ativação como qualquer bloco; ablação prevista: sem-cerebelo, sem-dopamina
```
Predição do CS que adoto como pred 153 (a registrar quando o F8 existir): *com regime, cérebro com δ + memória bate memória sem δ;
a diferença some sem regime.* Se falhar, a memória continua diário por outro motivo (o mundo não recompensa antecipar).

## Ordem na fila (1 processo na GPU)
g47 brainstorm → g48 completo → g49 import → P256, P512 (linear só) → v2b (basal) → v2d (orçamento) → v2f (regime curto) → v2h
(córtex) → v2g (tálamo) → v2e (canais) → v2i (temperatura) → v2a, v2c, ablação. Tempo: P128 linear ≈ 17 min ⇒ bateria n=10 a
P256 ≈ 3 h cada; a ordem acima é por valor esperado.
