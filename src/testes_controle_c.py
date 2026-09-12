#!/usr/bin/env python3
"""Testes stdlib da preparação do controle C."""
import copy
import json
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import prepara_controle_c as pc


def main():
    base = json.loads((ROOT / "cenarios/mundoC_cidade_da_vida.json").read_text())
    original = copy.deepcopy(base)
    a, b = pc.prepara(base)
    assert base == original
    assert a["mundo"]["corte_vivos"] == b["mundo"]["corte_vivos"] == 0
    assert a["protocolo"]["paciencia"] == b["protocolo"]["paciencia"] == 0
    assert (a["protocolo"]["G"], a["protocolo"]["P"], a["protocolo"]["R"], a["protocolo"]["seeds"]) == (5, 16, 1, [0, 1])
    assert a["protocolo"]["seres_juntos"] is b["protocolo"]["seres_juntos"] is False
    assert a["corpo"]["ativ_centrada"] is False and b["corpo"]["ativ_centrada"] is True
    aa, bb = copy.deepcopy(a), copy.deepcopy(b)
    aa.pop("nome"); bb.pop("nome"); aa.pop("predicao"); bb.pop("predicao")
    aa["corpo"].pop("ativ_centrada"); bb["corpo"].pop("ativ_centrada")
    assert aa == bb
    for args in ((0, 16, 1, [0, 1]), (5, 1, 1, [0, 1]), (5, 16, 0, [0, 1]), (5, 16, 1, [0, 0])):
        try: pc.prepara(base, *args)
        except ValueError: pass
        else: raise AssertionError("valor inválido aceito")
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "dir with spaces"
        resultados = Path(d) / "resultados com espaços"
        cmd = [sys.executable, str(ROOT / "scripts/prepara_controle_c.py"), "--out", str(out)]
        r = subprocess.run(cmd, text=True, capture_output=True, check=True)
        assert "não executados" in r.stdout and len(list(out.glob("*.json"))) == 2
        comandos = pc.comandos(
            [str(out / "mundoC_controle_ativ_descentrada.json"),
             str(out / "mundoC_controle_ativ_centrada.json")], 5, 16, 1, [0, 1], base, str(resultados))
        assert len(comandos) == 2 and comandos[0] != comandos[1]
        parsed = [shlex.split(c) for c in comandos]
        for argv in parsed:
            assert "NM_RETINA=1" in argv and "NM_RISCO=1" in argv
            assert "NM_PONTO=1" in argv and "NM_COMPILE=1" in argv
            assert "HSA_OVERRIDE_GFX_VERSION=10.3.0" in argv
            assert "--G" in argv and argv[argv.index("--G") + 1] == "5"
            assert "--P" in argv and argv[argv.index("--P") + 1] == "16"
            assert "--R" in argv and argv[argv.index("--R") + 1] == "1"
            assert argv[argv.index("--out") + 1].endswith(("e43_ativ_descentrada", "e43_ativ_centrada"))
            assert any("dir with spaces" in item for item in argv)
            assert any("resultados com espaços" in item for item in argv)
        assert parsed[0][parsed[0].index("--out") + 1] != parsed[1][parsed[1].index("--out") + 1]
        r = subprocess.run(cmd, text=True, capture_output=True)
        assert r.returncode != 0
    relativos = pc.comandos(['cenarios/a.json', 'cenarios/b.json'], 5, 16, 1,
                            [0, 1], base, 'resultados')
    saidas = [shlex.split(c)[shlex.split(c).index('--out') + 1] for c in relativos]
    assert saidas == ['resultados/e43_ativ_descentrada', 'resultados/e43_ativ_centrada']
    print("testes_controle_c: todos passaram")


if __name__ == "__main__":
    main()
