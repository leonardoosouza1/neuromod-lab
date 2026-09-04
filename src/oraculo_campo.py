"""E51 ORACULO (regra da metrica de degrau: calcular o TETO FISICO antes de evoluir contra ele).
Politica ESCRITA A MAO, sem genes: escolhe uma necessidade, TRANCA o alvo (compromisso: 'andar N ticks pra comida e depois
voltar pra agua'), anda em linha ate o ponto mais perto, compra o que cabe, solta o alvo, volta a trabalhar (passageiro).
Regra de dinheiro: pobre so atende necessidade CRITICA. Mede quantos sobrevivem no mundo com loja e sem loja.
Se o oraculo vive onde a evolucao morre -> o mundo e viavel e o gargalo e MONTAGEM (a evolucao nao acha);
se o oraculo tambem morre -> o mundo e duro demais e tem de ser recalibrado ANTES de qualquer arquitetura.
Tudo tensor; estado (alvo trancado) atualizado em atualizar() fora do grafo, como o Comite."""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(__file__))
import torch
from campo import *
from campo import _fit

COL = {0: 1, 1: 2, 2: 3, 3: 4}                       # alvo -> coluna de F: posto d_posto(1), comida d_comida(2), agua d_agua(3), oficina d_oficina(4)
ACAO_TIPO = torch.tensor([0, 0, 0, 0, 0, 2, 2, 1, -1, 3])   # acao de servico -> tipo de alvo (descanso -1: o oraculo nao descansa)

def fabrica_oraculo(liga=(.5, .6, .5, .5), critico=(.8, .85, .75, .7), caixa_min=15., noite_posto=False, nome='oraculo', oportunista=False, piso=0., baixo=.25, entrega_primeiro=False, fura_esfria=True):
    """liga/critico: limiar da urgencia (u_fuel=1-fuel/100, u_fome=fome/100, u_agua=1-agua/100, u_vida=1-vida/100) por alvo.
    caixa_min: abaixo disso so necessidade critica tranca (o resto do tempo trabalha). noite_posto: tranca posto a noite (fechado) ou nao."""
    liga_t = torch.tensor(liga, device=DEV); crit_t = torch.tensor(critico, device=DEV)
    U_ACAO = torch.tensor([0, 0, 0, 0, 0, 2, 2, 1, -1, 3])   # acao -> indice da urgencia (fuel, fome, agua, vida); descanso -1
    class Oraculo:
        NP = Linear.NP
        def reset(s, m, W):
            s.W = W; s.alvo = torch.full((m.B,), -1, dtype=torch.long, device=DEV); s.F = None; s.cool = torch.zeros(m.B, device=DEV)
            s.acao_tipo = ACAO_TIPO.to(DEV); s.u_acao = U_ACAO.to(DEV); s.e_posto = (s.acao_tipo == 0)
        def extra(s, m, W, F): s.F = F; return torch.zeros(m.B, G, device=DEV)
        def _urg(s, m): return torch.stack([1. - m.fuel/100., m.fome/100., 1. - m.agua/100., 1. - m.vida/100.], 1)   # (B,4)
        def decidir(s, tudo, m):
            B = m.B; F = s.F; alvo = s.alvo
            tem = alvo >= 0
            col = torch.zeros(B, dtype=torch.long, device=DEV)
            for k, c in COL.items(): col = torch.where(alvo == k, torch.full_like(col, c), col)
            dist = F.gather(2, col[:, None, None].expand(-1, G, 1)).squeeze(2)      # (B,G) distancia ao alvo apos cada opcao
            mov = dist.argmin(1)                                                        # anda reto pro alvo (ou pro passageiro: col 0 = d_alvo)
            # servico: se o alvo esta ao alcance (acao do tipo dele disponivel E paga -> tudo > -1e8), compra a de maior necessidade
            disp = tudo[:, G:] > -1e8                                                   # (B,S) disponivel E paga
            if piso > 0.:                                                               # [v2 poupador] gasolina so com o que sobra acima do piso de caixa (a gordura e o dinheiro, nao o tanque)
                sv_, pm_ = m.serv_ab(); cs_ = m.custos(pm_)
                disp = disp & (~s.e_posto[None, :] | ((m.dinh[:, None] - cs_) >= piso))
            do_alvo = (s.acao_tipo[None, :] == alvo[:, None]) & disp
            svn, _ = m.serv_need()
            quer = do_alvo
            if oportunista:                                                             # [v2] ja que esta aqui: compra tudo que precisa acima de 'baixo' (o campeao come toda vez que abastece)
                u = s._urg(m); ua = torch.cat([u, torch.zeros(B, 1, device=DEV)], 1)[:, s.u_acao]   # (B,S) urgencia da acao (descanso -> 0)
                quer = quer | (disp & (ua > baixo))
            nota = torch.where(quer, svn, torch.full_like(svn, -1.))
            melhor = nota.argmax(1); pode = nota.max(1).values > 0.
            return torch.where(pode, melhor + G, mov)
        def atualizar(s, m):
            u = s._urg(m); pobre = m.dinh < caixa_min; nv = m.noite_()
            lim = torch.where(pobre[:, None], crit_t[None, :], liga_t[None, :])
            on = u > lim
            if not noite_posto: on[:, 0] = on[:, 0] & (~nv | (u[:, 0] > crit_t[0]))   # posto fecha a noite: so tranca se critico
            # solta o alvo quando a urgencia dele caiu abaixo do limiar (comprou) — senao mantem (compromisso)
            ua = u.gather(1, s.alvo.clamp(min=0)[:, None]).squeeze(1); la = lim.gather(1, s.alvo.clamp(min=0)[:, None]).squeeze(1)
            solta = (s.alvo >= 0) & (ua < la - .15)
            # chegou e NAO consegue pagar nenhuma acao do tipo -> solta e vai trabalhar (esfria 60 ticks pra nao re-trancar na hora)
            sv, pm = m.serv_ab(); cs = m.custos(pm); paga = (m.dinh[:, None] >= cs) & (sv > 0)
            tipo = s.acao_tipo[None, :] == s.alvo[:, None]
            chegou = (tipo & (sv > 0)).any(1); pode_pagar = (tipo & paga).any(1)
            sem_grana = (s.alvo >= 0) & chegou & ~pode_pagar
            noite_fechado = (s.alvo == 0) & nv & ~(u[:, 0] > crit_t[0])                        # posto trancado de dia, anoiteceu e nao e critico: solta
            if noite_posto: noite_fechado = torch.zeros_like(noite_fechado)
            esfria = sem_grana | noite_fechado
            s.cool = torch.where(esfria, torch.full_like(s.cool, 60.), (s.cool - 1.).clamp(min=0.))
            alvo = torch.where(solta | esfria, torch.full_like(s.alvo, -1), s.alvo)
            # tranca: sem alvo, esfriado, e alguma necessidade ligada -> a mais urgente (relativa ao limiar); critica ignora o esfriamento
            pri = torch.where(on, u - lim, torch.full_like(u, -9.)); novo = pri.argmax(1)
            critico = (u > crit_t[None, :]).any(1)
            livre = (s.cool <= 0) | (critico if fura_esfria else torch.zeros_like(critico))       # [v3] sem furar: quebrado + critico NAO volta ao posto onde nao paga — trabalha (o guincho leva)
            if entrega_primeiro: livre = livre & ((m.pd_ < 0) | critico)                             # [v3] com passageiro a bordo: entrega antes (o campeao faz 27 entregas com 64% dos ticks ocupado; o oraculo 8 com 70%)
            s.alvo = torch.where((alvo < 0) & on.any(1) & livre, novo, alvo)
    Oraculo.nome = nome
    return Oraculo

VARIANTES = {
    'base':            dict(),
    'cedo':            dict(liga=(.35, .45, .35, .5)),
    'tarde':           dict(liga=(.65, .75, .65, .5)),
    'rico':            dict(caixa_min=40.),
    'sem_caixa':       dict(caixa_min=0.),
    'noite_posto':     dict(noite_posto=True),
    'cedo_sem_caixa':  dict(liga=(.35, .45, .35, .5), caixa_min=0.),
    'tarde_rico':      dict(liga=(.65, .75, .65, .5), caixa_min=40.),
    'oportunista':     dict(oportunista=True),
    'poupador':        dict(piso=8.),
    'poup_oport':      dict(oportunista=True, piso=8.),
    'poup_oport_tarde': dict(oportunista=True, piso=8., liga=(.65, .6, .5, .5)),
    'poup_oport_caixa0': dict(oportunista=True, piso=8., caixa_min=0.),
    'poup12_oport_tarde': dict(oportunista=True, piso=12., liga=(.65, .6, .5, .5), caixa_min=0.),
    'v3_entrega':      dict(oportunista=True, piso=8., entrega_primeiro=True),
    'v3_sem_fura':     dict(oportunista=True, piso=8., fura_esfria=False),
    'v3_ambos':        dict(oportunista=True, piso=8., entrega_primeiro=True, fura_esfria=False),
    'v3_ambos_tarde':  dict(oportunista=True, piso=8., entrega_primeiro=True, fura_esfria=False, liga=(.65, .6, .5, .5), caixa_min=0.),
    'v3_ambos_cedo':   dict(oportunista=True, piso=8., entrega_primeiro=True, fura_esfria=False, liga=(.4, .5, .4, .5), caixa_min=0.),
    'v3_ambos_piso0':  dict(oportunista=True, piso=0., entrega_primeiro=True, fura_esfria=False, caixa_min=0.),
}

def main(a):
    os.makedirs(a.out, exist_ok=True); T = int(240*a.dias)
    teste = [gerar_mapa(a.teste_seed + s, L=a.L) for s in range(3)]
    res = dict(L=a.L, dias=a.dias, mundos={})
    print(f'== E51 oraculo | L={a.L} dias={a.dias} copias={a.copias} x 3 mapas | variantes {list(VARIANTES)} ==', flush=True)
    for mundo, loja in (('com_loja', True), ('sem_loja', False)):
        cfg = CfgCampo(L=a.L, fitness=a.fitness, loja_no_posto=loja); res['mundos'][mundo] = {}
        for nome, kw in VARIANTES.items():
            if a.so and nome not in a.so: continue
            t1 = time.time(); A = fabrica_oraculo(nome=nome, **kw); W = torch.zeros(Linear.NP, device=DEV)   # W nunca e lido, mas um_passo fatia Wb[:, NF:NF+S]: precisa ter o tamanho do Linear
            med = medidas(A, W, teste, cfg, T=T, seed=7777, R=1, copias=a.copias); med['segundos'] = round(time.time() - t1)
            res['mundos'][mundo][nome] = med
            print(f'  {mundo:<8} {nome:<16} fit {med["fit"]:6.2f} ent {med["ent"]:5.1f} mortos {med["mortos"]:.2f} panes {med["panes"]:4.1f} fome {med["fome_fim"]:3.0f} '
                  f'agua {med["agua_fim"]:3.0f} dinh {med["dinh"]:5.0f} res {med["res"]:4.0f} come {med["n_come"]:4.1f} abast {med["n_posto"]:4.1f} L/abast {med["litros_por_abast"]:4.0f} ({med["segundos"]}s)', flush=True)
        tmp = os.path.join(a.out, f'e51{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e51{a.tag}.json'))
    sl = res['mundos'].get('sem_loja', {})
    if sl:
        come = max(v['n_come'] for v in sl.values())
        print(f'SANIDADE {"ok" if come > 1. else "FALHOU"}: max refeicoes sem loja = {come:.1f} (o oraculo TEM de comer longe da rota)', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--fitness', default='bemestar')
    ap.add_argument('--copias', type=int, default=128); ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--tag', default='')
    ap.add_argument('--so', nargs='*', default=None); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e51')
    main(ap.parse_args())
