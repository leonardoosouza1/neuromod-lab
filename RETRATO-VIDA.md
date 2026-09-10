# Mapa, caminho e o que acontece dentro do cérebro

Duas folhas: `mapa-caminhos.png` (a cidade e o que cada ser faz nela) e
`dentro-do-cerebro.png` (uma vida inteira vista por dentro). O gravador é
`src/retrato_vida.py` — passagem para frente, CPU, ~4 min, nada de evolução.

```
python retrato_vida.py --bateria .../e78/e43_P128.json --out DIR --dias 8 --passo 2 --sementes 2
```

Três campeões (linear, cérebro completo, sem hipocampo) rodam **no mesmo mundo**
(`jardim_comum=True`): mesmo berço, mesmo fluxo de passageiros. Tudo o que difere entre
os painéis é o ser.

A orientação da textura do mapa foi conferida por medição, não por olho: o custo médio sob
o caminho real é **2.05** contra **2.40** em pontos aleatórios com `custo[iy, ix]`, e
**2.65** (pior que o acaso) com os índices trocados.

---

## Folha 1 — a cidade e os caminhos

| ser | vive | entregas | panes | raio de ação | parado |
|---|---|---|---|---|---|
| linear (espinha) | 6.0 d | 22 | 3 | 41 m | 6 % |
| cérebro completo | 4.4 d | 8 | 8 | **28 m** | 0 % |
| sem hipocampo | 3.1 d | 12 | 3 | 43 m | 3 % |

Três coisas saltam do desenho:

1. **Os três vivem num canto.** A cidade tem 200×200 e o raio de ação é 28–43 m. Nenhum
   dos campeões chega perto de conhecer o mapa — eles operam num bairro. Isso reforça o
   diagnóstico do hipocampo por outro caminho: um mapa de 12 distritos é inútil para quem
   nunca sai de três.
2. **O cérebro completo é o mais encolhido** (raio 28 m contra 41 do linear) e é o que
   mais quebra (8 panes contra 3). Ele fica perto e mesmo assim seca o tanque — o que é
   consistente com gastar a faixa dinâmica em outra coisa que não a rota.
3. **O linear anda mais longe, entrega quase o triplo e vive mais.** O caminho dele tem
   trechos longos e retos pelas ruas claras; o do completo é um novelo curto.

## Folha 2 — dentro do cérebro completo, tique a tique

**(a) Corpo.** O padrão é um dente de serra limpo: fome sobe em rampa até 100 e cai a zero
quando ele come (verticais verdes); gasolina desce e é reabastecida (verticais azuis);
água quase não é problema. O dinheiro (laranja tracejado) é escada — sobe por entrega,
desce por compra. A partir do dia 2 a gasolina passa a viver perto de 15 e as panes
(verticais vermelhas) viram rotina: ele não está mais escolhendo abastecer, está sendo
rebocado.

**(b) Contribuição por bloco.** Tálamo e córtex dominam a direção a vida inteira
(~0.6 e ~0.6 de "dirige"), as camadas genéricas ficam duas ordens de grandeza abaixo
(~0.02), o reflexo em 0.005 e o **hipocampo em 0.0004** — quatro ordens de grandeza abaixo
do tálamo. É a mesma hierarquia que a bancada mostrou, agora ao longo de uma vida real e
sem ablação.

**(c) Atenção.** Aqui está o achado novo desta folha: os portões **não são estáticos, e não
são simétricos**. `rota` fica em ~1.5 (aberto, acima do neutro 1.0) e sobe devagar ao longo
da vida; `serviços`, `corpo`, `tempo` e `economia` ficam todos **abaixo de 1.0** e vão
**fechando** conforme ele envelhece. A soma dos cinco é 3.39, não 5 — o ser evoluído
**fecha atenção líquida** e concentra o que sobra na rota. Os degraus verticais coincidem
com os eventos do painel (a) — a atenção se reconfigura no abastecimento e na entrega.

**(d) Neurônios.** Das quatro unidades da camada rápida, uma está **morta** (`rápida 3`,
máximo exatamente 0) e uma quase nunca dispara (`rápida 1`, acima de 1 % do próprio máximo
em 3 % do tempo). As outras duas saturam alto (máximos 342 e 502) e ficam ligadas
praticamente o tempo todo. Já a camada lenta trabalha na faixa 1–5 e tem dinâmica visível
de escala de horas — é a única parte do sistema com memória de tempo longo que de fato se
move.

A diferença de escala entre as duas camadas é de **duas ordens de grandeza** (502 contra
4.9) e ninguém a projetou: saiu da evolução. Uma unidade rápida saturada em 500 é, na
prática, uma constante — o que explica por que a camada rápida "dirige" tão pouco (0.015)
apesar de ter 192 genes.

**(e) Memória.** `|MEM|` oscila entre 0 e 0.05 e **4 caixas de 12** são tocadas na vida
inteira. A memória sobe quando ele trabalha e decai quando para. Ela nunca chega perto de
conter um mapa da cidade.

---

## O que estas folhas sugerem medir a seguir

1. **Neurônio morto é gene morto.** `rápida 3` custa metabolismo (é dof) e nunca dispara.
   Sob o custo por ativação do Mundo B ela deveria ser eliminada — dá para conferir
   contando unidades mortas no campeão do A contra o do B. É uma leitura, não uma bateria.
2. **A atenção fecha, não abre.** Soma dos portões 3.39 contra o neutro 5.0. Vale medir
   isso em todos os campeões: se fechar for universal, o tálamo desta arquitetura é um
   **filtro de supressão**, e o nome certo para a peça muda.
3. **O raio de ação é uma métrica de juízo barata.** Ele separa os três braços melhor que
   mortalidade (28 / 41 / 43 m) e não satura. Entra no lote de "métricas que separam
   sobreviver de fazer bem".
4. **A cidade é grande demais para a vida que o ser tem.** Com raio de 30–40 m e 12
   distritos, quase todo sentido de longo alcance é ruído. Encolher a cidade (ou aumentar a
   vida) é uma mudança de mundo com predição clara.
