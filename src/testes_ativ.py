"""[spec Mundo Vivo F2] test_custo_identidade: (a) existencia == caminho de antes; (b) modo ativacao com lambda 0 == existencia bit a bit (os caches
nao mudam a matematica). test_custo_ativacao_gene_morto: hipocampo com pesos ENORMES mas ganho 0 (sinal sempre zero) custa cheio em
'existencia' e ~0 em 'ativacao'. test_metab_monotono: dobrar lambda dobra (metab-1)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from campo import _fit; from completo import SerCompleto, nomes_genes_completos
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
W = torch.randn(32, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(32, Linear.NP, generator=g, device=DEV)*.5
def cfg(modo, lam, centrada=False):
    c = CfgCampo(L=200., fitness='riqueza'); c.custo_modo = modo; c.custo_gene = lam; c.ativ_centrada = centrada; return c
def test_custo_identidade():
    m0 = rodar(SerCompleto, W, mapas, cfg('existencia', 0.), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W, mapas, cfg('ativacao', 0.), T=200, seed=3, R=1)
    ok = torch.equal(m0.pos, m1.pos) and torch.equal(m0.vida, m1.vida) and torch.equal(m0.fome, m1.fome); print('test_custo_identidade (ativacao lam 0 == existencia lam 0, bit a bit):', ok, flush=True); assert ok
    m2 = rodar(SerCompleto, W, mapas, cfg('existencia', .3), T=200, seed=3, R=1); print('  existencia lam .3: metab medio', round(float(m2.metab.mean()), 3), '(> 1 = custo cobrado como antes)', flush=True); assert float(m2.metab.mean()) > 1.
def test_custo_ativacao_gene_morto():
    nomes = nomes_genes_completos(); Wd = torch.zeros(32, SerCompleto.NP, device=DEV); Wd[:, :Linear.NP] = W[:, :Linear.NP]
    o = SerCompleto.O_HIP; Wd[:, o+1] = 0.   # hip_ganho = 0 -> tanh(0) = 0: memoria SEMPRE zero
    ih = [i for i, n in enumerate(nomes) if n.startswith('hipM')]; Wd[:, Linear.NP + torch.tensor(ih, device=DEV)] = 3.   # 87 genes de M_h com peso 3 (bem acima de gene_min) mas sinal morto
    me = rodar(SerCompleto, Wd, mapas, cfg('existencia', .3), T=200, seed=3, R=1); ma = rodar(SerCompleto, Wd, mapas, cfg('ativacao', .3), T=200, seed=3, R=1)
    e, a = float(me.metab.mean()), float(ma.metab.mean()); print(f'test_custo_ativacao_gene_morto: metab existencia {e:.3f} (cobra os 87 genes mortos) vs ativacao {a:.3f} (~1.0)', 'OK' if e > 1.2 and a < 1.02 else 'FALHOU', '| ativacao_bloco hip', round(float((ma.ativ_soma['hip']/ma.ativ_n).mean()), 4), flush=True)
    assert e > 1.2 and a < 1.02
def test_metab_monotono():
    m1 = rodar(SerCompleto, W, mapas, cfg('ativacao', .3), T=200, seed=3, R=1); m2 = rodar(SerCompleto, W, mapas, cfg('ativacao', .6), T=200, seed=3, R=1)
    r = float((m2.metab - 1.).mean())/max(float((m1.metab - 1.).mean()), 1e-9); print(f'test_metab_monotono: (metab-1) lam .6 / lam .3 = {r:.3f} (esperado 2.0)', 'OK' if abs(r - 2.) < .05 else 'FALHOU', '| ativacao_bloco:', {b: round(float((v/m1.ativ_n).mean()), 3) for b, v in m1.ativ_soma.items()}, flush=True); assert abs(r - 2.) < .05
def test_basal_impede_catatonia():
    nomes = nomes_genes_completos(); Wd = torch.zeros(32, SerCompleto.NP, device=DEV); Wd[:, :Linear.NP] = W[:, :Linear.NP]; Wd[:, SerCompleto.O_HIP+1] = 0.
    ih = [i for i, n in enumerate(nomes) if n.startswith('hipM')]; Wd[:, Linear.NP + torch.tensor(ih, device=DEV)] = 3.
    W0 = torch.zeros(32, SerCompleto.NP, device=DEV); W0[:, :Linear.NP] = W[:, :Linear.NP]
    c1 = cfg('ativacao', .3); c1.custo_basal = .15; c0 = cfg('ativacao', .3); c0.custo_basal = 0.
    md = rodar(SerCompleto, Wd, mapas, c1, T=200, seed=3, R=1); m0 = rodar(SerCompleto, W0, mapas, c1, T=200, seed=3, R=1); mb0 = rodar(SerCompleto, Wd, mapas, c0, T=200, seed=3, R=1)
    d, z, b0 = float(md.metab.mean()), float(m0.metab.mean()), float(mb0.metab.mean())
    ok = d > z + .10 and abs(b0 - 1.) < .02
    print(f'test_basal_impede_catatonia: 87 genes ligados e mudos: metab {d:.3f} vs genoma vazio {z:.3f} (basal .15 cobra o tecido em repouso); sem basal {b0:.3f} (~1.0)', 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_medidas_identidade():
    c = cfg('existencia', .3); T = 200; med = medidas(SerCompleto, W[0], mapas, c, T=T, seed=3, R=1, copias=32)
    m = rodar(SerCompleto, W[0][None, :].repeat(32, 1), mapas, c, T, 3, R=1)
    ok = med['metab'] == float(m.metab.mean()) and med['mortos'] == float((m.vida <= 0).float().mean()) and abs(med['fit'] - float(_fit(m, c, T).mean())) < 1e-6 and 'ativacao_bloco' in med
    print(f"test_medidas_identidade: medidas() (medir_ativ ligado) == rodar() cru: metab {med['metab']:.4f} mortos {med['mortos']:.3f} fit {med['fit']:.4f}; ativacao_bloco presente", 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_disparo_evento():
    cd = cfg('disparo', .3); ca = cfg('ativacao', .3); md = rodar(SerCompleto, W, mapas, cd, T=200, seed=3, R=1); ma = rodar(SerCompleto, W, mapas, ca, T=200, seed=3, R=1)
    fd = {b: float((v/md.ativ_n).mean()) for b, v in md.ativ_soma.items()}; fa = {b: float((v/ma.ativ_n).mean()) for b, v in ma.ativ_soma.items()}
    ok = all(0. <= v <= 1. for v in fd.values()) and all(fd[b] <= 1e-6 or fa[b] > 0. for b in fd) and abs(float(md.metab.mean()) - 1.) < 1.5
    print(f'test_disparo_evento: fracao de amostras em que o bloco DISPAROU (> .25 de ativ_ref) {dict((k, round(v, 2)) for k, v in fd.items())} vs magnitude {dict((k, round(v, 2)) for k, v in fa.items())} | metab disparo {float(md.metab.mean()):.3f}', 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_custo_canais():
    c1 = cfg('existencia', .3); c1.custo_basal = .15; c3 = cfg('existencia', .3); c3.custo_basal = .15; c3.custo_canais = ('fome', 'agua', 'calor'); c0 = cfg('existencia', .3); c0.custo_basal = .15; c0.custo_canais = ('fome',)
    m1 = rodar(SerCompleto, W, mapas, c1, T=200, seed=3, R=1); m0 = rodar(SerCompleto, W, mapas, c0, T=200, seed=3, R=1); m3 = rodar(SerCompleto, W, mapas, c3, T=200, seed=3, R=1)
    ident = torch.equal(m1.pos, m0.pos) and torch.equal(m1.agua, m0.agua) and torch.equal(m1.calor, m0.calor)
    a1, a3, k1, k3 = float(m1.agua.mean()), float(m3.agua.mean()), float(m1.calor.mean()), float(m3.calor.mean()); ok = ident and a3 < a1 and k3 > k1
    print(f'test_custo_canais: padrao == (fome,) bit a bit {ident} | 3 canais: agua {a1:.1f} -> {a3:.1f} (deve cair), calor {k1:.1f} -> {k3:.1f} (deve subir), metab {float(m3.metab.mean()):.3f}', 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_ativ_centrada():
    """[10/09 opus, pred 165] a conta do bloco deve cobrar o que MUDA a decisao. um_passo faz sc -= sc.mean(1): o que e' igual
    nas 9 opcoes tem efeito EXATAMENTE zero. Bloco de prova: camada LENTA com M so em sentidos do CORPO (iguais nas 9 opcoes,
    achado E58) -> saida puramente modo comum. Cru: cobra cheio. Centrado: cobra ~0. E identidade com lambda 0."""
    m0 = rodar(SerCompleto, W, mapas, cfg('existencia', 0.), T=200, seed=3, R=1); mc = rodar(SerCompleto, W, mapas, cfg('ativacao', 0., True), T=200, seed=3, R=1)
    idt = torch.equal(m0.pos, mc.pos) and torch.equal(m0.vida, mc.vida) and torch.equal(m0.fome, mc.fome)
    nomes = nomes_genes_completos(); NOP = len(NOMES_OP)
    Wc = torch.zeros(32, SerCompleto.NP, device=DEV); Wc[:, :Linear.NP] = W[:, :Linear.NP]
    ib = [i for i, n in enumerate(nomes) if n.startswith('len_b2_k')]
    im = [i for i, n in enumerate(nomes) if n.startswith('len_M_k') and '_'.join(n.split('_')[3:]) in NOMES_F[NOP:NF]]
    Wc[:, Linear.NP + torch.tensor(ib, device=DEV)] = 2.; Wc[:, Linear.NP + torch.tensor(im, device=DEV)] = 3.
    mr = rodar(SerCompleto, Wc, mapas, cfg('ativacao', .3), T=200, seed=3, R=1); mz = rodar(SerCompleto, Wc, mapas, cfg('ativacao', .3, True), T=200, seed=3, R=1)
    ar = float((mr.ativ_soma['len']/mr.ativ_n).mean()); az = float((mz.ativ_soma['len']/mz.ativ_n).mean())
    er, ez = float(mr.metab.mean()), float(mz.metab.mean()); ok = idt and ar > .05 and az < 1e-3 and er > ez + .05
    print(f'test_ativ_centrada: identidade lam 0 {idt} | lenta so-corpo (modo comum puro): ativacao cru {ar:.3f} -> centrado {az:.5f}; metab {er:.3f} -> {ez:.3f}', 'OK' if ok else 'FALHOU', flush=True); assert ok
if __name__ == '__main__':
    test_custo_identidade(); test_custo_ativacao_gene_morto(); test_metab_monotono(); test_basal_impede_catatonia(); test_medidas_identidade(); test_disparo_evento(); test_custo_canais(); test_ativ_centrada()
