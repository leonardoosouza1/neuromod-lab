# Dimensionamento — Calcular limiar e número de neurônios

## 1. O limiar sai por fórmula fechada

Da solução exata `h(t) = u·τ·(1 − e^(−t/τ))`:

```
t_disparo = −τ · ln(1 − θ/(u·τ))          tempo até cruzar o limiar
u_mínimo  = θ/τ                            piso de sensibilidade
```

**Só dispara se `u·τ > θ`.** Duas equações, dois parâmetros livres (θ, τ).

### Exemplo trabalhado

Requisitos:
1. detectar após 2,0 s de estímulo contínuo
2. ignorar um vislumbre de 0,3 s
3. ignorar estímulo parcial (u < 0,5)

```
escolhe τ = 3,0 s
θ = u·τ·(1 − e^(−t/τ)) = 1·3·(1 − e^(−0,667)) = 1,46

verificações:
  vislumbre 0,3 s → h = 3(1 − e^(−0,1)) = 0,29  <<  1,46   ✓
  piso u_min = θ/τ = 0,49                                   ✓
  esquecimento: h cai a 5% em 3τ = 9 s                      ✓
```

**Três requisitos comportamentais → dois números.** Sem tuning por tentativa.

## 2. Piso analítico para N

Não há fórmula fechada para o N ótimo, mas há limite inferior:

```
N_mín ≥ (ordens de derivada necessárias)      1 valor + 1 taxa = 2 τ distintos
      + 2 × (bits de estado persistente)      cada bit = par de inibição mútua
      + (graus de liberdade motores)
      + camada de mistura (~2× o maior acima)
```

**Validação:** quimiotaxia com 1 sensor precisa valor+taxa (2), 0 bits, 2 motores
→ piso ≈ 2. Ótimo medido: **6** (exp05). O piso acertou a ordem de grandeza.

## 3. Memória = atrator, não peso

O menor circuito de memória tem **dois neurônios em inibição mútua**:

```
A ──inibe──> B
B ──inibe──> A
```

Só um pode estar ativo → dois estados estáveis → 1 bit persistente.
É um flip-flop. Em hardware, é a válvula pneumática biestável.

```
h (estado)   → contexto imediato, volátil
atrator      → bit persistente (2 neurônios = 1 bit)
W (pesos)    → conhecimento permanente
topologia    → estrutura do problema
```

## 4. Onde isso NÃO se aplica

- **Não escala para percepção.** Reconhecer objeto em imagem precisa de milhões
  de parâmetros. Isto serve para **controle e decisão sobre sinais já reduzidos**.
- **N não transfere entre tarefas.** Cada tarefa exige sua própria varredura.
- **A varredura tem ruído.** Resultados do exp05 vêm de 2 seeds.

## 5. Referência de escala biológica

```
neurônios humanos:  ~86 bilhões (cerebelo ~69B, córtex ~16B)
sinapses:           ~10^14
potência:           ~20 W
esparsidade:        ~1-5% ativos simultaneamente
razão E/I:          ~80/20
```

Custo por evento sináptico ~10^-15 J; MAC digital ~10^-13 J.
**Duas a três ordens de grandeza** — a lacuna que motiva hardware neuromórfico.

**Fato humilhante:** o conectoma completo do *C. elegans* (302 neurônios) foi
publicado em **1986**. Quarenta anos depois o OpenWorm ainda não reproduz o
comportamento completo. **Ter o diagrama de fiação não dá a função.**
