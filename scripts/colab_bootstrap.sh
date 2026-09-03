#!/usr/bin/env bash
# Bootstrap do neuromod-lab num runtime do Google Colab (GPU CUDA). Uso dentro de uma célula:
#   %env GH_TOKEN=<token>   (repo privado)
#   !bash colab_bootstrap.sh e29b_reacoes.py --preset honesto --pena 5 --tag _colab   (o arquivo sobe pelo colab-mcp)
# Saidas em /content/out (JSON + log). Nao e bit-igual a maquina local (GPU diferente): comparar SO dentro do Colab.
set -euo pipefail
cd /content
# repo e PRIVADO: precisa de token (Colab: Secrets -> GH_TOKEN, ou export GH_TOKEN=... na celula). Sem token, use o upload do src/ pelo colab-mcp.
URL="https://${GH_TOKEN:+${GH_TOKEN}@}github.com/leonardoosouza1/neuromod-lab.git"
[ -d neuromod-lab ] || git clone -q "$URL"
cd neuromod-lab && git pull -q
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
mkdir -p /content/out
SCRIPT="${1:-e29b_reacoes.py}"; shift || true
NM_COMPILE=${NM_COMPILE:-1} python "src/$SCRIPT" --out /content/out "$@" 2>&1 | grep -v Warning | tee "/content/out/$(basename "$SCRIPT" .py).log"
ls -la /content/out
