# Controles experimentais reproduzíveis

Entrega: comparação dos campeões por semente evolutiva e preparação de C × C justa sem paradas compartilhadas. Não inclui bateria longa nem novo ambiente de memória.

- [x] Juiz: selecionar IDs evolutivos explicitamente, separados das sementes ambientais; preservar uso anterior e avaliar o genoma correto.
- [x] Cenários: gerar duas cópias da mesma base com G fixo, paciência e corte zero, execução por braço; variar somente a lei de atividade.
- [x] Testes curtos: genomas distintos, IDs inválidos, isolamento de configuração, diferenças exatas entre cenários e preservação dos arquivos existentes.
- [x] Revisão independente especializada e confirmação local dos testes.

Agentes: dois gpt-5.6-luna solicitados; o de cenários concluiu e o de juiz não iniciou (interrompido, implementação concluída pelo principal). Um gpt-5.6-sol faz a revisão final. Sem commits ou submissão à fila automática.

## Uso

`src/julga_politica.py` mantém os argumentos anteriores. Acrescente `--seeds-evolucao todas` para avaliar todos os genomas de `--braco`, ou IDs explícitos como `--seeds-evolucao 2 7`. `--seeds` continua selecionando somente as sementes ambientais. Para remover FICAR do campeão linear, use também `--W-politica campeao`.

O resultado contém `por_semente_evolucao`, `seeds_evolucao`, `seeds_ambientais`, `copias` e `T`. Os campos antigos no topo permanecem apenas no caso de um campeão. Não há agregação automática nem IC que trate cópias ou sementes ambientais como novas evoluções independentes. A política com pesos zero, repetida nos mesmos ambientes, também não se torna uma nova amostra independente a cada campeão.

O juiz agora retorna o horizonte configurado (antes devolvia 240 × dias mesmo com T_max diferente) e desliga corte/jardim na avaliação. Novas métricas: `fit` calculado por `_fit`, `t_vida_media` de todos os seres e `frac_teto`. `dia_morte` permanece legado, condicionado aos mortos; quando não há mortes, seu fallback é o horizonte. Não reconstruir fitness a partir dessa métrica.

**Resultados antigos de horizonte aberto não são diretamente comparáveis:** o juiz podia parar em 2400 ticks apesar de configurar 7200. Reavaliar os campeões antes de concluir sobre sobrevivência em 30 dias. `t_vida_media` é tempo observado até o limite, não estimativa da duração de vida além dele.

O par pronto fica em `cenarios/controle_c_fixo/`: P16, G5, R1, duas sementes, sem paciência, corte ou lote conjunto. É um controle pequeno, não uma bateria conclusiva. O preparador `scripts/prepara_controle_c.py --out DIRETORIO_NOVO` gera outro par e imprime comandos, com resultados separados em `/media/llm-data`. Não executa treino. Use `--G`, `--P`, `--R`, `--seeds` e `--resultados` para definir o orçamento e o destino.

Validação local: `src/testes_julga_politica.py` (orquestração, quatro testes), `src/testes_controle_c.py` e `src/testes_horizonte_juiz.py` passaram usando `.venv-rocm/bin/python`. `HSA_OVERRIDE_GFX_VERSION=10.3.0 .venv-rocm/bin/python neuromod-lab/src/testes_metricas_juiz.py` passou com GPU real, dois ticks por vida. Os testes de orquestração não comprovam equivalência física; o smoke GPU não mede qualidade de aprendizagem.

Revisão especializada gpt-5.6-sol: aprovada sem bloqueantes; repetiu os testes stdlib/orquestração e diff check. Ressalva: o smoke de métricas cobre todos sobreviventes, ainda não uma população mista morto/vivo.
