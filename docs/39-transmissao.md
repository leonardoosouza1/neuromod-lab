# 39 — E26: pressão de aprendibilidade (Kirby no táxi) — desenho, ainda não rodado

> **CANCELADO (2026-09-03):** dependia do aprendiz do E22/E25 sair do deserto; E25b confirmou o deserto (0.93 mortos) e fechou a linha. Predições 22–24 não rodam. Ver doc 38.

**De onde vem:** Kirby / Ren et al. 2020 (aprendizado iterado): um código fica
mais simples e aprendível quando cada geração tem de REAPRENDÊ-LO com pouco
input. No táxi não há pai que ensine, mas há morte: se o receptor
(hormônio → serviço) é aprendido em vida (E22/E25) e só quem aprende rápido
sobrevive até reproduzir, a seleção passa a favorecer hormônios FÁCEIS de
ouvir — o código do corpo fica mais simples por pressão de aprendibilidade.

## Pré-requisito
E25 mostrar que, com infância individual, o cérebro surdo aprende a ouvir
em vida (predição 18). Sem isso, não há aprendizado a pressionar.

## Desenho
- Corpo: rede de hormônios do genoma (E20), K=2, SEM prior — o código é
  evoluído.
- Cérebro: receptor aprendido em vida (E22) com infância (E25).
- Medida da aprendibilidade do código: passos até a 1ª refeição por
  iniciativa própria; correlação(h_k, fome) e (h_k, 1−tanque) ao longo das
  gerações; entropia dos genes de entrada da rede do corpo.
- Braços: (a) receptor herdado (E20 tri.3) — sem pressão; (b) receptor
  aprendido — com pressão; (c) receptor aprendido mas vida curta demais pra
  aprender (infância 0) — controle de que a pressão vem do tempo de aprender.

## Predições (antes de rodar)
22. Em (b), o código do corpo fica mais "limpo" que em (a): |corr(h0, fome)|
    e |corr(h1, 1−tanque)| ≥ 0.6 em ≥ 4/5 sementes, contra ≤ 0.4 em (a)
    (onde o receptor herdado tolera código misturado).
23. Passos até a 1ª refeição caem ao longo das gerações em (b) (≥ 30 % do
    início ao fim); em (c) não caem.
24. Fitness: (b) ≤ (a) + 0.5 (a pressão custa pouco); se (b) < (a) − 1.5, a
    pressão por aprendibilidade compete com o desempenho — resultado
    negativo que vale (Kirby diz que o custo é pago pela transmissão, e aqui
    quem paga é a morte).
