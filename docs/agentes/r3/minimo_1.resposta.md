```json
{
 "nome": "posto-so-industrial",
 "predicao": "Cenario MINIMO (variacao 1, agente 1): unico parametro mudado = dens posto por distrito (base.json inalterado no resto, pax_cidade false, npx12). centro dens[0] 1.0->0.0, periferia dens[0] 0.5->0.0, residencial ja era 0.0 (mantido), industrial mantido 2.5 (unico distrito com posto). Mecanismo: o linear decide por combinacao fixa de sensores locais (e_fuel, achado 84 nao le lugar na direcao); ele reabastece de forma reativa onde estiver quando o tanque cai, sem saber ONDE fica o posto mais proximo. Como so ha posto em industrial, taxis que trabalham em centro/residencial/periferia (3 de 4 distritos, a maior parte do mapa) ficam presos: caem em pane longe do industrial, o reboque (guincho 0, mas 8 kcal de reserva + 15L) consome tempo e reserva que deveriam ir para fome/agua, empilhando causas de morte. COMPLETO e bilinear risco (esc 3) leem risco/distancia (sentido tipo d_posto do braco 'minimo 3') e antecipam a ida ao industrial antes do fuel ficar critico, convertendo 'onde reabastecer' em decisao. Numeros esperados (vs referencia historica: campeao evoluido em mundo com posto multi-distrito = mortos 0.85, panes 6.8/vida, abastecidas 4.2/vida): linear mortos 0.88-0.93, panes 9-10/vida, abastecidas 2.5-3.0/vida, entregas ~9-11; COMPLETO mortos 0.75-0.80, panes 5-6/vida, abastecidas 4.0-4.5/vida, entregas ~14-16; bilinear risco (esc 3) mortos 0.77-0.82, panes 5.5-6.5/vida, abastecidas 3.8-4.3/vida, entregas ~13-15. Aposta: COMPLETO e bilinear risco batem o linear em >= 10pp de mortos e reduzem panes em >= 30% porque leem lugar (risco espacial) na hora de decidir reabastecer, o linear nao.",
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
   "dens": [0.0, 1.5, 1.0, 0.5, 1.0]
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
   "dens": [0.0, 0.5, 0.5, 0.5, 0.0]
  }
 },
 "passageiros": {
  "npx": 12,
  "respawn": 20,
  "pax_cidade": false,
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