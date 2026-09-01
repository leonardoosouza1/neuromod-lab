# 17 — Prefeito: co-evolução cidade ↔ táxis (linha de pesquisa)

**Origem (Leonardo, 2026-08-31):** *"um modelo jogando contra? ele precisa não
jogar contra em si, mas ele dita a sobrevivência da cidade e dos táxis —
controla imposto, trânsito e afins, tudo para que ambos cooperem mais sem
saber."* Status: DESENHO. Implementar depois do G2 do endócrino (docs/16) ou
em paralelo se os mundos do Colab travarem.

## 1. A ideia em uma frase

Um segundo ser evolutivo — o PREFEITO — controla as alavancas do mundo
(imposto, tráfego, preços, spawn) sem falar com os táxis; a fitness dele é o
FLORESCIMENTO da cidade, não a derrota de ninguém. Cooperação emerge (ou não)
sem canal de comunicação — é design de mecanismo evoluído.

## 2. O prefeito

| | |
|---|---|
| alavancas (ação a cada K=50 passos) | imposto (5–40%), preço dos serviços (×0.5–2), injeção de tráfego por região, taxa de spawn de passageiros |
| observação (interocepção da CIDADE) | entregas/passo, mortes/avarias da frota, caixa médio E MÍNIMO dos táxis, arrecadação — agregados, nunca o estado interno de um táxi |
| cérebro | mesmo formato dos táxis: linear (evoluível), NP pequeno |
| **fitness** | **MULTIPLICATIVA: arrecadação_sustentada × sobrevivência_da_frota** |

A fitness multiplicativa é a Lei da Moeda Cruzada aplicada: com fitness aditiva
o prefeito degenera (imposto máximo → arrecada muito e mata a frota — curto
prazo vence). Multiplicativo força o equilíbrio: cidade rica COM frota viva.

## 3. Perigos já pagos em outros lugares (não repetir)

1. **Viés de sobrevivência** (doc 14 §2.1: o semáforo SABOTADOR parecia ótimo
   medindo só quem chegava): medir vazão + estado de TODOS os táxis, inclusive
   os mortos, nunca médias de sobreviventes.
2. **Reward hacking do prefeito**: matar os táxis fracos melhora a média da
   frota — por isso caixa MÍNIMO e mortes entram na observação e a
   sobrevivência entra multiplicando.
3. **Red Queen / co-evolução instável**: nunca evoluir os dois SIMULTÂNEOS.
   Co-evolução POR ERAS: congela táxis → evolui prefeito → congela prefeito →
   evolui táxis → repete. Cada era com fitness medida contra população
   congelada (avaliação estacionária).
4. **Inspeção de trajetória obrigatória** (07 §11): um prefeito com fitness
   alta e comportamento absurdo é hack até prova em contrário.

## 4. Gates (mesma disciplina de sempre)

- **G0 identidade**: prefeito com alavancas travadas no default ≡ mundo atual
  bit a bit (spread 0.000 no portão).
- **G1 teto**: (a) grid search de imposto CONSTANTE → melhor valor fixo =
  baseline; (b) prefeito SCRIPTADO onisciente (regra à mão que vê tudo) =
  teto. Se teto − baseline < amplitude entre sementes, o mundo não tem espaço
  pra governança — engrossar (ex.: choques exógenos que exigem resposta).
- **G2 co-evolução por eras**, predições registradas ANTES:
  1. Imposto evoluído converge pra faixa INTERMEDIÁRIA (curva de Laffer
     emergente) — nem 5%, nem 40%.
  2. CONTROLE adversarial: prefeito com fitness = só arrecadação (aditiva)
     degenera a frota — se não degenerar, o mecanismo multiplicativo não está
     fazendo nada e o design cai.
  3. Frota sob prefeito evoluído > frota sob melhor imposto fixo (além do
     ruído entre sementes) — governança adaptativa paga.
  4. Táxis co-evoluídos com o prefeito ficam MENOS defensivos que táxis
     evoluídos sob choques aleatórios (cooperação implícita mensurável nos
     pesos: menor peso em custo/congestão).

## 5. Por que isso conversa com o resto

- O prefeito é NEUROMODULAÇÃO DO MUNDO: modula parâmetros (imposto, preço),
  não estado — mesmo princípio da segunda camada (docs/03), um nível acima.
- `ruas` morreu porque desvio de rota não é acionável em 1 salto (PREDICOES);
  as alavancas do prefeito são TODAS acionáveis (mudar um escalar global).
- Encaixa no mundo `cidade` do PRD (pico + casa + carga mental): o prefeito
  pode ditar o próprio horário de pico — e aí o endócrino dos táxis precisa
  rastrear um regime que RESPONDE a eles. Fechamento do loop ecológico.
