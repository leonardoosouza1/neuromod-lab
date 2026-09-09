```json
{
 "nome": "cidade-ima-centro-escasso",
 "predicao": "cidade ima: demanda extrema no centro (dem 4.0) vs periferia quase morta (dem .05), escassez cidade toda (npx 5, respawn 80), rua fora mais cara (4x) pra punir vagar sem alvo. (a) linear mortos >= .60, entrega <= 8, renda baixa: vaga sem mirar direcao do e_demanda (achado 84), gasta tempo fora do centro onde nao ha passageiro. (b) bilinear risco+demanda+espera e/ou COMPLETO mortos <= .40, entrega >= 14, renda >= +40% pareada: usam e_demanda/e_espera pra ficar perto do centro e ESPERAR embarque em vez de vagar. (c) bilinear risco (esc 3, sem e_demanda/e_espera) repete o linear, mortos >= .55: isola que a peca que falta e demanda+espera, nao risco. Mecanismo: so COMPLETO e o bilinear-demanda-espera enxergam ONDE a demanda mora; sem essa direcao, ficar/escolher lugar nao e possivel, so vagar.",
 "mundo": {
  "L": 200,
  "dias": 10,
  "regua": "riqueza",
  "K": 6,
  "ruas": {
   "dentro": 1,
   "fora": 4
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
   "dem": 4.0,
   "dens": [1.0, 1.5, 1.0, 0.5, 1.0]
  },
  "industrial": {
   "pmul": 0.6,
   "aliq": 0.1,
   "alug": 0.8,
   "dem": 0.2,
   "dens": [2.5, 0.0, 1.0, 0.0, 2.0]
  },
  "residencial": {
   "pmul": 1.0,
   "aliq": 0.15,
   "alug": 1.0,
   "dem": 0.5,
   "dens": [0.0, 2.0, 1.5, 2.0, 0.0]
  },
  "periferia": {
   "pmul": 0.5,
   "aliq": 0.0,
   "alug": 0.8,
   "dem": 0.05,
   "dens": [0.5, 0.5, 0.5, 0.5, 0.0]
  }
 },
 "passageiros": {
  "npx": 5,
  "respawn": 80,
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