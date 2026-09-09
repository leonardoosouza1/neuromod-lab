# Formulário — transporte, disparo e vínculo

Companheiro da folha `formulario.png`. Cada família de equações, o que ela faz, e o que
ela vale (ou não vale) para o neuromod-lab. A leitura rápida está na coluna de bolinhas:
**transporte** (o estado muda como ele muda), **difusão** (suavização), **vínculo global**
(não-local, instantâneo) e **disparo** (limiar).

---

## A. Transporte de um campo

**Navier–Stokes** tem os quatro papéis menos o disparo, e é o único da folha com todos os
outros três ao mesmo tempo:

- `(u·∇)u` — **auto-advecção**: o campo se transporta a si mesmo. É a fonte da
  dificuldade do problema e da turbulência.
- `ν∇²u` — **difusão**: suaviza.
- `−∇p/ρ` com `∇·u = 0` — **o vínculo**. A pressão não é uma força física independente:
  é o multiplicador de Lagrange que força a incompressibilidade. Ela se ajusta
  **instantaneamente e globalmente** (resolve uma Poisson a cada passo).

**Continuidade** é o vínculo puro: nada é criado nem destruído, só redistribuído.
**Advecção–difusão** é Navier–Stokes sem o vínculo — e sem ele some a não-localidade,
que é justamente a parte difícil e a parte interessante.

## B. Neurônio no tempo

Quatro modelos em ordem de custo. **LIF** é vazamento mais limiar: o disparo é imposto à
mão. **Hodgkin–Huxley** é o real — as condutâncias dependem da própria voltagem, o que é
auto-advecção em forma de portão. **Izhikevich** entrega quase todo o repertório de
disparo do HH com duas variáveis e um reset. **FitzHugh–Nagumo** é a versão geométrica:
uma variável rápida e uma lenta, e o disparo **emerge** do formato da nulóclina em vez de
ser um `if`.

O que interessa aqui: **nenhum tem vínculo global**. Cada neurônio decide sozinho.

## C. Redes líquidas

A assinatura da **LTC** é a constante de tempo dependente do estado: o τ efetivo vira
`τ/(1 + τ·f(x,I))`, ou seja, **a entrada muda a velocidade do neurônio**. É o parente
mais próximo da auto-advecção de Navier–Stokes dentro das redes neurais — a coisa
modifica como ela muda. A **CfC** é a mesma dinâmica em forma fechada, sem solver.

**E aqui tem uma coisa que os dados de hoje dizem.** As camadas genéricas do cérebro de
vocês (`rap` e `len`, com banco de τ evoluído) são, na prática, uma rede líquida discreta.
E o `dof_bloco` mostra que **62–67 % dos genes ligados estão exatamente nelas**, contra
~24 % no hipocampo e 1 % no reflexo. A evolução prefere a parte líquida aos órgãos
nomeados — sem que ninguém tenha pedido isso.

## D. Campo neural — espaço e tempo

**Wilson–Cowan / Amari** é o passo que falta para a analogia ficar honesta: neurônios
deixam de ser uma lista e viram um **campo** `u(x,t)`, com um núcleo de acoplamento
`w(x−y)` que é **não-local**. Com `w` do tipo chapéu-mexicano (excita perto, inibe longe)
você ganha de graça: bolha de atividade estável (memória de trabalho), competição
espacial (o vencedor apaga os vizinhos) e ondas.

**Reação–difusão** produz padrão espacial a partir de difusão desigual — forma sem
projetista, que é o tema-mãe do laboratório, mas sem papel claro num problema de decisão
com 9 ações.

**Kuramoto** é acoplamento de média de campo: cada oscilador sente a média de todos.
Só faz sentido quando existirem vários seres (F6) — aí vira a equação da coordenação.

## E. O vínculo global — o termo que falta

**Projeção de Helmholtz–Hodge** é como a pressão é de fato calculada: você dá um passo
livre, ele viola o vínculo, e você projeta de volta resolvendo uma Poisson.

**E a descoberta boa é que o cérebro tem esse termo, e ele tem nome:** a **normalização
divisiva** do córtex (`r_i = x_i^n / (σ^n + Σ_j x_j^n)`). É considerada uma computação
canônica — aparece em V1, em atenção, em adaptação, em olfato. E é **estruturalmente a
mesma coisa que a pressão**: um vínculo global, imposto instantaneamente, que
**redistribui** atividade entre unidades em vez de puni-las individualmente.

Foi daí que saiu o §E do `TAREFAS-CLAUDE-CODE.md`: orçamento de atividade em vez de
imposto metabólico.

---

## O outro caminho que você intuiu: a distribuição do líquido

Você disse "a distribuição do líquido", e é aí que a analogia deixa de ser analogia.

Hoje as glândulas do projeto (E16) produzem **escalares globais**: o hormônio sobe e
o corpo inteiro sente na mesma hora, igualmente. Não é assim que funciona. Neuromodulação
real é **transmissão de volume**: dopamina e serotonina são liberadas num ponto e se
espalham pelo meio extracelular, com difusão, decaimento e recaptação. O receptor lê a
**concentração local**. É literalmente advecção–difusão dentro do cérebro:

```
∂h/∂t = D∇²h  −  λ h  +  s(x,t)
        difunde   decai   liberação pela glândula
```

O que isso muda, e é bastante:

- **posição passa a existir** — a glândula tem lugar, e o alcance dela é um gene (`D`);
- **o hormônio ganha atraso e gradiente** — o efeito não é instantâneo nem uniforme, que
  é exatamente o que faltou para os "estados lentos acoplados" pagarem no N19;
- **o custo vira transporte**, não multiplicador: espalhar longe custa mais;
- e o modo de falha do N19 (o hormônio virar um multiplicador fixo saturado) fica mais
  difícil, porque um campo com decaimento não tem valor constante de graça.

Isso é um projeto real, não uma metáfora — e é a única forma de Navier–Stokes entrar no
laboratório fazendo trabalho de verdade em vez de decorar.

---

## O que eu tentaria, em ordem de retorno

| # | ideia | custo | por que |
|---|---|---|---|
| 1 | **vínculo global** (§E, normalização divisiva) | ~1 linha | conserta a catatonia e é a computação canônica do córtex |
| 2 | **custo por disparo** (evento, à la LIF) | pequeno | é a versão fisicamente correta do custo por ativação: o gene custa quando **dispara**, não quando é grande. Casa com o `λ_basal` do B1 |
| 3 | **hormônio como campo** (difusão + decaimento) | médio | dá espaço e atraso à neuromodulação; é a resposta ao N19 |
| 4 | **campo neural** (`w` chapéu-mexicano) | grande | memória de trabalho e competição espacial de graça — mas muda a arquitetura inteira |
| 5 | Kuramoto | — | esperar o multi-ser (F6) |
| 6 | reação–difusão | — | lindo, sem papel claro num problema de 9 ações |

O primeiro item é uma linha e ataca um problema que está travando o experimento **agora**.
O terceiro é o que a sua intuição sobre "distribuição do líquido" está apontando, e é o
mais original dos seis.
