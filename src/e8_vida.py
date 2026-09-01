"""E8 (doc 21): a VIDA EM FASES paga? A infancia conserta a bimodalidade do E4?

    python src/e8_vida.py                 # ruas + base, 3 sementes (~1h)
    python src/e8_vida.py --mundo ruas    # so um mundo

Bracos (mesma classe SerVital, modos diferentes; genes identicos zerados dao
politica IDENTICA entre bracos — portao proprio abaixo):
    direto           adulto desde o nascimento (sem infancia)      [e o E4/E6 de antes]
    sem_poda         infancia, orgaos nunca podados (paga tudo)
    poda             infancia + poda por CONTRIBUICAO (a tese)
    poda_aleatoria   infancia + poda com mesma contagem, sorteada  [controle]
    curta            infancia de 5% (periodo critico insuficiente) [controle]
Predicoes em PREDICOES.md ANTES desta rodada.
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Cfg, SerVital, evoluir_juntas, rodar

MODOS = ['direto', 'sem_poda', 'poda', 'poda_aleatoria', 'curta', 'lesao']


def variante(modo):
    """subclasse com nome/modo proprios (evoluir_juntas indexa por nome)."""
    return type(f'Ser_{modo}', (SerVital,), {'modo': modo, 'nome': f'vida:{modo}'})


def portao(cids, cfg):
    """genes zerados: os 5 modos tem que dar o MESMO resultado (a diferenca
    entre modos so pode vir dos genes vitais, nunca de bug de porte)."""
    print('--- portao E8 (5 modos, genes vitais zerados) ---')
    vals = []
    for modo in MODOS:
        A = variante(modo)
        W = torch.zeros(16, A.NP, device=DEV)
        W[:, 0] = 4.0; W[:, NF:NF+5] = torch.tensor([20.,14.,10.,18.,3.], device=DEV)
        W[:, NF+5] = -4.0
        # T_bebe=T_adulto=0 exige softplus(x)~0 -> x muito negativo
        W[:, NF+12] = -20.; W[:, NF+13] = -20.
        m = rodar(A, W, cids, cfg, T=1200, seed=1, R=2)
        vals.append(m.ent.mean().item())
        print(f'  {modo:<15} {vals[-1]:6.2f}')
    ok = max(vals)-min(vals) < 0.05
    print(f"  {'PASSOU' if ok else 'FALHOU'} (spread {max(vals)-min(vals):.3f})")
    return ok


def main(mundos, P, G, R, tevo, taval, sementes):
    for mundo in mundos:
        print(f'\n################ mundo {mundo} ################')
        treino = [gerar_cidade(s) for s in range(4)]
        teste  = [gerar_cidade(1000+s) for s in range(3)]
        cfg = Cfg(1.0, mundo=mundo)
        if mundo == 'ruas': cfg.cron_alto = 3.5
        if not portao(treino[:2], cfg):
            sys.exit('portao E8 falhou')
        ARQS_E8 = [variante(mo) for mo in MODOS]
        res = {A.nome: dict(ent=[], fit=[], sobrev=[], infancia=[]) for A in ARQS_E8}
        for sd in sementes:
            t0 = time.time()
            champs = evoluir_juntas(ARQS_E8, treino, cfg, P=P, ger=G, T=tevo,
                                    seed=sd, R=R, verbose=(sd==sementes[0]))
            for A in ARQS_E8:
                w = champs[A.nome][0]
                m = rodar(A, w[None,:].repeat(256,1), teste, cfg, T=taval, seed=7777)
                fit = (m.ent - 0.3*m.avar - getattr(m,'custo_neural',0.)).mean()
                res[A.nome]['ent'].append(round(float(m.ent.mean()),2))
                res[A.nome]['fit'].append(round(float(fit),2))
                # telemetria da vida: quem sobreviveu a poda (fracao de mundos
                # em que cada orgao ficou vivo) + duracao da infancia do campeao
                from lab import Lote, um_passo
                mL = Lote(teste[:1], 64, cfg, seed=4242, R=1)
                Wb = w[None,:].repeat(mL.B,1); ai = A(); ai.reset(mL, Wb)
                for _ in range(taval):
                    um_passo(mL, ai, Wb); ai.atualizar(mL)
                res[A.nome]['sobrev'].append(
                    [round(float(x),2) for x in ai.mask.mean(0)])
                frac = float(torch.sigmoid(w[NF+11])*.45+.05)
                res[A.nome]['infancia'].append(round(frac*A.T_REF))
            print(f'semente {sd} ({time.time()-t0:.0f}s): ' + ' | '.join(
                f"{k.split(':')[1]} {v['fit'][-1]}" for k,v in res.items()), flush=True)
        print(f'\n=== E8 {mundo} — fitness (entregas − avarias − custo neural) ===')
        for k, v in sorted(res.items(), key=lambda x: -sum(x[1]['fit'])/len(x[1]['fit'])):
            f_ = v['fit']; med = sum(f_)/len(f_)
            print(f"  {k:<22} media {med:6.2f}  amp {max(f_)-min(f_):.2f}  {f_}  "
                  f"entregas {v['ent']}  infancia(passos) {v['infancia']}")
            print(f"      sobrevivencia por orgao [memC, mapa, jan, corpo, rota]: {v['sobrev']}")
        saida = f'/media/llm-data/universe-runs/neuromod-lab-taxi/e8_vida_{mundo}.json'
        json.dump(dict(res=res, config=dict(P=P,G=G,R=R,tevo=tevo,taval=taval,
                                            sementes=list(sementes), mundo=mundo)),
                  open(saida,'w'))
        print('salvo:', saida)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mundo', default=None, choices=['base','ruas'])
    a = ap.parse_args()
    mundos = [a.mundo] if a.mundo else ['ruas', 'base']
    main(mundos, P=2048, G=60, R=4, tevo=600, taval=1500, sementes=[0,1,2])
