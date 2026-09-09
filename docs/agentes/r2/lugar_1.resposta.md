```json
{
 "nome": "cidade-contraste-demanda-r2a1",
 "predicao": "npx=22, respawn=12 (banda 20-40/10-30, extremo baixo deliberado: poucos passageiros mas repostos rapido, pra isolar CONTRASTE espacial de escassez total) + dem centro 2.4 vs periferia 0.6 (4x, industrial 0.8, residencial 1.0): linear fica mortos 0.50-0.60 (~0.55), entregas 14-16, renda ~120 -- ainda desperdica viagem/gasolina indo pra periferia porque a decisao nao pesa e_demanda por contraste, so reage ao passageiro mais perto no instante. COMPLETO bate o linear: mortos <=0.42 (>=10pp) OU renda >=30% maior (~160), porque hipocampo/talamo usam e_demanda pra preferir ficar circulando perto do centro (corrida 4x mais frequente ali) e evitar a periferia de retorno baixo. bilinear risco+demanda+espera (esc 1) bate o linear pelo mesmo mecanismo mas menor margem: mortos ~0.45-0.50, entregas ~17, renda ~145 (le demanda mas sem a integracao temporal do hipocampo). Mecanismo: dem por distrito pesa nascimento E reposicao do passageiro (E70); com respawn global rapido (12) a escassez total nao mata ninguem, mas o contraste 4x faz periferia render pouco por viagem -- pela primeira vez quem le o campo de demanda ganha por ROTA, nao por sobreviver a fome.",
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
   "dem": 2.4,
   "dens": [1.0, 1.5, 1.0, 0.5, 1.0]
  },
  "industrial": {
   "pmul": 0.6,
   "aliq": 0.1,
   "alug": 0.8,
   "dem": 0.8,
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
   "dem": 0.6,
   "dens": [0.5, 0.5, 0.5, 0.5, 0.0]
  }
 },
 "passageiros": {
  "npx": 22,
  "respawn": 12,
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