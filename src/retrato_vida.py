#!/usr/bin/env python3
"""retrato_vida.py — grava a VIDA de alguns campeoes no MESMO mundo (jardim comum) e tudo
que acontece dentro do cerebro deles, para desenhar mapa + caminho + estado interno.

Nao evolui nada: e' passagem para frente, CPU, segundos. Grava a cada `--passo` tiques:
  caminho   pos (B,2), acao escolhida, evento (abasteceu / comeu / entregou / pane)
  corpo     fuel, fome, agua, dinheiro, vida, calor, fadiga
  cerebro   contribuicao de cada bloco na nota de movimento, separada em DIRIGE (varia
            entre as 9 opcoes, e' o que o argmax ve) e DESLOCA (constante entre opcoes)
  atencao   os NG portoes do talamo
  camadas   estado da camada rapida (h) e lenta (z) do ser escolhido por --detalhe
  memoria   |MEM| e quantas caixas de distrito ja foram tocadas

Uso:
  python retrato_vida.py --bateria .../e43_P128.json --out DIR [--dias 8] [--passo 2]
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('NM_COMPILE', '0')
import torch
from campo import *
from completo import SerCompleto as SC, GRUPOS, NOMES_G
from politica_util import mundo, braco   # [10/09 pred 170a] mundo do cenario + classe/ajustes por braco


def carrega(bateria, arquiteturas):
    d = json.load(open(bateria)); saida = []
    for arm in d['bracos']:
        if arquiteturas and not any(a.lower() in arm.lower() for a in arquiteturas): continue
        Ws = d['bracos'][arm].get('W') or {}
        if not Ws: continue
        for sd in sorted(Ws):
            saida.append((arm, sd, torch.tensor(Ws[sd], dtype=torch.float32)))
    return saida, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bateria', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--dias', type=int, default=8); ap.add_argument('--passo', type=int, default=2)
    ap.add_argument('--mapa', type=int, default=0); ap.add_argument('--L', type=float, default=200.)
    ap.add_argument('--sementes', type=int, default=2, help='quantas sementes por arquitetura')
    ap.add_argument('--arqs', nargs='*', default=['linear', 'COMPLETO (', 'sem hipocampo'])
    ap.add_argument('--tag', default=''); ap.add_argument('--cenario', default=None, help='[10/09 pred 170a] cenario.json: cfg do mundo (custos, retina, precos, L) e mapa de TESTE (1000+mapa) via politica_util.mundo; sem ele, mundo padrao L --L')
    a = ap.parse_args()

    todos, meta = carrega(a.bateria, a.arqs)
    # no maximo `sementes` por arquitetura, e separado por NP (linear vs completo rodam em passadas diferentes)
    por_arq = {}
    for arm, sd, W in todos: por_arq.setdefault(arm, []).append((sd, W))
    sel = [(arm, sd, W) for arm, l in por_arq.items() for sd, W in l[:a.sementes]]
    print(f'{len(sel)} seres: ' + ', '.join(f'{arm[:22]}#{sd}' for arm, sd, W in sel), flush=True)

    if a.cenario:   # [10/09 pred 170a] o mundo do cenario, nao um L 200 generico (mesmo erro da pred 176)
        cfg, teste, _T, _ch = mundo(a.cenario); mapa = [teste[a.mapa]]; a.L = float(cfg.L)
    else:
        mapa = [gerar_mapa(a.mapa, L=a.L, distinto=True)]; cfg = CfgCampo(L=a.L, dias=a.dias)
    cfg.jardim_comum = True; cfg.medir_ativ = True
    T = 240*a.dias
    reg = {'meta': dict(bateria=os.path.basename(a.bateria), mapa=a.mapa, L=a.L, dias=a.dias, cenario=a.cenario,
                        passo=a.passo, nomes_g=NOMES_G, nomes_op=list(NOMES_OP), grupos=[g for g, _ in GRUPOS]),
           'mapa': {}, 'seres': []}

    # ---- o mapa, para desenhar
    m0 = Campo(mapa, 1, cfg, seed=0, R=1)
    reg['mapa'] = dict(custo=m0.custo_tex[0].tolist(), centros=m0.centros[0].tolist(),
                       serv={t: m0.serv[t][0][m0.serv_msk[t][0]].tolist() for t in TIPOS},
                       pmul=m0.pmul0[0].tolist(), aliq=m0.aliq[0].tolist(), alug=m0.alug[0].tolist())

    # ---- um lote por BRACO: a classe e os ajustes de cerebro vem do braco (sem cortex NAO e o SerCompleto cheio) [10/09 pred 170a; antes agrupava por NP e toda ablacao rodava como SC]
    grupos = {}
    for arm, sd, W in sel: grupos.setdefault(arm, []).append((arm, sd, W))
    for arm_, lote in grupos.items():
        NP = lote[0][2].shape[0]
        try: Arq, cfg_b = braco(meta, arm_, cfg)
        except KeyError: Arq, cfg_b = (SC if NP == SC.NP else Linear), cfg   # bateria antiga sem 'ser' e rotulo fora de BRACOS
        Wpop = torch.stack([W for _, _, W in lote]).to(DEV)
        m = Campo(mapa, Wpop.shape[0], cfg_b, seed=0, R=1)
        Wb = Wpop[m.gidx]; ser = Arq(); ser.reset(m, Wb)
        B = m.B
        tr = {i: dict(pos=[], acao=[], corpo=[], blk=[], gates=[], mem=[], ev=[]) for i in range(B)}
        ant = dict(posto=m.n_posto.clone(), come=m.n_come.clone(), ent=m.ent.clone(), pane=m.av_fuel.clone())
        det = {'h': [], 'z': []}
        for t in range(T):
            F, val = m.obs()
            sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + ser.extra(m, Wb, F)
            sc = sc - sc.mean(1, keepdim=True)
            svn, sv = m.serv_need(); ss = (svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]).masked_fill(sv <= 0, -1e9)
            esc = torch.cat([sc, ss], 1).argmax(1)
            if t % a.passo == 0:
                blk = getattr(ser, '_blk', {})
                gt = ser._gate(m) if hasattr(ser, '_gate') else None
                viv = (m.vida > 0)
                for i in range(B):
                    if not bool(viv[i]): continue
                    tr[i]['pos'].append([round(float(m.pos[i, 0]), 2), round(float(m.pos[i, 1]), 2)])
                    tr[i]['acao'].append(int(esc[i]))
                    tr[i]['corpo'].append([round(float(x[i]), 2) for x in
                                           (m.fuel, m.fome, m.agua, m.dinh, m.vida, m.calor, m.fad)])
                    if blk:
                        tr[i]['blk'].append({k: [round(float((v[i] - v[i].mean()).abs().mean()), 4),
                                                 round(float(v[i].mean()), 4)] for k, v in blk.items()})
                    if gt is not None: tr[i]['gates'].append([round(float(x), 3) for x in gt[i]])
                    if hasattr(ser, 'MEM'):
                        tr[i]['mem'].append([round(float(ser.MEM[i].abs().mean()), 4),
                                             int((ser.MEM[i].abs() > 1e-6).any(1).sum())])
                if hasattr(ser, 'h'):
                    det['h'].append([round(float(x), 3) for x in ser.h[0].mean(0)])
                    det['z'].append([round(float(x), 3) for x in ser.z[0]])
            m.passo(esc); ser.atualizar(m)
            if t % a.passo == 0:
                for nome, chave in (('posto', m.n_posto), ('come', m.n_come), ('ent', m.ent), ('pane', m.av_fuel)):
                    novo = (chave > ant[nome]).nonzero().flatten()
                    for i in novo.tolist(): tr[i]['ev'].append([len(tr[i]['pos']) - 1, nome])
                    ant[nome] = chave.clone()
            if t % 240 == 239 and not bool((m.vida > 0).any()): break
        for i, (arm, sd, W) in enumerate(lote):
            reg['seres'].append(dict(arm=arm, semente=sd, NP=int(NP), t_vida=float(m.t_vida[i]/240.),
                                     ent=int(m.ent[i]), panes=float(m.av_fuel[i]), dinh=float(m.dinh[i]),
                                     **tr[i], detalhe=(det if (i == 0 and NP == SC.NP) else None)))
            print(f"  {arm[:26]:<28}#{sd}  vive {float(m.t_vida[i]/240.):5.2f} d | {int(m.ent[i]):3d} entregas | "
                  f"{float(m.av_fuel[i]):4.1f} panes | {len(tr[i]['pos'])} pontos gravados", flush=True)
    os.makedirs(a.out, exist_ok=True)
    dest = os.path.join(a.out, f'retrato_vida{a.tag}.json')
    json.dump(reg, open(dest, 'w'))
    print('gravado', dest, f'({os.path.getsize(dest)/1e6:.1f} MB)', flush=True)


if __name__ == '__main__':
    main()
