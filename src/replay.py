"""Grava um EPISODIO INTEIRO tick a tick para o olho ver o que o log esconde.

Licao do Universe (volante cravado): metrica agregada dizia "andando", o olho
via circulo eterno. Este script usa a MESMA politica do rodar() oficial
(um_passo), so que com B=1 e gravando tudo — posicao, transito, corpo,
passageiros, escolha, entrega. E mede as metricas de volta-no-lugar.
"""
import json, sys, torch, os
sys.path.insert(0,'src')
os.environ.setdefault('NM_COMPILE','0')          # B=1: eager, sem compile
from lab import (DEV, NF, GMAX, NPX, gerar_cidade, Cfg, Lote, um_passo, ARQS)
POR_NOME = {A.nome: A for A in ARQS}

def grava(nome_arq, pesos, mundo, seed, T=1500):
    Arq = POR_NOME[nome_arq]
    cid = gerar_cidade(1000)                     # cidade 0 do conjunto de TESTE
    cfg = Cfg(1.0, mundo=mundo)
    W = torch.tensor(pesos, device=DEV, dtype=torch.float32)[None,:]
    m = Lote([cid], 1, cfg, seed=seed, R=1)
    a = Arq(); a.reset(m, W)
    fr = []
    ent_ant = 0.
    for t in range(T):
        # escolha (reproduz um_passo, mas capturando esc)
        F, val = m.obs(); viz = m.A_().clamp(min=0)
        sc = torch.einsum('bgf,bf->bg', F, W[:,:NF]) + a.extra(m, W, viz)
        sc = sc.masked_fill(~val, -1e9)
        svn, sv = m.serv_need()
        ss = (svn*W[:,NF:NF+5] + W[:,NF+5:NF+6]).masked_fill(sv<=0, -1e9)
        tudo = torch.cat([sc, ss],1)
        esc = a.decidir(tudo, m) if hasattr(a,'decidir') else tudo.argmax(1)
        from lab import passo
        passo(m, esc)
        if hasattr(a,'atualizar'): a.atualizar(m)
        e = float(m.ent[0])
        fr.append(dict(
            t=t, no=int(m.no[0]), indo=int(m.indo[0]), rest=float(m.rest[0]),
            par=float(m.tpar[0]), esc=int(esc[0]),
            po=[int(x) for x in m.po[0]], pd_=int(m.pd_[0]), po_=int(m.po_[0]),
            corpo=[round(float(x),1) for x in
                   (m.fuel[0], m.fome[0], m.fad[0], m.pneu[0], m.temp[0], m.oleo[0])],
            dinh=round(float(m.dinh[0]),1), ent=e, entregou=e>ent_ant,
            avar=float(m.avar[0])))
        ent_ant = e
    # metricas de VOLTA NO LUGAR
    nos = [f['no'] for f in fr]
    unicos = len(set(nos))
    janela = 60
    piores = 0
    for i in range(0, len(nos)-janela, janela//2):
        piores = max(piores, 1 - len(set(nos[i:i+janela]))/janela)
    censo = {k: float(getattr(m,k)[0]) for k in
             ('av_fuel','av_furo','av_oleo','av_quente','par_fad')}
    return dict(arq=nome_arq, mundo=mundo, T=T, censo=censo,
                cidade=dict(pos=[[round(float(x),3) for x in p] for p in cid['pos']],
                            A=cid['A'].tolist(), W=cid['W'].tolist(),
                            serv=cid['serv'].tolist()),
                frames=fr,
                loops=dict(nos_unicos=unicos, n_nos=int(cid['n']),
                           max_frac_repetida_60=round(piores,3)))

if __name__ == '__main__':
    d0 = json.load(open('resultados/resultado-taxi-base-s2-20260831-1314.json'))
    d1 = json.load(open('resultados/resultado-taxi-semgps-s0-20260831-2108.json'))
    eps = []
    for (dj, mundo, nome) in [(d0,'base','reativo'), (d0,'base','banco EMA'),
                              (d1,'semgps','hibrido'), (d1,'semgps','reativo')]:
        w = dj['resultados'][nome]['pesos_finais']
        ep = grava(nome, w, mundo, seed=31)
        print(f"{nome:>10} @{mundo}: entregas {ep['frames'][-1]['ent']:.0f} | "
              f"nós únicos {ep['loops']['nos_unicos']}/26 | "
              f"pior janela 60: {ep['loops']['max_frac_repetida_60']*100:.0f}% repetida")
        eps.append(ep)
    json.dump(eps, open('resultados/replay.json','w'))
    print('-> resultados/replay.json', os.path.getsize('resultados/replay.json')//1024, 'KB')
