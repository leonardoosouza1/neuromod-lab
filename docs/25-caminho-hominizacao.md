# 25 — O caminho: hominização digital por camadas (brainstorm 2026-09-01)

**Leonardo:** *"estudar formas da evolução humana — corpo, cérebro — e recriar
digitalmente, não igual, mas a ideia. O sono precisa pegar os FATOS ocorridos:
ficou 5 min numa fila; na próxima viagem no mesmo horário, lembra e tribla.
A espécie precisa se adaptar: o cérebro pedir melhorias no corpo (se sente
lento → algo que o faça ir mais rápido, com contra que ele aprende). E a
natureza menos passiva: grupos se formarem, sindicato, dominar distritos —
brigar mais pela sobrevivência. Sem perder o foco: EMERGIR."*

## 1. O caminho que os positivos e negativos desenharam (o mapa do desbloqueio)

Cada camada validada é a LICENÇA da seguinte — é a escada da hominização:

| camada | status | o que desbloqueou |
|---|---|---|
| corpo com economia (fome/fuel/dinheiro) | ✓ desde o início | seleção tem o que cobrar |
| eficiência como preço (κ no fitness) | ✓ | todas as invenções abaixo só existem porque consultar custa |
| órgãos calculistas | ✓ (E4→E8) | cálculo onde peso não alcança |
| ontogenia (bebê→poda→adulto) | ✓ 4/4 baterias | busca evolutiva destravada; cérebro enxuto |
| tálamo (rotear por passo) | ✓ campeão | 10% do cérebro ativo, mesmo desempenho |
| sono que aprende (leis globais) | ✓ mecanismo / ✗ lucro | aprendizado-em-vida sem gradiente |
| **memória episódica no sono** | ← AGORA (§2) | o "tribla a fila" |
| corpo evoluível a pedido do uso | ← fila (§3) | a espécie se adapta |
| sociedade (grupos/território) | ← fila (§4) | o sindicato emergente |

O padrão dos desbloqueios: NUNCA scriptamos o comportamento — damos o
INGREDIENTE (preço, órgão, gate, α do sono) e a seleção inventa o resto.
"Emergir" operacionalizado.

## 2. Sono v2: consolidar EPISÓDIOS, não só leis (o "tribla a fila")

Hoje o sono aprende leis GLOBAIS (k_agua — um número do mundo). O pedido é o
hipocampo de verdade: **o que aconteceu ONDE e A QUE HORA**.

- DIA (episódios): cada evento adverso grava (nó, hora-do-dia, custo sofrido)
  num buffer episódico — a fila dos 5 minutos vira a tripla (nó 17, 8h, +5).
- SONO (consolidação): o buffer vira o MAPA espaço-temporal
  `C(nó, faixa-horária)` — média por célula, com α(hora do sono) pesando
  quanto entra. Buffer decai (o dia é esquecido; o mapa fica).
- USO: o órgão-rota (E4/E8, já existe) roda o caminho-mínimo sobre
  `custo_aresta + C(destino, hora_da_viagem)` — replaneja POR HORÁRIO.
  "Tribla a fila" = a rota das 8h evita o nó 17 às 8h, não o dia todo.
- POR MUNDO: filas crônicas por (nó,hora) sorteadas por mundo (como k_agua) —
  indecoráveis pela evolução, só a vida alcança.
- Predições: ser-episódico > fixo além do ruído ONDE filas-por-hora existem
  (controle: mundo sem estrutura horária → empate); mapa aprendido correlaciona
  com o gabarito das filas; o custo do sono se paga porque o mapa vale mais
  que a lei escalar (teto maior — MEDIR O TETO ANTES, regra N2/N10).

## 3. A espécie que se adapta: corpo evoluível + Baldwin

"O cérebro pedir melhoria no corpo" tem duas vias, as duas reais na biologia:

1. **Em vida (já temos)**: upgrades da loja = melhoria comprada pelo
   comportamento. Expandir: catálogo com CONTRAS reais (motor rápido bebe
   mais; pneu duro aguenta e desliza) — ele aprende o trade-off vivendo.
2. **Na espécie (novo)**: genes MORFOLÓGICOS no genoma — velocidade base,
   tanque, eficiência, tamanho da retina (raio de visão) — cada um com preço
   metabólico (alometria! doc 08: não se aloca de graça). A pressão do USO
   esculpe o corpo entre gerações: população que vive de corridas longas
   evolui tanque; a de distrito denso evolui eficiência.
3. **Efeito Baldwin (a ponte, mensurável)**: o que o cérebro aprende em vida
   muda QUAL corpo é selecionado — ser que aprende a lei da água sobrevive
   com radiador menor; gerações depois o radiador encolhe de fato. Predição
   linda: corr(capacidade de aprender do braço, redução do órgão físico
   correspondente ao longo das gerações).

Telemetria: a série `alocacao_elite` ganha os genes do corpo — vê-se a
ESPÉCIE mudando de forma ao longo do tempo, que é o pedido do "ver a evolução
do mundo e seres ao longo do tempo".

## 4. Sociedade: o sindicato NÃO se scripta — se dá os ingredientes

Matemática conhecida (teoria evolutiva de jogos): grupos emergem quando há
(a) interação repetida no mesmo lugar, (b) RECONHECIMENTO (tag herdável),
(c) benefício de coordenação, (d) custo de conflito. A arena (já existe) dá o
(a). Faltam:

- **tag herdável** (um gene visível — "cor da frota"): permite assortment;
- **benefício local de densidade**: num distrito onde tua tag domina, custo
  de serviço −20% (oficina "da cooperativa") — coordenar passa a pagar;
- **conflito com custo**: disputar passageiro no mesmo nó = perda de tempo
  pros dois (briga) — brigar pela sobrevivência com preço.

Predições falsificáveis: com tag+benefício → clustering territorial por tag
(índice de assortment > controle sem tag); "sindicato" = quando a frota de
uma tag mantém preço/território estável entre gerações. Controle: sem
benefício de densidade, tags se misturam (deriva neutra). Perigos herdados:
viés de sobrevivência (medir TODOS), semáforo-sabotador (14 §2.1).

## 5. Treino mais rápido SEM bug (o pedido de perf)

Diagnóstico: GPU ocupada mas VRAM ~1GB — nos E-runs (B=16k) somos limitados
por LANÇAMENTO de kernel, não por conta. Alavancas, em ordem de segurança:

1. **Mega-lote de populações**: braços×sementes do MESMO experimento são o
   mesmo grafo de computação → empilhar 12 populações num Lote só
   (B 16k→196k, região onde a GPU rende) com seleção POR BLOCO e um Generator
   por bloco. Ganho esperado ~2-3×; bit-compatível provável (testar
   equivalência como no evoluir_juntas — o teste decide, não a fé).
2. **compile mode reduce-overhead** (cudagraphs/hipGraphs) no loop pequeno —
   testar na gfx1032; se capturar, mata o overhead de vez.
3. NUNCA: subir P por subir (P=8192 já mostrou retorno decrescente) ou
   afrouxar portões por velocidade.

## 6. Foco (pra não dispersar)

Tronco continua: **E11-cidade** (distritos+casa+relógio) — agora carregando
§2 (sono episódico com casa), §3 (corpo evoluível) e §4 (sociedade na arena
de distritos) como MÓDULOS do mesmo mundo. Ordem: perf §5.1 → sono episódico
§2 (com teto medido ANTES) → E11-D1 → §3 → §4. Cada um com portão, predição
e controle, como sempre.
