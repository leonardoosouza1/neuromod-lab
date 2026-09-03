
## E25b — curiosidade na infância (resultado 2026-09-03, triagem n=3): DESERTO de novo

| braço | fit | mortos | fome no fim |
|---|---|---|---|
| surdo + curioso ε=.2 (η=0) | 1.08 | 0.93 | 98 |
| aprende η=.1 + curioso ε=.2 | 0.69 | 0.94 | 98 |
| aprende η=.3 + curioso ε=.4 | 0.67 | 0.91 | 98 |

Predição 25 refutada. Quinto deserto da linha (E22 ×4 + este). Mecanismo:
ε sorteia um serviço disponível **no nó onde o táxi está**; o que mata é o
MOVIMENTO nunca levar ao nó de comida (fome 98 no fim = ninguém comeu), e
o movimento continua sendo só evolução — a plasticidade em vida mexe nos
ganhos de serviço, não em pra onde ir. Explorar sem chegar é explorar nada.
A comparação limpa: o direto com a mesma infância faz 0.47 mortos (E25).

**Linha fechada.** Aprender-em-vida como implementado (ΔG=η·h·usou·r) não
sobrevive ao pacote; o E26 (transmissão) dependia dele → cancelado. Se a
linha voltar, volta por outro caminho: plasticidade no MOVIMENTO
(recompensa ao chegar num serviço com necessidade alta), não nos ganhos.

Cláusula pré-registrada da predição 25 ("se o aprendiz continuar = surdo
curioso, a regra de recompensa está errada, não é falta de tentativa"):
aprendiz 0.94 = surdo curioso 0.93 → **a regra de recompensa está errada.**
Ela recompensa o ganho do serviço USADO; o que faltava era recompensar
CHEGAR. Fica como o diagnóstico da linha.
