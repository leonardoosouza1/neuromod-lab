#!/bin/bash
# Curvature census of procedural tracks over the FULL lap.
#
# `pista_check` prints only the first 600 m of arc unless `--ate` is given. On 15/09 a claim
# in the ledger ("it is not the radius: 8200's tightest curve is 21 m") was measured that way
# and was wrong: 8200 has a 12 m hairpin at 1 410 m, exactly where every rotation and
# random-start champion stops (ledger B3vc). This script reads the lap length first and then
# scans that lap, keeping only rows of the arc table (material column, arc multiple of 10).
#
#   scripts/track_census.sh 8005 $(seq 8100 5 8295) > /media/llm-data/scratch/track_radii.tsv
set -euo pipefail
PISTA_CHECK=${PISTA_CHECK:-$HOME/projects/LLM/Universe/target/release/pista_check}
echo -e "seed\tlap_m\tvalid\tmin_radius_m\tat_arc_m\tcurves_le_12m\tcurves_le_15m"
for s in "$@"; do
  head_txt=$(timeout 30 "$PISTA_CHECK" --seed "$s" 2>&1 || true)
  valid=yes; grep -q AVISO <<<"$head_txt" && valid=no
  lap=$(grep -oE "lap [0-9]+ m" <<<"$head_txt" | head -1 | grep -oE "[0-9]+" || true)
  [ -z "$lap" ] && { echo -e "$s\t-\t$valid\t-\t-\t-\t-"; continue; }
  timeout 30 "$PISTA_CHECK" --seed "$s" --ate "$lap" 2>/dev/null | awk -v s="$s" -v lap="$lap" -v v="$valid" '
    $2 ~ /^(Road|Grass|Wall|Hole)$/ && $1 ~ /^[0-9]+$/ && $1 % 10 == 0 {
      r = $5; sub("m$", "", r); r += 0
      if (min == "" || r < min) { min = r; at = $1 }
      if (r <= 12) a++; if (r <= 15) b++ }
    END { printf "%s\t%s\t%s\t%s\t%s\t%d\t%d\n", s, lap, v, min, at, a, b }'
done
