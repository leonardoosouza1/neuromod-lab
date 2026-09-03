#!/bin/bash
# scripts/fila.sh — fila genérica de baterias (E18, doc 28 §1 / doc 32-avaliacao.md)
#
# Padroniza o que era feito à mão em
# /media/llm-data/universe-runs/neuromod-lab-taxi/fila_e13*.sh: roda uma
# sequência de etapas, cada uma virando um `<tag>.log` + `<tag>.done`, e no
# fim grava `<nome-da-fila>_TUDO.done`. Serve de "semáforo" pra encadear
# filas (--depois-de) sem precisar de cron nem de um processo orquestrador —
# um `until [ -f ... ]; do sleep; done` simples, igual ao que já se fazia.
#
# USO
#   scripts/fila.sh <arquivo_de_fila> [--out DIR] [--depois-de ARQUIVO.done]
#
# ARQUIVO DE FILA (1 etapa por linha, campos separados por " | "):
#   tag | comando shell completo
#
#   Linhas em branco e linhas começando com # são ignoradas. O comando roda
#   via `bash -c`, então pode ter pipes, redirecionamentos extras, `&&` etc.
#   — mas normalmente é só uma chamada de python (ver scripts/exemplo_fila.txt).
#
# SAÍDA (em --out, default /media/llm-data/universe-runs/neuromod-lab-taxi/e18):
#   <out>/<tag>.log            stdout+stderr da etapa
#   <out>/<tag>.done           grava "FIM <status>" quando a etapa termina
#                               (grava mesmo se a etapa falhar — não trava
#                               quem espera; olhe o .log e o status no .done
#                               pra saber se deu certo)
#   <out>/<fila>_TUDO.done     grava no fim de TODAS as etapas (<fila> = nome
#                               do arquivo de fila sem extensão)
#
# ENCADEAR FILAS: `--depois-de ARQUIVO.done` espera esse arquivo existir
# ANTES de rodar a 1ª etapa (poll a cada 5s) — mesmo padrão usado à mão em
# fila_e13l.sh (`until [ -f $O/e13_fila_TUDO.done ]; do sleep 5; done`).
#
# EXEMPLO
#   scripts/fila.sh scripts/exemplo_fila.txt
#   scripts/fila.sh minha_fila2.txt --depois-de /media/.../e18/exemplo_fila_TUDO.done
set -u

DEFAULT_OUT=/media/llm-data/universe-runs/neuromod-lab-taxi/e18

FILA=''
OUT="$DEFAULT_OUT"
DEPOIS_DE=''

while [ $# -gt 0 ]; do
    case "$1" in
        --out) OUT="$2"; shift 2 ;;
        --depois-de) DEPOIS_DE="$2"; shift 2 ;;
        -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
        *)
            if [ -z "$FILA" ]; then FILA="$1"; shift
            else echo "argumento inesperado: $1" >&2; exit 2; fi
            ;;
    esac
done

if [ -z "$FILA" ]; then
    echo "uso: scripts/fila.sh <arquivo_de_fila> [--out DIR] [--depois-de ARQUIVO.done]" >&2
    exit 2
fi
if [ ! -f "$FILA" ]; then
    echo "arquivo de fila não existe: $FILA" >&2
    exit 2
fi

mkdir -p "$OUT"
NOME_FILA=$(basename "$FILA"); NOME_FILA="${NOME_FILA%.*}"

if [ -n "$DEPOIS_DE" ]; then
    echo "[fila.sh] esperando $DEPOIS_DE ..."
    until [ -f "$DEPOIS_DE" ]; do sleep 5; done
    echo "[fila.sh] $DEPOIS_DE apareceu, começando"
fi

N=0
while IFS= read -r linha || [ -n "$linha" ]; do
    # ignora linha em branco/comentário
    case "$linha" in
        ''|'#'*) continue ;;
    esac
    tag="${linha%%|*}"
    cmd="${linha#*|}"
    tag="$(echo "$tag" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    cmd="$(echo "$cmd" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [ -z "$tag" ] || [ -z "$cmd" ]; then
        echo "[fila.sh] linha mal formada (esperado 'tag | comando'): $linha" >&2
        continue
    fi
    N=$((N+1))
    log="$OUT/$tag.log"
    done_file="$OUT/$tag.done"
    if [ -f "$done_file" ] && grep -q "status=0" "$done_file" 2>/dev/null; then   # RETOMADA: etapa ja feita (ex.: PC desligou no meio)
        echo "[fila.sh] etapa '$tag' ja concluida ($done_file) — pulando"; continue
    fi
    echo "[fila.sh] ($N) $tag :: $cmd"
    t0=$(date +%s)
    bash -c "$cmd" > "$log" 2>&1
    status=$?
    dt=$(( $(date +%s) - t0 ))
    echo "FIM status=$status ${dt}s $(date -Iseconds)" > "$done_file"
    if [ $status -ne 0 ]; then
        echo "[fila.sh] AVISO: '$tag' terminou com status $status (${dt}s) — ver $log" >&2
    else
        echo "[fila.sh] ok: $tag (${dt}s)"
    fi
done < "$FILA"

echo FIM > "$OUT/${NOME_FILA}_TUDO.done"
echo "[fila.sh] fila '$NOME_FILA' completa ($N etapas) -> $OUT/${NOME_FILA}_TUDO.done"
