```json
{
 "nome": "contraste-demanda-conservado-r3-lugar1",
 "predicao": "Ponto fixo (pax_cidade true, npx 48, respawn 20 — calibração limpa: linear 0.78). Único parâmetro mudado: dem por distrito, mantendo sum(dem)=4.0 igual ao base (variação 1: CONTRASTE PURO, sem inflar demanda total — diferente de só somar mais no centro). centro 2.0->3.0 (75% da demanda da cidade), residencial 1.0->0.7, industrial 0.7->0.2, periferia 0.3->0.1 (2.5%, quase morta). LINEAR (controle): não lê e_demanda/e_espera na direção (achado 84) — continua rodando em industrial/periferia como se a demanda ainda fosse uniforme; essas viagens de busca agora batem em vazio (só 7.5% da demanda fora do centro/residencial). Predição: mortos sobe de 0.78 para 0.85-0.90, entregas cai de 20.9 para 10-13, renda cai >=35% (gasta fuel_passo/fad_passo/calor sem achar passageiro fora do centro). COMPLETO: usa e_demanda para se posicionar perto do centro, reduz viagem vazia -> bate linear em >=10pp mortos (ex.: 0.70-0.75) OU >=30% renda pareada. BILINEAR risco+demanda+espera (esc 1): mecanismo mais fino, pesa espera x demanda explicitamente -> prefere ESPERAR perto do centro (75% de chance de pax nascer ali) em vez de rodar até periferia à toa; ganha o tempo que o linear perde andando; também >=10pp mortos ou >=30% renda sobre linear. RISCO/honestidade: se os pesos do linear (evoluídos em mundo uniforme) já favorecem ficar perto do centro por causa de pmul/aliq mais altos lá (correlação espúria, não leitura de demanda), o efeito pode aparecer sozinho por acidente de treino, não por mecanismo causal — nesse caso contraste sozinho não prova nada. Se isso acontecer, o que separaria de verdade: reativar ponto=30 junto do contraste (paga esperar de propósito — achado 95 mostrou que espera só vale com escassez+ponto simultâneos). Mas o cenário abaixo muda só demanda, como pedido.",
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
   "dem": 3.0,
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
   "dem": 0.7,
   "dens": [0.0, 2.0, 1.5, 2.0, 0.0]
  },
  "periferia": {
   "pmul": 0.5,
   "aliq": 0.0,
   "alug": 0.8,
   "dem": 0.1,
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