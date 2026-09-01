# 22 — Cidade com Distritos: economia regional, relógio de 24h e ROTINAS

**Direção do Leonardo (2026-09-01):** mundo grande e espaçado, separado em
DISTRITOS — aluguel, combustível e manutenção com preço por região; barreiras;
upgrades como TIPOS de táxi (melhor sem ser overpower); sobrevivência
COMPETITIVA (não mais difícil): imposto+manutenção+aluguel+combustível = muitos
parâmetros pra compreender e se adaptar. Dia de 24h com recuperação por
horário (noite 100%, pós-meia-noite 50%, dia 20%) → **rotinas de sono
emergentes**. Picos de demanda aleatórios ou seguidos.

## 1. Sobre "distância vira teleporte" — já resolvido, mas o ponto fica

Mover custa TEMPO hoje: aresta de custo 10 = ~10 passos PRESO em trânsito
(rest), queimando combustível/fadiga. Dois nós a 100 km = muitos passos de
viagem, não teleporte. O que falta não é física de distância — é **geografia
ECONÔMICA**: hoje todo lugar custa igual. Distritos consertam isso.

## 2. O mundo `distritos`

- Cidade grande (n=120+, `--n-cidade` pronto) particionada em D=4-6 distritos
  (por proximidade espacial no gerar_cidade).
- **Preços por distrito**: combustível (posto do centro 2×, periferia 0.7×),
  manutenção (borracharia do distrito industrial barata), comida.
- **Moradia**: alugar CASA num distrito (custo recorrente por dia); dormir em
  casa recupera melhor que na rua. Centro = caro e perto da demanda; periferia
  = barato e longe (o trade-off de localização clássico → rotina de commute).
- **Barreiras**: pedágio nas arestas entre distritos (custo dinheiro, não
  tempo) — atravessar tem que valer a corrida.
- **Demanda por distrito**: centro concentra passageiros no PICO, bairros à
  noite (gente voltando) — geografia acoplada ao relógio.

## 3. Relógio de 24h e o SONO (a regra do Leonardo, literal)

- Dia = 480 passos (1 passo ≈ 3 min). T_evo ≥ 3 dias (1440+) — perf atual
  aguenta (~15 ms/passo na escala de bateria).
- **Recuperação do descanso DEPENDE DA HORA** (gradiente que cria rotina):
  - dormir 20h–00h: 100% da taxa de recuperação (fadiga E carga mental)
  - dormir 00h–06h: 50%
  - dormir de dia: 20% (e só fadiga; carga mental não recupera de dia)
  - em CASA: recupera carga mental; na rua: só fadiga (liga no PRD 16)
- O relógio é OCULTO (fase por mundo aleatória); sinal fraco observável:
  "luz" = senoide ruidosa do dia (proxy, como luminosidade real).
- **Picos**: manhã e fim de tarde (2-3× demanda), com jitter; modo
  `picos-aleatorios` como controle (sem estrutura → rotina não deve emergir).

## 4. Tipos de táxi (upgrades SEM dominância — design por nicho)

| tipo | custo | nicho onde é ótimo |
|---|---|---|
| popular (nasce) | — | equilíbrio |
| econômico | $$ | corridas curtas, distrito denso (menos fuel/km) |
| veloz | $$$ | corridas longas entre distritos (+15% vel, +20% fuel) |
| resistente | $$ | distritos esburacados (metade do desgaste de pneu/óleo) |

Regra de balanceamento DECLARADA antes de rodar: para cada tipo existe um
regime em que ele maximiza lucro/dia — verificado por especialistas scriptados
ANTES da evolução (se um tipo domina todos os regimes, recalibrar UMA vez).

## 5. Competitivo, não difícil (arena)

K táxis no MESMO mapa (arena já existe, WIP de 2026-09-01): passageiro pego
não existe pro outro; posto com fila; preço de combustível por distrito SOBE
com a demanda local (mercado emergente). A pressão vem dos OUTROS, não de
knobs de dificuldade — exatamente o pedido. Prefeito (doc 17) entra depois
governando POR DISTRITO (imposto regional).

## 6. Como MEDIR "rotina emergiu" (a métrica que faltava)

Rotina = periodicidade endógena no comportamento. Métrica: espectro (FFT) da
série temporal de cada AÇÃO (dormir/abastecer/trabalhar) ao longo de 3+ dias:

    rotina ⟺ pico espectral em f=1/480 passos, acima do controle

Controles: (a) mundo `picos-aleatorios` (sem estrutura de 24h → sem pico
espectral); (b) recuperação CONSTANTE por hora (sem gradiente → dormir vira
indiferente ao horário). Visual: mapa 24h×dias das ações (o "sonograma" do
táxi) — dá pra VER a rotina se formando com as gerações.

## 7. Idéias adicionais (minhas, pra discutir)

1. **Commute como assinatura**: distância casa↔centroide-de-trabalho por ser —
   distribuição bimodal esperada (moradores do centro vs periféricos).
2. **Manutenção preventiva vs corretiva**: revisar barato no distrito
   industrial vs quebrar longe (guincho caro) — rotina de manutenção.
3. **Fim de semana** (a cada 7 dias, demanda diferente) — testa rotina de 2ª
   ordem (semanal em cima da diária).
4. **Métrica de nicho na arena**: overlap espacial entre táxis — competição
   deve ESPALHAR os seres pelos distritos (partição de nicho emergente, tipo
   Universe/fingerprint).
5. Ontogenia em cima (E8): bebê explora a cidade toda; poda decide o
   TERRITÓRIO e o TIPO de táxi do adulto.

## 8. Ordem de implementação

| fase | entrega | gate |
|---|---|---|
| D1 | distritos + preços regionais + aluguel/casa (single-agent) | perito com rotina scriptada ≥8× aleatório; nenhum preço degenerado (ninguém falido/rico demais) |
| D2 | relógio 24h + regra de sono + picos | teto: especialista COM relógio visível vs sem (oráculo) > ruído |
| D3 | tipos de táxi | especialistas por nicho sem dominância |
| D4 | espectro de rotina + sonograma no painel | predição: pico em 1/480 só com gradiente de recuperação |
| D5 | arena competitiva no distritos | partição de nicho emergente |
| D6 | prefeito distrital | doc 17 |

Predições formais entram no PREDICOES.md quando D1 estiver implementado.
