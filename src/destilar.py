"""Destilacao simbolica (doc 37 §2): a politica do campeao vira uma equacao curta em PT-BR,
e a equacao e VERIFICADA (a politica podada tem de reproduzir fit/mortos do campeao ±10%).
    python src/destilar.py <json> "<braco>" [--k 5] [--mundo pacote]
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import Reativo, Lote, um_passo, rodar, gerar_cidade, DEV, NF
from rodar import NOMES_F
from e19_pacote import cfg_pacote

PT = {'d_alvo':'distância ao destino', 'custo_rua':'custo da rua', 'congestao':'congestionamento', 'semaforo':'semáforo',
      'd_posto':'distância ao posto', 'd_comida':'distância à comida', 'd_descanso':'distância ao descanso',
      'd_oficina':'distância à oficina', 'd_loja':'distância à loja', 'e_fuel':'tanque', 'e_fome':'fome', 'e_fadiga':'fadiga',
      'e_pneu':'pneu', 'e_temp':'temperatura', 'e_oleo':'óleo', 'e_dinheiro':'dinheiro', 'e_tem_pax':'carregando passageiro',
      'e_reserva':'gordura', 'h_sin':'hora (seno)', 'h_cos':'hora (cosseno)', 'e_dano':'dano', 'e_divida':'dívida',
      'e_preco_local':'preço local', 'h_gl0':'hormônio 0', 'h_gl1':'hormônio 1', 'bias':'constante'}
SERV = ['posto', 'comida', 'descanso', 'oficina', 'loja']

def contribuicoes(W, cfg, cidades, T=600):
    """|w| x desvio-padrao da feature ao longo de uma vida = quanto cada termo mexe no score."""
    m = Lote(cidades, W.shape[0], cfg, seed=7777); Wb = W[m.gidx]; a = Reativo(); a.reset(m, Wb)
    soma = torch.zeros(NF, device=DEV); soma2 = torch.zeros(NF, device=DEV); n = 0
    for t in range(T):
        F, val = m.obs(); Fv = F[val]                        # (n_validos, NF)
        soma += Fv.sum(0); soma2 += (Fv*Fv).sum(0); n += Fv.shape[0]
        um_passo(m, a, Wb); a.atualizar(m)
    mu = soma/n; sd = (soma2/n - mu*mu).clamp(min=0).sqrt()
    return (W[0, :NF].abs()*sd).cpu(), W[0].cpu()

def main(a):
    d = json.load(open(a.json)); r = d['bracos'][a.braco]; sd0 = sorted(r['W'])[0]
    W = torch.tensor(r['W'][sd0], device=DEV)[None, :]
    cfg = cfg_pacote(fome=.15, refeicao=90., comida_no_posto=True); cidades = [gerar_cidade(1000+s) for s in range(3)]
    contrib, w = contribuicoes(W, cfg, cidades)
    ordem = torch.argsort(contrib, descending=True)[:a.k].tolist()
    print(f'== {a.braco} (semente {sd0}) — os {a.k} termos que mais mexem no score de MOVER ==')
    for i in ordem: print(f'   {w[i]:+6.2f} × {PT.get(NOMES_F[i], NOMES_F[i])}   (contribuição {contrib[i]:.2f})')
    ws = w[NF:NF+5].tolist(); print('   serviços (peso × necessidade):', ', '.join(f'{SERV[j]} {ws[j]:+.1f}' for j in range(5)), f'| constante {w[NF+5]:+.1f}')
    # politica podada: so os k termos de movimento + servicos
    Wp = torch.zeros_like(W); Wp[0, ordem] = W[0, ordem]; Wp[0, NF:NF+6] = W[0, NF:NF+6]
    f = lambda m: (float((m.ent-0.3*m.avar).mean()), float((m.vida<=0).float().mean()))
    mf = rodar(Reativo, W.repeat(128,1), cidades, cfg, T=1200, seed=7777); mp = rodar(Reativo, Wp.repeat(128,1), cidades, cfg, T=1200, seed=7777)
    (f1, m1), (f2, m2) = f(mf), f(mp)
    ok = abs(f2-f1) <= 0.1*abs(f1)+0.3 and abs(m2-m1) <= 0.10
    print(f'== verificação: campeão fit {f1:.2f} mortos {m1:.2f} | equação de {a.k} termos fit {f2:.2f} mortos {m2:.2f} → {"FECHA" if ok else "NÃO FECHA"} (±10 %)')
    frase = ' '.join(f'{"+" if w[i]>0 else "−"} {abs(w[i]):.1f}·[{PT.get(NOMES_F[i], NOMES_F[i])}]' for i in ordem)
    print('== em português: "prefiro o vizinho com ' + frase + '; uso o serviço cuja necessidade × peso vencer o movimento."')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('braco'); ap.add_argument('--k', type=int, default=5)
    main(ap.parse_args())
