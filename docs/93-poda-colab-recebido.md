# 16 — Poda como Operador de Busca

**Documento de resultados.** Testa se *selecionar* conexões supera *gerar* pesos,
no benchmark de táxis com corpo.

**Origem da hipótese:** observação do usuário de que o cérebro humano superproduz
sinapses e depois poda — desenvolvimento é subtrativo. Redes neurais fazem o
oposto: ajustam todos os pesos o tempo todo.

---

## 1. A hipótese

> O cérebro atinge pico de densidade sináptica por volta de 1-2 anos e depois
> **perde** cerca de metade das sinapses até a adolescência. Ele seleciona, não gera.
>
> Redes neurais geram pesos. Talvez selecionar seja melhor.

Precedente na literatura: **Lottery Ticket Hypothesis** (Frankle & Carbin, 2019) —
uma rede densa contém uma sub-rede esparsa que, treinada isoladamente, atinge a
mesma acurácia. Ou seja, o treino denso talvez já esteja *selecionando*.

---

## 2. Implementação

Cada genoma ganha uma máscara binária `M` do mesmo tamanho de `W`.
O score usa `W * M`. Três estratégias de mutação:

```
gerar     w += ruido(σ=0.30)                          — o padrão
podar     nasce M=1; desliga com p=5%, religa p=1.5%;  w += ruido(σ=0.15)
crescer   nasce M~Bernoulli(0.25); liga com p=5%;      w += ruido(σ=0.15)
desenv.   cronograma: explode(σ=.30) → poda(σ=.15,p=.06) → consolida(σ=.06)
```

A mutação de peso é **menor** quando há poda (0.15 contra 0.30) — a poda faz o
trabalho grosso, o ruído só refina.

**Protocolo:** população 300, 60 gerações, 3 cidades amostradas por geração de um
pool de 6, avaliação final em 5 cidades **nunca vistas**, 60 mundos por cidade.
20 sementes independentes. Total: 6.000 amostras por modo.

---

## 3. Resultado

### 3.1 Fitness de treino — significativo

| | gerar | podar | diferença | t | p | vitórias |
|---|---|---|---|---|---|---|
| fitness | 9,04 ± 0,69 | **10,54 ± 1,15** | **+1,50 ± 0,32** | 4,67 | **<0,00001** | **18/20** |

### 3.2 Generalização em cidades novas — no limiar

| | gerar | podar | diferença | t | p | vitórias |
|---|---|---|---|---|---|---|
| entregas | 13,76 ± 2,52 | 15,38 ± 2,33 | +1,62 ± 0,84 | 1,93 | **0,053** | 12/20 |

> **A diferença é quase idêntica nos dois casos (+1,50 e +1,62), mas o ruído na
> generalização é 2,6× maior.** É o ruído que impede a conclusão, não a ausência
> de efeito.

### 3.3 Curva de aprendizado

```
geração     0     6    12    18    24    30    36    42    48    54
gerar     1,7   5,7   6,8   7,2   8,0   8,1   8,2   8,6   8,7   9,5
podar     1,7   6,2   7,4   8,1   8,7   8,8   8,9   9,3  10,0  10,2
conexões  100%   76%   63%   55%   47%   42%   39%   37%   36%   35%
```

**A poda é melhor em 57 das 60 gerações.** Isso é mais forte que a média final:
sob a hipótese nula, 57/60 numa direção tem probabilidade desprezível.

E a esparsidade **estabiliza em 35%** — não colapsa a zero. Bate com a biologia:
a poda sináptica desacelera e para.

---

## 4. Núcleo convergente

20 evoluções independentes, partindo de sementes diferentes:

| MANTIDO | % | DESCARTADO | % |
|---|---|---|---|
| `d_alvo` | **100 %** | `e_tem_pax` | **0 %** |
| `sv_posto` | 95 % | `semaforo` | **0 %** |
| `e_temperatura` | 85 % | `custo_rua` | **0 %** |
| `e_fadiga` | 70 % | `d_loja` | **0 %** |
| `e_fuel` | 55 % | `d_descanso` | **0 %** |
| `congestao` | 50 % | `d_oficina` | 5 % |

**Cinco features descartadas em 20/20 sementes.** Não é acaso — é convergência
estrutural, e é interpretável:

- `e_tem_pax` — **redundante**: `d_alvo` já aponta para o destino quando há passageiro
- `custo_rua` — **contido** em `d_alvo`
- `semaforo` — o agente aprende a não depender de olhar a luz

Mas apenas **9 de 24 features têm decisão estável** (>90 % ou <10 %). As outras 15
ficam entre 15 % e 85 % — a poda não converge nelas, sugerindo que são
**substituíveis entre si**, não claramente úteis ou inúteis.

---

## 5. Por que podar vence a busca

O mecanismo é a **qualidade do sinal de seleção**:

```
mutar peso:  w += ruído   →  efeito pequeno e ambíguo, diluído entre 24 dimensões
desligar:    w  = 0       →  efeito discreto e atribuível a UMA conexão
```

A seleção julga "esta conexão atrapalha" muito melhor que "este peso deveria ser
0,3 em vez de 0,4". É busca no espaço de **estrutura**, não de valores — e cada
passo estrutural é informativo.

Evidência de apoio: com mutação livre, o peso médio nas features úteis e inúteis
é praticamente igual (razão 1,01×) — **a mutação livre não distingue**.

---

## 6. ⚠️ O que NÃO se confirmou

### 6.1 Cronograma desenvolvimentista

A tradução direta da biologia — superprodução → poda → consolidação — **não
superou a poda constante**. A fase de "superprodução" foi implementada como
mutação forte de pesos (σ=0,45) e isso destruiu o progresso inicial.

Diagnóstico provável: no cérebro a superprodução é de **conexões**, não de ruído
nos valores. A fase 1 deveria criar diversidade estrutural, não sacudir pesos.
Isso não foi testado.

### 6.2 Amostra pequena mentiu

Uma primeira rodada com **2 sementes** deu "+55 % para a poda". Com 20 sementes, a
mesma comparação de generalização deu p=0,053.

> Se eu tivesse documentado com 2 sementes, teria registrado um efeito falso de
> magnitude 20× maior que o real. **Invariante I4 elevado para ≥10 sementes.**

---

## 7. Achados acionáveis

| # | Achado | Ação |
|---|---|---|
| PD1 | Poda supera mutação livre no treino (p<0,00001, 18/20) | usar máscara + mutação menor |
| PD2 | Vantagem aparece em 57/60 gerações, não só no fim | não é sorte de parada |
| PD3 | Esparsidade estabiliza em 35 % | não precisa de regularizador |
| PD4 | 5 features descartadas em 20/20 | poda faz seleção de features interpretável |
| PD5 | Só 9/24 features têm decisão estável | as demais são substituíveis |
| PD6 | Generalização no limiar (p=0,053) | **não afirmar** sem mais sementes |
| PD7 | Cronograma desenvolvimentista não superou | não implementar como está |

---

## 8. Próximo passo

**Hipótese para a lacuna de generalização:** a poda especializa nas cidades de
treino e descarta features que cidades novas precisariam.

**Teste:** poda com mais cidades de treino (12 ou 20 em vez de 6). Se a fraqueza é
especialização excessiva, mais variedade durante a poda deve fechar a lacuna.

Segundo teste: **poda tardia** — evoluir 30 gerações sem máscara e só então ativar
a poda. Se a vantagem vem de podar *depois* de encontrar uma boa região, isso
deveria ser melhor que podar desde o início.

---

## 9. Ressalvas

- Um único domínio (táxis com corpo, grafo de 24 nós). Não generaliza automaticamente.
- Arquitetura reativa apenas (24 parâmetros). Não testado nas arquiteturas com memória.
- As probabilidades de poda (5 % desligar, 1,5 % religar) foram escolhidas a olho,
  sem busca de hiperparâmetro. Um valor melhor pode existir.
- O teste t pareado assume normalidade das diferenças; com n=20 é razoável, mas o
  p=0,053 está perto demais do limiar para ser tratado como conclusivo em qualquer direção.
- A simulação é numpy single-thread. Os números de tempo não são comparáveis com a
  versão torch.
