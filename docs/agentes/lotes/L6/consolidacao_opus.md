Rodar o ajuste no shell foi barrado (comando exigia aprovação, sessão não-interativa), então fiz a regressão à mão sobre as 19 políticas do placar+feedbacks — os números abaixo vêm dessa conta, não de um script.

**O que ainda mata a melhor política.** A melhor é L6 p4 = 0.56 (fome 47 % / dano 48 % / sede 21 %), ou seja ~0.26 absoluto de fome, ~0.27 de dano, ~0.12 de sede. A série está achatando: 0.66 → 0.62 → 0.57 → 0.56 (último ganho: 0.01). O padrão real não é limiar: **mortalidade é quase função linear do throughput** — ajuste sobre as 19 políticas dá `mortos ≈ 1.48 − 0.047 × corridas`, r = −0.97 (14.3 corridas → 0.78; 19.0 → 0.56). Toda alavanca que custou ticks perdeu (noite 3×, reparo cedo 4×, fila no posto). Onde há tick sobrando, medido: a política explícita fica **42.8 % do tempo livre parada dentro do raio de um serviço, contra 26.2 % do campeão** — 16 pp de ociosidade ≈ 1.5 corridas ≈ −0.07 de mortos pela regressão. Essa é a alavanca com mais chance, e é nova (H6 tirou o `ficar` inteiro e explodiu para 0.88; aqui é *limitar*, não remover). Segunda: o buraco noturno de comida — entre 1h e 5h a política faz 27 refeições contra ~400 do campeão, com o posto fechado; fome ainda é 47 %. Terceira: gasolina, única direção que pagou 3 lotes seguidos (0.62 → 0.57 → 0.56, com corridas subindo 18.4 → 19.0). E um aviso: **água chegou no fim** — cortar mais levou sede de 7 % para 34 % e mortos de 0.56 para 0.62.

```tarefa
Base = L6 p4 (mortos 0.56, 19.0 corridas, fome 47 % / dano 48 % / sede 21 %).
REGRA DURA: mortos ~= 1.48 - 0.047 x corridas (r=-0.97 em 19 politicas). Nenhuma mudanca pode derrubar corridas abaixo de 18.5 — se sua alavanca custa ticks, ela perde.
ALVO DO LOTE: o tempo LIVRE parado no raio de um servico e' 42.8 % (campeao: 26.2 %). Cortar essa ociosidade vale ~1.5 corridas ~= -0.07 de mortos.
p1 COMIDA: nao mexer no limiar de dia (come com fome ~64, morre a 90 — ja e' bom). Atacar SO' o buraco 1h-5h (27 refeicoes contra ~400 do campeao): estocar comida antes das 21h e comer em ponto de comida com fome > 55 entre 22h e 6h.
p2 AGUA: NAO cortar mais (sede foi de 7 % para 34 % quando cortaram). Beber so' com agua < 35, comprar no maximo 1x por parada.
p3 REPARO: oficina so' com vida < 35 E caixa > 40, e desvio maximo de 8 u ate' a oficina. Reparo cedo ja' perdeu 4 vezes (0.63/0.66/0.82).
p4 GASOLINA: seguir a direcao que venceu 3x (mais paradas, menos litros): top-up de 20-25 L sempre que passar a <= 2 u de um posto com tanque < 60. Meta: panes de ~7 para < 4 por vida SEM perder corrida.
p5 ORDEM/TICKS: alavanca saturada (0.57). Unico teste: sair do raio no tick seguinte a' ultima compra pendente, maximo 3 ticks parados por parada.
p7 RUA: manter peso 0.15 como desempate (peso 5.0 paralisa). Unico teste novo: dobrar para 0.30 quando vida < 40, ja' que dano e' 48 % das mortes.
p6/p8 LIVRE: NOITE/descanso esta' APOSENTADA (0.74-0.78 em 3 lotes) — nao usar. Use o slot para CACAR PASSAGEIRO: livre e sem compra pendente = sair do raio do servico e mover na direcao do ultimo embarque/da regiao de maior demanda.
Antes de rodar, preveja mortos, corridas e o % de cada causa (fome/dano/sede).
```

```hipoteses
| H23 | GASOLINA: paradas ainda mais frequentes com menos litros (3o teste, sobre L5 p4) | ✓ 0.57 → 0.56, corridas 18.9 → 19.0 — melhor global; unica direcao que pagou 3 lotes seguidos | L6 p4 |
| H24 | ORDEM das compras + ticks parado (3o teste, base nova) | ~ 0.57: empata com a base — alavanca saturada, nao repetir sem mudar de eixo | L6 p5 |
| H25 | NOITE/descanso/fadiga | ✗ 3 lotes: 0.78 / 0.74 / 0.78, corridas 15.0 / 16.0 / 14.3 — corta renda e nao mexe na fome. APOSENTAR a alavanca | L4 p6, L5 p6, L6 p6 |
| H26 | AGUA mais agressiva sobre a base de gasolina | ✗ 0.56 → 0.62: sede sobe de 21 % para 34 % das mortes. Agua chegou ao fim do curso util | L6 p2 |
| H27 | REPARO mais cedo/mais barato (4o teste) | ~ 0.63: dano cai de 48 % para 42 % mas corridas caem para 17.8 — o caixa gasto na oficina falta depois | L6 p3 |
| H28 | mortalidade e' funcao do throughput: mortos ≈ 1.48 − 0.047 × corridas (r = −0.97, n=19) | ✓ regressao sobre placar+feedbacks; explica por que noite/reparo/fila sempre perdem | L3–L6 |
| H29 | LIVRE sem eixo proprio (agente escolheu fadiga de novo) | ✗ 0.77, corridas 14.9 — slot LIVRE precisa de eixo prescrito, senao repete alavanca morta | L6 p8 |
| H30 | ficar parado no raio do servico so' enquanto ha' compra pendente (livre = cacar passageiro): 42.8 % → ~26 % do campeao | ⏳ a testar — previsao −0.05 a −0.08 de mortos via +1.5 corridas | L7 |
| H31 | comida estocada antes das 21h para cobrir 1h-5h (27 refeicoes contra ~400 do campeao) | ⏳ a testar — fome e' 47 % e o furo e' noturno, nao diurno (H12/H22 ja' mostraram) | L7 |
| H32 | RUA com peso dependente da vida (0.15 normal, 0.30 com vida < 40) | ⏳ a testar — primeira tentativa de atacar dano sem gastar caixa na oficina | L7 |
```

O ponto de virada do lote 7: parar de calibrar limiares de consumo e passar a caçar tick perdido. Os três recursos (fome, dano, sede) já estão num equilíbrio onde apertar um solta o outro — quatro lotes de evidência mostram isso (água apertada empurra sede de 7 % para 34 %, reparo apertado empurra corridas para baixo). O que não está em equilíbrio é o tempo: 42.8 % do tempo livre parado no raio de um serviço e um intervalo mediano de 61 ticks entre corridas (~6 h) contra 57 do campeão. Se a regressão segurar, 20.5 corridas coloca a política em ~0.51 sem tocar em nenhum limiar de sobrevivência — e é a primeira vez na série que uma alavanca ataca a causa em vez do sintoma. Vale também prescrever o eixo do slot LIVRE: das duas vezes em que ficou aberto, o agente reinventou fadiga e entregou 0.77.