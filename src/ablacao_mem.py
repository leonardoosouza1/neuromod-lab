"""A evolucao USOU a memoria ou a desligou? A paisagem nao responde (amplitude
igual ate em peso morto = ruido de avaliacao). Ablacao responde: zera o bloco
de memoria do GENOMA FINAL e mede a queda com as MESMAS 6 cidades de teste.

  queda >> ruido  -> a memoria contribui de verdade
  queda ~ 0       -> a evolucao a desligou (ou ela nunca fez nada)

Controle embutido: reativo (memoria morta por construcao) TEM que dar queda 0.
Qualquer coisa diferente de 0 ali e a regua de ruido do proprio teste.
"""
import json, glob, sys, torch
sys.path.insert(0, 'src')
from lab import DEV, NF, gerar_cidade, Cfg, rodar, ARQS
POR_NOME = {A().nome if hasattr(A(),'nome') else A.nome: A for A in ARQS}

def avalia(Arq, w, cfg, seeds=512):
    teste = [gerar_cidade(1000+s) for s in range(6)]
    W = w[None,:].repeat(seeds,1)
    m = rodar(Arq, W, teste, cfg, 1500, seed=7777, R=1)
    f = m.ent - 0.3*m.avar
    return float(m.ent.mean()), float(f.mean()), float(m.ent.std())

print(f"{'run':<12}{'arq':<14}{'intacto':>9}{'ablado':>9}{'queda':>8}   veredito")
for fj in sorted(glob.glob('resultados/*.json')):
    d = json.load(open(fj)); tag = fj.split('resultado-taxi-')[1].rsplit('-',2)[0]
    mundo = tag.split('-s')[0]
    cfg = Cfg(1.0, mundo=mundo)
    for nome, r in sorted(d['resultados'].items()):
        if not (isinstance(r,dict) and 'pesos_finais' in r): continue
        Arq = POR_NOME.get(nome)
        if Arq is None: continue
        w = torch.tensor(r['pesos_finais'], device=DEV, dtype=torch.float32)
        if w.numel() < 36: continue
        e1,_,dp = avalia(Arq, w, cfg)
        wa = w.clone(); wa[NF+6:] = 0.          # zera mem_0..5 e corpo_0..5
        e0,_,_ = avalia(Arq, wa, cfg)
        q = e1-e0
        sem = dp/ (512**.5) * 2                  # ~2 erros-padrao
        v = "USA a memória" if q > 2*sem else ("ATRAPALHA(!)" if q < -2*sem else "desligada")
        if nome=='reativo': v += "  <- controle: deve ser ~0"
        print(f"{tag:<12}{nome:<14}{e1:>9.2f}{e0:>9.2f}{q:>+8.2f}   {v}")
