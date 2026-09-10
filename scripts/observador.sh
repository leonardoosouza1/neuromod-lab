#!/bin/bash
# [10/09 Leonardo] OBSERVADOR de 10 min: checa a fila/GPU/RAM/logs e SAI (acordando o Fable) so quando algo esta errado.
# Deterministico, zero tokens. Codigos de saida: 2 daemon caiu | 3 portao/bateria exit!=0 | 4 RAM baixa | 5 VRAM alta | 6 Traceback novo | 7 job travado | 8 fila vazia e ociosa
SP=/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd; INTERVALO=${1:-600}; TRAVADO=${2:-1800}
last=$(wc -l < $SP/nmd.log); echo "$(date +%H:%M) observador iniciado (linha $last do nmd.log)" >> $SP/observador.log
while true; do
  sleep $INTERVALO
  pid=$(ps -eo pid,args | grep '[s]cripts/nmd.py' | awk '{print $1}' | head -1); [ -z "$pid" ] && { echo "ALERTA 2: daemon nmd caiu"; exit 2; }
  novas=$(tail -n +$((last+1)) $SP/nmd.log); last=$(wc -l < $SP/nmd.log)
  bad=$(echo "$novas" | grep "terminou" | grep -v "exit=0" | head -3); [ -n "$bad" ] && { echo "ALERTA 3: exit!=0 -> $bad"; exit 3; }
  avail=$(free -m | awk '/Mem/{print $7}'); [ "$avail" -lt 1500 ] && { echo "ALERTA 4: RAM disponivel $avail MB"; exit 4; }
  v=$(rocm-smi --showmemuse 2>/dev/null | grep -o 'VRAM%): [0-9]*' | grep -o '[0-9]*$' | head -1); [ "${v:-0}" -gt 85 ] && { echo "ALERTA 5: VRAM $v %"; exit 5; }
  tb=$(find $SP/log -mmin -$((INTERVALO/60+1)) -name '*.log' -exec grep -l "Traceback" {} \; 2>/dev/null | head -2 | tr '\n' ' '); [ -n "$tb" ] && { echo "ALERTA 6: Traceback em $tb"; exit 6; }
  ult=$(tail -1 $SP/nmd.log); run=$(echo "$ult" | grep -o 'rodando [^:]*' | awk '{print $2}')
  if [ -n "$run" ] && [ -f "$SP/log/$run.log" ]; then idade=$(( $(date +%s) - $(stat -c %Y "$SP/log/$run.log") )); [ $idade -gt $TRAVADO ] && { echo "ALERTA 7: $run sem escrever no log ha $idade s"; exit 7; }; fi
  npend=$(ls $SP/pedidos 2>/dev/null | wc -l); if [ "$npend" -eq 0 ] && [ -z "$run" ]; then echo "ALERTA 8: fila vazia e GPU ociosa (ultima linha: $ult)"; exit 8; fi
  echo "$(date +%H:%M) ok | rodando ${run:-nada} | pendentes $npend | RAM $avail MB | VRAM ${v:-?}%" >> $SP/observador.log
done
