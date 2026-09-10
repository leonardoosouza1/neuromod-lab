#!/bin/bash
# Roda o observador DESTACADO do harness (o watchdog de memoria do Claude Code mata processos em background quando 'free' cai
# abaixo de ~1 GB, mesmo com 5 GB disponiveis). Cada alerta vai para _nmd/observador.alertas com hora; o supervisor (Fable) le
# esse arquivo em toda acordada. Depois de um alerta, espera INTERVALO e volta a vigiar.
SP=/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd; INTERVALO=${1:-600}; TRAVADO=${2:-1800}; AQUI=$(dirname "$0")
while true; do
  msg=$(bash "$AQUI/observador.sh" "$INTERVALO" "$TRAVADO"); rc=$?
  echo "$(date '+%d/%m %H:%M') rc=$rc $msg" >> "$SP/observador.alertas"
  sleep "$INTERVALO"
done
