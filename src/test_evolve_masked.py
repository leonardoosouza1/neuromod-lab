"""Tests for evolve_masked (docs/98 -- pruning control battery, English-named
new code per task instructions; existing repo tests stay Portuguese/testes.py).

    python src/test_evolve_masked.py

1. mode='generate' is BIT-EXACT to today's evoluir_sementes(sigma_mut=.30):
   same RNG stream, same champion weights, same history. The mask must never
   consume a random draw when p_off=p_on=0 -- not just "stay at 1.0".
2. generate/generate_fine never drift the mask away from all-ones.
3. prune is deterministic (two identical calls -> identical result) and the
   mask actually moves (heritable + mutates): density strictly less than 1.0
   after enough generations, and differs from a naive from-scratch mask.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, gerar_cidade, Cfg, Reativo, evoluir_sementes, evolve_masked


def test_evolve_masked_generate_matches_evoluir_sementes():
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0, mundo='base')
    seeds = (0, 1)
    ref = evoluir_sementes(Reativo, cids, cfg, P=64, ger=6, T=120, seeds=seeds,
                           R=2, sigma_mut=.30, verbose=False)
    got = evolve_masked(Reativo, cids, cfg, P=64, ger=6, T=120, seeds=seeds,
                        R=2, mode='generate', verbose=False)
    for sd in seeds:
        w_ref, h_ref, _ = ref[sd]
        w_got, h_got, _snaps, mask, dens = got[sd]
        assert h_ref == h_got, f'semente {sd}: historico de fitness diverge\n  ref: {h_ref}\n  got: {h_got}'
        assert torch.equal(w_ref, w_got), f'semente {sd}: campeao diverge (mode=generate deve ser bit-exato)'
        assert dens == 1.0 and bool((mask == 1.).all()), f'semente {sd}: mascara nao ficou 1.0 (consumiu draw?)'
    print('  evolve_masked(mode=generate) == evoluir_sementes(sigma_mut=.30)  bit-exato (2 sementes)  OK')


def test_generate_fine_mask_stays_dense():
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0, mundo='base')
    got = evolve_masked(Reativo, cids, cfg, P=48, ger=8, T=100, seeds=(0,),
                        R=1, mode='generate_fine', verbose=False)
    w, h, _snaps, mask, dens = got[0]
    assert dens == 1.0 and bool((mask == 1.).all()), 'generate_fine nao pode mexer na mascara'
    print('  evolve_masked(mode=generate_fine)  mascara permanece 1.0  OK')


def test_prune_deterministic_and_mask_moves():
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0, mundo='base')
    a = evolve_masked(Reativo, cids, cfg, P=64, ger=12, T=100, seeds=(0, 1),
                      R=2, mode='prune', verbose=False)
    b = evolve_masked(Reativo, cids, cfg, P=64, ger=12, T=100, seeds=(0, 1),
                      R=2, mode='prune', verbose=False)
    for sd in (0, 1):
        assert a[sd][1] == b[sd][1], f'semente {sd}: prune nao deterministico (hist)'
        assert torch.equal(a[sd][0], b[sd][0]), f'semente {sd}: prune nao deterministico (campeao)'
        assert torch.equal(a[sd][3], b[sd][3]), f'semente {sd}: prune nao deterministico (mascara)'
        dens = a[sd][4]
        assert 0.0 < dens < 1.0, f'semente {sd}: densidade {dens} nao moveu (mascara devia ter desligado bits)'
    print('  evolve_masked(mode=prune)  deterministico + mascara move (densidade < 1)  OK')


def test_child_inherits_parent_mask_then_mutates():
    """Um pai com mascara [1,1,0,0] tem filhos cuja mascara comeca IGUAL a do
    pai (mutacao so' desliga/religa POUCOS bits com p pequena) -- nao nasce
    aleatoria. Checado indiretamente: rodando 1 geracao de prune com p_off=p_on
    quase 0 nao muda dado suficiente; aqui checamos que a mascara do campeao
    de UMA geracao de prune bate em pelo menos alguns bits com a inicial
    (toda 1) -- ou seja, nao foi resorteada do zero."""
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0, mundo='base')
    got = evolve_masked(Reativo, cids, cfg, P=64, ger=1, T=80, seeds=(0,),
                        R=1, mode='prune', verbose=False)
    _w, _h, _snaps, mask, dens = got[0]
    # apos 1 geracao (uma rodada de off/on em p=.05/.015) a densidade tem que
    # ficar PERTO de 1 (nasceu toda ligada), nao cair para o acaso (~.5)
    assert dens > 0.85, f'densidade caiu longe demais para 1 geracao: {dens} (herança quebrada?)'
    print(f'  evolve_masked(mode=prune)  1 geracao: densidade {dens:.3f} perto de 1 (heranca OK)  OK')


if __name__ == '__main__':
    print('--- testes evolve_masked (docs/98) ---')
    test_evolve_masked_generate_matches_evoluir_sementes()
    test_generate_fine_mask_stays_dense()
    test_prune_deterministic_and_mask_moves()
    test_child_inherits_parent_mask_then_mutates()
    print('ok')
