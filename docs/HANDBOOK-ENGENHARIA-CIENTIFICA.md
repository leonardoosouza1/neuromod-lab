# Handbook de engenharia científica

Guia curto para todos os agentes/modelos, incluindo Codex, que trabalham no
`Universe` e no `neuromod-lab`.
Esta é a versão canônica do laboratório. O `Universe` depende deste arquivo pelo
caminho irmão `../neuromod-lab/docs/HANDBOOK-ENGENHARIA-CIENTIFICA.md`.

## Como falar sobre evidência

Nas conclusões relevantes, distinga **verificado**, **estático**, **inferido** ou
**hipótese**. Verificado tem comando, artefato, data, seed e escopo. Estático é
leitura de código/configuração. Inferido é cálculo ou interpretação derivada.
Hipótese é o mecanismo ainda não discriminado. Um relatório de agente é pista,
nunca evidência: abra o `arquivo:linha` e confirme.

Antes de uma coleta confirmatória, registre a previsão que ela testa. Declare população,
semente, horizonte, unidade, geometria, mortes e censura. Guarde manifesto com
commit, caminho do binário, SHA-256 do binário/genoma/configuração e comando exato.
Não recompile nem substitua o binário de uma corrida em andamento: registre o SHA
que realmente rodou. Se os dados já existem, marque a análise como exploratória e
não reescreva a previsão como se tivesse sido anterior à coleta.

Um resultado precisa dizer quem foi medido. Campeão, população, sobreviventes e
todos os seres são conjuntos diferentes. Para evolução, mostre primeiro, meio e
última geração; para população, mostre distribuição. Prefira média das últimas N
gerações e seeds pareadas. A melhor observação isolada não é a estimativa.

## Pré-voo antes de enfileirar GPU

1. Leia [`REVISAO-CHECKLIST.md`](REVISAO-CHECKLIST.md) e
   [`controle-experimental.md`](../controle-experimental.md).
2. Escreva a hipótese, a previsão numérica, o efeito mínimo detectável (MDE) e o
   critério de parada antes de executar.
3. Fixe commit, binário, cenário, unidades, geometria, seeds evolutivas e seeds
   ambientais. Separe identidade do genoma de aleatoriedade ambiental.
4. Faça smoke barato: parse, unidade, soma dos blocos, índices, round-trip e
   comparação bit a bit do default. Oracle CPU serve para matemática e I/O; não é
   prova de desempenho ou comportamento na GPU.
5. Calcule o teto físico do horizonte. Um 0% ou 100% no teto pode ser censura,
   não falha do modelo. Registre cobertura, mortes e tempo observado.
6. Para uma intervenção, mude uma variável. A/B usa os mesmos seeds e o mesmo
   ponto de partida. Se mudar duas variáveis, chame de intervenção conjunta.
7. Para causalidade, ablacione o sinal mantendo órgão, genoma e bias; compare
   `memory erase/keep bias` e desligue o órgão em braço separado. Remover o órgão
   mistura causas.
8. Verifique espaço e orçamento. Saídas pesadas vão para
   `/media/llm-data/universe-runs/<nome>/`; não use `/tmp` nem a árvore-fonte.
   Não inicie uma bateria cara sem autorização já existente; use a fila NMD
   configurada e verificada quando aplicável. Agentes baratos podem fazer análise
   delimitada; a confirmação final cabe ao agente principal. Não é obrigatório
   executar dezenas de variantes.
9. Se um gate falhar, aborte. Desvio datado não vira PASS retroativo. Registre o
   bloqueio e o próximo teste discriminante.

## Controles, memória e evolução

O controle experimental deve separar `seeds_evolucao` de `seeds_ambientais`.
Cópias do mesmo genoma ou ancestrais compartilhados não são linhagens
independentes. Não trate política de pesos zero como nova amostra por campeão.
O juiz deve devolver o horizonte configurado; `t_vida_media` é tempo observado
até o limite, não vida além dele. Não reconstrua fitness a partir de `dia_morte`.

Para `u1v`, a observação histórica de 12/09/2026 (Universe commit `8ce51dc`)
usou 3 seeds, 15 gerações e 40 seres, com o mesmo campeão inicial `m23-s77`
e pista `8005`. Cada valor é a média, nas últimas 5 gerações, da quantidade de
seres que completaram pelo menos 2 voltas, entre os 40: `ctrl=[37.8,37.8,39]` e
`hip=[34,28.2,33.4]`. A diferença média t2/t1
foi `0.001553`, SD `0.007014`, `p=.738`, MDE `0.022894`. A estimativa pontual foi
pequena, com estudo sem potência para equivalência; p não
significativo não prova equivalência. Não houve novas corridas neste registro.

No `hip_check`, uma magnitude máxima foi usada como se provasse memória zero. A
verificação posterior encontrou `bias(memory)-bias(empty)` com média absoluta
`[.0839,.0236,.0227]` em `s031`: há sinal de bias/memória não zero. O vetor não zero
prova presença numérica, não utilidade causal.

Na revisão de 12/09, um caso sintético de setor interrompido após 1 tick,
comparado à passagem completa de 200 ticks, produziu `r=0,005` (aparentes 99,5%
de redução). O setor não foi concluído. Exigir identificação e exclusão do setor
terminal interrompido; separar cobertura completa/parcial. Os registros `u1v`
examinados não continham parciais.

Retirar a coluna constante garante viés zero somente quando ambas as memórias lidas
estão vazias. Na primeira passagem pelo setor 23, o próximo setor é 0 e sua memória
já pode estar escrita. Não prometer primeira volta neutra sem testar essa fronteira.
A mudança de duas variáveis é intervenção conjunta, e o MDE antigo `.016` está
obsoleto.
Atualize o MDE quando o desenho e a variância mudarem.

## Causalidade e métricas

“Memória existe” e “memória melhora a decisão” são perguntas diferentes. Meça
estado, ação e resultado sob pares casados. Mantenha bias quando apagar memória;
apague o sinal, não o componente inteiro. Inclua controles vazio, memória mantida
e órgão desligado, com a mesma semente e genoma.

Rotule “inconclusivo” quando n não suporta a conclusão. “Não detectado” não é
“ausente”. Informe intervalo ou MDE e o número de pares. Relate mortes, censura,
alcance do horizonte e unidades. Parâmetros, unidades e geometria precisam ser
iguais; analogia visual não é equivalência física.

Métricas novas exigem teste de regressão sintético, adversarial e físico. Compare
o default bit a bit antes de mudar interpretação. Se números deveriam divergir e
ficam idênticos, pare: suspeite de binário antigo, caminho não alimentado,
ceiling não vinculante, mudança só de display ou artefato de unidade.

## Contrato matemático

Documente a equação realmente executada, com unidades, faixa, `dt`, condições
iniciais e de contorno. Se o gene armazena a taxa de decaimento `d`, registre que
o tempo físico é `tau=1/d`; não troque parâmetro por analogia de nome. Verifique
estabilidade da discretização e a quantidade conservada, quando houver. Amplitude
dinâmica não é transporte; difusão não é decaimento; número de neurônios não é
grau de liberdade ativo. Nome de modelo não estabelece equivalência física.

## GPU, dados e contratos

GPU é um fluxo de dados: prove residência dos buffers, entradas, saídas e perfil.
Diferença entre Rust e WGSL não prova que o writer alimenta o reader. Abra os
bindings e valide o caminho completo. Um comentário, nome ou relatório não prova
execução.

Não crie defaults RNG implícitos. Salve estado e formato de checkpoint; rejeite
incompatibilidade explicitamente. Mudanças de percepção/física entram atrás de
flag desligada por padrão e têm A/B pareado. Não chame smoke de aprendizagem.

Se um hook falhar, descubra o caminho realmente configurado e suas dependências;
não desative o hook às cegas. Se o código não carrega uma informação, diferencie
“sem fonte”, “fonte não conectada” e “fonte varia apenas no tempo”.

## Incidentes históricos que devem orientar leitura

| Data/escopo | Observação | Regra operacional |
|---|---|---|
| 12/09, Universe `8ce51dc` | ancestrais compartilhados e n pequeno | não chamar linhagens independentes |
| 12/09, lab `c973454` | carimbo/relatório histórico | data não torna conclusão atual |
| 12/09, hip_check | magnitude não zerou memória | presença não implica utilidade |
| 12/09, horizonte parcial | razão `.005` | comparar horizontes completos |
| 12/09, auditoria GPU | writer 78–80 confirmado; erro anterior o chamou de ausente | abrir [`perception.wgsl`](../../Universe/src/gpu/perception.wgsl) e seguir o fluxo |
| histórico GPU | comentário divergiu da constante | abrir `file:line` |

Em 12/09, a revisão confirmou que o writer dos canais 78–80 existe em
`../../Universe/src/gpu/perception.wgsl`; a auditoria anterior do agente disse
erradamente que ele não estava escrito. Esta é uma razão para abrir o arquivo e
seguir o dataflow. Estas linhas são observações datadas, não uma lista de bugs atuais. O código pode
ter mudado; confirme o estado presente antes de agir.

## Handoff mínimo

```text
Pergunta/hipótese:
Previsão antes do número:
Status: verificado | estático | inferido | hipótese
Commit e SHA do binário/genoma/config:
Comando, data, seeds evolutivas/ambientais:
População, mortes, censura, horizonte e unidades:
Resultado (média, dispersão, n, MDE/IC):
Evidência: caminho:linha, manifesto e artefato:
Limite/causa ainda não isolada:
Próximo teste discriminante:
``` 

Ao editar, mantenha este handbook como referência do lab. Se o link irmão no
`Universe` estiver ausente, localize-o ou peça o caminho antes de depender dele;
continue trabalho independente que não depende do link. A autorização de escopo do
usuário prevalece sobre defaults históricos.

## Estado da mudança documental

Limite as edições ao escopo autorizado. Antes do handoff, confira `git status`,
`git diff --check` e os diffs de cada repositório; informe mudanças pré-existentes
sem atribuí-las ao handbook. Não faça commit automaticamente.
