# Plano de refatoração — terceiro olho

Objetivo: tornar resultados comparáveis antes de alterar fórmulas ou investir em novas baterias.

## Entrega atual: integridade experimental
- [x] Registrar configuração efetiva por braço, protocolo, ambiente NM_*, identidade do código e backend executado. Hash deve mudar com configuração efetiva.
- [x] Parear métricas por ID de semente; rejeitar IDs duplicados, dados inválidos e configurações incompatíveis. Comparação legada exige opção explícita.
- [x] Separar evolução compartilhada, evolução individual, avaliação e tempo total; não atribuir tempo compartilhado arbitrariamente aos braços.
- [x] Testar regressões sem executar baterias evolutivas; documentar uso e limitações.

## Próximas etapas, após a base confiável
1. Controle comportamental: sempre parado, campeão linear e mesmo campeão sem ação ficar. Mesmos mundos, sementes e orçamento; medir sobrevivência, renda e contexto das pausas. Não alterar recompensa com base apenas na frequência de ficar.
2. Universe: testes de transição de embarque, respawn e compra com estado inicial e sorteios controlados; depois comparação distributiva P4. Não confundir RNG distinto com erro físico.
3. Memória: ensaio com observações presentes iguais e pistas passadas distintas; comparar memória intacta, reiniciada e pistas embaralhadas.

Critérios científicos: campeão no teste independente e média de elites são métricas distintas; trajetórias não substituem sementes evolutivas independentes. Nenhuma conclusão de desempenho sem medição comparável. Compilação fica incluída na etapa que a dispara até existir instrumentação específica.

## Uso da entrega atual

Resultados novos têm `bracos.<nome>.manifesto` e `config_hash` (SHA-256). O antigo `cenario_hash` continua identificando somente o JSON de cenário. O manifesto inclui configuração por braço, parâmetros/sementes dos mapas, juiz, protocolo, flags NM_* e hash dos fontes Python/HIP/CUDA presentes. Esse hash detecta fontes locais modificados mesmo sem commit.

```bash
# Mesmo protocolo e configuração; alinha pelos IDs, independentemente da ordem.
python scripts/analise_campo.py resultado.json --ref linear --metrica fit

# Ablação intencional: declarar somente os campos alterados indicados pelo erro.
python scripts/analise_campo.py resultado.json --ref linear --metrica fit --variar cfg.talamo_norm

# Resultados anteriores sem manifesto: comparabilidade assumida explicitamente.
python scripts/analise_campo.py antigo.json --legado
```

`--legado` não inventa IDs ausentes nem aceita sementes duplicadas. Diferenças de código também precisam ser declaradas (`--variar codigo`) quando intencionais. Campos duplicados em `flags` e `cfg` exigem declarar ambos quando diferirem. P-valores são exploratórios, sem correção de múltiplas comparações; MDE é aproximado. DP elevada não é evidência suficiente de bimodalidade.

`tempos.evolucao_conjunta_s` pertence ao experimento. Nos braços conjuntos, `tempos.evolucao_s=null`; `total_local_s` e o campo legado `segundos` não incluem evolução compartilhada. `avaliacao_s` mede o juiz. `tempos.total_s` global mede até o registro do braço mais recente, antes da escrita final. Sincronização GPU ocorre nas fronteiras; compilação permanece incluída na etapa que a executa. `motor` identifica HIP/Torch selecionado para evolução e `motor_avaliacao` identifica o juiz; não certifica sucesso do torch.compile.

Validação: `src/testes_proveniencia.py` passou 5 testes, incluindo runner com evolução/avaliação simuladas, sem bateria GPU. Compilação sintática e `git diff --check` passaram. Ruff não está instalado no ambiente. Não foram produzidas novas conclusões comportamentais nem medições de desempenho. Universe permanece para a etapa de transições controladas.
