# 28 — Sociedade: economia real, hormônios evolutivos, cérebro com produtos (plano, 2026-09-02)

**Leonardo:** *"o táxi é um meio; depois entregador e outros trabalhos; o ser
escolhe trabalho, onde mora, onde trabalha; mais seres; um prefeito que
administra imposto, saúde, segurança; distritos com imposto pela origem da
corrida; várias cidades. Inteligência é pequena, multiplicada cresce. Preços
são hormônios: alto = estresse, baixo = tranquilidade; hormônio não é
controlado pelo cérebro, o corpo ajuda; precisa do reverso (dopamina). E
estresse deve EMERGIR, não ser roteirizado."*

## 1. Revisão: o que o E13/E14 deixou de pé e o que falta

De pé (5 sementes): corpo que fere e morre; gordura contínua; peso por
massa via limiar de fervura; reboque só no corpo (multa em dinheiro =
espiral); morte só selecionada quando visível (R=16 vidas/genoma; pena
opcional/fácil, necessária/difícil); a alavanca que faltava era um
PRODUTO de sinais (tanque baixo × distância ao posto).

Falta, em ordem de dependência:

| # | entrega | por quê | onde |
|---|---|---|---|
| E15 | **Economia real**: dinheiro compra tudo (aluguel, água, imposto ao receber e ao gastar), distritos com alíquota e preços, imposto pela ORIGEM da corrida, reboque em CALORIAS, dívida com juros (não morte instantânea por dinheiro) | dá motivo pra planejar; sem saída fixa o dinheiro é raso | `lab.py` blocos [E15], `src/e15_economia.py`, doc 29 |
| E16 | **Glândulas evolutivas** (K=2, sem nome): integrador com vazamento, entradas = déficits + eventos de ganho, saídas = ganhos multiplicativos (necessidade, exploração, metabolismo, sono, velocidade); custo em calorias; sono limpa | hormônio que emerge, com o reverso (dopamina) possível; primeiro mundo onde a Tese do Corpo prevê teto alto | `lab.py` blocos [E16], `src/glandulas.py`, `src/e16_glandulas.py`, doc 30 |
| E17 | **Cérebro com produtos**: termos bilineares necessidade × distância (5 serviços) + hora × necessidade | a política linear não expressa o que a sobrevivência exige | `src/produtos.py`, `src/e17_produtos.py`, doc 31 |
| E18 | **Avaliação honesta como padrão**: R=16, 6 cidades, 5 sementes, fila com done-files, tabela automática | regra 13/14; hoje é artesanal | `src/avaliacao.py`, `scripts/fila.sh`, `src/runner_comum.py` |
| E19 | Mercado + arena multi-ser (tarifa por distrito com oferta/demanda), casa e trajeto | depende do E15 | 2ª onda |
| E20 | Prefeito como glândula da cidade (imposto por distrito lendo mortes/renda) | depende do E15/E19 | 2ª onda |
| E21 | Escolha de trabalho e corpo (entregador) | depende do E19 | 3ª onda |

## 2. Regras de convivência (4 agentes em paralelo, worktrees)

- Cada agente edita SÓ seus blocos rotulados em `lab.py` (`# [E15 ...]`
  … `# [E15 fim]`) e seus arquivos novos. Slots de feature reservados:
  E15 usa `e15_a/e15_b`, E16 usa `e16_a/e16_b` (zero até serem usados).
- Flag desligada = identidade bit-exata: portão `perito base ent 7.9740
  av_fuel 25.1302` + `NM_COMPILE=0 src/testes.py`.
- Predições ANTES de rodar, no doc do próprio agente. Validação rápida só
  (fumaça + 1 semente curta); baterias de 5 sementes/R=16 rodam depois do
  merge, uma de cada vez.
- Contratos do `lab.py`: zero sync CPU↔GPU, tudo mascarado, `extra()` pura
  (rebind ok, in-place não), estado in-place só em `passo()`/`atualizar()`.
- Dados em `/media/llm-data/universe-runs/neuromod-lab-taxi/<tag>/`.

## 3. Hormônios: o desenho que não dá nome

```
h_k ← h_k − h_k/τ_k + Σ_i a_ki · x_i      x = [déficits…, eventos de ganho…]
ganho_j = 1 + Σ_k b_kj · h_k              j ∈ {necessidade, exploração, metabolismo, sono, velocidade}
custo   = κ_h · Σ_k h_k  (calorias, gordura primeiro) ; sono: h ← h/2
```
τ, a, b são genes. Predições (E16): (1) as duas glândulas ficam com τ
distintos por > 3×; (2) uma correlaciona com déficit e reduz gasto/
exploração, a outra com ganho e aumenta esforço; (3) U invertido na escala
dos ganhos (EXP10); (4) com sono limpando h, dormir passa a pagar; (5) com
preços variáveis (E15), glândulas > sem glândulas e o ganho acompanha o
teto da Tese do Corpo. Negativo possível: as duas viram a mesma coisa —
este mundo só precisa de um eixo.

## 4. Seres no limite + imposto alto (predições pra E19/E20)

Lei da moeda cruzada → população bimodal e desigualdade; arrecadação em U
invertido cujo pico desloca pra esquerda quando a reserva média é menor;
Yerkes-Dodson: imposto intermediário produz MAIS que zero.

## 5. Diário de merge (onda 1)

- **E18 avaliação** → `3eed84a`: só arquivos novos (`avaliacao.py`, `runner_comum.py`,
  `scripts/fila.sh`, `testes_e18`, doc 32). Portão bit-exato, testes ok.
- **E17 produtos** → `0664907`: só arquivos novos (`produtos.py`, `e17_produtos.py`,
  `analise_produtos.py`, `testes_e17` 9/9, doc 31). Achado do agente na
  validação curta (G=10, 1 semente, pena 5): a ordem de mortos é o inverso da
  de fitness — `ReativoProdutoFull` faz 0.01 de mortos com 0.13 entregas: com
  pena, PARAR vira o atrator barato e o produto é a alavanca que deixa parar
  barato. Nenhuma conclusão do E17 pode ser lida em mortos sozinho; a bateria
  séria precisa do controle `pena_morte=0` e do limiar `relu(nec−θ)` proposto
  no doc 31. Alavanca à mão (regra 15) é viva (mortos 0.25 → 0.02 ou 0.81),
  mas enxertada num genoma não co-adaptado custa fitness em 13/13.
