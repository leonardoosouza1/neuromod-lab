# Como demonstrar a tese em poucos dias

**A tese, em forma testável:** *a mesma cabeça, com o mesmo preço por gene, termina com
genes diferentes ligados conforme o que o mundo esconde e cobra — e os genes que sobram
são os que fazem sentido funcional para aquela demanda.*

Note o que essa formulação exige: **um cruzamento**, não uma escada. Todas as baterias
até aqui variaram um fator por vez, e é por isso que "a peça não paga" ficou ambíguo
por dois meses — sem o cruzamento não dá para separar *"a peça é inútil"* de *"este
mundo não pede a peça"*. É a mesma diferença entre medir a altura de uma planta no sol
e comparar sol contra sombra.

---

## Parte I — O que já está pronto (não refazer)

| peça | estado |
|---|---|
| régua pareada por semente | `analise_campo.py`; `_por_semente` para 15 medidas no `e43_campo` |
| juiz preciso | 128 cópias × 3 mapas; confirmação de 5 sementes diverge da triagem em **+0.001** |
| política que resolve o mundo | agentes, **0.557** (L10 p2) contra 0.85 do campeão evoluído |
| névoa (mundo que esconde) | patch instalado, portão `nevoa=inf` idêntico bit a bit |
| custo suave de gene | `campo.py:425`, `custo_suave` — tira o degrau que criava o vale de aptidão |
| preço da pane | `t1_pane_cara` rodando agora |
| clone política → cérebro | `t2_clone_L6p4` na fila |
| canal de execução | daemon `nmd`, 94 jobs feitos |

## Parte II — Os três instrumentos que ainda faltam (posso fazer hoje, sem GPU)

**1. `dof_por_bloco` — o instrumento central, e ninguém tem.**
Hoje o resultado grava `dof` como **um número**: quantos genes sobreviveram. A tese não
é sobre quantos, é sobre **quais**. Sem quebrar o `dof` por bloco (tálamo, córtex,
hipocampo, reflexo, rápida, lenta) o experimento principal não tem desfecho mensurável.
São ~15 linhas: os nomes já existem em `completo.py:109` (`nomes_genes()`), é só somar
por faixa de índice e gravar `dof_bloco: {...}`.

**2. `--nevoa` no caminho do juiz de política.**
`politica_util.py:34` fixa `nevoa=float('inf')` no namespace. Ou seja: **a névoa não
alcança as políticas dos agentes**. Sem isso não dá para perguntar "a política explícita
sofre quando o mundo esconde?", que é o controle mais importante do dia 3.

**3. `_por_semente` no juiz de política** (o `e43_campo` já tem; o juiz de política
não). Sem isso a régua pareada não se aplica ao placar dos agentes.

Menores, se sobrar tempo: sementes de confirmação independentes das de triagem (o viés
medido é +0.001, então é higiene, não urgência) e gravar `torch.cuda.get_device_name()`
no JSON.

---

## Parte III — A cadeia decisiva, em ordem obrigatória

A ordem importa: cada degrau só é interpretável se o anterior passou.

### Dia 1 — Pré-condições (~2 h de GPU)

**1a. O preço da pane restaurou o gradiente?** (`t1_pane_cara`, rodando)
Critério: amplitude de mortalidade entre as 8 melhores sobe de 1.6 pp para **≥ 8 pp**, e
panes/dia passa a correlacionar com mortalidade (Spearman ≤ −0.4).
Se ✗: a pane não era a amarra; o platô é de outra coisa e o dia 3 vira prioridade.

**1b. O clone preservou a política?** (`t2_clone_L6p4`, na fila)
Critérios, **os dois**: fidelidade de ação ≥ 90 % **e** mortalidade do clone dentro de
5 pp da política explícita.
Se ✗: o experimento do dia 2 mediria o fracasso do clone, não o da evolução. Conserto na
ordem: mais amostras de Φ → clonar no bilinear em vez do linear → aceitar o clone como
inicialização parcial e declarar isso.

**1c. A névoa deixa o mundo comparável?** (triagem, não bateria)
Rodar só o controle linear em névoa 40 / 25 / 15 e exigir a **banda de controle
0.40–0.80** que vocês já usam. Se névoa 15 cravar 1.00, o nível cai fora — é mundo
impossível, não mundo difícil.

### Dia 2 — A lacuna de montagem (~3 h)

A pergunta mais barata e mais informativa do laboratório inteiro, e ela existe pela
primeira vez porque agora há uma política **melhor que tudo que a evolução achou**.

Semear a evolução a partir do clone, λ = 0, 5 sementes, mundo com pane cobrada; braço de
controle: a mesma arquitetura do zero.

| resultado | leitura | o que fazer em seguida |
|---|---|---|
| **perde** (mortalidade sobe acima do clone) | a busca destrói o que recebe: σ = 0.3 fixa para todo gene, clamp ±5, sem crossover, sem niching | consertar a busca antes de qualquer coisa (σ por bloco auto-adaptativo) |
| **segura mas não melhora** | a política está num ótimo local estreito; a paisagem é o gargalo | niching / novidade, ou aceitar o clone como piso e evoluir só o excedente |
| **melhora** | o laço agente → clone → evolução funciona | esse laço vira o motor do laboratório |

Registre a aposta antes. A minha, pelo que li da busca: **perde ou empata**.

### Dia 3 — O mundo que pede (~4 h, paralelizável)

Névoa no nível que passou na banda (provavelmente 25), com a pane cobrada.
Braços: linear · só-camadas · COMPLETO · **a política explícita** (controle novo e
muito mais duro que o linear).

Critério para "o mundo passou a pedir": em névoa, uma arquitetura com memória bate o
linear por **≥ 10 pp pareado por semente** com `ent ≥ 15`, e o mesmo braço **não** batia
no mundo transparente.

### Dia 4 — O experimento principal: alocação (~4 h)

O cruzamento. Uma arquitetura só (COMPLETO), semeada do clone, 5 sementes:

|  | λ = 0 | λ = 0.3 (custo suave) |
|---|---|---|
| **mundo transparente** | dof_A | dof_B |
| **mundo com névoa** | dof_C | dof_D |

**A tese está demonstrada se, e somente se:** dof_D ≫ dof_B (o custo poda muito menos
quando o mundo esconde) **e** os genes que sobram em D estão concentrados no bloco de
memória, enquanto os de B são espinha. Isso é uma *interação* — o efeito do custo depende
do mundo — e é literalmente a frase "a peça vira função quando o mundo cobra e esconde".

Referência de hoje, para dimensionar: no mundo transparente com λ = 0.3, sobram **3 de
355** genes. Se em névoa sobrarem ≥ 30, no bloco certo, é o resultado do ano.

Aviso de potência: interação exige a diferença de diferenças, então a variância dobra.
Com a régua atual (DP entre sementes ~2.6 pp) 5 sementes detectam ~9 pp de interação; se
quiser folga, 8 sementes.

### Dia 5 — Autópsia, régua e escrita

Ablação do bloco sobrevivente no campeão de névoa (se tirar não dói, a co-adaptação
enganou de novo — negativo N5, quarta aparição); análise pareada de tudo; uma figura:
**dof sobrevivente por bloco × mundo × λ**; linha no ledger para cada predição.

---

## Parte IV — O que significa "resultado ótimo", e como isto pode falhar honestamente

**Ótimo** = o cruzamento do dia 4 dá a interação, com mecanismo: o bloco que sobrevive ao
custo sob névoa é o bloco de memória, a ablação dele dói, e a política explícita **também**
piora sob névoa (mostrando que a dificuldade é real e não um artefato do cérebro).

Três maneiras honestas de falhar, e o que cada uma ensina:

1. **A névoa não separa** (todos morrem igual): o eixo "esconder" não é a demanda certa
   neste mundo. Sobra o Minecraft (`mc-farol`), onde a observação é parcial por construção.
2. **A névoa separa, mas nenhum gene sobrevive ao custo**: memória ajuda mas não paga o
   próprio metabolismo. Conclusão forte e publicável — e aí λ vira o objeto de estudo
   (qual é o λ crítico?), não um parâmetro de fundo.
3. **A evolução não segura o clone** (dia 2): o gargalo é a busca, não a tese. O programa
   pausa e vira engenharia de otimizador — que é chato mas é o caminho curto.

## Parte V — Por que isto cabe em cinco dias

Porque nada aqui é uma bateria grande. Os itens caros do passado eram varreduras
exploratórias de 8–14 h; esta cadeia é composta de perguntas com desfecho binário:
o clone preserva ou não; a evolução segura ou não; a interação existe ou não. Rodadas
semeadas convergem cedo (`--paciencia 40`), o juiz de política leva ~1 min, e o
cruzamento do dia 4 são quatro células. **Total estimado: 13 h de GPU em cinco dias** —
menos do que uma escada de névoa completa rodada às cegas.

O que faz caber não é velocidade: é que agora existe uma política que resolve o mundo.
Ela transforma toda pergunta de *"isto é possível?"* em *"o mecanismo acha ou segura?"* —
que é uma pergunta com resposta em uma rodada.
