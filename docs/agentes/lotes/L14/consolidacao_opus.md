Li o placar, o `feedback.md` do L14, `hipoteses.md`, a base (`L14/p7.politica.py`) e a física em `src/campo.py:279-346` + o config do juiz (`src/julga_politica.py:35`: `kcal_pane=8, dinh0=10, guincho=0, fuel_pane=15`).

**(1) O que ainda mata a melhor política.** Base = L14 p7: mortos 0.52 (5 sementes 0.496), 18.3 corridas, **6.2 panes**, 10.2 abastecidas, 8.3 refeições, morre no dia 5.89, causa fome 49 % / dano 40 % / sede 29 %. A conta que ninguém fez: `campo.py:296` dá `dn = D_PANE 6 + (KCAL_PANE 8 − min(res,8))` → com `res = 0` (todas as 100+ políticas) cada pane custa **14**, e 6.2 panes = **87 de dano por vida** ≈ **59 % de todo o dano que uma vida absorve** (100 de vida + 25×~1.9 de oficina ≈ 148). Manter `res ≥ 8` derruba para 37: **−50 de dano/vida**. E a reserva não exige o tier 150: `campo.py:309-310` manda **qualquer sobra** (`fuel+litros−100`) para `res` com perda de 15 % — 9.4 L excedentes = 8 de reserva = 8 de vida, por 2.8 de caixa (1.7 no industrial), contra oficina a 0.4/ponto **mais** o desvio em ticks (que é o que matou H17/H23/H27). Contrapeso real: `peso = 1+.002·res` (res 50 = +10 % de gasolina) e perda 2 %/dia — logo existe dose ótima, não é "encher". Nota metodológica: a coluna "causa" do juiz é **estado na morte** (`c_fome` = fome ≥ 90 ao morrer, sobrepondo `c_sede`; `c_dano` é o resto), então parte dos 49 % de "fome" é táxi faminto morto pelo dano da pane.

```tarefa
TAREFA L15 — alvo: o DANO DA PANE (eixo nunca atacado). Base = L14 p7 (0.52; 5 s 0.496).
Conta: 6.2 panes/vida x [6 + (8 - min(res,8))] = 87 de dano = ~59% do orcamento de vida
(100 + 25x1.9 de oficina ~ 148). Todas as politicas ate hoje andam com res = 0 o tempo todo.
Manter res >= 8 corta para 37 (-50 de dano/vida) por 10-17 de caixa (renda 171/vida).
Mecanica: QUALQUER compra acima da falta gera sobra -> res += sobra*0.85 (RES_MAX 120). res so
paga pane e pesa (peso = 1+.002*res: res 50 = +10% de gasolina; perda 2%/dia). Dose otima 16-48.
p5 RESERVA: depois da pane o taxi esta NO posto com 15 L -> comprar tier 150 (G+4) quando disp[:,4]
  (disp ja embute preco e posto fechado a noite): tanque 100 + res 55. Senao 100 L. Nunca res > 60.
p4 GASOLINA: um tier ACIMA da falta quando dinh > 45 e res < 24 (sobra 25-50 -> res 21-42).
p3 (troca TRABALHO/LUGAR, refutado 3x) e p7 (troca RUA, no-op 3x): dose de reserva alvo 16 vs 48,
  e reparo na oficina SO quando ja no raio (vida < .5, sem desvio). p8 LIVRE: ler e_reserva
  (F[:,0,17]*120), nunca lido por ninguem. p1 comida: 0.35 no posto PIOROU (0.56, 7.0 refeicoes) —
  manter 0.15 e comer tambem em ponto de comida a < 6 com fome > .45. p2 agua: beber em ponto de
  comida a noite com agua < .35. Prever 0.44-0.50 nas de reserva; >= 0.51 refuta a teoria.
```

```hipoteses
| # | hipótese | resultado | onde |
| H55 | lote 14 = platô (0.52–0.56): p3/p6/p8 saíram com métricas idênticas à base (18.6 / 8.4 / 5.9) — TRABALHO/LUGAR, TRABALHO/CORRIDA e RUA são no-op sobre esta base pela 2ª–4ª vez; parada mínima colapsou de novo (0.96) | ✗ retirar os 3 slots e realocar | L14 |
| H56 | aritmética da pane (campo.py:296): 6.2 panes × (6 + 8 não coberto pela reserva) = 87 de dano/vida ≈ 59 % do orçamento de vida (100 + 25×1.9 de oficina ≈ 148); 100+ políticas rodaram com res = 0 | ⏳ L15 p5/p4/p3/p7 — previsão −0.03 a −0.08 de mortos | L15 |
| H57 | a reserva NÃO exige o tier 150: qualquer compra acima da falta vira sobra e res += sobra×0.85 (campo.py:309-310); 8 de reserva = 9.4 L = 2.8 de caixa (1.7 no industrial) = 8 de vida, contra 0.4/ponto da oficina MAIS o desvio em ticks | ⏳ L15 p4 (tier acima da falta) vs p5 (tier 150 após a pane) decidem qual é mais barato | L15 |
| H58 | a reserva tem custo: peso = 1 + .002·res (res 50 = +10 % de gasolina ≈ 12 de caixa/vida) e perda 2 %/dia; res só é lida pela pane (8 por evento) → dose ótima ~16–48, encher é pior | ⏳ L15 p3 (alvo 16) vs p7 (alvo 48) medem a dose | L15 |
| H59 | a coluna "causa" do juiz é ESTADO na morte, não causa: c_fome = fome ≥ 90 ao morrer e se sobrepõe a c_sede (49+40+29 > 100); c_dano é só o resíduo | ✓ julga_politica.py:44-47 — "fome 49 %" superestima a fome; dano da pane aparece dentro dela | auditoria do código |
| H60 | e_reserva (F[:,0,17] = res/120) nunca foi lida por nenhuma das 100+ políticas dos 14 lotes | ✓ grep nos lotes L1–L14 | consolidação L14 |
| H61 | limiar de COMIDA: 7º teste (L14 p1, posto .15 → .35) deu 0.56 com 7.0 refeições contra 0.52/8.3 da base — subir o limiar perde; a fome não é limiar, é acesso (posto fecha à noite) | ✗ aposentar o eixo "limiar de fome"; comer oportunista no posto é bom porque é barato (2·pmul) e o tick já está gasto | L14 p1 |
```

A alavanca do L15 é a primeira em muitos lotes que não é um limiar reajustado: é uma linha de dano que hoje vale 87 pontos por vida e que ninguém tocou, comprada com dinheiro que a política já gasta no mesmo tick de posto que já visita — por isso não paga o pedágio de ticks que afundou reparo, descanso e parada mínima. Calibrando pelo histórico (todo ganho estrutural previsto nos últimos 8 lotes rendeu 0–2 pp), eu previsto **0.46–0.50 para a melhor de reserva e 0.51–0.55 para o resto do lote**; se nenhuma variante de reserva descer de 0.51, a teoria está errada e o dano restante é calor + dívida, não pane — nesse caso o próximo eixo é o `tpar = 18` de cada pane (112 ticks parados por vida, 8 % do tempo) e não mais o dano. Duas coisas dependem de você: (a) `scripts/agentes/lote.py` já tem RESERVA no slot 5 (commit f9ddc06), mas os slots 3, 6 e 7 continuam com alavancas refutadas — sugiro trocá-los pelas variantes de dose acima antes de disparar; (b) não verifiquei em execução nenhum destes números de dano — são leitura de `campo.py:279-346` mais os campos `panes`/`dia`/`c_*` do `placar.json`, e o juiz é quem decide.