"""E43: baterias no CAMPO (mundo continuo). Bracos: linear, reflexo, minimo-3. Presets triagem/honesto. --L tamanho do mapa.
Saidas: /media/llm-data/universe-runs/neuromod-lab-taxi/e43/. So GPU (TORCHINDUCTOR_COMPILE_THREADS=1 no ambiente)."""
import sys, os, json, time, argparse, hashlib, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from campo import *
import lab
from completo import SerCompleto, SemTalamo, SemCortex, SemHipocampo, SemReflexo, SemLivre, SoCamadas, SemRapida, SemLenta, nomes_genes_completos
_PARTES = (('talamo', 'tal'), ('cortex', 'cor'), ('hipocampo', 'hip'), ('reflexo', 'ref'), ('rapida', 'rap'), ('lenta', 'len'))
def _ser_entrada(rotulo, nome, A, ov):
    """[10/09 seres no lote] um ser = SerCompleto com PARTES ligadas/desligadas (mascara de genes por nome + flags) e ajustes de cerebro; linear = so a espinha"""
    nomes = nomes_genes_completos(); liga = dict(SerCompleto.liga, rapida=True, lenta=True) if issubclass(A, SerCompleto) else dict(talamo=False, cortex=False, hipocampo=False, reflexo=False, livre=False, rapida=False, lenta=False)
    if issubclass(A, SerCompleto): liga.update(A.liga)
    if not liga['livre']: liga['rapida'] = liga['lenta'] = False
    msk = torch.ones(SerCompleto.NP, device=DEV)
    if not issubclass(A, SerCompleto): msk[Linear.NP:] = 0.
    for parte, pref in _PARTES:
        if not liga[parte]: msk[Linear.NP + torch.tensor([i for i, n in enumerate(nomes) if n.startswith(pref)], device=DEV)] = 0.
    ent = dict(rotulo=rotulo, nome=nome, **{k: float(v) for k, v in liga.items()}, **{k: (v if k == 'talamo_norm' else float(v)) for k, v in ov.items()}); return ent, msk
PRESETS = {'triagem': dict(P=1024, G=40, T_evo=1200, T_aval=1200, R=8, seeds=(0, 1, 2)),
           'honesto': dict(P=1024, G=120, T_evo=1200, T_aval=1200, R=16, seeds=(0, 1, 2, 3, 4)),
           'fumaca': dict(P=512, G=25, T_evo=1200, T_aval=1200, R=4, seeds=(0,))}
_BASE_CORPO = ['e_fuel', 'e_agua', 'e_fome', 'e_fadiga', 'e_calor', 'e_vida', 'e_dinheiro', 'e_reserva', 'e_tem_pax', 'h_sin', 'h_cos', 'e_noite', 'custo_aqui', 'bias', 'e_consumo', 'e_autonomia']
_LAYOUTS = {}   # NP linear antigo -> NOMES_F daquele layout (sem nomes_f gravado): base 26 sentidos; +risco; +risco+demanda+espera
for _extra in ([], ['e_risco'], ['e_risco', 'e_demanda', 'e_espera'], ['e_demanda', 'e_espera']):
    _nf = ['d_alvo', 'd_posto', 'd_comida', 'd_agua', 'd_oficina', 'd_descanso', 'custo_frente', 'preco_frente', 'aliq_frente', 'casa_frente'] + _BASE_CORPO + _extra   # NOMES_OP fixo dos layouts antigos
    _LAYOUTS[len(_nf) + S + 1] = _nf + [f'sv_{a[0]}{int(a[1]) if a[1] else ""}' for a in ACOES] + ['sv_bias']
def alinha_semente(v, nomes=None):
    """[E68 → pre-F3] semente LINEAR de outro layout de sentidos: mapeia gene por NOME (nomes = NOMES_F do JSON de origem, ou tabela
    por NP para JSONs antigos); sentido que nao existia nasce 0. Sentido novo em QUALQUER posicao (corpo ou opcao) fica correto.
    Maior que Linear.NP (arquitetura nao-linear): devolve como esta."""
    v = [float(x) for x in v]
    if len(v) > Linear.NP or (len(v) == Linear.NP and nomes is None): return v
    src = nomes or _LAYOUTS.get(len(v))
    if src is None or len(src) != len(v): raise SystemExit(f'alinha_semente: layout de origem desconhecido (NP {len(v)}); grave nomes_f no JSON')
    pos = {n: i for i, n in enumerate(src)}; return [v[pos[n]] if n in pos else 0. for n in NOMES_F]

BRACOS = [('linear', Linear), ('reflexo', Reflexo), ('produto (need x dist, portao)', Produto), ('modos gaussianos K=3', Modos), ('produto trend (olho multi-escala)', ProdutoTrend), ('reflexo 2 raizes (histerese)', ReflexoRaizes), ('reflexo alcance (km ate esvaziar)', ReflexoAlcance), ('cerebro livre (rapida+lenta, sem pista)', Cerebro), ('COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', SerCompleto), ('completo sem talamo', SemTalamo), ('completo sem cortex', SemCortex), ('completo sem hipocampo', SemHipocampo), ('completo sem reflexo', SemReflexo), ('completo sem livre (so camadas)', SoCamadas), ('completo sem rapida', SemRapida), ('completo sem lenta', SemLenta), ('minimo 3 (d_alvo, d_posto, e_fuel)', fabrica_minimo(['d_alvo', 'd_posto', 'e_fuel'])), ('minimo 4 (+autonomia)', fabrica_minimo(['d_alvo', 'd_posto', 'e_fuel', 'e_autonomia'])), ('bilinear (corpo x opcao)', Bilinear), ('bilinear autonomia+consumo', fabrica_bilinear(['e_autonomia', 'e_consumo']))] + ([('bilinear risco (esc 1)', fabrica_bilinear(['e_risco'], esc=1.)), ('bilinear risco (esc 3)', fabrica_bilinear(['e_risco'], esc=3.))] if 'e_risco' in NOMES_CORPO else []) + ([('bilinear risco+demanda+espera (esc 1)', fabrica_bilinear(['e_risco', 'e_demanda', 'e_espera'], esc=1.))] if 'e_demanda' in NOMES_CORPO and 'e_risco' in NOMES_CORPO else [])   # [E68]

def _set(a, dst, v):
    if dst not in getattr(a, '_explicit', ()): setattr(a, dst, v)
def aplica_cenario(a, cen):
    """[E71] cenario.json (doc 53) sobrescreve os flags; o que o cenario nao define fica como esta (identidade)."""
    if not hasattr(a, '_explicit'): a._explicit = set()   # [10/09 opus] chamador sem argv (politica_util.mundo -> trajetoria/julga/clona/dados_campeao) nao tem _explicit: sem isto, AttributeError desde o fix de precedencia de 09-09
    m = cen.get('mundo', {}); px = cen.get('passageiros', {}); co = cen.get('corpo', {}); pr = cen.get('protocolo', {})
    if co.get('reproducao') is not None and 'reproducao' not in a._explicit: a.reproducao = json.dumps(co['reproducao']) if isinstance(co['reproducao'], dict) else co['reproducao']
    if m.get('regime') is not None and 'regime' not in a._explicit: a.regime = json.dumps(m['regime']) if isinstance(m['regime'], dict) else m['regime']   # [spec F4]
    if m.get('retina') is not None and 'retina' not in a._explicit: a.retina = json.dumps(m['retina']) if isinstance(m['retina'], dict) else m['retina']   # [spec F3]
    for k, dst in (('L', 'L'), ('dias', 'dias'), ('regua', 'fitness'), ('nevoa', 'nevoa'), ('horizonte', 'horizonte'), ('T_max', 'T_max'), ('w_trab', 'w_trab'), ('corte_vivos', 'corte_vivos'), ('obs_rapido', 'obs_rapido'), ('obs_grade', 'obs_grade')):   # [spec F1] null = hoje
        if m.get(k) is not None: _set(a, dst, m[k])
    for k, dst in (('npx', 'npx'), ('respawn', 'respawn'), ('pax_cidade', 'pax_cidade'), ('ponto', 'ponto')):
        if px.get(k) is not None: _set(a, dst, px[k])
    for k, dst in (('dinh0', 'dinh0'), ('fome_passo', 'fome_passo'), ('kcal_pane', 'kcal_pane'), ('guincho', 'guincho'), ('fuel_pos_pane', 'fuel_pane'), ('custo_gene', 'custo_gene'), ('custo_basal', 'custo_basal'), ('orcamento_ativ', 'orcamento_ativ'), ('limiar_disparo', 'limiar_disparo'), ('custo_canais', 'custo_canais'), ('custo_modo', 'custo_modo'), ('ativ_centrada', 'ativ_centrada'), ('gene_min', 'gene_min'), ('custo_suave', 'custo_suave')):   # [spec 2.1] corpo.custo_*
        if co.get(k) is not None: _set(a, dst, co[k])
    for k, dst in (('P', 'P'), ('G', 'G'), ('paciencia', 'paciencia'), ('R', 'R'), ('seeds', 'seeds'), ('crn', 'crn'), ('sigma_mut', 'sigma_mut'), ('campeao', 'campeao'), ('jardim_comum', 'jardim_comum'), ('seres_juntos', 'seres_juntos')):
        if pr.get(k) is not None: _set(a, dst, pr[k])
    if cen.get('bracos') and a.so is None and 'so' not in a._explicit: a.so = cen['bracos']
    ce = cen.get('cerebro', {})
    for k, dst in (('talamo_norm', 'talamo_norm'), ('cortex_amp', 'cortex_amp'), ('temp_decisao', 'temp_decisao'), ('hip_esc', 'hip_esc')):
        if ce.get(k) is not None: _set(a, dst, ce[k])
    if cen.get('distritos'): a.mundo = 'distinto'
    return dict(perfis=cen.get('distritos') or None, K=m.get('K'), ruas=tuple(m['ruas'].get(k, d) for k, d in (('dentro', 1.), ('fora', 3.))) if m.get('ruas') else (1., 3.),
                amp_preco=(m.get('precos') or {}).get('amp'), periodo_preco=(m.get('precos') or {}).get('periodo'), tarifa_base=px.get('tarifa_base'), tarifa_km=px.get('tarifa_km'))

def cfg_de_flags(a, ex, T_aval):
    """[10/09 astra] UNICO lugar que monta o CfgCampo a partir dos flags (+ extras do cenario). main() e politica_util.mundo() chamam aqui:
    antes o juiz montava o cfg por fora e perdia custo_gene/custo_modo/custo_basal/ativ_centrada (campeoes avaliados noutro mundo)."""
    cfg = CfgCampo(L=a.L, pena_morte=a.pena, fitness=a.fitness, loja_no_posto=not a.sem_loja); cfg.custo_gene = a.custo_gene; cfg.custo_basal = a.custo_basal; cfg.orcamento_ativ = a.orcamento_ativ; cfg.custo_suave = a.custo_suave; cfg.gene_min = float(getattr(a, 'gene_min', cfg.gene_min)); cfg.jardim_comum = bool(a.jardim_comum); cfg.corte_vivos = float(a.corte_vivos); cfg.obs_rapido = bool(a.obs_rapido); cfg.obs_grade = bool(a.obs_grade); cfg.talamo_norm = (a.talamo_norm if a.talamo_norm in ('teto', 'fixo') else bool(a.talamo_norm)); cfg.hip_esc = a.hip_esc; cfg.cortex_amp = float(a.cortex_amp); cfg.temp_decisao = float(a.temp_decisao); cfg.custo_modo = a.custo_modo; cfg.ativ_centrada = bool(a.ativ_centrada); cfg.custo_canais = tuple(a.custo_canais) if isinstance(a.custo_canais, (list, tuple)) else tuple(x.strip() for x in a.custo_canais.split(',')); assert set(cfg.custo_canais) <= {'fome', 'agua', 'calor'} and 'fome' in cfg.custo_canais, cfg.custo_canais; cfg.limiar_disparo = a.limiar_disparo; cfg.amostra_ativ = a.amostra_ativ; cfg.varredura = a.varredura; cfg.KCAL_PANE = a.kcal_pane; cfg.dinh0 = a.dinh0; cfg.GUINCHO = a.guincho; cfg.FUEL_POS_PANE = a.fuel_pane; cfg.nevoa = a.nevoa; cfg.reproducao = (None if a.reproducao in (None, 'off') else (dict(REPRODUCAO_PADRAO) if a.reproducao == 'padrao' else json.loads(a.reproducao))); cfg.regime = (None if a.regime in (None, 'off') else (dict(REGIME_PADRAO) if a.regime == 'padrao' else json.loads(a.regime))); cfg.retina = (None if a.retina in (None, 'off') else (dict(RETINA_PADRAO) if a.retina == 'padrao' else json.loads(a.retina))); cfg.horizonte = a.horizonte; cfg.T_max = T_aval; cfg.w_trab = a.w_trab; cfg.ponto = a.ponto; cfg.NPX = a.npx; cfg.respawn = a.respawn; cfg.pax_cidade = a.pax_cidade
    for k in ('amp_preco', 'periodo_preco', 'tarifa_base', 'tarifa_km'):
        if ex.get(k) is not None: setattr(cfg, k, ex[k])
    if a.fome_passo is not None: cfg.fome_passo = a.fome_passo
    assert cfg.retina is None or RETINA, 'cenario/flag com retina exige NM_RETINA=1 no ambiente (senao a retina nao existe e o resultado e falso)'
    assert cfg.regime is None or REGIME, 'cenario/flag com regime exige NM_REGIME=1 no ambiente'
    return cfg

def main(a):
    a._explicit = {x[2:].split('=')[0].replace('-', '_') for x in sys.argv[1:] if x.startswith('--')}
    cen = json.load(open(a.cenario)) if a.cenario else {}; ex = aplica_cenario(a, cen)
    p = dict(PRESETS[a.preset]); os.makedirs(a.out, exist_ok=True)
    p['T_evo'] = p['T_aval'] = int(240*a.dias)          # vida em dias (5 dias = viver de poupanca e otimo; 10 obriga a trabalhar)
    if a.horizonte == 'aberto': p['T_evo'] = p['T_aval'] = int(a.T_max or 240*30)   # [spec F1] guarda dura do laco (30 dias); o laco sai antes se todos morrerem
    if a.seeds: p['seeds'] = tuple(a.seeds)
    if a.R: p['R'] = a.R
    if a.G: p['G'] = a.G
    if a.P: p['P'] = a.P   # [busca x8] populacao por semente
    cfg = cfg_de_flags(a, ex, p['T_aval'])
    if cfg.horizonte == 'aberto': print(f'  [F1] horizonte aberto: T_max {cfg.T_max} ticks; resultado INVALIDO se t_vida.frac_teto > 0.05', flush=True)
    gm = dict(L=a.L, distinto=a.mundo == 'distinto', perfis=ex['perfis'], K=ex['K'], ruas=ex['ruas'])
    treino = [gerar_mapa(s, **gm) for s in range(4)]; teste = [gerar_mapa(a.teste_seed + s, **gm) for s in range(3)]
    res = dict(nomes_f=NOMES_F, cenario=a.cenario, cenario_json=cen, cenario_hash=hashlib.md5(json.dumps(cen, sort_keys=True).encode()).hexdigest()[:10], dispositivo=dict(gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu', torch=torch.__version__, hip_ou_cuda=(torch.version.hip or torch.version.cuda)), argv=sys.argv[1:], predicao=cen.get('predicao'), ponto=a.ponto, npx=a.npx, respawn=a.respawn, pax_cidade=a.pax_cidade, nevoa=a.nevoa, preset=a.preset, L=a.L, fitness=a.fitness, pena=a.pena, NF=NF, S=S, bracos={})
    print(f'== E43 campo | {a.preset} L={a.L} dias={a.dias} regua={a.fitness} P={p["P"]} G={p["G"]} R={p["R"]} x{len(p["seeds"])} | pena {a.pena} | sigma_mut {a.sigma_mut} crn {a.crn} jardim {bool(a.jardim_comum)} ==', flush=True)
    _cls = dict(BRACOS); seres = [((b, b, {}) if isinstance(b, str) else (b.get('rotulo', b['nome']), b['nome'], dict(b.get('cerebro', {})))) for b in (a.so if a.so else [n for n, _ in BRACOS])]   # [10/09 Leonardo] um mundo, SERES diferentes: braco = nome da classe + rotulo + overrides de cerebro
    juntos = bool(a.seres_juntos) and all(issubclass(_cls[n], (Linear, SerCompleto)) for _, n, _ in seres); champs_j = None
    if juntos:   # [10/09 Leonardo: um mundo, seres diversos no MESMO lote] uma evolucao so: populacoes (semente x ser) no eixo S, genes travados por mascara, ajustes por ser
        ents, msks = zip(*[_ser_entrada(r, n, _cls[n], ov) for r, n, ov in seres]); cfg_j = copy.copy(cfg); cfg_j.seres = dict(P=p['P'], lista=list(ents))
        pops = [(sd, j) for sd in p['seeds'] for j in range(len(seres))]; masc = torch.stack([msks[j] for _, j in pops]); t0j = time.time(); W0 = None
        if a.init_from:
            JJ = json.load(open(a.init_from[0])); J = JJ['bracos'][a.init_from[1]]['W']; W0 = {sd: alinha_semente(J.get(str(sd), J[sorted(J)[sd % len(J)]]), JJ.get('nomes_f')) for sd in p['seeds']}
        print(f'  [seres no lote] {len(seres)} seres x {len(p["seeds"])} sementes = {len(pops)} populacoes de {p["P"]} num lote so', flush=True)
        champs_j = evoluir(SerCompleto, treino, cfg_j, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=True, W0=W0, paciencia=a.paciencia, sigma_espinha=a.sigma_espinha, sigma0=a.sigma0, crn=a.crn, sigma_mut=a.sigma_mut, campeao=a.campeao, pops=pops, mascaras=masc)
        print(f'  [seres no lote] evolucao conjunta em {round(time.time() - t0j)} s', flush=True)
    for jser, (rotulo, nome, ov) in enumerate(seres):
        A = _cls[nome]; cfg_b = copy.copy(cfg)
        for k, v in ov.items(): setattr(cfg_b, k, v)
        t1 = time.time(); W0 = None
        if champs_j is not None:
            champs = {sd: ((champs_j[(sd, jser)][0][:Linear.NP] if not issubclass(A, SerCompleto) else champs_j[(sd, jser)][0]), champs_j[(sd, jser)][1], champs_j[(sd, jser)][2]) for sd in p['seeds']}
        else:
            if cfg_b.orcamento_ativ is not None and not issubclass(A, Cerebro): print(f'  [aviso] orcamento_ativ={cfg_b.orcamento_ativ} nao se aplica ao braco {rotulo} (nao e Cerebro): roda sem orcamento', flush=True)
            if a.init_from:
                JJ = json.load(open(a.init_from[0])); J = JJ['bracos'][a.init_from[1]]['W']; W0 = {sd: alinha_semente(J.get(str(sd), J[sorted(J)[sd % len(J)]]), JJ.get('nomes_f')) for sd in p['seeds']}   # semente sem campeao no JSON (ex.: 3 sementes -> 5): usa o campeao de outra semente (ciclico)
            champs = (lab.evoluir_es(A, treino, cfg_b, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=True, W0=W0, paciencia=a.paciencia, avaliar_fn=avaliar, sigma_es=a.es_sigma, lr=a.es_lr) if a.otim == 'es'   # [E65] gradiente estimado, mesmo orcamento
                      else (lab.evoluir_sementes(A, treino, cfg_b, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=True, W0=W0, paciencia=a.paciencia, sigma_espinha=a.sigma_espinha, sigma0=a.sigma0, crn=a.crn, sigma_mut=a.sigma_mut, campeao=a.campeao, avaliar_fn=__import__('vida_hip').avaliar_hip) if (a.motor == 'hip' and A is Linear)
                  else evoluir(A, treino, cfg_b, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=True, W0=W0, paciencia=a.paciencia, sigma_espinha=a.sigma_espinha, sigma0=a.sigma0, crn=a.crn, sigma_mut=a.sigma_mut, campeao=a.campeao)))
        med = {}; por = {}
        for sd in p['seeds']:
            por[sd] = medidas(A, champs[sd][0], teste, cfg_b, T=p['T_aval'], seed=7777, R=1, copias=128)
        for k in por[p['seeds'][0]]:
            if isinstance(por[p['seeds'][0]][k], dict): med[k] = {b: sum(por[sd][k].get(b, 0.) for sd in p['seeds'])/len(p['seeds']) for b in por[p['seeds'][0]][k]}   # [spec I1a] dof_bloco: media por bloco
            else: med[k] = sum(por[sd][k] for sd in p['seeds'])/len(p['seeds'])
        # [regua pareada] por-semente para TODAS as medidas, nao so fit/mortos: as sementes sao as MESMAS em
        # todos os bracos, e comparar medias joga o pareamento fora (a variancia entre sementes entra duas vezes).
        for k in list(med):
            if isinstance(med[k], (int, float)): med[k + '_por_semente'] = [round(por[sd][k], 3) for sd in p['seeds']]   # dof_bloco (dict) fica so na media
        med['W'] = {sd: [float(x) for x in champs[sd][0]] for sd in p['seeds']}; med['segundos'] = round(time.time() - t1); med['otim'] = a.otim
        med['ger_efetiva'] = {str(sd): len(champs[sd][1]) for sd in p['seeds']}; med['seeds'] = list(p['seeds']); med['sigma_mut'] = (a.es_sigma if a.otim == 'es' else a.sigma_mut); med['crn'] = a.crn; med['campeao'] = a.campeao; med['ativ_centrada'] = bool(a.ativ_centrada); med['jardim_comum'] = bool(a.jardim_comum); med['corte_vivos'] = float(a.corte_vivos); med['obs_rapido'] = bool(a.obs_rapido); med['obs_grade'] = bool(a.obs_grade); med['motor'] = (a.motor if A is Linear else 'torch'); med['sigma0'] = a.sigma0; med['sigma_espinha'] = a.sigma_espinha; med['gene_min'] = cfg.gene_min; med['G'] = p['G']; med['P'] = p['P']; med['R'] = p['R']; med['T_evo'] = p['T_evo']; med['T_aval'] = p['T_aval']
        med['ser'] = dict(nome=nome, cerebro=ov, juntos=bool(champs_j is not None)); res['bracos'][rotulo] = med
        print(f'  {rotulo:<36} NP {A.NP:3d} fit {med["fit"]:6.2f} {med["fit_por_semente"]} ent {med["ent"]:5.1f} mortos {med["mortos"]:.2f} {med["mortos_por_semente"]} '
              f'panes {med["panes"]:4.1f} fome {med["fome_fim"]:3.0f} agua {med["agua_fim"]:3.0f} dinh {med["dinh"]:4.0f} res {med["res"]:4.0f} L/abast {med["litros_por_abast"]:4.0f} abast {med["n_posto"]:4.1f} dof {med["dof"]:4.0f} metab {med["metab"]:.2f} ({med["segundos"]}s)', flush=True)
        tmp = os.path.join(a.out, f'e43{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e43{a.tag}.json'))

def parser():
    ap = argparse.ArgumentParser()   # [10/09 astra] unico lugar dos flags: main() e politica_util.mundo() usam o mesmo parser
    ap.add_argument('--preset', default='triagem', choices=tuple(PRESETS)); ap.add_argument('--L', type=float, default=400.)
    ap.add_argument('--fitness', default='sobrevive', choices=('padrao', 'sobrevive', 'bemestar', 'riqueza', 'vida', 'filhos')); ap.add_argument('--horizonte', default='fixo', choices=('fixo', 'aberto'), help='[spec F1] aberto = roda ate todos morrerem ou T_max'); ap.add_argument('--T-max', type=int, default=None, help='[spec F1] guarda dura (default 240*30)'); ap.add_argument('--w-trab', type=float, default=1., help='[spec F1] peso da renda na regua vida: dias + w*renda/300'); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e43'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None); ap.add_argument('--G', type=int, default=None); ap.add_argument('--P', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--tag', default=''); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--sem-loja', action='store_true', help='servicos SEPARADOS: comida/agua nao vendidas no posto (E47)'); ap.add_argument('--init-from', nargs=2, default=None); ap.add_argument('--fome-passo', type=float, default=None, help='[calibracao doc 51] fome por tick (default .32)'); ap.add_argument('--guincho', type=float, default=0., help='[E61b] preco do guincho na pane'); ap.add_argument('--fuel-pane', type=float, default=15., help='[E61b] litros com que o guincho deixa o ser no posto'); ap.add_argument('--dinh0', type=float, default=20., help='dinheiro inicial (10 = pobre de verdade: 5 refeicoes)'); ap.add_argument('--kcal-pane', type=float, default=20., help='[E56c] calorias que a pane cobra da reserva (falta vira dano); 20 = pane mata, 8 = pane doi'); ap.add_argument('--paciencia', type=int, default=None, help='[E61d] parada antecipada: N ger. sem melhora > 1%'); ap.add_argument('--mundo', default='padrao', choices=('padrao', 'distinto'), help='[E56] distinto = ruas + distritos com perfil + precos que mudam'); ap.add_argument('--nevoa', type=float, default=float('inf'), help='[E63] raio de visibilidade dos servicos (m); alem dele a distancia satura. inf = onisciente (padrao, identico a hoje)'); ap.add_argument('--varredura', default='exata', choices=('exata', 'grade'), help='[chunks] grade = KG candidatos por celula (16x menos varredura)'); ap.add_argument('--orcamento-ativ', type=float, default=None, help='[CS E] orcamento de atividade por tick: soma das saidas dos blocos projetada para <= B (None = hoje)'); ap.add_argument('--custo-basal', type=float, default=0., help='[CS B1] metabolismo em repouso: lambda_basal x dof_existencia (0 = hoje); com ativacao, custo = basal + lambda_ativ x ativacao'); ap.add_argument('--motor', default='torch', choices=('torch', 'hip'), help='[10/09 kernel de vida inteira] hip = uma geracao inteira num kernel (so braco linear, NP 40, sem retina/regime/custo); o juiz (medidas) continua em torch'); ap.add_argument('--seres-juntos', action='store_true', help='[10/09] todos os seres do cenario evoluem no MESMO lote (populacoes semente x ser; genes travados por mascara; ajustes por ser): N seres pelo preco de 1'); ap.add_argument('--obs-grade', action='store_true', help='[reprojeto CS #2] servico mais perto pela grade 128x128 pre-computada (ponto escolhido no centro da celula; distancia exata a esse ponto): aproximado, portao de tolerancia testes_obs_grade'); ap.add_argument('--obs-rapido', action='store_true', help='[reprojeto CS #1+#3] obs() com constantes 0-dim e eixo de tipo vetorizado: identico bit a bit (portao testes_obs), 1.2x mais rapido'); ap.add_argument('--corte-vivos', type=float, default=0., help='[10/09] horizonte aberto: para a geracao quando a fracao de vivos <= isto (0 = hoje: so quando ninguem vive; o ultimo sobrevivente segurava 7200 ticks); os truncados entram em frac_teto'); ap.add_argument('--jardim-comum', action='store_true', help='[CS JARDIM-COMUM] sorteios do mundo (berco, passageiros, destinos, ponto, respawn) por BLOCO (NC*R), iguais para todos os genomas da geracao: selecao pareada; o juiz (medidas) fica SEMPRE fora do jardim'); ap.add_argument('--sigma-mut', type=float, default=.3, help='[09-09] desvio da mutacao gaussiana por filho (era .3 cravado em lab.evoluir_sementes; todos os genes mutam)'); ap.add_argument('--crn', default='rotativo', choices=('rotativo', 'fixo'), help='[09-09] sementes do mundo na avaliacao por geracao: rotativo = 777000+13*ger (hoje; ruido +-13%% entre geracoes, paciencia dispara por sorte); fixo = mesmas sementes em todas as geracoes (common random numbers; aptidao determinista por genoma)'); ap.add_argument('--campeao', default='ultimo', choices=('ultimo', 'reavaliado'), help='[10/09 opus, pred 166] ultimo = argmax da ultima geracao (hoje; maldicao do vencedor com SNR .72); reavaliado = a elite e reavaliada num mundo novo e o campeao sai da media das duas medidas (~.25 % do custo do run)'); ap.add_argument('--talamo-norm', default='', help='[CS brainstorm 1] denominador no talamo: teto (soma dos portoes <= NG) | fixo (soma == NG, divisiva canonica)'); ap.add_argument('--hip-esc', type=float, default=None, help='[CS bancada] escala da saida do hipocampo (None = Cerebro.ESC .01 de hoje; 1.0 = sem handicap)'); ap.add_argument('--cortex-amp', type=float, default=.5, help='[CS brainstorm 2] amplitude do delta do cortex (.5 = hoje; 2.0 pode inverter sinal)'); ap.add_argument('--temp-decisao', type=float, default=0., help='[CS brainstorm 4] temperatura da decisao (gumbel-max, escala = desvio das notas); 0 = argmax'); ap.add_argument('--custo-canais', default='fome', help='[CS eq.3] canais do corpo que a conta do cerebro multiplica: fome | fome,agua,calor'); ap.add_argument('--limiar-disparo', type=float, default=.25, help='[formulario] fracao de ativ_ref acima da qual o bloco DISPAROU'); ap.add_argument('--custo-modo', default='existencia', choices=('existencia', 'ativacao', 'disparo'), help='[spec F2] ativacao = o gene custa pelo sinal que emite (por bloco)'); ap.add_argument('--ativ-centrada', action='store_true', help='[10/09 opus, pred 165] a conta do bloco mede |saida - media entre as 9 opcoes| (o que muda a decisao) em vez de |saida| (99.7 % modo comum, descartado pelo G1 em campo.py um_passo)'); ap.add_argument('--amostra-ativ', type=int, default=10); ap.add_argument('--custo-suave', action='store_true', help='[CS] custo de gene sem degrau: w^2/(w^2+w0^2)'); ap.add_argument('--sigma0', type=float, default=.2, help='[pred 144] ruido de semeadura nos genes NOVOS (default .2 = hoje)'); ap.add_argument('--sigma-espinha', type=float, default=.05, help='[CS] ruido de semeadura na espinha copiada (genes novos usam sigma0 .2)'); ap.add_argument('--reproducao', default=None, help="[spec F5] 'padrao' | JSON dict(custo_kcal, limiar_res)"); ap.add_argument('--regime', default=None, help="[spec F4] 'padrao' | JSON dict(periodo_dias, amp, canais)"); ap.add_argument('--retina', default=None, help="[spec F3] 'padrao' | JSON dict(R_dia,R_noite,passo,custo,k_cego); exige NM_RETINA=1"); ap.add_argument('--cenario', default=None, help='[E71] cenario.json (doc 53): sobrescreve flags; o que nao define fica default'); ap.add_argument('--pax-cidade', action='store_true', help='[E70] passageiro nasce na cidade (~demanda) e o taxi vai buscar; reposicao ~ demanda do lugar'); ap.add_argument('--npx', type=int, default=12, help='[E69] passageiros privados por ser (12 = de hoje; 3 = escasso)'); ap.add_argument('--respawn', type=float, default=20., help='[E69] slot usado reaparece com prob demanda/(respawn*tarifa) por tick (20 = de hoje; 100 = escasso)'); ap.add_argument('--ponto', type=float, default=0., help='[E68] ponto de taxi: espera media (ticks) a demanda 1.0 para o passageiro vir ate o taxi parado; 0 = desligado'); ap.add_argument('--otim', default='ga', choices=('ga', 'es'), help='[E65] ga = selecao por elite; es = estrategia evolutiva antitetica (gradiente estimado), mesmo orcamento'); ap.add_argument('--es-sigma', type=float, default=.1); ap.add_argument('--es-lr', type=float, default=.3); ap.add_argument('--custo-gene', type=float, default=0., help='[E55] fome x (1 + custo*dof/100): cada gene ligado alem da espinha custa calorias')
    return ap
if __name__ == '__main__': main(parser().parse_args())
