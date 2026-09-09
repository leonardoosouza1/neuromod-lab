# Checklist de revisão (obrigatório antes de enfileirar GPU) — origem: falhas de 08–09/09/2026

Para cada diff em `src/` ou `scripts/`, o revisor (agente Sonnet) responde SIM/NÃO com linha:linha:
1. **Identidade**: o valor padrão do parâmetro novo reproduz o mundo de hoje? Há teste que compara bit a bit? O teste termina com `assert`/`sys.exit(1)`?
2. **Sentidos**: todo sentido novo é anexado no MESMO ponto em que o nome entra em `NOMES_OP`/`NOMES_CORPO`? Há leitura por nome (não por índice) em quem consome?
3. **Sync**: nada de `.item()`, `.any()`, `bool(tensor)`, `torch.tensor(...)` criado dentro de `obs/passo/extra/atualizar`? (buffers no `reset`)
4. **Sintaxe**: nenhuma edição pôs `#` antes de código na mesma linha? `ast.parse` passou?
5. **Índices cravados**: algum `F[:, :, 14]`, `range(26, NF)`, `[0, 6, 9, 18]` que quebra com sentido novo?
6. **DRY do mundo do juiz**: parâmetros do mundo num lugar só (`politica_util.mundo`) e impressos na 1ª linha do log?
7. **Env/daemon**: flag de env nova está em `_nmd/envs.json`? script novo na `whitelist.json`?
8. **Contrato**: texto que um agente vai ler foi GERADO do código (não escrito de memória)?
9. **Decomposição**: soma dos blocos == total (teste)?
10. **Predição**: a aritmética fecha (n de genes por bloco, escala das medidas)? Aposta própria registrada?
11. **Import**: nomes com underscore importados explicitamente?
12. **Relançamento**: o caminho "máquina reiniciou / laço relançado" usa o estado mais recente?
