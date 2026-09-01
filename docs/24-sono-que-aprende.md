# 24 — O sono que APRENDE: consolidação circadiana + corpo que desgasta

**Leonardo, 2026-09-01:** *"o ser humano não aprende na hora — precisa do dia +
noite de descanso. No horário do sono a gente MELHORA o modelo: durante o dia
ele salva o que foi feito, e usamos isso pra treinar. O fator do horário entra
como ALFA: dormiu na hora certa retém 100% — aprende como deveria; depois da
meia-noite 50%; de dia 20%. E o corpo desgasta: pneu, motor, freio, ÁGUA do
radiador — sem água aquece, para, morre — e ele aprende que água importa."*

## 1. Por que está biologicamente certo (e já meio validado em casa)

- Sono consolida: replay hipocampo→córtex (docs 08 §5.3, 09 §4.3, 10 §5.1).
  Dormir mal = não consolidar — o α dele é a versão computável disso.
- O MOTOR já existe e funcionou ONTEM: e5_leis provou que o solve fechado
  W=(ΦᵀΦ+λI)⁻¹ΦᵀY recupera as leis do mundo da experiência vivida (Δfuel =
  −2.101·custo, exato). Faltava o QUANDO — o sono é o quando.

## 2. O laço dia/noite (E9b)

```
DIA (acordado):    vive + GRAVA experiência no hipocampo-buffer (Φ, Y)
                   — barato: só acumula ΦᵀΦ e ΦᵀY (matrizes 36×36, O(1)/passo)
SONO (dormindo):   resolve W_novo = solve(buffer) e CONSOLIDA:
                   W ← W + α(hora)·(W_novo − W)
                   α = 1.0 dormindo 20h-00h | 0.5 pós-meia-noite | 0.2 de dia
                   buffer decai (esquece o dia) — replay gasto
```

**O que se aprende (v1, alvo bem-definido):** o MODELO DO CORPO — as leis
Δfuel/Δfadiga/Δtemp/Δágua em função da ação (e5). As leis alimentam o órgão
PREVISOR: o score passa a usar custo PREVISTO pela lei aprendida (em vez do
peso evoluído fixo). Lei melhor = decisão melhor = quem dorme certo dirige
melhor. (v2, arriscado: consolidar os próprios pesos de política via ridge
sobre resultado denso — só depois do v1, reward-shaping é campo minado 07 §11.)

**A consequência que importa: dormir vira a porta do APRENDIZADO, não só da
energia.** A rotina de sono passa a emergir por DUAS moedas (recuperação +
retenção), como na biologia. E aprendizado-em-vida finalmente tem um relógio.

## 3. Corpo que desgasta (as novas moedas de cuidado)

| recurso | dinâmica | falha | manutenção |
|---|---|---|---|
| **água (radiador)** | consome ao andar ∝ temp | água baixa → temp sobe 2× mais rápido → superaquece → parada longa; seco+quente = MORTE | posto (barato) |
| motor | desgasta dirigindo QUENTE (temp>90 sustentado) | motor fraco → velocidade cai (espiral) | oficina (caro) |
| freio | desgasta com paradas bruscas/km | freio ruim → +risco de avaria em congestionamento | oficina |

Regra de projeto: cada recurso tem ciclo próprio (água rápido, motor lento) —
banco de τ no corpo; e a manutenção custa em moeda cruzada (tempo+dinheiro).
Predição: o ser aprende a HIERARQUIA de cuidado (água toda hora, motor por
semana) — medível pela periodicidade de cada serviço no sonograma.

## 4. E9b — braços e predições (registrar no PREDICOES antes de rodar)

① sem consolidação (pesos fixos da evolução — hoje) ② consolidação com α
CONSTANTE (sono não importa pro aprender — controle) ③ consolidação com α
circadiano (a tese) ④ ③ + forçado a dormir de DIA (retém 20% — dose-resposta).

1. ③ melhora DENTRO da vida em cidade nunca vista (curva de entregas por dia
   sobe; ① fica plana) — aprendizado-em-vida visível.
2. ③ > ② em rotina: pico espectral de 24h no sono maior (duas moedas > uma).
3. ④ aprende ~5× mais devagar que ③ (razão dos α) — dose-resposta limpa.
4. Água: ser que aprende a lei da água morre menos de superaquecimento que o
   que só evolui pesos (a lei nova entra em vida via sono).

## 5. Encaixe na pilha

Sono (24) usa o solve (19 nível 2) gateado pelo relógio do mundo (22), pago em
carga mental (16/23), com corpo multi-τ (este doc) — e a ontogenia (21) decide
na infância QUAIS leis valem a pena consolidar. Cada peça já tem gate próprio.
