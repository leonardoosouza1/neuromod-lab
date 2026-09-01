# 21 — Ontogenia: bebê → adulto como arquitetura (a 3ª escala de tempo)

**Pergunta do Leonardo (2026-08-31):** como funciona o cérebro do bebê vs o do
adulto — e como planejar algo que EVOLUA em vida, com a matemática como língua
comum ("se gero redes distintas com matemática, todas falam a mesma língua —
nasce algo mega eficiente porque a rede já compreendeu").

## 1. O retrato biológico (números verificados)

| fase | o que acontece |
|---|---|
| nascimento | ~todos os 86 bi de neurônios JÁ existem (neurogênese é quase toda pré-natal); as SINAPSES não — o bebê nasce com o hardware e quase nenhuma fiação fina |
| 0–3 anos | EXPLOSÃO sináptica: densidade de sinapses atinge o PICO aos 2–3 anos (Huttenlocher), bem acima do adulto |
| ~5 anos | pico ENERGÉTICO: consumo de glicose do córtex chega a >2× o do adulto — o cérebro chega a tomar ~metade do metabolismo de repouso, e o CRESCIMENTO DO CORPO DESACELERA pra pagar a conta (Kuzawa, PNAS 2014). Energia comprada com corpo: a infância é um SUBSÍDIO metabólico |
| ~6 anos | volume cerebral ~adulto; mielinização segue intensa até ~10 e no pré-frontal até os 20+ (de trás pra frente: sensorial primeiro, executivo por último) |
| adolescência | PODA em massa: sinapses pouco usadas somem ("use it or lose it"); ~50% dos neurônios gerados morrem por competição trófica (doc 08 §6) |
| adulto | esparso, mielinizado (rotas quentes = rápidas e baratas), plasticidade GATEADA por neuromodulação — período crítico fecha quando a inibição PV amadurece e REABRE com ACh (doc 08 §8) |
| reflexos | o bebê nasce com reflexos primitivos (subcorticais) que o córtex depois INIBE e substitui — o inato é andaime, não produto final |
| antes do mundo | a retina gera ondas espontâneas ANTES de o olho abrir e elas já esculpem os mapas (doc 08 §5.5) — o cérebro treina no próprio ruído estruturado |

**Síntese em uma frase: o bebê é o cérebro CARO, denso e plástico que compra
informação; o adulto é o cérebro BARATO, podado e mielinizado que a executa.
A infância é o período em que a energia é gasta pra descobrir O QUE PODAR.**

## 2. A lição arquitetural mais profunda (a língua comum dele)

O genoma humano (~1.5 GB) NÃO codifica a fiação (86 bi neurônios × milhares de
sinapses — não cabe). Codifica **REGRAS**: cronograma de proliferação (late =
large), gradientes fracos de protomapa, regra hebbiana + competição, poda
trófica proporcional ao uso, períodos críticos. A anatomia EMERGE (doc 08,
princípio central — 4 forças locais, zero conhecimento global).

A intuição do Leonardo é exatamente essa, dita em matemática: **o genoma não
guarda pesos — guarda FÓRMULAS GERADORAS** (hierarquia do doc 19: nível 1
estrutura, nível 2 coeficientes resolvidos em vida). Se toda parte do cérebro
é gerada da mesma família matemática (EMA/filtros/solve fechado/regras de
poda), as partes são COMPONÍVEIS e o recém-nascido "já compreendeu": os
priors estão na regra, não no peso. Genoma compacto → seres baratos de
transmitir → evolução rápida. (É o DNA-V4 do Universe com outra roupa.)

## 3. As TRÊS escalas de tempo (o programa completo)

| escala | quem age | o que fixa | já temos |
|---|---|---|---|
| evolução (gerações) | seleção | as REGRAS geradoras (estrutura, cronograma, quando podar) | motor evolutivo ✓ |
| **desenvolvimento (UMA vida, estagiado)** | **ontogenia** | **quais órgãos sobrevivem, alocação, fiação** | **← o buraco; E8 abaixo** |
| vida online (segundos) | solve fechado / hormônios | coeficientes do momento | e5_leis ✓, PRD 16 |

## 4. O bebê digital resolve um problema que JÁ MEDIMOS

E4 (hoje): paisagem do órgão-Dijkstra é bimodal — 2 de 3 sementes nunca acham
a bacia de confiança positiva e afundam. A ontogenia é a semeadura NATURAL:

- **fase bebê** (primeiros T_b passos da vida): TODOS os órgãos ligados, gates
  abertos, temperatura de decisão alta (motor babbling), custo metabólico
  SUBSIDIADO (os "pais pagam" — na conta biológica, o corpo paga);
- **poda** (adolescência): órgão sobrevive ⟺ contribuição medida > limiar do
  Garimpo com trófico PROPORCIONAL AO USO (doc 08 §6.1 — com trófico fixo a
  poda não se adapta; já validado);
- **fase adulta**: só o que sobreviveu roda, custo pleno, plasticidade gateada
  (endócrino do PRD 16 decide reabrir — ACh reabre período crítico).

O órgão bom nunca depende de a evolução ACHAR a bacia: todo bebê NASCE com o
órgão ligado e a vida decide se ele fica. Bimodalidade morre por construção.

## 5. E8 — ontogenia no táxi (predições antes de rodar, como sempre)

Braços: ① adulto direto (sem infância — é o E4/E6 atual) ② infância sem poda
(paga tudo pra sempre) ③ infância + poda por uso ④ infância + poda ALEATÓRIA
com a mesma taxa (controle) ⑤ poda precoce (T_b curto — período crítico
insuficiente).

Predições: ③ ≥ ① em fitness adulta COM custo menor que ②; ③ acha a bacia boa
do órgão em ≥ 3/3 sementes (vs 1/3 do E4); ④ < ③ além do ruído (podar por uso
é o mecanismo, não podar por podar); ⑤ mata órgãos antes de provarem valor
(infância curta = adulto pobre — análogo do D3 do doc 08). Dados: o filme
`alocacao_elite` por geração + duty-cycle por órgão POR FASE DA VIDA.

Fontes externas: Kuzawa et al., PNAS 2014 (custo metabólico do desenvolvimento);
Chugani, PET do desenvolvimento; Huttenlocher (densidade sináptica);
doc 08 (Finlay & Darlington, Rakic, Hensch) — já no repo.
