# ESPECIFICAÇÃO — Mundo Vivo (v1)

Documento de implementação para quem vai escrever o código. Cada item traz **contrato,
algoritmo com formas de tensor, ponto de inserção, portão, testes e critério de aceite**.
Escrito a partir da leitura do código em 2026-09-09 (HEAD com `custo_suave`, `nevoa`,
juízes de política e daemon `nmd`).

Origem: `docs/56-mundo-de-verdade.md` (o porquê) e `docs/55-programa-5-dias.md` (a ordem
experimental). Este arquivo é o **como**.

---

## §0. Regras de engajamento — inegociáveis

1. **Padrão idêntico bit a bit.** Todo parâmetro novo nasce com um valor que reproduz o
   mundo de hoje exatamente. A prova é rodar a mesma configuração antes e depois e
   comparar **todas** as medidas do JSON exceto `segundos`. Sem esse portão, o item não
   entra. Modelo já validado: `nevoa=float('inf')`.
2. **Uma feature por commit**, com o portão no próprio commit.
3. **Nada de sincronismo CPU↔GPU dentro do laço de tempo.** Sem `.item()`, `.any()`,
   `if tensor:` dentro de `for t in range(T)`. Contagens vão para tensores acumuladores.
4. **`extra()` roda dentro do `torch.compile`** — não pode mutar tensor nem ter ramo
   dependente de dado. Estado muda em `atualizar(m)`, fora do grafo (padrão do `Comite`).
5. **Determinismo por semente.** Duas execuções com a mesma semente dão resultado igual
   bit a bit (`testes.py::test_determinismo` já cobre; estender às features novas).
6. **Predição escrita antes** em `PREDICOES.md`, com critério numérico e cláusula de
   morte da hipótese. Negativo com mecanismo é resultado.
7. **Não amaciar.** Se uma feature nova leva a mortalidade a 1.00, o conserto é a régua
   (F1), não baixar a dificuldade. Ver §3-F1.
8. **Sem bateria em CPU.** CPU serve para portão de identidade e fumaça.

---

## §1. Arquitetura atual (mapa para o implementador)

### Arquivos e papéis

| arquivo | papel |
|---|---|
| `src/campo.py` | **o mundo**. Classe `Campo` (estado em tensores), `obs()`, `passo`, `rodar()`, `_fit()`, `dof_de()`, `gerar_mapa()` |
| `src/lab.py` | motor evolutivo: `DEV`, `Cfg`, `evoluir_sementes()`, arquiteturas base (`Reativo`, `Linear`, …), `torch.compile` do passo |
| `src/completo.py`, `src/camadas.py` | cérebro completo (tálamo, córtex, hipocampo, reflexo) e camadas rápida/lenta; `nomes_genes()` |
| `src/e43_campo.py` | CLI da bateria no campo |
| `src/politica_util.py`, `src/julga_lote.py`, `src/julga_politica.py` | juízes de política explícita (agentes) |
| `src/base_fechada.py` | clone por fórmula fechada W* = (ΦᵀΦ+λI)⁻¹ΦᵀY |
| `src/diag_oraculo.py`, `src/oraculo_campo.py` | política escrita à mão = teto físico do mundo |
| `src/rodar.py --perito` | portão obrigatório antes de bateria |
| `scripts/nmd.py` | daemon de execução (fila em disco, lista branca) |
| `scripts/analise_campo.py` | régua pareada por semente + MDE |

### Contratos que não podem quebrar

```
Campo.obs()      -> F (B, G, NF), val (B, G)        G = 9 (8 direções + ficar)
Campo.serv_need()-> (svn, sv)  (B, S)               S = len(ACOES) = 10
esc < G  => movimento    |    esc >= G => serviço
rodar(Arq, W, mapas, cfg, T, seed, R=1) -> Campo    laço `for t in range(T)` (campo.py:410)
_fit(m, cfg, T) -> (B,)                             campo.py:428
dof_de(Wb, cfg) -> (B,)                             campo.py:420
```

### Layout dos sentidos (campo.py:20-26)

```
NOMES_OP     por opção de movimento (distâncias a alvo/serviços, custo, preço à frente)
NOMES_CORPO  iguais nas 9 opções: e_fuel, e_agua, e_fome, e_fadiga, e_calor, e_vida,
             e_dinheiro, e_reserva, e_tem_pax, h_sin, h_cos, e_noite, custo_aqui, bias,
             e_consumo, e_autonomia (+ e_risco se NM_RISCO, +e_demanda/e_espera se PONTO)
NOMES_F      = NOMES_OP + NOMES_CORPO + sv_* (notas de serviço) + sv_bias
```

**Armadilha central (achado 84):** o `Linear` centra as notas por opção, então **sentido
do corpo é invisível na direção** — só entra no serviço. Qualquer sentido novo que deva
influenciar *para onde ir* tem de ser **por opção** (entrar em `NOMES_OP`) ou passar pelo
caminho bilinear. Isto derrubou dois meses de experimentos; não repetir.

### Grades pré-computadas (campo.py:90-109)

`GR = 128`. Já existem, por mapa: `campo_dist` (distrito da célula, Voronoi) e os campos
de custo/ruas. Indexação padrão (campo.py:144):
```python
ix = (p[...,0]/s.L*GR).long().clamp(0, GR-1); iy = (p[...,1]/s.L*GR).long().clamp(0, GR-1)
```
Toda feature nova que precise de mapa deve usar essa mesma indexação.

---

## §2. Contratos de dados

### 2.1 `cenario.json` v1 (estende o v0 do doc 53)

```json
{"nome": "...", "predicao": "...",
 "mundo":  {"L":200, "dias":10, "regua":"riqueza", "K":6, "ruas":{"dentro":1,"fora":3},
            "horizonte":"fixo", "T_max":null, "nevoa":null,
            "retina": null,
            "regime": null,
            "precos":{"amp":0.5,"periodo":3}},
 "corpo":  {"dinh0":10, "kcal_pane":8, "guincho":10, "fuel_pane":5,
            "custo_gene":0.0, "custo_modo":"existencia", "gene_min":0.5, "custo_suave":false},
 "distritos": { "...": {"pmul":..., "aliq":..., "alug":..., "dem":..., "dens":[...]} }}
```
Regra: **todo campo novo aceita `null` e `null` = comportamento de hoje.**

### 2.2 JSON de resultado — campos novos obrigatórios

```
dof_bloco        {"ref":n, "tal":n, "cor":n, "hip":n, "rap":n, "len":n}   por braço
ativacao_bloco   mesma chave, média de |w·x| por bloco ao longo da vida
t_vida           {"media":, "mediana":, "p10":, "p90":, "frac_teto":}
dispositivo      {"gpu": torch.cuda.get_device_name(0) ou "cpu", "torch":, "hip_ou_cuda":}
<medida>_por_semente   para TODAS as medidas (já feito em e43_campo; falta nos juízes)
```

### 2.3 Pedido `nmd` — sem mudança de contrato
Scripts novos entram na lista branca de `scripts/nmd.py`; flags novas passam pela regex
de nome de flag (aceita maiúsculas).

---

## §3. Features

Ordem obrigatória: **F1 → I1 → F2 → F3 → F4 → F5 → F6 → F7**. F1 primeiro porque sem
régua sem teto toda hostilidade nova parece regressão.

### F1 — Régua sem teto (vida ilimitada)

**Porquê.** A taxa de adaptação é proporcional à variância de aptidão (Fisher). Com
"sobreviveu 10 dias?" há dois tetos: mundo fácil → todos vivem; mundo duro → todos
morrem. Nos dois a variância vai a zero e a evolução para. O E62 a 15 dias está no
segundo teto (0.99–1.00 em todos os braços): a bateria não mede nada.

**Contrato.**
```
cfg.horizonte : 'fixo' (padrão, = hoje) | 'aberto'
cfg.T_max     : int, guarda dura do laço. 'aberto' usa 240*30 (30 dias)
cfg.fitness   : + 'vida'  (novo)
```

**Algoritmo.** Não mexer no laço. `rodar()` continua `for t in range(T)`; mortos já são
mascarados por `vivo` em todo lugar, então rodar T grande só custa tempo, não corrompe.
O que muda é `_fit` e o relatório:

```python
elif cfg.fitness == 'vida':                       # campo.py:_fit
    # sem pena_morte, sem separar vivo/morto: todo mundo morre, a pergunta e' quando e quanto fez
    fit = m.t_vida/240. + cfg.w_trab*(m.rec/300.)          # dias vividos + trabalho acumulado
```
Relatório novo (§2.2): média, mediana, p10, p90 de `t_vida/240`, e
`frac_teto = (t_vida >= T_max).float().mean()`.

**Guarda do teto.** Se `frac_teto > 0.05`, o horizonte está amarrando e o resultado é
inválido — subir `T_max` e repetir. Imprimir aviso no fim da bateria.

**Custo.** `T_max` de 30 dias = 7200 passos, 3× o de hoje. Mitigação: com `horizonte
='aberto'`, checar `vivo.any()` **uma vez por dia simulado** (a cada 240 passos) e sair
do laço — 1 sincronismo por dia, não por passo, o que a regra 3 permite. Implementar com
`if cfg.horizonte=='aberto' and t % 240 == 239 and not bool(m.vida.gt(0).any()): break`.

**Ponto de inserção.** `campo.py:_fit` (428), `campo.py:rodar` (410), `e43_campo.py`
(flag `--horizonte`, `--T-max`), `politica_util.py:34` (namespace do juiz).

**Portão.** `horizonte='fixo'` + `fitness` existente → idêntico bit a bit.

**Testes** (`src/testes.py`):
- `test_horizonte_identidade`: fixo vs HEAD, todas as medidas.
- `test_vida_sem_teto`: num mundo brutal (guincho 10, dinh0 5), o **coeficiente de
  variação** de `t_vida` na população ≥ 0.15. É o teste de "a régua ainda ordena".
- `test_teto_avisa`: com `T_max` pequeno de propósito, `frac_teto > 0.05` e o aviso sai.

**Critério de aceite.** Num mundo onde a mortalidade de 10 dias satura em 1.00, a régua
`vida` ainda separa braços com efeito ≥ 10 pp equivalente (teste pareado por semente).

**Predição a registrar.** Com `fitness='vida'` no mundo do E62 (15 dias, todos morrem):
os braços que hoje empatam em 0.99–1.00 se separam em `t_vida` por ≥ 0.8 dia, e a ordem
entre eles **não** é a ordem de hoje (hoje é ruído).

---

### I1 — Instrumentos (pré-requisito do F2 e do dia 4)

**I1a. `dof_por_bloco`.** Hoje `dof` é um escalar: quantos genes sobreviveram. A tese é
sobre **quais**. Os nomes já existem — `completo.py:nomes_genes()` devolve
`ref + tal + cor + hip` e `camadas.py` acrescenta rápida/lenta.

```python
# campo.py, ao lado de dof_de
BLOCOS = ('ref', 'tal', 'cor', 'hip', 'rap', 'len')
def dof_por_bloco(Wb, cfg, Arq):
    nomes = Arq.nomes_genes()                      # len == Arq.NP - Linear.NP
    w = Wb[:, Linear.NP:]
    liga = (w*w/(w*w + cfg.gene_min**2)) if cfg.custo_suave else (w.abs() > cfg.gene_min).float()
    idx = {b: torch.tensor([i for i,n in enumerate(nomes) if n.startswith(b)], device=DEV) for b in BLOCOS}
    return {b: float(liga.index_select(1, ix).sum(1).mean()) for b, ix in idx.items() if len(ix)}
```
Gravar em `medidas()` (campo.py:453) ao lado de `dof`.

**I1b. `--nevoa` e `--retina` no caminho do juiz.** `politica_util.py:34` fixa
`nevoa=float('inf')` no namespace — **a névoa não alcança as políticas dos agentes**.
Expor as duas flags em `julga_lote.py` e `julga_politica.py` e repassar ao `cfg`.
Sem isso não existe o controle "a política explícita também sofre quando o mundo
esconde?", que é o mais duro do dia 3.

**I1c. `_por_semente` no juiz de política.** O `e43_campo` já grava para 15 medidas
(`for k in list(med): med[k+'_por_semente'] = ...`). Replicar em `julga_lote.py` para
que `analise_campo.py` funcione sobre o placar dos agentes.

**I1d. Dispositivo no JSON.** `torch.cuda.get_device_name(0)`, `torch.__version__`,
`torch.version.hip or torch.version.cuda`. Aritmética de ponto flutuante difere entre
GPUs; sem esse campo, misturar máquinas contamina o ledger em silêncio.

**Portão.** Todos são aditivos: nenhuma medida existente muda.

---

### F2 — Custo por ativação (o metabolismo físico)

**Porquê.** Hoje `dof_de` cobra por **ter** o gene (`|w| > gene_min`), e `metab` é
calculado **uma vez antes do laço** (`campo.py:409`). Na biologia a conta do cérebro é
dominada por **sinalização** — correntes pós-sinápticas e potenciais de ação (Attwell &
Laughlin, 2001) —, não por existir. A consequência de desenho é grande: um reflexo que
dispara raramente deve ser quase de graça, e um córtex sempre ligado deve ser caro. É
exatamente a diferença entre "peça é decoração" e "peça é função".

**Contrato.**
```
cfg.custo_modo : 'existencia' (padrão, = hoje) | 'ativacao'
cfg.custo_gene : λ, como hoje
cfg.amostra_ativ : int, amostrar a ativação a cada N passos (padrão 10)
```

**Algoritmo.** Acumular, **fora do grafo compilado**, a magnitude de contribuição por
bloco. Em `Arq.atualizar(m)` (que já roda fora do `compile`), a cada `amostra_ativ`
passos:
```python
# a = |w · x| media por gene, agregada por bloco -> (B, n_blocos)
m.ativ_soma += contrib_por_bloco(W, F)      # buffer (B, n_blocos) criado no reset
m.ativ_n    += 1
```
e no bloco de fome (campo.py:~342), trocar o `metab` fixo por:
```python
metab_t = 1. + cfg.custo_gene*(m.ativ_soma.sum(1)/m.ativ_n.clamp(min=1))/100.
```

**Nota de implementação.** `contrib_por_bloco` precisa de `F` (os sentidos) e de `W`. O
caminho mais barato é a própria arquitetura expor `ultima_contrib` já calculada no
`extra()` — mas `extra()` não pode mutar. Solução: `extra()` **retorna** a contribuição
como parte do valor e `atualizar()` a lê de um atributo escrito pelo chamador fora do
grafo. Se ficar difícil, a alternativa aceitável é amostrar num passo eager a cada 10
(`fn = um_passo` em vez do compilado nesse tick) — custa ~10 % de tempo e mantém a
regra 4 intacta.

**Portão.** `custo_modo='existencia'` → idêntico bit a bit.

**Testes.**
- `test_custo_identidade` (existência vs HEAD).
- `test_custo_ativacao_gene_morto`: um gene com |w| grande mas cujo sentido é sempre 0
  (ex.: `e_risco` num mundo sem risco) custa ~0 em `'ativacao'` e custa cheio em
  `'existencia'`. É o teste que prova que o modo novo mede o que promete.
- `test_metab_monotono`: dobrar λ dobra o custo em regime estacionário.

**Critério de aceite.** No mundo transparente com λ=0.3, `'ativacao'` preserva **mais**
genes que `'existencia'` (hoje sobram 3 de 355) e os preservados são majoritariamente do
bloco `ref` (reflexo — dispara raro).

**Predição a registrar.** dof sobrevivente sob λ=0.3 sobe de 3 para ≥ 15, com ≥ 60 %
deles no bloco `ref`; a mortalidade **não** piora (se piorar, o custo por ativação está
cobrando de quem trabalha).

---

### F3 — Retina (visão de verdade, substitui a névoa)

**Porquê.** `obs()` chama `_perto_todos(pos)`, que varre o mapa inteiro e devolve
distância exata aos cinco serviços mais próximos, todo tick, de qualquer ponto. O ser é
onisciente; a névoa é um remendo do sintoma. Com raios, oclusão e luz, memória e atenção
passam a ter valor mensurável — e a noite vira cegueira, não "o posto fechou".

**Contrato.**
```
cfg.retina : None (padrão, = hoje) | {
    'K': 8,            # raios de rótulo (sentidos do CORPO)
    'fov': 2.0,        # abertura em radianos do leque de rótulo
    'R_dia': 60.,      # alcance de dia (metros de mundo)
    'R_noite': 15.,    # alcance de noite
    'passo': 4.,       # amostragem ao longo do raio
    'custo': 0.0,      # caloria por raio por tick (0 = sensor de graça)
    'k_cego': 2.0 }    # o que o ser assume quando nao ve (pessimista; ver abaixo)
```

**Grades novas** (em `gerar_mapa`, junto das existentes):
```
opac  (GR,GR) bool    — quadra edificada = opaca. Derivar do campo de ruas:
                        célula fora de rua E longe de serviço = opaca.
tipo_g(GR,GR) int8    — 0 = nada, 1..5 = índice em TIPOS do serviço naquela célula
```

**Algoritmo (vetorizado, sem laço em Python sobre raios).**
```
n_s = ceil(R/passo)                                    # amostras por raio
ang = cab[:,None] + fov*(arange(K)/(K-1) - .5)         # (B,K)
dir = stack([cos(ang), sin(ang)], -1)                  # (B,K,2)
p   = pos[:,None,None,:] + dir[:,:,None,:]*(arange(1,n_s+1)*passo)[None,None,:,None]   # (B,K,n_s,2)
ix,iy = indexação padrão (campo.py:144) sobre p        # (B,K,n_s)
op  = opac[cid,iy,ix]                                  # (B,K,n_s) bool
tp  = tipo_g[cid,iy,ix]                                # (B,K,n_s)
bloq = op.cumsum(-1) > 0                               # tudo depois do 1o obstáculo é invisível
vis  = (~bloq) & (tp > 0)
j1   = vis.float().argmax(-1)                          # 1ª amostra visível com serviço
achou= vis.any(-1)
ret_d = where(achou, (j1+1)*passo, k_cego*R)/100.      # (B,K)  PESSIMISTA quando não vê
ret_t = where(achou, gather(tp, j1), 0)                # (B,K)  rótulo
```
Memória: B·K·n_s. Com B=32768, K=8, n_s=16 → 4.2 M elementos por tipo — cabe folgado.

**Onde os sentidos entram — o ponto crítico.** Pelo achado 84, sentido do corpo **não
muda a direção**. Portanto:

- os `K` raios de rótulo entram em **`NOMES_CORPO`** (`ret_d_k`, `ret_t_k`) — servem para
  decidir *o que fazer*, não *para onde ir*;
- e acrescenta-se **um raio por opção de movimento**: para cada uma das 9 direções, a
  distância livre naquela direção → sentido **`livre_g`** em **`NOMES_OP`**. É literalmente
  "até onde consigo ir por aqui", é por opção por construção, e é o que dá à retina
  efeito no volante.

Sem essa segunda parte a retina nasce cega para a direção e o experimento repete o
achado 84.

**Luz.** `R = where(noite_(), R_noite, R_dia)` — a mesma máscara de noite que já existe.

**Custo do sensor.** `metab += custo * K` por tick. Com `custo > 0`, **quanto enxergar
vira gene**: em v2, `K` passa a ser um gene inteiro (0..K_max) e a evolução escolhe. Base
biológica: o custo energético da visão limita o projeto de olhos em animais (Niven &
Laughlin, 2008).

**Portão.** `retina=None` → idêntico bit a bit. Com `retina` ligada e `R_dia` ≥ diagonal
do mapa e `opac` toda falsa, os `ret_d` devem bater com `_dist` do modo onisciente
(tolerância = `passo`) — este é o teste que prova que a retina não está mentindo.

**Testes.**
- `test_retina_identidade` (None).
- `test_retina_sem_oclusao_bate_oraculo` (acima).
- `test_retina_parede`: ser encostado numa quadra opaca lê `ret_d` curto naquela direção
  e longo na oposta.
- `test_retina_noite`: com `R_noite < R_dia`, a distância média lida cai à noite.
- **portão de sensibilidade** (o de vocês) para `livre_g`: mudar o sentido tem de mudar a
  direção escolhida em ≥ 1 % dos casos.

**Critério de aceite.** Com a retina ligada e oclusão real, o controle linear cai na
**banda 0.40–0.80** de mortalidade (nem trivial nem impossível) na régua `vida`.

**Predição a registrar.** (a) O linear piora ≥ 15 pp com retina vs onisciente; (b) o
braço com hipocampo passa a bater o linear por ≥ 10 pp pareado, coisa que **nunca**
aconteceu no mundo transparente; (c) a política explícita dos agentes **também** piora
≥ 10 pp — se ela não piorar, a dificuldade é artefato do cérebro e não do mundo.

---

### F4 — Regime não estacionário (estações)

**Porquê.** N19 mediu que hormônio/neuromodulação **não paga sem regime que mude**, e o
próprio negativo pediu: *"próxima chance honesta: mundo com REGIME que exige trocar de
política"*. Sem regime, estado lento não tem o que codificar.

**Contrato.** `cfg.regime : None | {'periodo_dias': 5, 'amp': 0.5, 'canais': ['consumo','preco','demanda','dia_curto']}`

**Algoritmo.** Fase `φ = 2π·(t/240)/periodo_dias`; multiplicadores senoidais por canal
aplicados onde o canal já existe (consumo em `cuf`, preço em `pref_mult`, demanda em
`s.demanda`, duração do dia em `noite_()`). Sentidos novos **`est_sin`, `est_cos`** em
`NOMES_CORPO`, espelhando `h_sin`/`h_cos` que já existem para a hora.

**Portão.** `regime=None` → idêntico.

**Testes.** `test_regime_identidade`; `test_regime_ciclo` (o multiplicador tem período
correto e média 1.0 ao longo de um ciclo inteiro — regime muda o *quando*, não o *quanto*
médio; senão vira dificuldade disfarçada).

**Critério de aceite.** Média do multiplicador sobre um ciclo = 1.0 ± 0.01 em todo canal.

**Predição.** As camadas lentas (τ > 100), que hoje têm correlação 0.00 com tudo, passam
a correlacionar com a fase (|r| ≥ 0.3), e a ablação delas passa a doer ≥ 5 pp.

---

### F5 — Reprodução e capacidade de suporte (seleção mole)

**Porquê.** Com reprodução custeada em energia e recurso finito, a seleção passa a ser
*relativa aos vizinhos* (seleção mole, Wallace 1975): **hostilidade nunca zera o
gradiente**, só troca quem se reproduz. É a solução definitiva para o problema do teto.

**Contrato.** `cfg.reproducao : None | {'custo_kcal': 60., 'limiar_res': 90., 'K_suporte': N}`

**Algoritmo v1 (dentro da geração, sem mexer no GA):** quando `res > limiar_res`, o ser
gasta `custo_kcal` e incrementa `m.filhos`. Aptidão = `m.filhos` (+ desempate por
`t_vida`). Capacidade de suporte entra como competição por recurso finito, que exige F6;
até lá, aproximar com respawn de passageiro/serviço proporcional à população viva.

**Escopo.** Esta feature muda o significado de aptidão. Fazer **depois** de F1 estar
estabilizada e com um braço de controle na régua `vida` rodando em paralelo.

**Teste.** `test_reproducao_conserva`: energia gasta em filhos = energia removida da
reserva (conservação; sem isso vira o N15 de novo).

---

### F6 — Vários seres no mesmo mundo (Rainha Vermelha)

**Porquê.** A dificuldade deixa de ser parâmetro calibrado e vira **endógena**: o mundo
fica tão difícil quanto a população é competente. Nunca satura, nunca precisa de
recalibração.

**Mudança estrutural.** Hoje `B = P × NC × R` são mundos **independentes**. Competição
exige `NB` seres **no mesmo** mundo: passageiro pego por um some para os outros, posto
tem fila, comida acaba e repõe.

**Contrato.** `cfg.NB : 1 (padrão, = hoje) | int`. Com `NB=1` o código novo tem de ser
idêntico ao atual.

**Algoritmo.** Passageiros e serviços passam a ter dono: `px_dono (NC, NPX)` com −1 =
livre. Na captura, resolver disputa por menor distância com desempate determinístico por
índice (nunca `rand` sem semente — quebra o determinismo). Fila no posto: `serv_ocupado`
com contador de ticks.

**Risco.** É a feature mais cara e a que mais pode quebrar determinismo. Fazer por
último, com `test_determinismo` estendido para `NB>1`.

---

### F7 — Energia unificada (refatoração)

**Porquê.** Cinco acumuladores independentes (`fuel_passo`, `fome_passo`, `agua_passo`,
fadiga, calor) é onde exploits nascem: nada obriga a conta a fechar. Física: **um
orçamento** com eficiências explícitas η₁ (comida→reserva), η₂ (reserva→trabalho),
η₃ (trabalho→combustível), e **calor como resíduo de toda conversão** (segunda lei).
Basal escala com massa^0,75 (Kleiber) e tecido neural é desproporcionalmente caro
(Aiello & Wheeler, 1995).

**Escopo.** Refatoração pura, sem feature nova. Fazer por último, com o portão exigindo
que a parametrização equivalente reproduza as trajetórias de hoje dentro de 1 %.

---

## §4. Plano de testes

### Hierarquia de portões (nesta ordem, sempre)

| portão | o que prova | onde |
|---|---|---|
| **identidade** | padrão novo == HEAD, bit a bit, todas as medidas menos `segundos` | por feature |
| **determinismo** | mesma semente → mesmo resultado | `testes.py::test_determinismo` |
| **perito** | política à mão bate o aleatório por margem larga; igual em todas as arquiteturas | `rodar.py --perito` |
| **sensibilidade** | cada sentido consegue mudar direção e serviço | `testes_sentidos.py` |
| **escala** | ruído de semeadura não afoga a espinha | `testes_sentidos.py` |
| **oráculo** | o mundo é viável: a política à mão sobrevive com margem | `diag_oraculo.py` |
| **banda de controle** | linear entre 0.40 e 0.80 — nem trivial nem impossível | novo, ver abaixo |

### Novo: `rodar.py --portao-mundo`

Um comando que roda os sete portões acima contra um `cenario.json` e imprime uma tabela
PASSOU/FALHOU. **Nenhuma bateria deve ser enfileirada sem esse comando verde.** É o
único item desta especificação que economiza tempo já no primeiro uso: as três últimas
baterias (E62 15 dias, guincho4, riqueza10) foram rodadas em mundos que este portão teria
recusado antes de gastar GPU.

### Testes unitários novos (em `src/testes.py`, idioma da casa: `test_*` + `assert`)

```
test_horizonte_identidade          test_retina_identidade
test_vida_sem_teto                 test_retina_sem_oclusao_bate_oraculo
test_teto_avisa                    test_retina_parede
test_custo_identidade              test_retina_noite
test_custo_ativacao_gene_morto     test_regime_identidade
test_metab_monotono                test_regime_ciclo
test_dof_bloco_soma                test_reproducao_conserva
```
`test_dof_bloco_soma`: a soma dos blocos == o `dof` escalar (a decomposição não pode
perder nem inventar gene).

---

## §5. Ordem de execução (checklist de merge)

Cada linha é um commit independente, com portão no próprio commit.

```
[ ] I1d  dispositivo no JSON                                   ~10 linhas
[ ] I1a  dof_por_bloco + test_dof_bloco_soma                   ~20 linhas
[ ] I1c  _por_semente nos juízes                                ~5 linhas
[ ] I1b  --nevoa/--retina no caminho do juiz                   ~10 linhas
[ ] F1   régua sem teto + guarda de teto + 3 testes            ~60 linhas
[ ] --portao-mundo (os 7 portões num comando)                  ~80 linhas
[ ] F2   custo por ativação + 3 testes                        ~100 linhas
[ ] F3   retina: grades, raios, livre_g por opção + 5 testes   ~150 linhas
[ ] F4   regime + 2 testes                                     ~60 linhas
[ ] F5   reprodução (depois de F1 estável)                     ~80 linhas
[ ] F6   NB seres por mundo (por último, risco de determinismo) ~200 linhas
[ ] F7   energia unificada (refatoração pura)                  ~200 linhas
```

Os quatro primeiros são meia hora de trabalho e desbloqueiam o experimento do dia 4 do
`docs/55-programa-5-dias.md`.

---

## §6. Armadilhas desta base (custaram caro; não repetir)

1. **Achado 84** — sentido do corpo é invisível na direção (centragem por opção). Todo
   sentido que deva mudar *para onde ir* precisa ser por opção. Foi o que motivou o
   `livre_g` do F3.
2. **Ruído de semeadura afoga a espinha** — ao semear uma arquitetura maior a partir de
   uma menor, os genes novos precisam de escala pequena (0.01–0.1) ou de serem exatamente
   zero. Já afogou 58 % das decisões do cérebro completo.
3. **Uso ≠ contribuição (N5, quatro aparições)** — ablação exagera a importância de um
   módulo porque o resto se afinou a ele. Protocolo correto: knock-out **de nascença**
   (evoluir sem a peça) além do knock-out no campeão.
4. **Subsídio vira renda (N15)** — qualquer socorro sem preço é explorado até virar a
   estratégia principal. O guincho grátis voltou pela porta dos juízes em setembro;
   conferir `politica_util.py:34` sempre que uma métrica melhorar sem explicação.
5. **Almoço grátis (N19)** — canal de modulação que baixa preço de física tem de ser
   limitado a ≥ 1 ou custar mais do que economiza no pior caso.
6. **`torch.quantile` não aceita bfloat16**; **`nice -n 19` starva** (usar 5);
   **matriz [N,N] na GPU durante forward = OOM**.
7. **Orçamento de hardware**: nunca passar de 80 % de VRAM/RAM; declarar o pico esperado
   antes de rodar.
