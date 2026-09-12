# 90 — Auditoria do commit 1b60290 (Astra/Codex via Leonardo, 11/09 21:30): juiz, controle C, testes

Conferido por um agente de leitura (Sonnet) contra `docs/REVISAO-CHECKLIST.md` e consolidado por Fable, 12/09 12:15.
Testes CPU rodados; os 2 testes com GPU (`testes_cli_juiz.py`, `testes_metricas_juiz.py`) NÃO rodaram — entram pela fila.

## Veredito: aceito, com uma ressalva de comparabilidade

| item | veredito | evidência |
|---|---|---|
| Identidade de `braco()` | intacta | `politica_util.py:53-58`, corpo não tocado; chamadores `retrato_vida.py:75`, `trajetoria.py:14`, `julga_politica.py:68` |
| Identidade de `mundo()` | intacta no padrão | `T_aval` só muda com `horizonte == 'aberto'` (`--horizonte` padrão `fixo`, `e43_campo.py:174`); `testes_horizonte_juiz.py:16-19` prova `(fixo, 7200, 10) → 2400` |
| Identidade de `mede()` | intacta no padrão | força `corte_vivos = 0` e `jardim_comum = False` numa CÓPIA do cfg (`politica_util.py:60`); são os padrões de hoje; `dia_morte` fallback `T/240` = 10,0 no caso histórico |
| `carrega(path, fonte=None)` | sem caminho novo de leitura | `politica_util.py:8-21`: `fonte` omitida ⇒ lê `path` como antes; `julga_politica.py:72` passa o texto já lido — não pode carregar outro arquivo |
| Item 13 (W = 0, `tudo` = 0 / −1e9) | verdadeiro | `campo.py:485-497` não tocado; `--W-politica zero` continua padrão (`julga_politica.py:61,111`) |
| Testes terminam em assert/exit | sim | 4 CPU rodaram verdes (`testes_controle_c`, `testes_estado_politica`, `testes_horizonte_juiz`, `testes_julga_politica` 7/7); `py_compile` ok nos 9 `.py` |
| Armazenamento | ok | `prepara_controle_c.py` escreve 2 JSONs de config em `--out`; `--resultados` aponta para `/media/llm-data/universe-runs/` |

## Ressalva (única que muda leitura de resultado)

Para cenários com `horizonte: "aberto"`, o juiz agora usa `T_max` (ou 7 200) e avalia com `corte_vivos = 0` e
`jardim_comum = False`. Resultados de horizonte aberto ANTERIORES a 11/09 21:30 foram julgados com T = 240·dias e o
corte/jardim do cenário — não são comparáveis aos novos. O `controle-experimental.md` avisa; fica aqui também para
quem reler as baterias o3/o4 de 10/09.

## Código morto, sem risco

`julga_politica.py:72-75` tem `try/except TypeError` "compatibilidade com politica_util antiga" que nunca dispara (os
dois arquivos são versionados juntos). `round(x, 4)` sumiu dos campos `*_por_semente` — precisão a mais, nenhum
consumidor depende do arredondamento.

## O que o `controle-experimental.md` pede e o que faço

Controle C × C pareado (mesma base, G/paciência/corte fixos, só `ativ_centrada` variando) com IDs evolutivos separados
das sementes de mundo. Entra na fila do lab DEPOIS do `u1` do Universe (GPU serial), como `o5_controle_c_pareado`, com
os 2 testes GPU do commit rodando antes como portão.
