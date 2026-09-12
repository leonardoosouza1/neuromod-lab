"""Smoke real em GPU: dois ticks, duas cópias, duas sementes; sem evolução."""
import os
os.environ['NM_COMPILE'] = '0'
os.environ['NM_RISCO'] = '1'
os.environ['NM_PONTO'] = '1'
os.environ['NM_RETINA'] = '0'
os.environ['NM_REGIME'] = '0'
import torch
from campo import CfgCampo, Linear, gerar_mapa, rodar, G, ACOES
from politica_util import mede, traco


def main():
    assert torch.cuda.is_available(), 'este smoke exige GPU real'
    cfg = CfgCampo(L=200., fitness='vida')
    cfg.corte_vivos = 1.
    cfg.jardim_comum = True
    cfg.horizonte = 'aberto'
    cfg.T_max = 2
    mapas = [gerar_mapa(1000, L=200.)]
    W = torch.zeros(Linear.NP, device='cuda')
    resultado = mede(Linear, W, cfg, mapas, 2, [11, 13], copias=2)
    assert cfg.corte_vivos == 1. and cfg.jardim_comum is True
    assert resultado['mortos'] == 0.
    assert abs(resultado['t_vida_media'] - 2/240) < 1e-7
    assert resultado['frac_teto'] == 1.
    assert resultado['dia_morte'] == 2/240  # fallback legado respeita horizonte
    esperado = resultado['t_vida_media'] + cfg.w_trab*resultado['rec']/300
    assert abs(resultado['fit'] - esperado) < 1e-6
    assert len(resultado['fit_por_semente']) == 2

    class Misto(Linear):
        def reset(self, m, w):
            super().reset(m, w)
            m.vida[0] = 0.

    misto = mede(Misto, W, cfg, mapas, 2, [11], copias=2)
    assert misto['mortos'] == .5 and misto['frac_teto'] == .5
    assert misto['dia_morte'] == 0.
    assert abs(misto['t_vida_media'] - 1/240) < 1e-7

    cfg.corte_vivos = 0.; cfg.jardim_comum = False
    cfg.temp_decisao = .7
    cfg.grava_acoes = True
    W = torch.linspace(-1, 1, Linear.NP, device='cuda')
    canonico = rodar(Linear, W[None, :].repeat(2, 1), mapas, cfg, 3, 17)
    hist = traco(Linear, W, cfg, mapas, T=3, B=2, seed=17)
    vivos = canonico.traj[:, :, 6] > 0
    contagem = torch.bincount(canonico.acoes[vivos], minlength=G + len(ACOES)).float()
    freq = (contagem/contagem.sum()).tolist()
    assert abs(hist['mover'] - sum(freq[:G-1])) < 1e-6
    assert abs(hist['ficar_no_raio'] + hist['ficar_fora'] - freq[G-1]) < 1e-6
    for k, (tipo, q) in enumerate(ACOES):
        assert abs(hist[f'{tipo}{int(q) if q else ""}'] - freq[G+k]) < 1e-6
    print('testes_metricas_juiz: GPU real, todos passaram')


if __name__ == '__main__':
    main()
