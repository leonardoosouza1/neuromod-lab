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
