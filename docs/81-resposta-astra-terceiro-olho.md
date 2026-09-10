# 81 — Auditoria do `plano-terceiro-olho.md` (Astra) e do código que veio junto — 10/09 18:50

O plano diz "[x] entregue" e é verdade: às 18:25 apareceram no repo, SEM commit, `src/proveniencia.py` (novo), `src/testes_proveniencia.py` (novo), e edições em `src/e43_campo.py` e `scripts/analise_campo.py`. Li linha a linha (não rodei nada fora da fila).

## O que o código faz (conferido no diff)
1. **Manifesto por braço** (`med['manifesto']`): `vars(cfg_b)` (a config EFETIVA, não os flags), protocolo (P/G/R/T/seeds), mapas (parâmetros + sementes 0–3 treino, 1000–1002 teste), juiz (7777, R 1, 128 cópias, sem jardim, corte 0), flags do argparse (menos out/tag/cenario/so/seeds/motor; `init_from` vira sha256 do arquivo), `codigo` = commit + sha256 de TODOS os .py/.cu/.hip em src/ e scripts/ (detecta fonte editado sem commit), ambiente NM_*. `config_hash` = sha256 disso. `cenario_hash` antigo continua.
2. **Tempos honestos**: `res['tempos']` (preparacao, evolucao_conjunta, total) e `med['tempos']` (evolucao_s = null nos braços do lote, avaliacao_s = juiz, total_local_s). `segundos` mantém o significado de antes (juiz nos braços do lote). Sincroniza a GPU só nas fronteiras.
3. **Pareamento por ID**: `analise_campo` alinha `fit_por_semente` pelos `seeds`, recusa sementes duplicadas/faltantes/NaN, recusa `--ref` inexistente, e **recusa comparar resultados sem manifesto a menos que `--legado`**. Diferença de manifesto entre braços exige `--variar caminho`.
4. `fit_por_semente` deixou de ser arredondado a 3 casas (mais precisão; a linha do log fica longa).
5. Guardas novas: sementes duplicadas → erro; `--seres-juntos` com `otim != ga` → erro.

## Riscos que encontrei e o que fiz
- **Risco 1 — cair DEPOIS da evolução.** O manifesto é montado por braço após juiz; se `vars(cfg_b)` tivesse um tensor, `json.dumps` quebraria e o lote inteiro morreria com o resultado na mão. Conferi `CfgCampo.__init__` (campo.py:36–62): só float/int/bool/str/None/tuple/dict; `retina/regime/reproducao` viram dict; `nevoa=inf` é normalizado para 'inf'. Deve passar — mas o teste do Astra usa `SimpleNamespace`, não um `CfgCampo` real, e o runner com mocks não passa pelo juiz. Portão real na fila: `g0c_e43_gate_prov` (Mundo A, 5 seres no lote, P 16, G 2, 2 sementes, ~3 min) roda ANTES de qualquer célula nova.
- **Risco 2 — mudança silenciosa.** `juntos` passou de `issubclass(cls, (Linear, SerCompleto))` para `cls is Linear or issubclass(cls, SerCompleto)`: com `--seres-juntos` e um ser Reflexo/Bilinear (subclasses de Linear) o lote caía em silêncio no caminho por ser. A restrição está certa (o lote trunca em `Linear.NP`), o silêncio não: agora levanta `ValueError` (e43_campo.py, linha após `juntos =`).
- **Risco 3 — fila quebrada.** `o3a_pareado_C` (analise_pareada de e79 C5 com `--mais` A5/B5) falharia: nenhum resultado até hoje tem manifesto. Pedido corrigido com `legado: true`. TODO resultado até e83 é "legado" para o `analise_campo` novo.
- **Risco 4 — testes não verificados por mim.** "5 testes passaram" é afirmação do Astra; vai como `g0a_testes_proveniencia` (whitelist atualizada) e `g0b_testes_cenario` (o e43 mudou; c9l era verde antes).
- **`src/hip/vida.hip`** no commit f2127f3 (18:19, mensagem de IDE) é artefato do hipify (torch gera ao compilar `vida.cu`), não fonte. Fora do índice do git e no `.gitignore` (`src/hip/*.hip`); o arquivo fica no disco.
- Revisor Sonnet com `docs/REVISAO-CHECKLIST.md` rodando em paralelo; commit do código do Astra só com g0a/g0b/g0c verdes e revisão sem NÃO grave.

## Próximas etapas do plano
1. Controle comportamental → pred 179 na fila (o3e parada, o3f linear sem FICAR, nos 3 mundos, mesmos mundos/sementes/orçamento do juiz).
2. Universe: transições controladas + P4 distributivo → parado até o OK do Leonardo (docs/48 16:20).
3. Memória (pistas passadas distintas, memória intacta/reiniciada/embaralhada) → desenhar depois dos controles; encosta na pred 154a/163 (delegação e trajetória).

## Critérios do Astra que adoto
Campeão no teste independente ≠ média de elites; trajetórias não substituem sementes evolutivas; compilação fica na etapa que a dispara; p-valores exploratórios sem correção; DP alta não é bimodalidade (o aviso BIMODAL saiu do `analise_campo`).

## Revisão Sonnet (checklist docs/REVISAO-CHECKLIST.md, 19:00) — LIBERA COM RESSALVA / políticas LIBERA
- 12 itens: 8 SIM, 4 N.A.; `ast.parse` ok; `relogio()` só nas fronteiras (nunca em `um_passo`/`rodar`).
- Risco B confirmado nulo: `CfgCampo` só tem float/int/bool/str/None/tuple; `inf` e tupla passam por `normaliza`; `cfg_b` é cópia do `cfg` original, nunca do `cfg_j` (o único com tensores em `seres`); `flags` exclui `_explicit` (set). `init_from` vira sha256.
- Nenhum pedido combina `--seres-juntos` com subclasse de Linear; `e79/*5.json` têm `seeds` em todos os braços e nenhum tem manifesto → `--legado` obrigatório (o3a ok); `analise_pareada` repassa `--legado`.
- Políticas: contrato batido (índice 8 = FICAR, 19 colunas, shapes, `DEV` no namespace, nenhum padrão PROIBIDO).
- Ressalvas (não bloqueiam): (1) o `clamp(0, G+S-1)` do `esc` só existe em `politica_util.traco`, não em `campo.um_passo` — uma política futura fora do intervalo não é protegida; (2) não há teste que rode `carrega()` sobre as políticas novas. Anotadas para o próximo ciclo de infra.
