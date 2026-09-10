# A parábola, o modelo nulo da deriva, e uma delegação que ninguém programou

Você viu a banheira no painel do córtex e disse que o tálamo parecia o inverso. Está certo,
e a causa é exata. Puxando esse fio saíram três coisas maiores que a observação inicial.
Figura: `deriva-delegacao.png`.

---

## 1. Por que um é banheira e o outro é sino

```
córtex   δ = 0.5·tanh(w)                     UMA unidade saturante
tálamo   Σ_k 2·σ(a_k + b_k·need + c_k·pax)   soma de CINCO
```

`tanh` de um peso uniforme em ±1.5 satura: **26,5 %** da massa fica a menos de 0.1 das
travas. A banheira não é um acidente do desenho, é o que uma saturante faz com ruído.

O tálamo tem a mesma saturação por grupo (DP de um portão = 0.472), mas a **soma de cinco**
traz de volta ao centro pelo teorema central do limite (DP da soma = 1.058, e não 5×0.472
= 2.36). Sino.

Então a sua intuição de "inverso" é literalmente isso: **uma saturante empurra para as
bordas, somar saturantes traz para o meio.** É a mesma matemática das duas, com contagem
diferente.

## 2. O modelo nulo que o laboratório nunca teve

Se `tanh` satura com ruído, então a **deriva sozinha** — passeio aleatório, sem seleção
nenhuma — já produz uma distribuição estruturada. Simulei exatamente isso: 4000 genomas
nascendo transparentes (tudo em zero, regra 17), σ = 0.3 por geração, **zero seleção**:

| geração | genes ligados (dof) | córtex encostado na trava |
|---|---|---|
| 0 | 0 de 502 | 0.000 |
| 5 | 229 | 0.101 |
| 20 | 356 | 0.413 |
| 60 | 416 | 0.635 |
| 120 | **441 de 502 (88 %)** | 0.739 |
| 200 | 455 | 0.796 |

**A deriva pura liga 441 de 502 genes em 120 gerações.** Isso reclassifica todo uso de
`dof` como desfecho: um campeão com 88 % dos genes ligados não mostra nada — é o valor
esperado de não fazer nada. Combina com o que já tínhamos visto (o bloco desligado do
hipocampo tinha *mais* genes ligados que o funcional).

**Regra nova:** `dof` só é interpretável contra a deriva de mesma geração. Um único número
de referência resolve, e ele é barato: rode este passeio uma vez por configuração de σ.

## 3. O campeão comparado com o nulo

Campeão COMPLETO de `e77/v1_sigma02` (5 sementes, retina ligada, NP 765):

- **dof 519 de 765 = 67,8 %** — abaixo dos 88 % da deriva a 120 gerações;
- **córtex na trava: 0.346** — equivale a ~15 gerações de deriva pura.

Ou seja, a seleção está **segurando** o córtex longe das travas. É evidência de que há
seleção agindo ali, e é o primeiro sinal positivo sobre o córtex neste laboratório.

> **Lacuna de instrumento encontrada aqui:** o JSON da bateria **não registra o número de
> gerações**, nem as sementes, nem σ. Sem isso a comparação com o nulo fica em "≈ 15
> gerações" em vez de um teste. São três campos no `res` do `e43_campo.py`.

## 4. O tálamo não é uma válvula uniforme — e não é o que foi desenhado

Portões do campeão, por grupo (necessidade = 0; neutro = 1.00):

| grupo | COMPLETO | sem hipocampo (melhor braço) |
|---|---|---|
| rota | 1.25 | **1.34** |
| serviços | 0.72 | **0.32** |
| corpo | 1.21 | 0.82 |
| economia | 0.64 | 0.61 |
| tempo | 0.81 | 0.59 |

DP entre grupos = 0.51–0.56: **seletivo, não uniforme.** O tálamo amplifica a rota e cala
os serviços. E sob necessidade fecha ainda mais (serviços 0.72 → 0.40 no COMPLETO).

Isso não é "atenção por grupo" como desenhado — é uma **política de o que ignorar**, e ela
tem conteúdo: o ser aprendeu a não olhar para onde ficam os postos.

## 5. A descoberta: delegação entre dois órgãos

Por que calar justo os sentidos de serviço? Porque **o reflexo já faz esse trabalho** por
um caminho próprio (`w·a_ref` empurra ao posto, sem passar pela política geral).

Testando: nos 10 genomas (2 braços × 5 sementes), quanto mais o tálamo fecha o portão dos
serviços, mais forte é o empurrão do reflexo ao posto.

```
ρ = −0.76   p = 0.011   (10 genomas)
dentro do braço COMPLETO:  ρ = −1.00   (n = 5, ordenação perfeita)
```

**Dois órgãos dividindo trabalho, sem que ninguém tenha pedido.** O tálamo desliga a via
lenta para o posto porque a via rápida do reflexo cobre; e onde o reflexo é fraco, o tálamo
reabre o portão. É o resultado mais parecido com "emergência de função" que este
laboratório produziu até agora — e ele estava guardado nos pesos de uma corrida que já
tinha sido analisada só pela mortalidade.

Ressalvas honestas: n = 5 por braço; a diferença **entre** braços não é significativa
(p = 0.19 no portão de serviços); a correlação é sobre genomas, não uma intervenção. O
teste que fecharia isso é uma **ablação cruzada**: matar o reflexo e ver se o portão dos
serviços reabre por evolução. Isso é uma bateria de GPU, e é a que eu poria na fila
primeiro.

---

## O que isto muda no método

1. **`dof` sempre contra a deriva.** Um passeio aleatório por configuração de σ, uma vez.
2. **Registrar gerações, sementes e σ no JSON** — três campos; sem eles não há comparação
   com o nulo.
3. **Ler os pesos, não só as métricas.** A delegação estava numa corrida já analisada. O
   painel de arquitetura (portões por grupo, peso efetivo, genes do reflexo) deveria sair
   junto de toda bateria — é `nm_efetivo.json`, custa segundos de CPU.
4. **A saturação é uma armadilha de desenho.** Qualquer gene que passe por `tanh`/`sigmoid`
   sozinho vai para as travas por deriva. Onde isso não for desejado, somar unidades ou
   pôr um custo que puna a trava.
