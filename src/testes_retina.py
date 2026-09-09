"""[spec Mundo Vivo F3] portao da retina (roda com NM_RETINA=1): (1) raio: servico colocado a d na direcao k e' lido em ret_d_k = d (+-passo) com o
rotulo certo, e a coluna d_* por opcao aponta para ele; (2) parede: quadra opaca a frente encurta 'livre' naquela direcao e esconde o servico
atras dela; (3) noite: R_noite < R_dia -> mais raios cegos; (4) sem oclusao e R >= diagonal: para servico NO raio, ret_d == oraculo _dist.
A identidade com NM_RETINA=0 e' coberta por testes_cidade/testes_campo (a flag desligada nao executa nada novo)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'; assert os.environ.get('NM_RETINA') == '1', 'rodar com NM_RETINA=1'
import torch; from campo import *
c = CfgCampo(L=200., fitness='riqueza'); c.retina = dict(RETINA_PADRAO); mapas = [gerar_mapa(1000, L=200., distinto=True)]
NOP = len(NOMES_OP); ID = lambda n: NOMES_CORPO.index(n) + NOP
def campo_limpo(B=8, hora_noite=False):
    m = Campo(mapas, B, c, seed=3, R=1); m.pos[:] = 100.; m.opac[:] = False; m.tipo_g[:] = 0
    if hora_noite: m.fase[:] = 23.5*c.dia/24. - float(m.t)   # hora() ~ 23.5 -> noite
    return m
def celula(m, x, y): ix = int(x/m.L*GR); iy = int(y/m.L*GR); return iy, ix
def test_raio():
    m = campo_limpo(); d = 24.; ok = True
    for k in range(KR):
        p = m.pos[0] + m.dirs[k]*d; iy, ix = celula(m, float(p[0]), float(p[1])); m.tipo_g[0, iy, ix] = 1 + (k % 5)   # tipo por raio
    F, _ = m.obs(); rd = torch.stack([F[0, G - 1, ID(f'ret_d_{k}')]*100. for k in range(KR)]); rt = torch.stack([F[0, G - 1, ID(f'ret_t_{k}')]*5. for k in range(KR)])
    ok = bool(((rd - d).abs() <= c.retina['passo']).all()) and all(int(round(float(rt[k]))) == 1 + (k % 5) for k in range(KR))
    print(f'test_raio: ret_d {[round(float(x)) for x in rd]} (esperado ~{d:.0f} +-{c.retina["passo"]:.0f}) rotulos {[int(round(float(x))) for x in rt]}', 'OK' if ok else 'FALHOU', flush=True); assert ok
    # a coluna d_posto por opcao (tipo 1 = posto, raios 0 e 5) aponta para o posto visto: a opcao que anda na direcao 0 fica mais perto
    dp = F[0, :, NOMES_OP.index('d_posto')]; assert float(dp[0]) < float(dp[4]), (float(dp[0]), float(dp[4])); print('  d_posto por opcao: andar rumo ao raio 0 aproxima', round(float(dp[0]), 1), '< oposto', round(float(dp[4]), 1), flush=True)
def test_parede():
    m = campo_limpo(); d = 24.; p = m.pos[0] + m.dirs[0]*d; iy, ix = celula(m, float(p[0]), float(p[1])); m.tipo_g[0, iy, ix] = 1
    q = m.pos[0] + m.dirs[0]*8.; iy, ix = celula(m, float(q[0]), float(q[1])); m.opac[0, iy-1:iy+2, ix-1:ix+2] = True   # quadra a 8 m na direcao 0
    F, _ = m.obs(); l0 = float(F[0, 0, NOMES_OP.index('livre')]*100.); l4 = float(F[0, 4, NOMES_OP.index('livre')]*100.); rd0 = float(F[0, G - 1, ID('ret_d_0')]*100.)
    ok = l0 < 12. and l4 >= 50. and rd0 >= c.retina['k_cego']*c.retina['R_dia'] - 1
    print(f'test_parede: livre dir0 {l0:.0f} (< 12) vs oposto {l4:.0f} (>= 50); posto atras da parede: ret_d_0 {rd0:.0f} (= cego {c.retina["k_cego"]*c.retina["R_dia"]:.0f})', 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_noite():
    md = campo_limpo(); mn = campo_limpo(hora_noite=True); assert bool(mn.noite_()[0]) and not bool(md.noite_()[0]), 'relogio'
    for m in (md, mn):
        for k in range(KR):
            p = m.pos[0] + m.dirs[k]*40.; iy, ix = celula(m, float(p[0]), float(p[1])); m.tipo_g[0, iy, ix] = 1
    Fd, _ = md.obs(); Fn, _ = mn.obs(); dd = float(sum(Fd[0, G - 1, ID(f'ret_d_{k}')] for k in range(KR))/KR*100.); dn = float(sum(Fn[0, G - 1, ID(f'ret_d_{k}')] for k in range(KR))/KR*100.)
    ok = dd < 50. and dn >= c.retina['k_cego']*c.retina['R_dia'] - 1; print(f'test_noite: servico a 40 m: de dia le {dd:.0f}, de noite (R {c.retina["R_noite"]:.0f}) le {dn:.0f} = cego', 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_sem_oclusao_bate_oraculo():
    m = campo_limpo(); m.cfg.retina = dict(RETINA_PADRAO, R_dia=300.); d = 72.; p = m.pos[0] + m.dirs[3]*d; iy, ix = celula(m, float(p[0]), float(p[1])); m.tipo_g[0, iy, ix] = 2
    m.serv['comida'][0, 0] = p; m.serv_msk['comida'][0] = False; m.serv_msk['comida'][0, 0] = True   # o oraculo tambem so' tem esse ponto
    F, _ = m.obs(); rd = float(F[0, G - 1, ID('ret_d_3')]*100.); ora = float(m._dist[0, 1]); ok = abs(rd - ora) <= m.cfg.retina['passo']
    print(f'test_sem_oclusao_bate_oraculo: retina {rd:.1f} vs oraculo {ora:.1f} (tolerancia {m.cfg.retina["passo"]:.0f})', 'OK' if ok else 'FALHOU', flush=True); assert ok
if __name__ == '__main__':
    print(f'NF {NF} NOP {NOP} Linear.NP {Linear.NP}', flush=True); test_raio(); test_parede(); test_noite(); test_sem_oclusao_bate_oraculo()
