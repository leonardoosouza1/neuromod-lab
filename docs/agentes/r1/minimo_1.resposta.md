```json
{
 "nome": "minimo-pax-cidade-flip",
 "predicao": "Único parâmetro mudado (menor desvio possível do base.json): passageiros.pax_cidade false -> true. Mecanismo (achado 84): o linear não lê direção/posição nos sentidos do corpo ao decidir a ação — sua política ignora onde o passageiro está. Quando o passageiro nasce perto do táxi (base), essa cegueira não custa nada; quando nasce em qualquer ponto da cidade (pax_cidade=true), buscar exige rota eficiente, e só o COMPLETO tem hipocampo/córtex para orientar o deslocamento. Números: linear mortos sobe para >= 0.55 (de uma base quase nula com passageiro grátis rodando) porque perde ticks andando sem rumo eficiente, consumindo fuel_passo .15/tick e agua/fome sem repor renda, entrando em dívida (LIMITE_DIVIDA 60) ou pane (KCAL_PANE 8); COMPLETO mortos <= 0.40 por rotear com menos ticks ociosos/tortuosos por corrida. Gap esperado >= 15 pp, cumprindo o corte de 10 pp. Nenhum outro campo do mundo, distrito, corpo ou protocolo foi alterado — isola o efeito único de precisar NAVEGAR até o passageiro em vez de ele aparecer ao lado.",
 "mundo": {
  "L": 200,
  "dias": 10,
  "regua": "riqueza",
  "K": 6,
  "ruas": {
   "dentro": 1,
   "fora": 3
  },
  "precos": {
   "amp": 0.5,
   "periodo": 3
  }
 },
 "distritos": {
  "centro": {
   "pmul": 2.0,
   "aliq": 0.35,
   "alug": 2.5,
   "dem": 2.0,
   "dens": [1.0, 1.5, 1.0, 0.5, 1.0]
  },
  "industrial": {
   "pmul": 0.6,
   "aliq": 0.1,
   "alug": 0.8,
   "dem": 0.7,
   "dens": [2.5, 0.0, 1.0, 0.0, 2.0]
  },
  "residencial": {
   "pmul": 1.0,
   "aliq": 0.15,
   "alug": 1.0,
   "dem": 1.0,
   "dens": [0.0, 2.0, 1.5, 2.0, 0.0]
  },
  "periferia": {
   "pmul": 0.5,
   "aliq": 0.0,
   "alug": 0.8,
   "dem": 0.3,
   "dens": [0.5, 0.5, 0.5, 0.5, 0.0]
  }
 },
 "passageiros": {
  "npx": 12,
  "respawn": 20,
  "pax_cidade": true,
  "ponto": 0,
  "tarifa_base": 3,
  "tarifa_km": 0.25
 },
 "corpo": {
  "dinh0": 10,
  "fome_passo": 0.32,
  "kcal_pane": 8,
  "guincho": 0,
  "fuel_pos_pane": 15
 },
 "bracos": ["linear", "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)"],
 "protocolo": {
  "P": 1024,
  "G": 120,
  "paciencia": 40,
  "R": 4,
  "seeds": [0, 1, 2, 3, 4]
 }
}
```