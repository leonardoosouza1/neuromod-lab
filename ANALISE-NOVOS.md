# Os resultados novos — a régua, o handicap do hipocampo, e dois erros meus

Figura: `novos-resultados.png`. Três coisas fecharam, e duas delas corrigem análises que
eu mesmo entreguei antes.

---

## 1. A régua: dobrar a população vale 7.7× (e é significativo)

Três células do `e78`, mesmo cenário `mundo_vivo_v1`, mesmo braço linear, 5 sementes,
`ger_efetiva` 33–36:

| config | DP entre sementes | s/semente | poder por segundo |
|---|---|---|---|
| P 256, sementes rotativas | 0.685 | 88.6 | 1.0× |
| P 256, sementes fixas (CRN) | 0.451 | 99.4 | **2.1×** |
| P 512, sementes rotativas | **0.211** | 122.0 | **7.7×** |

`F = 10.56, p = 0.042` para P512 contra P256 (razão de variâncias, 4 e 4 g.l.). O CRN
reduz a DP em 34 % mas não alcança significância com n = 5 (`F = 2.30, p = 0.44`).

Traduzindo em decisão: para um MDE de 0.5 no fit, P256 rotativo precisa de **32 sementes
(47 min de GPU por braço)**; P512 precisa de **5 sementes (10 min)**. Menor efeito
detectável com n = 5: 34 % da média em P256, **10 % em P512**.

Isso contraria a regra da casa "prefira réplicas a tamanho de população". A regra vale
para réplicas de *mundo* dentro de uma avaliação; **não** vale para o tamanho da
população, que é o que reduz a variância da própria busca.

Ressalvas: as três células usaram `--init-from` a partir do mesmo campeão, então o que foi
medido é a DP do *refinamento*, não da evolução do zero — o ganho pode ser menor partindo
de zero. E n = 5 torna a própria estimativa de DP grosseira.

## 2. O hipocampo tem 100× de atenuação escrito no código

Medindo a contribuição de cada bloco na nota de movimento **sem ablação** — pela via que o
próprio `completo.py` já calcula (`s._blk`), no campeão evoluído, ao longo de 4 dias de
vida real:

| bloco | dirige |
|---|---|
| tálamo | 0.4986 |
| córtex | 0.2753 |
| lenta | 0.0269 |
| rápida | 0.0151 |
| reflexo | 0.0029 |
| **hipocampo** | **0.0018** |

E a causa é uma constante: `s.HESC = Cerebro.ESC = 0.01` (`completo.py:52`). A saída do
hipocampo entra multiplicada por **1/100**. Como o termo é exatamente linear em `HESC`, o
mesmo campeão com `hip_esc = 1.0` daria **0.18** — terceiro lugar, acima das camadas
rápida e lenta.

**Toda conclusão de "o hipocampo não paga" foi obtida com a memória abaixada 100×.** A
pergunta "memória serve?" nunca foi feita numa escala em que a memória pudesse agir. O
cenário `v2j_hip_esc` (pred 155) já existe e é a bateria que responde.

Isto também corrige o que eu disse ontem: atribuí a fraqueza do hipocampo à *geometria da
leitura*. A causa próxima é mais simples e mais boba — é um fator de escala.

## 3. Dois erros meus na bancada, corrigidos

**(a) A ablação estava contaminada.** Para medir um bloco eu criava um segundo ser com
aquele bloco zerado e copiava `c` e `MEM` — mas **não** copiava `z`, o estado da camada
lenta, que tem centenas de tiques de história. A diferença medida incluía essa diferença
de estado. Sintoma que denunciou: injetar memória 17× maior não mudava nada no resultado
do hipocampo. A via correta é `s._blk`, que o código já calcula e que não cria ser nenhum.

**(b) As duas bancadas injetaram memória demais.** Medindo `|MEM|` numa vida real do
campeão, com `atualizar()` chamado como o laço faz:

```
|MEM| real          0.059
bancada CS (minha)  0.600   →  10×
bancada CC          1.000   →  17×
```

E o número que importa mais: **só 3.2 das 12 caixas de distrito são tocadas numa vida
inteira** — 16.2 entregas divididas por 12 distritos dá **1.35 amostras por caixa**. Três
quartos do hipocampo lê memória que nunca foi escrita, e o quarto restante estima uma
média com uma amostra. Dos três registros, o único com conteúdo é `mem_espera` (0.11),
justamente o menos informativo; `mem_renda` fica em 0.016–0.061.

Então há **dois** handicaps empilhados: escala 1/100 e dados quase inexistentes. Subir
`hip_esc` sozinho testa o primeiro; reduzir `DMAX` de 12 para 3–4 caixas (ou indexar a
memória por algo frequente, não por distrito) ataca o segundo.

## 4. Uma mudança no laço que valida a métrica

`um_passo` agora faz `sc = sc - sc.mean(1, keepdim=True)` — o modo comum é removido, e o
viés de serviço passa a ser o único árbitro de mover-vs-servir. Consequência: a parcela
"desloca" **deixou de existir** como canal para o movimento. Só "dirige" conta, o que
torna a métrica da bancada a métrica certa por construção, e não por escolha minha.

---

## O que eu poria na fila da GPU agora

| # | bateria | por quê |
|---|---|---|
| 1 | `v2j_hip_esc` (hip_esc 1.0) | a memória nunca foi testada em escala que permita agir |
| 2 | hip_esc 1.0 **+ DMAX 4** | ataca os dois handicaps; sem isso o item 1 pode dar nulo por falta de dados |
| 3 | ablação cruzada reflexo × tálamo (pred 154) | transforma a correlação ρ = −0.76 em causa |
| 4 | tudo o mais em **P 512** | 7.7× de poder por segundo; barato e melhora todas as leituras seguintes |

O item 4 não é uma bateria, é uma mudança de padrão: se P512 se confirmar fora do
`init-from`, o preset honesto deveria subir P antes de subir sementes.
