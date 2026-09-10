# 74 — Resposta à auditoria do Astra (10/09, 13:25)

Leonardo pediu ao Astra uma terceira leitura do laboratório (bugs, algoritmo, engenharia). A análise foi cortada pelo limite de uso.
Cada ponto que chegou foi conferido no código e consertado onde real. Veredito por item (evidência = linha do código antes do conserto).

| # | Ponto do Astra | Veredito | Evidência | Conserto |
|---|---|---|---|---|
| 1 | `gene_min` do cenário aceito mas não chega ao cfg | **real** | `e43_campo.py:53` põe em `a.gene_min`; `main` (linha 75) copiava `custo_gene/basal/suave` mas não `gene_min` | `cfg.gene_min = float(getattr(a, 'gene_min', cfg.gene_min))`; portão em `testes_cenario` |
| 2 | intermediário da análise pareada "apaga" arquivos pelo nome da pasta | **real (descarta argumento, não apaga arquivo)** | `analise_pareada.py`: com `--out`, filtrava todo argumento que começasse com `.../e7` → o `--mais e79/...` sumia | tira só o par `--out <dir>` |
| 3 | `round(w, 5)` muda se um gene é ativo | **real, impacto ~1e-5** | `e43_campo.py:119` | grava `float(x)` sem arredondar |
| 4 | kernel HIP fixa 12 passageiros e aceita outro NPX | **real** | `vida.cu:15 #define NPX 12`; `cfg.NPX` vem de `passageiros.npx` | `vida_hip.rodar_hip` recusa NPX ≠ 12 (assert com mensagem) |
| 5 | `alinha_semente` com genoma completo + `nomes_f` → `SystemExit` | **real (borda)** | `e43_campo.py:33` só devolvia como está quando `nomes is None` | `len(v) > Linear.NP` devolve como está |
| 6 | `testes_cenario` sem assert/raise | **real** | 0 asserts, só `print(True/False)` | reprova com exit 1; +3 checagens (juiz recebe corpo/cérebro, `braco()`, `gene_min`) |
| 7 | `testes_vida_hip` chama `_fit` sem importar | **real** | `from campo import *` não traz nomes com `_`; `campo` sem `__all__` | `from campo import _fit` |
| 8 | dof por limiar depende da parametrização (U=.4,V=2 ≡ U=.8,V=1) | **válido por construção** | `campo.dof_de`: conta `|w| > gene_min` | é o limite do `custo_gene`; o Mundo B cobra ATIVIDADE (`ativ_centrada`), invariante a reescala. Registrado, sem mudança |

## O que a auditoria destravou (achados meus ao conferir)
1. **O juiz rodava noutro mundo.** `politica_util.mundo()` montava o cfg sem `custo_gene/custo_modo/custo_basal/ativ_centrada` e sem o ajuste de cérebro por ser. `trajetoria`, `julga_politica`, `clona_politica`, `dados_campeao` avaliavam campeões dos Mundos A/B **sem o custo de ativação** com que evoluíram, e `trajetoria` quebrava em 'COMPLETO talamo fixo' (rótulo ≠ classe). Conserto: `mundo()` copia corpo+cérebro do cenário; `braco(d, nome, cfg)` resolve rótulo → classe + ajuste. Pred 176 refaz a4/b4.
2. **Nulo de deriva com σ errado.** `campeao_vs_nulo` comparava com um passeio de σ_mut .3; as baterias usam σ .1. "Campeão dof .25 vs nulo .76 = seleção poda" era artefato. Pred 175; nulo regerado com σ .1, nome do arquivo carrega o σ, placar imprime os dois.
3. **Fila recusava o portão do kernel**: a regex de valor de env não aceitava `/` (`TORCH_EXTENSIONS_DIR`). Corrigida (`[\w./-]{1,80}`), daemon reiniciado.

## Sobre as sugestões de engenharia que o Astra não chegou a enviar
O que já existe e ele pode auditar: fila única de GPU (`scripts/nmd.py`, um processo por vez, whitelist/envs com hot-reload), observador a cada 10 min (`scripts/observador.sh`), predições antes de rodar (`PREDICOES.md`, 176 entradas), gates de identidade bit a bit após qualquer mudança em `campo.py` (`testes_passo_identidade.py`), checklist de revisão (`docs/REVISAO-CHECKLIST.md`), log de alterações dos agentes (`docs/AGENTE-OPUS-LOG.md`).
Fraquezas que reconheço e que ele deve mirar quando voltar: (a) `e43_campo.main` monta o cfg numa linha de 1.400 caracteres e `politica_util.mundo()` a repete por fora — dois lugares para a mesma verdade (foi a causa do achado 1; o próximo passo é extrair `cfg_de_flags()` e usá-lo nos dois); (b) `campeao=reavaliado` e `corte_vivos` ainda não têm célula fechada; (c) o Rust v0 não tem custo de gene nem retina — só serve de motor para o braço linear no mundo v0.
