# Hierarquia de Latência, Sistemas de Memória e Roteamento Sensorial

**Documento de arquitetura.** Como separar caminhos por escala de tempo, como sensores diferentes se alinham, e por que reflexo é memória. Com números medidos e um erro de projeto corrigido.

**Pré-requisitos:** `docs/01` (neurônio ≡ EMA), `docs/03` (neuromodulação), `docs/09` (emulação, §5).

**Status:** §3 contém um resultado que **refuta** uma suposição implícita nos documentos anteriores. Ler antes de implementar qualquer fusão de sensores.

---

## 1. O princípio central

> Não existe "sensor rápido" e "sensor lento" em absoluto. Existe **caminho curto** e **caminho longo**, e a escolha de qual usar depende do regime — distância, urgência, banda disponível.
>
> A separação por latência **não é otimização — é o que garante estabilidade.** Um sistema onde tudo espera o nível lento não sobrevive a eventos rápidos; um sistema só de reflexos não aprende contexto.

Três descobertas independentes do mesmo princípio:

| Origem | Nome | Estrutura |
|---|---|---|
| Neurociência | reflexo espinhal vs córtex | curto e dedicado ∥ longo e flexível |
| Este projeto (`docs/03`) | núcleo vs modulador | rápido aditivo ∥ lento multiplicativo |
| Google (Nested Learning, 2025) | Continuum Memory System | módulos com frequências de atualização distintas |

---

## 2. Hierarquia de latência — medida

### 2.1 Por via

| Via | Sinapses ~ | Latência |
|---|---|---|
| Reflexo corneano R1 (toque) | 2 | 10–12 ms |
| Reflexo corneano R2 (bilateral) | 5 | 30–40 ms |
| Reflexo de ameaça (looming, colículo superior) | 4 | 60–100 ms |
| Resposta cortical (V1 → motor) | 12 | 100–150 ms |
| Percepção consciente / relato verbal | 25 | 200–300 ms |
| Decisão deliberada | 40 | 300–500 ms |

### 2.2 O caso do piscar — cálculo trabalhado

Objeto aproximando a 5 m/s, detectado a 50 cm:

```
tempo até colisão = 0,5 / 5 = 100 ms

reflexo corneano R1       10 ms  →  CHEGOU A TEMPO
reflexo de ameaça         60 ms  →  CHEGOU A TEMPO
resposta cortical        100 ms  →  no limite
percepção consciente     200 ms  →  TARDE DEMAIS
```

> **Você não fecha o olho sem perceber. Você percebe depois de já ter fechado.**
> A consciência recebe o relatório de um evento já resolvido.

O reflexo de ameaça nem passa pelo córtex visual — vai retina → colículo superior → tronco. Circuito dedicado, curto e "burro". É isso que o torna rápido.

### 2.3 Regra de projeto

```
LATÊNCIA CURTA  →  circuito local, dedicado, pouca lógica, sempre pronto
LATÊNCIA LONGA  →  circuito global, flexível, contextual

O nível lento NÃO fica no caminho crítico.
Ele ajusta o GANHO / LIMIAR do nível rápido.
```

É a mesma relação entre medula e córtex: o reflexo patelar funciona em pessoa com secção medular; o córtex apenas modula a excitabilidade.

---

## 3. Transdução sensorial — a premissa invertida

### 3.1 Audição é mais rápida que visão no cérebro

| Sentido | Transdução | Até o córtex | Mecanismo |
|---|---|---|---|
| **Audição** | 0,1 ms | 10–15 ms | **mecânica direta**: estereocílios abrem o canal por força |
| Vestibular | 0,1 ms | 8–10 ms | mecânica direta |
| Tato (Aβ) | 1,0 ms | 20–25 ms | mecanorreceptor + fibra mielinizada (~50 m/s) |
| **Visão** | 25 ms | 40–70 ms | **cascata bioquímica**: rodopsina → transducina → PDE → cGMP |
| Dor (Aδ) | 2 ms | 80–120 ms | mielinizada fina (~15 m/s) |
| Dor (fibra C) | 2 ms | 1–2 s | **não mielinizada** (~1 m/s) |
| Olfato | 120 ms | 150–400 ms | difusão química + cascata de proteína G |
| Paladar | 100 ms | 150–300 ms | cascata química |

**A luz chega primeiro. O sensor de luz é lento.** A física da propagação favorece a visão; a química da transdução favorece a audição.

### 3.2 Horizonte de simultaneidade

Com atraso neural (visão − audição) ≈ 40 ms e som a 343 m/s (2,92 ms/m):

```
distância   som ao córtex   luz ao córtex   quem chega antes
    1 m        12,9 ms         50,0 ms         AUDIÇÃO
   10 m        39,2 ms         50,0 ms         AUDIÇÃO
 13,7 m        49,9 ms         50,0 ms         ← EMPATE
   20 m        68,3 ms         50,0 ms         VISÃO
  100 m       301,5 ms         50,0 ms         VISÃO
```

> **Dentro de ~14 m o som chega antes ao cérebro. Além disso, a luz.**

**Consequência de projeto:** o roteamento correto não é "por sensor", é **por regime de distância**. Perto → confie no de transdução rápida. Longe → confie no de propagação rápida.

### 3.3 Eixos de classificação de sensores

Latência é apenas um eixo. Os outros importam tanto:

| Eixo | Extremo rápido/alto | Extremo lento/baixo |
|---|---|---|
| **Latência** | audição, vestibular | olfato, dor C |
| **Largura de banda** | visão (~10⁷ bit/s) | olfato (~10² bit/s) |
| **Alcance** | audição (omnidirecional, atravessa obstáculo) | tato (contato) |
| **Custo energético** | tato | visão (retina é cara) |
| **Reversibilidade** | visão (fecha o olho) | dor (não desliga) |
| **Prioridade de interrupção** | dor, vestibular | olfato |

**Regra emergente:**

```
rápido + baixa banda   →  alimenta REFLEXO
lento  + alta banda    →  alimenta MODELO DE MUNDO
```

Não é o sensor que decide o destino — é a combinação **latência × banda**.

---

## 4. ⚠️ Correção de arquitetura: banco de τ NÃO alinha sensores

### 4.1 O experimento

Dois sensores reportando o mesmo evento oculto, com defasagem de 22 passos entre eles. Tarefa: prever o evento 20 passos à frente.

```
A) fusão ingênua (valores atuais, sem alinhar)      −2,25 %
B) hardcoded com offset CORRETO (22)                +3,05 %   ← melhor
C) hardcoded com offset ERRADO (8)                  −2,57 %
D) banco de 6 τ por sensor + readout ridge           0,04 %
E) banco de 9 τ por sensor + readout ridge           0,35 %
```

**O hardcode correto venceu. O banco de τ não recuperou o alinhamento.**

### 4.2 Por quê — a distinção que faltava

```
EMA:      h[n] = α·h[n−1] + (1−α)·x[n]     BORRA o passado; desloca o centroide, mas DEFORMA
Atraso:   h[n] = x[n−k]                     DESLOCA sem deformar
```

São operações **diferentes**. EMA é filtro causal assimétrico — suaviza, não translada limpo. Para alinhar sinais defasados é preciso **atraso puro** (buffer circular).

> **Este resultado corrige uma suposição implícita nos documentos anteriores:** o banco de τ log-espaçado resolve extração multi-escala, **não** resolve alinhamento temporal. São duas necessidades distintas e exigem dois mecanismos.

### 4.3 A arquitetura correta

```
POR SENSOR:
  1. linha de atraso (buffer circular de k passos)   ← ALINHA
  2. banco de τ sobre o sinal já alinhado             ← extrai escalas
  3. readout linear aprende a combinar

k é calibrável/aprendível. O banco de τ NÃO substitui k.
```

### 4.4 O cérebro faz exatamente isso

**Recalibração temporal.** Exposição repetida a uma defasagem consistente desloca o ponto de simultaneidade percebida — é por isso que vídeo com áudio dessincronizado incomoda no começo e depois "assenta". O cérebro ajusta o `k`, não filtra.

**Compensação por comprimento de membro.** Tocar o pé e o nariz simultaneamente: o sinal do pé demora ~30 ms a mais (fibra mais longa). A percepção é de simultaneidade. A calibração é aprendida no desenvolvimento.

---

## 5. Sistemas de memória — são tecidos diferentes

### 5.1 Taxonomia

```
DECLARATIVA (verbalizável)
  ├─ episódica: "ontem almocei X"        → hipocampo → córtex
  └─ semântica: "4×5=20"                 → córtex temporal
     substrato: sinapses corticais, consolidação lenta, replay no sono

NÃO-DECLARATIVA (só demonstrável)
  ├─ procedimental: andar de bicicleta   → estriado (gânglios da base)
  ├─ condicionamento: piscar antecipado  → CEREBELO
  ├─ emocional: medo condicionado        → amígdala
  └─ habituação / priming                → circuitos locais
```

### 5.2 A prova de que são separados

Pacientes com lesão hipocampal bilateral (caso H.M.) perdem completamente a capacidade de formar memórias declarativas novas — não conseguem aprender um fato — **mas adquirem condicionamento palpebral normalmente**, sem nenhuma lembrança de ter treinado.

> **O corpo aprendeu; a pessoa não sabe.** Não é uma memória com dois modos de acesso — são sistemas fisicamente distintos, com regras de aprendizado distintas.

### 5.3 Reflexo É memória — com timing aprendido

Simulação do condicionamento palpebral (modelo Marr-Albus-Ito):

```
ISI (CS→US) = 150 ms  →  pico da resposta em 155 ms   (erro +5 ms)
ISI (CS→US) = 250 ms  →  pico da resposta em 255 ms   (erro +5 ms)
```

Perfil temporal da resposta aprendida:

```
ISI=150:  |          ....+++###############+++++++........          |
ISI=250:  |                    ......++++++###################+++++|
           0ms                                              500ms
```

**A mesma rede, com os mesmos neurônios, aprendeu momentos diferentes** — só mudando quando o sinal de erro chega. E a resposta **antecipa**: sobe antes do estímulo aversivo. É previsão, não reação.

### 5.4 A arquitetura que permite isso

```
células granulares  = base temporal (banco de τ + atrasos distribuídos)
célula de Purkinje  = readout linear treinado
fibra trepadeira    = sinal de erro, entregue no instante exato do US
regra               = LTD nas fibras paralelas ativas quando o erro chega
```

**O "quando" fica guardado nos pesos sobre um espectro de constantes de tempo.** É o reservoir + readout ridge de `docs/01` §5, implementado em tecido — com ~69 dos 86 bilhões de neurônios do cérebro.

E a fibra trepadeira é o **terceiro fator** de `plasticity.py`: o traço espera, o sinal de erro chega, consolida.

### 5.5 Limite medido

```
ISI = 400 ms  →  pico em 270 ms  (erro −130 ms)  ← FALHOU
```

A base temporal simulada ia até τ = 300 ms. **Existe um limite superior de ISI condicionável, determinado pela extensão da base temporal.** Em coelhos, o condicionamento palpebral realmente falha para ISI muito longo — o modelo reproduz a limitação biológica.

---

## 6. Aplicação: o piloto virtual

### 6.1 Roteamento por latência × banda

```
CAMINHO REFLEXO  (τ ~ ms, sem rede grande no caminho)
  entrada: proximidade, colisão iminente, perda de tração
  característica: baixa banda (1–8 bits), alta prioridade
  saída: freio, correção de esterço
  o modelo lento NÃO participa — apenas ajusta o limiar

CAMINHO MODELO   (τ ~ 100 ms – s)
  entrada: câmera, mapa, trajetória
  característica: alta banda, latência tolerável
  saída: linha de corrida, política de velocidade
  ajusta o ganho e o limiar do caminho reflexo

CAMINHO MODULADOR (τ ~ s – min)
  entrada: temperatura, desgaste, energia, histórico de erro
  saída: reconfigura parâmetros dos dois acima (multiplicativo)
```

### 6.2 Checklist de implementação

1. **Cada sensor tem seu buffer de atraso** — calibrado, não assumido (§4)
2. **Depois** do alinhamento, banco de τ por sensor
3. Reflexo em caminho separado, sem passar pelo modelo
4. Modelo ajusta limiar do reflexo, nunca o substitui
5. Modulador atua multiplicativamente sobre τ e ganho
6. Medir a latência real de cada caminho — não confiar no diagrama

### 6.3 Erros a evitar

| Erro | Consequência |
|---|---|
| Colisão iminente passando pela rede principal | latência do modelo vira latência do reflexo |
| Fundir sensores sem alinhar | pior que usar um só (medido: −2,25 %) |
| Usar banco de τ para alinhar | não funciona (medido: 0,04 %) |
| Modelo lento no caminho crítico | sistema instável sob evento rápido |
| Reflexo sem modulação de limiar | não adapta a contexto (chuva, pista, pneu) |

---

## 7. Predições testáveis

| # | Predição | Refuta se |
|---|---|---|
| L1 | Buffer de atraso calibrado + banco de τ supera qualquer um isolado | banco sozinho iguala |
| L2 | Erro de calibração de `k` degrada monotonicamente o desempenho | insensível a `k` |
| L3 | Caminho reflexo separado reduz a latência de resposta a colisão em ≥5× | latência igual |
| L4 | Modelo ajustando limiar do reflexo supera limiar fixo em ambiente variável | sem diferença |
| L5 | Base temporal mais extensa amplia o ISI máximo condicionável | ISI máximo independente da base |

L5 já tem evidência parcial (§5.5).

---

## 8. Ressalvas

- As latências de transdução e via foram compiladas de conhecimento de literatura e **não verificadas contra publicações primárias** nesta sessão. Confirmar antes de uso formal.
- O horizonte de simultaneidade de ~14 m depende do valor de atraso neural adotado (40 ms); a literatura reporta faixa, não valor único.
- O experimento de §4 usou sinais sintéticos com defasagem fixa e conhecida. Em sistema real a defasagem varia com carga e temperatura — o `k` precisa ser adaptativo, e isso não foi testado.
- A simulação de condicionamento é um modelo simplificado de Marr-Albus-Ito; não reproduz a microcircuitaria cerebelar completa.
- O caso H.M. e a dissociação declarativa/não-declarativa são consenso estabelecido; a atribuição precisa de cada subtipo a cada estrutura tem nuances em disputa.
