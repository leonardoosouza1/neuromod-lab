```json
{
 "nome": "deserto-de-descanso",
 "predicao": "Mudei só 2 números: dens[descanso] de centro 0.5->0.0 e periferia 0.5->0.0 (industrial já era 0 no base), concentrando TODO descanso em residencial. Mantive pax_cidade=false, ponto=0, npx/respawn/preços/corpo iguais ao base — isola o eixo fadiga/planejamento-de-retorno sem misturar com geografia de passageiro ou escassez (eixos que outros agentes do grupo já mexem). Mecanismo: fadiga sobe .15/tick andando e só baixa em posto de descanso; o linear (mapa direto obs->ação, sem memória de tendência nem integração fadiga×distância-até-residencial) só reage quando a fadiga já está perto do limite, e se estiver em centro/industrial/periferia nesse instante não chega a tempo — cai em pane de fadiga repetida, perdendo vida/dinheiro em cascata (sem oficina por perto pra reparar rápido). O COMPLETO (hipocampo guarda histórico de fadiga e posição; córtex/tálamo cruzam fadiga atual x distância até residencial) antecipa a subida e desvia pra residencial com folga, evitando a pane. Números: linear mortos sobe pra >= 0.90 (referência do campeão linear evoluído ~0.80-0.85 no base); COMPLETO fica <= 0.75 (já tinha vantagem de ~7-8pp mesmo sem esse mecanismo, cf. pred 95/q13: 0.73 vs 0.81); gap pareado >= 15pp, acima dos 10pp pedidos.",
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
   "dens": [1.0, 1.5, 1.0, 0.0, 1.0]
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
   "dens": [0.5, 0.5, 0.5, 0.0, 0.0]
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