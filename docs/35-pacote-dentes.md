# 35 — Pacote de dentes (E19): parar não pode ser de graça — 2026-09-02

**Leonardo:** *"estou cheirando a bug; vale implementar mais coisas de uma vez e
ir tirando o que der errado."*

## O buraco
Um táxi que não faz nada por 5 dias terminava com **vida 100, fome 100 e
fitness 0**, com ou sem economia. Fome nunca feria; aluguel atrasado nunca
cobrava. Parar era de graça e seguro — o atrator dos três colapsos da onda 1
(muitos produtos com pena, reboque do tanque, "sempre"). Com pena por morte
no objetivo, uma população que espirala nas primeiras gerações cai em
"parar" e nunca sai (não há gradiente: qualquer movimento → pane → morte).

## O pacote (tudo atrás de flags; desligado = identidade bit-exata)
1. **Fome mata**: `fome_mata=0.5` de vida por passo com fome em 100 (escala
   a partir de 90). Parado sem comer: morre em ~1 dia. Verificado: 0 vivos.
2. **Dívida mata**: `divida_mata` — dinheiro abaixo de −60 = perde o carro.
   Com aluguel 8/dia dá 10 dias sem renda; sempre dá pra trabalhar pra sair.
3. **Reboque cobra gordura, resto na vida** (padrão novo do E15).
4. **Produto com limiar**: `relu(nec − 0.5)` — o produto só puxa pro serviço
   quando a necessidade passa da metade (onda 1: sem limiar, 5 produtos =
   −2.4 e "descanso" vira atrator).

## Predições (antes de rodar; R=16, 5 sementes, pena 5, cidades 1000+)
Âncora (corpo sem economia, Reativo): 8.54 / mortos 0.19.
1. `pacote`: ninguém para (entregas ≥ 9 em 5/5 sementes); fit ≥ 6.0 (a
   economia custa ~2), mortos ≤ 0.25.
2. `− fome`: com parar de graça de novo, ≥ 2 sementes desabam (entregas < 5)
   ou fit ≤ pacote − 0.5. Se ficar igual: a fome não era o dente decisivo.
3. `− dívida`: ≈ pacote (±0.5): o limite de −60 raramente é atingido em 5 dias.
4. `− limiar` (5 produtos crus): fit ≤ pacote − 1.5 (a órbita volta).
5. `− produto` (Reativo puro): mortos ≥ pacote + 4 pp (sem a alavanca do posto).
6. `− economia`: fit ≥ pacote + 1.5 (sem aluguel/imposto), mortos ≈.
Critério do pacote: se 1 vale e cada remoção piora ou empata, o pacote
fica inteiro; peça cuja remoção MELHORA sai.
