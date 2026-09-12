#!/usr/bin/env python3
"""Prepara o par pareado do controle C; nunca executa uma bateria."""
import argparse
import copy
import json
import os
import shlex

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_CENARIO = os.path.join(REPO, "cenarios", "mundoC_cidade_da_vida.json")
PYTHON = "/home/leonardo/projects/LLM/.venv-rocm/bin/python"


def _positive(name, value, minimum=1):
    if value < minimum:
        raise ValueError(f"{name} deve ser >= {minimum}")


def valida(G, P, R, seeds):
    _positive("G", G)
    _positive("P", P, 2)
    _positive("R", R)
    if not seeds:
        raise ValueError("seeds não pode ser vazio")
    if len(set(seeds)) != len(seeds):
        raise ValueError("seeds devem ser distintos")


def prepara(base, G=5, P=16, R=1, seeds=(0, 1)):
    """Retorna (controle sem centragem, controle com centragem)."""
    valida(G, P, R, seeds)
    comuns = copy.deepcopy(base)
    comuns.setdefault("mundo", {})["corte_vivos"] = 0
    protocolo = comuns.setdefault("protocolo", {})
    protocolo.update({"G": G, "P": P, "R": R, "paciencia": 0,
                      "seeds": list(seeds), "seres_juntos": False})
    a = copy.deepcopy(comuns)
    b = copy.deepcopy(comuns)
    a["nome"] = "mundoC_controle_ativ_descentrada"
    b["nome"] = "mundoC_controle_ativ_centrada"
    a["predicao"] = "controle C: ativação sem centragem"
    b["predicao"] = "controle C: ativação centrada"
    a.setdefault("corpo", {})["ativ_centrada"] = False
    b.setdefault("corpo", {})["ativ_centrada"] = True
    return a, b


def comandos(paths, G, P, R, seeds, base, resultados=None):
    # Protocolo C usa explicitamente o layout rico (risco+ponto+retina).
    # NM_COMPILE=1 preserva o caminho otimizado da bateria longa; não executamos aqui.
    env = {"NM_RETINA": "1", "NM_REGIME": "0", "NM_RISCO": "1",
           "NM_PONTO": "1", "NM_COMPILE": "1", "HSA_OVERRIDE_GFX_VERSION": "10.3.0"}
    prefix = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
    common = [PYTHON, os.path.join(REPO, "src", "e43_campo.py"), "--cenario"]
    flags = ["--G", str(G), "--P", str(P), "--R", str(R), "--seeds"] + [str(s) for s in seeds]
    raiz_resultados = resultados or os.path.dirname(paths[0])
    variantes = ("e43_ativ_descentrada", "e43_ativ_centrada")
    return [prefix + " " + " ".join(shlex.quote(x) for x in common + [p] + flags + ["--out", out])
            for p, out in zip(paths, (os.path.join(raiz_resultados, v) for v in variantes))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="diretório novo para os cenários")
    ap.add_argument("--resultados", default="/media/llm-data/universe-runs/neuromod-lab-taxi/controle_c_fixo",
                    help="raiz dos resultados das baterias (não é o diretório dos cenários)")
    ap.add_argument("--base", default=BASE_CENARIO)
    ap.add_argument("--G", type=int, default=5)
    ap.add_argument("--P", type=int, default=16)
    ap.add_argument("--R", type=int, default=1)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    a = ap.parse_args(argv)
    try:
        with open(a.base, encoding="utf-8") as f:
            base = json.load(f)
        primeiro, segundo = prepara(base, a.G, a.P, a.R, a.seeds)
        os.makedirs(a.out, exist_ok=True)
        paths = [os.path.join(a.out, "mundoC_controle_ativ_descentrada.json"),
                 os.path.join(a.out, "mundoC_controle_ativ_centrada.json")]
        if any(os.path.exists(p) for p in paths):
            raise ValueError("não sobrescrevo JSON existente no diretório de saída")
        for path, data in zip(paths, (primeiro, segundo)):
            with open(path, "x", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("Comandos e43 (não executados):")
        for command in comandos(paths, a.G, a.P, a.R, a.seeds, base, a.resultados):
            print(command)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    main()
