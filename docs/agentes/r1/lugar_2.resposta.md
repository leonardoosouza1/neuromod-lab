```json
{
 "nome": "oasis-central-recompensa-espera",
 "predicao": "MECANISMO: pax_cidade nasce em volta do centro DO DISTRITO com intensidade ~dem; aqui dem centro=5.0 vs industrial=0.1/residencial=0.15/periferia=0.05 (~30-100x), então ~95%+ dos passageiros da cidade toda nascem dentro/perto do centro. Fora do centro, pmul cai (industrial .6, residencial 1.0, periferia .4) então mesmo o raro passageiro achado longe paga pouco. Rua fora=6 (dobro do base) torna caçar passageiro fora do centro caro (ida+volta cara sem garantia de achar). Logo o ótimo é: ficar parado DENTRO do centro esperando o próximo spawn (que vem rápido, pois respawn escala com dem alta) em vez de rodar cego. LINEAR não condiciona a ação em e_demanda/e_espera por posição (não distingue 'estou no centro, vale esperar' de 'estou na periferia, vale ir embora') — mantém o mesmo padrão andar/parar não importa o distrito, gastando tempo e combustível em desertos de demanda. Números: linear mortos >= .75, entregas <= 8 em 10 dias, tempo parado-esperando <= 5% (igual ao achado 95, ele não espera). COMPLETO e/ou bilinear risco+demanda+espera (esc 1), que leem e_demanda/e_espera, aprendem a estacionar no centro e esperar: mortos <= 0.55 OU renda pareada >= +30% vs linear, com entregas >= 14 e tempo parado-em-centro >= 20% do tempo total. bilinear risco (esc 3, sem e_demanda/e_espera) fica preso perto do linear (mortos >= .70) por não enxergar a assimetria espacial — serve de controle de que a peça que falta é o sentido de lugar, não geometria de risco pura.",
 "mundo": {
  "L": 200,
  "dias": 10,
  "regua": "riqueza",
  "K": 6,
  "ruas": {
   "dentro": 1,
   "fora": 6
  },
  "precos": {
   "amp": 0.5,
   "periodo": 3
  }
 },
 "distritos": {
  "centro": {
   "pmul": 3.0,
   "aliq": 0.35,
   "alug": 2.5,
   "dem": 5.0,
   "dens": [1.5, 2.0, 1.5, 1.0, 1.0]
  },
  "industrial": {
   "pmul": 0.6,
   "aliq": 0.10,
   "alug": 0.8,
   "dem": 0.1,
   "dens": [1.0, 0.0, 0.5, 0.0, 1.0]
  },
  "residencial": {
   "pmul": 1.0,
   "aliq": 0.15,
   "alug": 1.0,
   "dem": 0.15,
   "dens": [0.0, 1.0, 1.0, 1.0, 0.0]
  },
  "periferia": {
   "pmul": 0.4,
   "aliq": 0.0,
   "alug": 0.8,
   "dem": 0.05,
   "dens": [0.3, 0.3, 0.3, 0.3, 0.0]
  }
 },
 "passageiros": {
  "npx": 6,
  "respawn": 15,
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
 "bracos": [
  "linear",
  "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)",
  "bilinear risco+demanda+espera (esc 1)",
  "bilinear risco (esc 3)"
 ],
 "protocolo": {
  "P": 1024,
  "G": 120,
  "paciencia": 40,
  "R": 4,
  "seeds": [0, 1, 2, 3, 4]
 }
}
```