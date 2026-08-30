#!/usr/bin/env python3
"""Bateria de taxis. Roda igual em CPU, GPU local ou Colab.

    python src/rodar.py --smoke               # teste de fumaca (segundos)
    python src/rodar.py --perito              # PORTAO de validacao (obrigatorio)
    python src/rodar.py --bateria             # bateria completa
    python src/rodar.py --bateria -P 8192 -G 100 -R 8
"""
import argparse, json, os, sys, time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, numpy as np
from lab import (DEV, GMAX, NPX, NF, gerar_cidade, Cfg, Lote, passo,
                 Reativo, BancoEMA, Diadica, Corpo, Hibrido, ARQS,
                 rodar, avaliar, evoluir)

NOMES_F = (['d_alvo','custo_rua','congestao','semaforo',
            'd_posto','d_comida','d_descanso','d_oficina','d_loja',
            'e_fuel','e_fome','e_fadiga','e_pneu','e_temp','e_oleo',
            'e_dinheiro','e_tem_pax','bias']
           + ['sv_posto','sv_comida','sv_descanso','sv_oficina','sv_loja','sv_bias']
           + [f'mem_{i}' for i in range(6)] + [f'corpo_{i}' for i in range(6)])


def perito_W(NP):
    """pesos escritos a mao — referencia humana. Memoria fica ZERADA de proposito."""
    w = torch.zeros(NP, device=DEV)
    w[0]=4.0; w[1]=0.6; w[2]=0.8; w[3]=1.2
    w[4]=1.2; w[5]=.10; w[6]=.05; w[7]=.60; w[8]=.05
    w[NF:NF+5] = torch.tensor([20.,14.,10.,18.,3.], device=DEV)
    w[NF+5] = -4.0
    return w


def limpar():
    import gc
    for _ in range(2):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def smoke():
    print('--- teste de fumaca ---')
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0)
    for A in ARQS:
        W = torch.randn(4, A.NP, device=DEV)*.8
        m = rodar(A, W, cids, cfg, T=150, seed=0)
        print(f'  {A.nome:<12} entregas {m.ent.mean():5.2f}  B={m.B}  OK')
    print('ok')


def portao(T=1200, n_cid=3, rep=16, R=2):
    """PORTAO OBRIGATORIO.

    Com os pesos de memoria zerados, as 5 arquiteturas sao a MESMA politica.
    Elas TEM que produzir resultado identico. Se divergirem, ha bug de porte
    (NaN silencioso, indice fora de faixa, gerador consumido em ordem diferente).
    Este teste pegou 5 bugs durante a migracao CPU -> GPU.
    """
    print('--- portao de validacao ---')
    cids = [gerar_cidade(s) for s in range(n_cid)]
    cfg = Cfg(1.0)
    print(f"  {'arquitetura':<12}{'PERITO':>9}{'aleatorio':>11}{'razao':>8}{'avarias':>9}")
    vals = []
    for A in ARQS:
        Wp = perito_W(A.NP)[None,:].repeat(rep,1)
        mp = rodar(A, Wp, cids, cfg, T=T, seed=1, R=R)
        Wr = torch.randn(rep, A.NP, device=DEV)*.8
        mr = rodar(A, Wr, cids, cfg, T=T, seed=1, R=R)
        ep, er = mp.ent.mean().item(), mr.ent.mean().item()
        av = mp.avar.mean().item()
        vals.append(ep)
        print(f'  {A.nome:<12}{ep:>9.1f}{er:>11.1f}{ep/max(er,.05):>7.1f}x{av:>9.1f}')
        limpar()
    ok = (max(vals) - min(vals)) < 0.05
    print(f"\n  {'PASSOU' if ok else 'FALHOU'}: as 5 "
          f"{'batem' if ok else 'DIVERGEM'} (spread {max(vals)-min(vals):.3f})")
    if not ok:
        print('  >>> bug de porte. NAO rode a bateria.')
    return ok


def paisagem(Arq, w, cidades, cfg, T=400, R=2, passos=9, raio=1.5):
    """Perturba CADA peso em 9 pontos -> revela os VALES e PICOS de f(w).
    Tudo num batch so: (NP*9) genomas avaliados de uma vez."""
    NPw = w.shape[0]
    d = torch.linspace(-raio, raio, passos, device=DEV)
    Wp = w[None,None,:].repeat(NPw, passos, 1)
    ii = torch.arange(NPw, device=DEV)[:,None].expand(-1,passos)
    jj = torch.arange(passos, device=DEV)[None,:].expand(NPw,-1)
    Wp[ii, jj, ii] = w[ii] + d[None,:]
    f = avaliar(Arq, Wp.reshape(NPw*passos, NPw), cidades, cfg, T, seed=555, R=R)
    return dict(deltas=[round(x,3) for x in d.tolist()],
                curvas=[[round(x,4) for x in l] for l in f.view(NPw,passos).tolist()])


def trajetoria(Arq, w, cidades, cfg, T=1500, amostras=200):
    """Serie temporal de UM mundo: como o corpo e o dinheiro evoluem."""
    m = Lote(cidades[:1], 1, cfg, seed=4242, R=1)
    Wb = w[None,:].repeat(m.B,1)
    a = Arq(); a.reset(m, Wb)
    pa = max(1, T//amostras); buf = []
    for t in range(T):
        F, val = m.obs(); viz = m.A_().clamp(min=0)
        s = (torch.einsum('bgf,bf->bg', F, Wb[:,:NF])
             + a.extra(m, Wb, viz)).masked_fill(~val, -1e9)
        svn, sv = m.serv_need()
        ss = (svn*Wb[:,NF:NF+5] + Wb[:,NF+5:NF+6]).masked_fill(sv<=0, -1e9)
        passo(m, torch.cat([s,ss],1).argmax(1))
        if t % pa == 0:
            buf.append(torch.stack([m.fuel[0], m.fome[0], m.fad[0], m.pneu[0],
                                    m.temp[0], m.oleo[0], m.dinh[0], m.ent[0],
                                    m.avar[0], m.no[0].float(),
                                    (m.pd_[0] >= 0).float()]))
    M = torch.stack(buf)
    ks = ['fuel','fome','fadiga','pneu','temp','oleo','dinheiro',
          'entregas','avarias','no','tem_pax']
    return {k: [round(x,2) for x in M[:,i].tolist()] for i,k in enumerate(ks)}


def bateria(P, GER, R, T_EVO, T, n_treino, n_teste, seeds, saida_dir, seed_evo=0):
    treino = [gerar_cidade(s) for s in range(n_treino)]
    teste  = [gerar_cidade(1000+s) for s in range(n_teste)]
    cfg = Cfg(1.0, trafego=.35, imposto=.18)
    print(f'mundos/geracao: {P*n_treino*R:,} | por genoma: {n_treino*R}')

    if torch.cuda.is_available():
        limpar(); torch.cuda.reset_peak_memory_stats()
        _ = rodar(Hibrido, torch.randn(P, Hibrido.NP, device=DEV),
                  treino, cfg, T=5, seed=0, R=R)
        pico = torch.cuda.max_memory_allocated()/1e9
        tot = torch.cuda.get_device_properties(0).total_memory/1e9
        print(f'memoria: {pico:.2f} de {tot:.1f} GB ({pico/tot*100:.0f}%)')
        del _; limpar()
        if pico > tot*0.8:
            sys.exit(f'REDUZA P (sugestao {int(P*tot*0.7/pico)})')
        print(f'cabe ate P ~= {int(P*tot*0.7/max(pico,1e-6)):,}')

    res = {}; t0 = time.time()
    for Arq in ARQS:
        print(f'\n=== {Arq.nome} ({Arq.NP} params) ===')
        ta = time.time()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        w, hist, snaps = evoluir(Arq, treino, cfg, P, GER, T_EVO, R=R,
                                seed=seed_evo)

        m = rodar(Arq, w[None,:].repeat(seeds,1), teste, cfg, T, seed=7777, R=1)
        ent, avr, ups = m.ent, m.avar, m.up
        rec, imp, din = m.rec, m.imp, m.dinh
        q = torch.tensor([0,.10,.25,.50,.75,.90,1.0], device=DEV)
        lo, hi = float(ent.min()), float(ent.max())
        hb = torch.histc(ent, bins=20, min=lo, max=max(hi, lo+1e-3))
        est = dict(
            params=int(Arq.NP), hist=hist, snapshots=snaps,
            pesos_finais=[round(x,4) for x in w.tolist()],
            nomes_pesos=NOMES_F[:Arq.NP],
            entregas=dict(media=round(float(ent.mean()),3),
                          dp=round(float(ent.std()),3),
                          percentis=[round(x,2) for x in torch.quantile(ent,q).tolist()],
                          histograma=[int(x) for x in hb.tolist()],
                          hist_min=round(lo,2), hist_max=round(hi,2)),
            avarias=dict(media=round(float(avr.mean()),3),
                         dp=round(float(avr.std()),3)),
            upgrades=dict(media=round(float(ups.sum(1).mean()),3),
                          por_tipo=[round(x,3) for x in ups.mean(0).tolist()]),
            receita=dict(media=round(float(rec.mean()),2),
                         imposto=round(float(imp.mean()),2),
                         dinheiro_final=round(float(din.mean()),2)),
            n_amostras=int(ent.numel()))
        del m; limpar()

        print('  paisagem...')
        est['paisagem'] = paisagem(Arq, w, treino[:2], cfg); limpar()
        print('  trajetoria...')
        est['trajetoria'] = trajetoria(Arq, w, teste, cfg, T=T); limpar()

        est['tempo_s'] = round(time.time()-ta, 1)
        est['vram_pico_gb'] = (round(torch.cuda.max_memory_allocated()/1e9, 2)
                               if torch.cuda.is_available() else 0)
        res[Arq.nome] = est
        print(f"  -> {est['entregas']['media']:.1f} +- {est['entregas']['dp']:.1f} "
              f"entregas ({est['n_amostras']} amostras, {est['tempo_s']:.0f}s)")

    print(f'\nTOTAL: {time.time()-t0:.0f}s')
    os.makedirs(saida_dir, exist_ok=True)
    out = dict(
        data=datetime.now().isoformat(),
        config=dict(P=P, R=R, geracoes=GER, T_evo=T_EVO, T_aval=T,
                    cidades_treino=n_treino, cidades_teste=n_teste, seeds=seeds,
                    mundos_por_geracao=P*n_treino*R, mundos_por_genoma=n_treino*R,
                    dificuldade=1.0, trafego=.35, imposto=.18),
        dispositivo=(torch.cuda.get_device_name(0)
                     if torch.cuda.is_available() else 'cpu'),
        resultados=res)
    cam = os.path.join(saida_dir, f'resultado-taxi-{datetime.now():%Y%m%d-%H%M}.json')
    with open(cam, 'w') as f:
        json.dump(out, f)
    print('salvo:', cam, '|', round(os.path.getsize(cam)/1e6, 2), 'MB')
    print('\nRESUMO:')
    for k, v in sorted(res.items(), key=lambda x: -x[1]['entregas']['media']):
        print(f"  {k:<12}{v['entregas']['media']:>7.1f} +- "
              f"{v['entregas']['dp']:>5.1f}  avarias {v['avarias']['media']:>5.1f}  "
              f"upg {v['upgrades']['media']:>4.1f}  ({v['params']} par)")
    return cam


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--smoke',   action='store_true', help='teste rapido')
    ap.add_argument('--perito',  action='store_true', help='portao de validacao')
    ap.add_argument('--bateria', action='store_true', help='bateria completa')
    ap.add_argument('-P', type=int, default=2048, help='populacao')
    ap.add_argument('-G', '--geracoes', type=int, default=60)
    ap.add_argument('-R', type=int, default=8, help='replicas por genoma')
    ap.add_argument('--tevo',  type=int, default=600)
    ap.add_argument('--taval', type=int, default=1500)
    ap.add_argument('--treino', type=int, default=8)
    ap.add_argument('--teste',  type=int, default=6)
    ap.add_argument('--seeds',  type=int, default=512)
    # I4: a evolucao rodava SEMPRE com seed 0 — uma unica corrida evolutiva por
    # arquitetura. Rode a bateria com --seed-evo 0/1/2 e compare: diferenca
    # entre sementes e o ruido de base; efeito menor que isso nao e efeito.
    ap.add_argument('--seed-evo', type=int, default=0, dest='seed_evo')
    ap.add_argument('--out', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resultados'))
    a = ap.parse_args()

    print(f'dispositivo: {DEV}')
    if torch.cuda.is_available():
        print('GPU:', torch.cuda.get_device_name(0),
              f'| {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB')

    if a.smoke:
        smoke()
    if a.perito:
        portao()
    if a.bateria:
        if not portao():
            sys.exit('portao falhou — corrija antes de rodar a bateria')
        bateria(a.P, a.geracoes, a.R, a.tevo, a.taval,
                a.treino, a.teste, a.seeds, a.out, seed_evo=a.seed_evo)
    if not (a.smoke or a.perito or a.bateria):
        ap.print_help()
