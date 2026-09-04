# 41 — E42 Cidade Grande: mais mundo e mais corpo pro cérebro (spec, 2026-09-03 21:30)

**Leonardo:** *"a cidade maior com mais distritos, vamos dar mais ambiente e corpo
para o cérebro; o cérebro em camadas, cada parte com sua função — tálamo,
córtex, memória."*

## 0. O que já existe e o que falta (honesto)
Existe e está LIGADO em todas as rodadas de hoje: E15 economia (3 distritos por
partição espacial, alíquota .10/.20/.30, multiplicador de preço por distrito,
imposto ao receber pela origem da corrida e ao gastar, aluguel + água à
meia-noite, dívida com juros, KCAL do reboque). Existe no código, testado e
NÃO adotado no honesto (mundo de 26 nós não exige): SerTalamo (gate por órgão
por passo), SerVital (hipocampo 3×3), SerGlandular (K integradores),
SerCorpoFala (hormônios com prior), ReativoAtencao (WTA), memória (mem_0..5
slots do Reativo, mortos por construção). Campeão atual = política linear +
reflexo de emergência (7 genes). Falta: cidade grande, moradia, escolha de
onde trabalhar (emergente), cérebro em camadas de verdade, profissões e
prefeito (fase 2).

## 1. Contratos (valem pros dois agentes)
- **Flag desligada = identidade bit a bit.** `NM_COMPILE=0 python src/rodar.py
  --perito` tem de imprimir `PASSOU: as 7 batem (spread 0.000)` e
  `NM_COMPILE=0 python src/testes.py` tem de passar. Toda mudança em `lab.py`
  fica atrás de flag de cfg com default = comportamento atual.
- **Sem sync CPU↔GPU no laço quente**: checar com
  `torch.cuda.set_sync_debug_mode("error")` (ver src/reacoes.py, testes no fim
  dos arquivos e29*/e3*). Nada de `.item()`, `float()`, `if tensor` dentro de
  `passo`/`extra`/`atualizar`.
- **Gene novo nasce desligado** (regra 17): com genes 0 a arquitetura nova tem
  de ser bit-igual ao pai (Reativo ou ReativoReacoes).
- **Nada em /tmp**; saídas em `/media/llm-data/universe-runs/neuromod-lab-taxi/e42/`.
- Cada agente edita SÓ seus blocos rotulados (`# [E42 mundo ...]`, `# [E42
  cerebro ...]`) e seus arquivos novos. Sem `git add -A`. Commits no worktree.
- Predições ANTES de rodar, no próprio doc (docs/42-*.md e docs/43-*.md).
  Validação rápida (fumaça + 1 semente curta P=256 G=10). Baterias honestas
  rodam depois do merge, uma por vez, na fila (scripts/fila2.sh).

## 2. Agente MUNDO (docs/42-mundo-grande.md) — `src/cidade_grande.py` + blocos `[E42 mundo]` em lab.py/e15_economia.py
1. `gerar_cidade(seed, n=104)` já escala serviços com n (esc_n). Verificar que
   o grafo fica conexo e com d_posto máx ≤ 6 saltos; se não, +postos.
2. **6 distritos** espaciais (partição por k-means ou grade 3×2 sobre `pos`),
   `cfg.D=6`, alíquotas e multiplicadores de preço por distrito sorteados de
   faixas (alíquota .05–.35; preço ×0.7–×1.6; aluguel ×0.5–×2.0 por distrito).
3. **Passageiros cruzam distritos**: destino sorteado com prob. ∝ 1/(1+d) mas
   ≥ 30 % em outro distrito; tarifa = base × distância × multiplicador do
   distrito de ORIGEM; imposto pela origem (já existe).
4. **Moradia**: `m.casa` = distrito onde nasceu (v1). Descansar (serviço
   `descanso`) no distrito-casa custa o aluguel já cobrado; fora custa hotel
   (preço do distrito × HOTEL). Sentido novo `e_em_casa` (1 se está no
   distrito-casa) num slot reservado (`h_gl0` → renomear). Dormir na rua
   (parado à noite fora de casa sem descanso) = fadiga não recupera.
5. Sentidos por distrito já existem (`e_preco_local`, `e_divida`). Acrescentar
   `e_aliq_local` (alíquota do distrito atual) no slot `h_gl1`.
6. Presets: `cfg_cidade_grande(**kw)` = cfg_pacote + n=104 + D=6 + moradia.
   Runner `src/e42_mundo.py`: braços direto vs reações vs mínimo-3 (E23) na
   cidade grande, seeds (0,1,2), teste 1000+ (cidades grandes com o mesmo
   seed). Predição 49 é do mundo: mínimo-3 perde ≥ 1.0 de fit pro completo.

## 3. Agente CÉREBRO (docs/43-ser-camadas.md) — `src/camadas.py`
`SerCamadas(ReativoReacoes)`: nasce == ReativoReacoes com genes extras em 0.
Camadas, cada uma com função e genes próprios, ligáveis pela evolução:
1. **Tálamo** (atenção): gate por GRUPO de sentidos (5 grupos: rota, serviços,
   corpo, economia, tempo) = sigmoid(a_g + b_g·necessidade_dominante +
   c_g·carregando); multiplica o bloco de features do grupo. Genes 15. Gate=1
   com genes 0 (nasce transparente).
2. **Córtex** (política por contexto): os pesos de movimento ganham uma
   modulação por distrito: w_ef = w·(1 + δ_d) com δ_d ∈ 6 distritos × 4
   features-chave (d_alvo, d_posto, custo_rua, e_preco_local) = 24 genes;
   δ=0 nasce transparente.
3. **Hipocampo** (memória por distrito): 6 slots EMA por distrito de
   (renda por corrida, espera por passageiro, preço pago), τ gene; entram como
   3 sentidos do distrito ATUAL nos slots mem_0..2 (hoje mortos) — genes de
   peso já existem no Reativo (mem_*), τ = 1 gene. Atualização in-place em
   `atualizar` (fora do grafo).
4. **Glândulas** (corpo fala): reaproveitar `corpo_fala.py` K=2 (τ, entradas,
   saídas em ganho de serviço). Se o merge complicar, deixar pra fase 2 e
   dizer.
5. Retrato por camada: `retrato.py` já lê `_ativ()`; expor `s.ativacao()` →
   dict {talamo: gate médio por grupo, cortex: |δ| usado, hipocampo: variância
   dos slots} pra `retrato.py` gravar.
Predições 50 (hipocampo ≥ 5 pp de mortos ou +10 % renda vs sem memória na
cidade grande) e 51 (tálamo usado em ≥ 3/5 linhagens: gate médio < 0.8 em
algum grupo).

## 4. Integração (eu): merge mundo → cérebro → portão → fila honesta
(G=120, 5 sementes, R=16) com retrato de cada braço; régua = a que o E41
apontar (padrão até lá). Fase 2 (depois): profissões (entregador), prefeito
como glândula da cidade, várias cidades.
