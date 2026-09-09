"""[revisao §E] SerCompleto com ORCAMENTO sob torch.compile == eager (o dict _blk passa a ser lido dentro do grafo por _fator_orc): compara
rodar() (compilado) com um laco eager identico; tolerancia = a de testes_campo (empates de argmax: <= 3 seres em 384)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import SerCompleto
c = CfgCampo(L=200., fitness='riqueza'); c.orcamento_ativ = 1.0; mapas = [gerar_mapa(1000, L=200., distinto=True)]
g = torch.Generator(device=DEV); g.manual_seed(5); W = torch.randn(64, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5
mc = rodar(SerCompleto, W, mapas, c, T=200, seed=3, R=2)
me = Campo(mapas, 64, c, seed=3, R=2); Wb = W[me.gidx]; a = SerCompleto(); a.reset(me, Wb)
for t in range(200): um_passo(me, a, Wb); a.atualizar(me)
dif = int(((mc.pos - me.pos).abs().max(1).values > 1e-6).sum()); B = mc.pos.shape[0]; ok = dif <= 3
print(f'SerCompleto + orcamento: compilado vs eager: seres com pos diferente {dif}/{B} (tolerancia 3) | max dif pos {float((mc.pos-me.pos).abs().max()):.2e} vida {float((mc.vida-me.vida).abs().max()):.2e}', 'OK' if ok else 'FALHOU', flush=True)
sys.exit(0 if ok else 1)
