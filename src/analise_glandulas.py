"""E16: o que cada glandula VIROU — leitura DEPOIS de evoluir, sem dar nome antes.

    python src/analise_glandulas.py [--json .../e16_glandulas_a.json] [--braco NOME]

Roda o campeao de cada braco em 3 cidades e imprime:
  - tau de cada glandula (memoria em passos e em dias)
  - correlacao de h_k com cada DEFICIT e com cada EVENTO de ganho
  - o sinal dos ganhos de saida (b) por canal
  - a classificacao, feita SO agora:
        "estresse-like"  = sobe com deficit  e REDUZ gasto/esforco
        "dopamina-like"  = sobe com evento de ganho e AUMENTA esforco
        "inerte"         = |b| desprezivel ou h ~ 0
        "misto"          = as duas coisas (ou nenhuma das duas puras)
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, Reativo, gerar_cidade, rodar
from glandulas import ser_glandular, ler_genes, NOMES_X, NG
from e16_glandulas import cfg_gl, _corr, OUT

DEFICITS = NOMES_X[:6]
EVENTOS = NOMES_X[6:]
# canais REALMENTE aplicados no passo/arquitetura (doc 30 §3). `exploracao` so
# vale com expl_on=True e `velocidade` nao e aplicada em lugar nenhum: os genes
# desses dois canais sao DERIVA e nao podem entrar em nenhuma leitura — foi o 2o
# erro que este script cometeu (somar 5 canais como se os 5 mordessem).
APLICADOS = ('necessidade', 'metabolismo', 'sono')
INERTES = ('exploracao', 'velocidade')


def classificar(tau, a, b, corr, h_med, canais, lim_b=.08, lim_r=.15, lim_h=.02):
    """Sem nome dado antes: a etiqueta sai do sinal medido.

    Glandula com h~0 e INERTE e ponto: as correlacoes dela sao ruido em cima de
    zero e o tau dela e um gene que deriva sem pressao. Nao entra em predicao
    nenhuma — foi o erro que a 1a versao deste script cometeu ("2 papeis
    distintos" contando uma glandula desligada como se fosse um papel)."""
    if h_med < lim_h:
        return 'inerte (h~0)', False
    bj = {cn: float(b[j]) for j, cn in enumerate(canais)}
    gasto = bj['metabolismo']                              # o unico canal de GASTO aplicado
    manut = bj['necessidade'] + bj['sono']                 # prioridade de cuidar do corpo
    if abs(gasto) < lim_b and abs(manut) < lim_b:
        return f'inerte (b aplicados ~0: gasto {gasto:+.3f} manut {manut:+.3f})', False
    # QUEM LEVANTA h: com clamp em 0, so os pesos POSITIVOS empurram h pra cima.
    # Peso NEGATIVO em deficit = a glandula sobe quando o deficit SOME (o
    # "reverso" pode aparecer pela retificacao, sem gene de evento nenhum).
    pos = [(NOMES_X[i], float(a[i])) for i in range(10) if float(a[i]) > .2]
    pos.sort(key=lambda kv: -kv[1])
    neg_def = [NOMES_X[i] for i in range(6) if float(a[i]) < -.5]
    driver = pos[0][0] if pos else None
    if driver is None:
        tipo = 'ausencia de deficit' if neg_def else None
    else:
        tipo = 'deficit' if driver.startswith('def_') else 'evento de ganho'
    if tipo is None:
        return (f'sem driver claro (gasto {gasto:+.2f} manut {manut:+.2f})'), True
    if tipo == 'deficit':
        nome = 'ESTRESSE-like' if gasto < 0 else 'MOBILIZADORA'
    else:
        nome = 'DOPAMINA-like' if gasto > 0 else 'SACIEDADE-like'
    d = f'{driver}' if driver else '+'.join(neg_def)
    return (f'{nome} (sobe com {tipo}: {d}; gasto {gasto:+.2f} manut {manut:+.2f})'), True


def analisar(nome, dados, teste_seed=1000, T=1200, n_rep=64):
    w = torch.tensor(dados['W'][list(dados['W'])[0]], device=DEV)
    K = 2 if 'K=2' in nome or dados.get('arq', '').endswith('K2') else None
    if K is None:
        K = int(dados['arq'].split('K')[-1][0]) if 'glandula' in dados.get('arq', '') else 0
    if K == 0:
        print(f'\n== {nome} == (sem glandulas: braco de referencia)')
        return None
    A = ser_glandular(K)
    kw = dict(glandulas=True, K=K)
    if 'regime' in nome: kw['regime'] = .35
    if 'sono5' in nome: kw['sono_come'] = 5.
    if 'b=' in nome: kw['escala_b'] = float(nome.split('b=')[1])
    c = cfg_gl(**kw)
    cids = [gerar_cidade(teste_seed + i) for i in range(3)]
    m = rodar(A, w[None, :].repeat(n_rep, 1), cids, c, T=T, seed=7777)
    tau, a, b = ler_genes(w.cpu(), K=K, cfg=c)
    r = _corr(m).cpu()
    h_med = (m.h_soma/m.h_n).mean(0).cpu()
    mult = (m.mult_soma/m.h_n).mean(0).cpu()
    print(f'\n== {nome} ==  fit {float((m.ent-0.3*m.avar).mean()):.2f} '
          f'ent {float(m.ent.mean()):.2f} mortos {float((m.vida<=0).float().mean()):.2f} '
          f'| custo do hormonio {float(m.h_custo.mean()):.1f} de fuel/vida, '
          f'sono limpou {float(m.h_sono.mean()):.1f}')
    print('   ganhos medios: ' + '  '.join(f'{cn} {float(mult[j]):.3f}'
                                           for j, cn in enumerate(c.GL_CANAIS)))
    saida = []
    for k in range(K):
        print(f'\n   glandula h{k}:  tau {float(tau[k]):7.1f} passos '
              f'({float(tau[k])/c.dia:5.2f} dias)   h medio {float(h_med[k]):.3f}')
        print('     corr com DEFICIT : ' + '  '.join(
            f'{nm[4:]} {float(r[k,i]):+.2f}' for i, nm in enumerate(DEFICITS)))
        print('     corr com EVENTO  : ' + '  '.join(
            f'{nm[3:]} {float(r[k,6+i]):+.2f}' for i, nm in enumerate(EVENTOS)))
        print('     pesos de ENTRADA : ' + '  '.join(
            f'{nm} {float(a[k,i]):+.2f}' for i, nm in enumerate(NOMES_X) if abs(float(a[k,i])) > .5))
        print('     ganhos de saida b: ' + '  '.join(
            f'{cn} {float(b[k,j]):+.3f}' + ('*' if cn in INERTES else '')
            for j, cn in enumerate(c.GL_CANAIS)) + '   (* = canal nao aplicado, gene a deriva)')
        cl, ativa = classificar(tau[k], a[k], b[k], r[k], float(h_med[k]), c.GL_CANAIS)
        print(f'     -> {cl}')
        saida.append(dict(tau=float(tau[k]), h=float(h_med[k]), classe=cl, ativa=ativa,
                          corr={nm: round(float(r[k, i]), 3) for i, nm in enumerate(NOMES_X)},
                          b={cn: round(float(b[k, j]), 3) for j, cn in enumerate(c.GL_CANAIS)}))
    ativas = [i for i, s_ in enumerate(saida) if s_['ativa']]
    print(f'\n   glandulas ATIVAS: {len(ativas)}/{K}')
    if len(ativas) < 2:
        print('   PREDICAO 1 (tau > 3x) e PREDICAO 2 (papeis opostos): NAO TESTAVEIS '
              '— menos de duas glandulas ligadas (tau de glandula inerte e gene a deriva)')
    else:
        ts = [saida[i]['tau'] for i in ativas]
        razao = max(ts)/min(ts)
        print(f'   PREDICAO 1 (tau diferem > 3x, so entre ATIVAS): razao {razao:.2f}x -> '
              f'{"CONFIRMA" if razao > 3 else "NAO confirma"}')
        classes = {saida[i]['classe'].split(' ')[0] for i in ativas}
        print(f'   PREDICAO 2 (papeis opostos, so entre ATIVAS): {sorted(classes)} -> '
              f'{"CONFIRMA" if len(classes) > 1 else "NAO confirma (as duas viraram a mesma coisa)"}')
    del m
    return saida


def main(caminho, so=None, teste_seed=None, T=1200):
    with open(caminho) as fh:
        d = json.load(fh)
    ts = teste_seed if teste_seed is not None else d.get('teste_seed', 1000)
    print(f'--- analise E16 | {caminho} | fase {d.get("fase")} | cidades {ts}+ ---')
    out = {}
    for nome, dados in d['bracos'].items():
        if so and nome not in so: continue
        out[nome] = analisar(nome, dados, ts, T)
    alvo = caminho.replace('.json', '_analise.json')
    with open(alvo, 'w') as fh: json.dump(out, fh, indent=1)
    print(f'\n-> {alvo}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=os.path.join(OUT, 'e16_glandulas_a.json'))
    ap.add_argument('--braco', nargs='*', default=None)
    ap.add_argument('--teste-seed', type=int, default=None)
    ap.add_argument('--T', type=int, default=1200)
    a = ap.parse_args()
    main(a.json, a.braco, a.teste_seed, a.T)
