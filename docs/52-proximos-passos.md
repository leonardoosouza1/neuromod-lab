# 52 — Próximos passos após o fechamento do táxi (para decisão do Leonardo)

**Estado (2026-09-08 21:20).** A linha "peça que paga no táxi" fechou por três lados independentes (busca ×4,
otimizador com gradiente em 3 variantes, ruído da nota pela metade): o campeão linear é um pico local da régua
"riqueza em 10 dias" (painel 55). Não há mais teste barato que mude isso sem mexer em régua ou mundo. GPU livre.

## As três portas (uma escolha, não três)

| Porta | O que muda | Custo | Predição registrável | Risco |
|---|---|---|---|---|
| **A. Farol (Minecraft)** | mundo real com sensores, villagers como seres; cérebro (espinha + sensores + portões) vira cliente do `mc-farol` | 2–3 dias de ponte (spike já verificado: 5 fps, 64 entidades, 93 µs/tick) | "no farol, o mesmo cérebro que empata no táxi passa a diferenciar arquiteturas em ≥ 10 pp porque o mundo pune parar" | construir muito antes de medir; performance do servidor |
| **B. Régua/mundo novo no táxi** | vida GANHA por trabalho (não dada); demanda que cresce com serviço; custo fixo de existir > renda de parar | 1 dia (campo.py já tem os ganchos) | "com vida ganha, dirigir vira obrigatório e o bilinear-risco bate o linear ≥ 10 pp (a peça passa a pagar)" | é um portão desenhado à mão? Não: muda o que o mundo cobra, não o que o cérebro faz. Mas é o Leonardo quem decide se isso é 'natureza' ou 'muleta' |
| **C. Kernel HIP do tick** | tick fundido em wave32, sem 159 lançamentos | 2 dias | "≥ 3× no passo linear (2.0 → ≤ 0.7 ms)" | só vale se o táxi continuar bancada; não muda nenhuma conclusão científica |

**Recomendação:** B antes de A, um dia só, com predição registrada — porque a lição do dia (e da OpenAI em
Navier–Stokes: Euler antes de N–S) é que o degrau mais barato que muda o sinal vem antes do mundo grande. Se B
também empata, A vira obrigatório e a gente chega no farol sabendo que o problema não era a régua do táxi.

## O que já está pronto para qualquer porta
- Cérebro completo com portões de identidade/sensibilidade (`testes_*.py`), semeadura só em genes novos, ES e GA.
- Fila `nmd` (whitelist hot-reload; **todo pedido declara `env.NM_RISCO=1`**), régua pareada entre arquivos.
- Diagnósticos: `diag_oraculo.py` (autópsia), `diag_snr.py` (a régua enxerga?), `retrato_cerebro.py` (EEG/ablação).

## Disco (não mexi)
`/media/llm-data`: 8,8 GB livres de 90. Modelos 52 GB, venv 17 GB, runs 4,3 GB, datasets 3,2 GB. As baterias do
táxi somam poucos MB. Se precisar de espaço, a decisão é sobre os modelos (lista no relatório da sessão).
