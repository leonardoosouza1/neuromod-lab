import sys, numpy as np, json, os; sys.path.insert(0,'/tmp')
from taxi_np import *
TR=[gerar_cidade(s) for s in range(6)]
TE=[gerar_cidade(900+s) for s in range(5)]
cfg=Cfg(1.0)
def evoluir(modo,P=300,ger=60,T=450,seed=0,elite=.15,ncid=3):
    r=np.random.default_rng(seed)
    W=r.standard_normal((P,NPAR))*.8
    M=np.ones((P,NPAR)) if modo!="crescer" else (r.random((P,NPAR))<.25).astype(float)
    hist=[]; espar=[]
    for it in range(ger):
        ids=r.choice(len(TR),ncid,replace=False)
        f=avaliar(W,M,[TR[i] for i in ids],cfg,T,seed+it*13)
        o=np.argsort(f)[::-1]; W=W[o]; M=M[o]; f=f[o]
        hist.append(float(f[0])); espar.append(float(M.mean()))
        ne=max(2,int(P*elite)); pw=W[:ne]; pm=M[:ne]
        idx=r.integers(0,ne,P-ne); fw=pw[idx].copy(); fm=pm[idx].copy()
        fr=it/ger
        if modo=="gerar":        sig,pd_,pr=.30,0.,0.
        elif modo=="gerar_fino": sig,pd_,pr=.15,0.,0.
        elif modo=="podar":      sig,pd_,pr=.15,.05,.015
        elif modo=="podar_forte":sig,pd_,pr=.15,.10,.01
        elif modo=="crescer":    sig,pd_,pr=.15,0.,.05
        else:
            if fr<.25:  sig,pd_,pr=.30,0.,0.
            elif fr<.75:sig,pd_,pr=.15,.06,.01
            else:       sig,pd_,pr=.06,0.,0.
        if modo=="crescer": fm=np.where(r.random((P-ne,NPAR))<pr,1.,fm)
        elif pd_>0:
            fm=np.where(r.random((P-ne,NPAR))<pd_,0.,fm)
            fm=np.where(r.random((P-ne,NPAR))<pr,1.,fm)
        fw=np.clip(fw+r.standard_normal((P-ne,NPAR))*sig,-5,5)
        W=np.vstack([pw,fw]); M=np.vstack([pm,fm])
    return W[0]*M[0],hist,M[0],espar
if __name__=="__main__":
    modo=sys.argv[1]; s=int(sys.argv[2])
    w,h,M,esp=evoluir(modo,seed=s)
    ents=[]; avs=[]
    for cid in TE:
        m=rodar(np.repeat(w[None],60,0),cid,cfg,1200,seed=7777)
        ents+=m.ent.tolist(); avs+=m.avar.tolist()
    out=dict(modo=modo,seed=s,fit=float(h[-1]),teste=float(np.mean(ents)),
             teste_dp=float(np.std(ents)),n=len(ents),avarias=float(np.mean(avs)),
             esparsidade=float(M.mean()),mask=M.tolist(),
             hist=[float(x) for x in h],esp_curva=esp)
    with open('/tmp/poda2.jsonl','a') as f: f.write(json.dumps(out)+'\n')
    print(f"{modo:<12} s{s}  fit {h[-1]:6.2f}  teste {np.mean(ents):6.1f}+-{np.std(ents):4.1f}"
          f"  conex {M.mean()*100:3.0f}%  n={len(ents)}")
