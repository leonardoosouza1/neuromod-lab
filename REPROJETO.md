# Se eu refizesse o projeto do zero

Resposta medida, não opinada. Figura: `reprojeto.png`.

Duas metades que não se misturam: **rápido de rodar** e **rápido de descobrir**. A segunda
custou muito mais caro aqui do que a primeira, mas você perguntou pelas duas.

---

# Parte 1 — o que eu manteria sem mexer

Antes do que mudaria, porque isto é raro e vocês têm:

- **Ledger com predição escrita antes.** 168 entradas com ✓/✗ e mecanismo. É o que
  permitiu, hoje, dizer "o jardim comum deu nulo" em vez de esquecer que eu tinha previsto
  outra coisa.
- **Portões de identidade.** `jardim_comum=False` idêntico bit a bit; `testes_retina`
  pegando colunas do corpo deslocadas em 2. Sentido lido na posição errada é o bug que
  produz meses de resultado limpo e errado.
- **Genes nascendo em zero = espinha exata.** Toda peça nova nasce transparente. Sem isso
  nenhuma ablação significa nada.
- **Registro de negativos com mecanismo.** N1, N5, N14, N15, N19 são propriedade
  intelectual real; a maior parte dos laboratórios joga isso fora.
- **A fila em disco.** Simples, sem rede, auditável.

Isso é o esqueleto metodológico e ele está certo. O que segue é sobre o corpo.

---

# Parte 2 — rápido de rodar

## 2.1 O diagnóstico: o laço é limitado por LANÇAMENTO, não por conta

Medido num tique com B = 1024 e retina ligada:

```
obs()  (os sentidos)   55 %          4 486 operações aten por tique
passo() (física)       23 %          das quais ~930 são conversão de tipo
extra() (o cérebro)     8 %
serv_need + atualizar  12 %
```

Agora a aritmética que fecha tudo. Uma bateria de 60 gerações × 1200 tiques = **72 000
tiques**. O `P256R4jan` levou **792 s**. Isso dá **11.0 ms por tique** — e 11.0 ms ÷ 4 486
operações = **2.45 µs por operação**, que é exatamente o custo de lançar um kernel em
ROCm.

**O tempo da bateria é o número de operações vezes o custo de lançamento.** A conta em si
não aparece. Três consequências imediatas:

1. **População é quase de graça.** Dobrar P dobra o tamanho dos tensores, não o número de
   lançamentos — e de fato P512 custou só 1.26× o tempo de P256 por geração. Isso não é
   coincidência, é a mesma medição vista de outro lado.
2. **Otimizar o cérebro é perda de tempo.** Ele é 8 % do tique. Mesmo zerando o cérebro
   inteiro a bateria cai 8 %.
3. **Cortar operações é o único ganho real**, e é multiplicativo com tudo o mais.

## 2.2 O mundo é um campo, não uma lista de pontos

Esta é a mudança que eu faria primeiro, e eu já a prototipei e medi.

Hoje a distância ao serviço mais perto é recalculada a cada tique, varrendo os pontos.
A grade pré-computada de 128×128 **já existe no código** — mas só guarda o distrito.
Estendendo-a para guardar também a distância a cada tipo de serviço:

| | hoje | campo pré-computado | ganho |
|---|---|---|---|
| distância na posição | 1.404 ms | 0.065 ms | **21.7×** |
| distância por opção de movimento | 2.009 ms | 0.150 ms | **13.4×** |
| operações | 239 | 49 | 4.9× |

Custo: **328 KB por mapa**. Erro: **0.37 m em média, p95 0.78 m** — e o ser anda 1.0 m por
tique, então o erro está **abaixo de um passo**. Não é aproximação perceptível; é
quantização mais fina que a ação.

Generalizando: **tudo que é estático vira canal de uma pilha `(C, GR, GR)`** — custo do
terreno, distrito, distância a cada um dos 5 serviços, multiplicador de preço, alíquota,
aluguel, demanda, opacidade. São ~12 canais; em float16 a 128×128 dá **393 KB por mapa**.
Subir para 256×256 custa 1.6 MB e derruba o erro para 0.19 m — continua sendo nada.

Com isso **todo sentido estático é um `gather`**. Um único `gather` de (B,G) índices numa
pilha de 12 canais substitui a maior parte do `obs()`. E a retina deixa de marchar sobre
pontos: marcha sobre a mesma pilha.

O que **não** entra na pilha: passageiros (movem), preços do dia (variam com o ciclo),
corpo. Esses são tensores pequenos e baratos.

## 2.3 O tique é um kernel, não 4 486 operações

Três fontes de operação supérflua, todas visíveis no perfil:

1. **~930 conversões de tipo por tique.** Nenhuma é explícita — todas nascem de
   `torch.where(cond, tensor, 0.15)`, `clamp(0., L)`, `full_like(x, c.nevoa)` com escalares
   Python. Cada uma aloca um tensor 0-dim e faz uma cópia. **Conserto**: promover todas as
   constantes de `cfg` a tensores 0-dim uma vez no `reset` e usar sempre a versão tensor.
   Barato, mecânico, e sozinho deve cortar centenas de operações.
2. **Laços Python sobre tipos.** `for j in (0,1,2,4,3)` no `obs()` executa 5 vezes um bloco
   de ~8 operações. Com a pilha de canais isso vira **uma** operação sobre o eixo de tipo.
3. **Concatenações e `stack` intermediários.** `F = [...]` acumula 10–11 tensores e depois
   `stack`. Com a pilha, `Fop` sai pronto do `gather`.

Alvo realista: **de 4 486 para 300–500 operações por tique**. Pela aritmética acima, isso é
uma bateria de 792 s virando **60–90 s**, na mesma GPU, com o mesmo resultado numérico
(dentro do erro de 0.37 m, que é gateável).

E aí `torch.compile` passa a valer a pena de verdade: com poucas operações grandes o
Inductor funde bem; com 4 486 minúsculas ele passa o tempo a compilar grafos que não
cabem.

## 2.4 A ordem que eu seguiria

| # | mudança | ganho esperado | risco |
|---|---|---|---|
| 1 | constantes de `cfg` como tensores 0-dim | −20 a −30 % de operações | nenhum, portão bit a bit não passa (muda ordem de ponto flutuante? não — mesma conta) |
| 2 | pilha `(C,GR,GR)` para distâncias a serviço | −13× naquele trecho | erro 0.37 m, precisa de portão de tolerância |
| 3 | vetorizar o eixo de tipo | −5 laços Python | nenhum |
| 4 | `obs()` inteiro como um gather + um cat | o grosso dos 55 % | reescrita, precisa de portão forte |
| 5 | `torch.compile` depois de 1–4 | fusão real | recompilação |

Cada uma com o mesmo portão de sempre: mesma configuração antes e depois, todas as medidas
iguais (ou dentro da tolerância declarada, no caso do 2).

---

# Parte 3 — rápido de descobrir

Aqui está o desperdício grande, e ele não é de GPU.

## 3.1 O mundo nunca foi dimensionado contra a vida do ser

Três números medidos, todos a mesma doença:

| grandeza | está | precisaria de | fração |
|---|---|---|---|
| ciclos do regime por vida | 0.86 | ≥ 3 | 29 % |
| amostras por caixa de memória | 1.35 | ≥ 5 | 27 % |
| fração da cidade que o ser visita | 11 % | ≥ 50 % | 21 % |

O regime tem período de 5 dias e o ser vive 4.3 — ele morre antes de ver a estação repetir,
então não há nada aprendível numa vida. A memória tem 12 caixas de distrito e o ser faz
16 entregas — 1.35 amostras por caixa. E o raio de ação é 37 m numa cidade de 200×200: ele
conhece 11 % do mapa.

**Nenhuma dessas três é um problema de arquitetura. São constantes de mundo escolhidas em
unidades absolutas.** Um hipocampo perfeito não estima nada com 1.35 amostras; um sistema
de plasticidade perfeito não aprende um ciclo que nunca se repete.

**A regra que eu poria na fundação do projeto novo:** nenhuma constante de mundo é definida
em unidade absoluta. Toda constante é definida como **razão contra a vida do ser** —
período do regime = ⅓ da vida esperada, número de caixas de memória = entregas por vida ÷ 5,
lado da cidade = 3× o raio de ação. Quando a vida muda (e ela muda a cada mundo novo), as
constantes acompanham. Isso é uma função `dimensiona(cenario, vida_esperada)` chamada antes
de qualquer bateria, e um portão que recusa rodar se alguma razão estiver fora da faixa.

## 3.2 A capacidade da peça vem antes do experimento com a peça

Três instrumentos invalidaram meses de leitura, e todos rodam em segundos de CPU:

- **Bancada de capacidade** — o hipocampo dirige 0.0004 contra 0.645 do tálamo; o córtex
  não consegue inverter sinal (`|δ| ≤ 0.5`) num mundo que exige inversão. Resultado nulo de
  peça que não pode expressar a função não é resultado sobre a peça.
- **Nulo da deriva** — a deriva pura liga 88 % dos genes em 120 gerações. `dof` como
  desfecho é inválido sem esse controle.
- **Trajetória** — 27 % de concordância de ação e desfecho parecido: o mapa
  comportamento→destino é degenerado.

No projeto novo esses três existem **antes** da primeira bateria, e cada um é um portão:
peça que não passa na bancada não entra em bateria.

## 3.3 A medida que eu faria no dia 1

Antes de escrever qualquer cérebro: **medir a resolução do mundo**. Ou seja, quanta
diferença de comportamento é necessária para produzir diferença de desfecho.

O procedimento é o que a trajetória já faz: pegar políticas explícitas deliberadamente
diferentes, rodar no jardim comum, e medir a curva "diferença de ação × diferença de
tempo de vida". Se 27 % de concordância dá o mesmo desfecho — como deu aqui — **o mundo
não tem resolução para distinguir arquiteturas**, e nenhuma bateria vai resolver isso.

Um mundo bom para esta tese é um mundo onde essa curva é **íngreme**. Isso é uma
propriedade projetável, e é a primeira coisa que eu ajustaria — antes de qualquer órgão.

## 3.4 Uma moeda só

Dinheiro, gasolina, caloria e calor são quatro escalares com câmbio definido caso a caso, e
**toda exploração já encontrada mora numa dessas conversões**: N15 (subsídio vira renda),
N19 (almoço grátis), a pedra, o guincho-táxi, a catatonia do v2. Tapar um faz a evolução
achar o próximo, porque procurar isso é literalmente o trabalho dela.

Um orçamento único de energia com as conversões viradas **eficiências em (0,1]** fecha a
classe inteira, inclusive os buracos que ainda não foram descobertos. É a diferença entre
adicionar uma regra e adicionar uma conservação.

---

# Parte 4 — o esqueleto que eu escreveria

```
mundo/
  campo.py        pilha (C,GR,GR) imutável + estado dinâmico pequeno
  dimensiona.py   constantes em RAZÃO contra a vida; portão de faixa
  passo.py        um tique = um punhado de operações grandes
seres/
  espinha.py      a política linear, sempre o controle
  pecas/          cada órgão com contrato: nasce transparente, tem custo, tem teste de capacidade
bancada/
  capacidade.py   dirige / desloca / muda-a-ação por peça — portão antes da bateria
  deriva.py       nulo sem seleção, por geração
  trajetoria.py   concordância, divergência, ponto de decisão
  resolucao.py    a curva diferença-de-ação × diferença-de-desfecho do mundo
regua/
  pareado.py      teste pareado + MDE do protocolo
  preregistro.py  hipótese → critério → n, travado antes
```

Duas regras de contrato que eu poria por escrito na fundação:

1. **Nada de estático é calculado dentro do laço.** Se não muda durante a vida, é canal da
   pilha. Portão: contar operações por tique e falhar se passar do orçamento declarado.
2. **Nenhuma peça entra em bateria sem passar na bancada de capacidade.** Peça que dirige
   menos que 1 % da espinha por gene tem resultado nulo garantido pela geometria — medir
   isso custa segundos e economiza dias.

---

# Parte 5 — o número final

Juntando as duas metades, com o que está medido:

| eixo | hoje | reprojetado | fonte |
|---|---|---|---|
| operações por tique | 4 486 | 300–500 | perfil + protótipo |
| tempo de bateria (60 ger) | 792 s | 60–90 s | 11.0 ms/tique ÷ ganho de operações |
| população pelo mesmo preço | 256 | 1024+ | custo é lançamento, não tamanho |
| MDE do protocolo (n=5) | 34 % da média | 10 % | P512 já medido, p=0.042 |
| baterias que não podiam detectar nada | várias | zero | portão de capacidade + dimensionamento |

O ganho de engenharia é ~10×. O ganho de método é maior e não tem número: é a diferença
entre rodar 60 baterias e ter 6 resultados, ou rodar 20 e ter 15.
