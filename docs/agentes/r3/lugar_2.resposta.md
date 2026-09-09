```json
{
 "nome": "r3-lugar2-demanda-bimodal-centro-periferia",
 "predicao": "Variação 2 (distinta do gradiente monotônico centro>residencial>industrial>periferia usado por outro agente): contraste BIMODAL — dois polos de demanda opostos no mapa (centro miolo, periferia borda) contra dois desertos (industrial, residencial). dem: centro=1.6, periferia=1.6, industrial=0.4, residencial=0.4 (soma=4.0, igual ao base). Ponto de trabalho fixo mantido: pax_cidade=true, npx=48, respawn=20; só 'dem' muda. MECANISMO: linear não lê e_demanda/e_espera (achado 84); ao ficar livre ele roda sem saber qual polo está quente AGORA. Como centro e periferia ficam ~100-140u distantes (atravessando os desertos industrial/residencial, rua-fora custo 3), o linear frequentemente termina corrida num polo e o próximo passageiro nasce no polo oposto — viagem longa 'as cegas', sem garantia de encontrar demanda do outro lado. Na calibração limpa, npx48 já deixa o linear na borda da banda (mortos 0.78); o bimodal deve empurrar pra cima por tempo extra em trânsito: PREDIÇÃO linear mortos 0.80–0.84 (perto do teto da banda; ~16-18 entregas, abaixo das 20.9 do base uniforme). COMPLETO e bilinear risco+demanda+espera leem e_demanda (qual polo está quente) e e_espera (evitar polo já concorrido/recém-esvaziado), podendo se reposicionar ANTES de ficar livres, na direção do polo certo: PREDIÇÃO mortos ≤0.75 (≥8-10pp abaixo do linear) OU renda pareada ≥+25%, com menos tempo em trânsito puro entre desertos e mais tempo perto de demanda ativa. RISCO DECLARADO: se o linear ultrapassar 0.84 (banda estourada), é resultado negativo com mecanismo — bimodal nesta escala de npx é grande demais pro corpo aguentar a travessia, e a alavanca seguinte seria trimodal (3 polos mais próximos entre si) em vez de 2 polos nos extremos do mapa.",
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
   "dem": 1.6,
   "dens": [1.0, 1.5, 1.0, 0.5, 1.0]
  },
  "industrial": {
   "pmul": 0.6,
   "aliq": 0.1,
   "alug": 0.8,
   "dem": 0.4,
   "dens": [2.5, 0.0, 1.0, 0.0, 2.0]
  },
  "residencial": {
   "pmul": 1.0,
   "aliq": 0.15,
   "alug": 1.0,
   "dem": 0.4,
   "dens": [0.0, 2.0, 1.5, 2.0, 0.0]
  },
  "periferia": {
   "pmul": 0.5,
   "aliq": 0.0,
   "alug": 0.8,
   "dem": 1.6,
   "dens": [0.5, 0.5, 0.5, 0.5, 0.0]
  }
 },
 "passageiros": {
  "npx": 48,
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
 "bracos": [
  "linear",
  "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)",
  "bilinear risco+demanda+espera (esc 1)"
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