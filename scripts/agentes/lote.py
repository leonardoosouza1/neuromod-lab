"""LAÇO CONTÍNUO (doc 53, v2 — 09/09 08:30): 8 agentes Sonnet EM PARALELO por lote, cada um com uma alavanca distinta; um job de juiz em
lote por lote; placar automático; realimentação com dados (autópsia, traço, placar, hipóteses); consolidação Opus a cada K lotes.
Fases: gerar | placar | loop (roda gerar→espera juiz→placar→próxima tarefa, lote atrás de lote, em setsid nohup)."""
import sys, os, json, re, subprocess, argparse, glob, time
from concurrent.futures import ThreadPoolExecutor
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(REPO, 'scripts'))
CLAUDE = '/home/leonardo/.local/bin/claude'; R = '/media/llm-data/universe-runs/neuromod-lab-taxi'; DA = os.path.join(REPO, 'docs', 'agentes'); ENV = {'NM_RISCO': '1', 'NM_PONTO': '1'}
ALAVANCAS = ['limiar de COMIDA no posto e fora (fome)', 'AGUA: quando e quanto comprar', 'TRABALHO/LUGAR: quando LIVRE (sem passageiro, sem compra pendente), para onde ir — desempate por preco_frente (tarifa x pmul do distrito a frente) e aliq_frente, ou rumo ao centro; NUNCA mude o resto', 'GASOLINA: quantos litros por parada conforme dinheiro', 'PARADA MINIMA: no raio do posto decidir tudo em <= 2 ticks (100 L se dinheiro >= 35 senao 50; comida se fome > .3; nada mais) e sair — sem quebrar as compras que ja funcionam', 'TRABALHO/CORRIDA: preferir passageiro cujo DESTINO e mais longe/mais caro? (so d_alvo esta visivel: use e_tem_pax e preco_frente para decidir se vale seguir reto ou cacar em outro distrito)', 'RUA: penalizar sair da rua (custo_frente) ao ir ao alvo', 'LIVRE: qualquer coisa que os dados do campeao sugiram e ninguem testou (ver hipoteses.md)']
def ler(p, n=None):
    s = open(p).read() if os.path.exists(p) else ''; return s if n is None else s[-n:]
def api():
    sys.path.insert(0, os.path.join(REPO, 'src')); os.environ.setdefault('NM_RISCO', '1'); os.environ.setdefault('NM_PONTO', '1')
    import campo
    ac = [f'{k}: {t} {int(q) if q else ""}'.strip() for k, (t, q) in enumerate(campo.ACOES)]
    return f"""## CONTRATO politica.py (o juiz executa na GPU; nada e' aceito pelo que voce diz, so pelo que o simulador mede)
Defina `fabrica()` que devolve uma CLASSE com EXATAMENTE: `def reset(self, m, W)`, `def extra(self, m, W, F)` -> torch.zeros(m.B, G) e guarda self.F = F, `def decidir(self, tudo, m)` -> LongTensor (m.B,), `def atualizar(self, m)`. Nao acrescente parametros. Use device=DEV em todo tensor novo.
- F (B, G=9, NF={campo.NF}): opcao g (8 direcoes + ficar = g 8); colunas 0..9 = NOMES_OP {campo.NOMES_OP} (distancias em unidades andadas APOS a opcao; d_alvo = passageiro mais perto ou destino se carrega); colunas 10.. = NOMES_CORPO {campo.NOMES_CORPO} (iguais nas 9 opcoes; escalas 0..1; dinheiro/150; autonomia=(tanque/consumo - d_posto)/100; e_risco > 0 = luz de reserva acesa).
- tudo (B, G+S): G+k = servico k DISPONIVEL e pago (> -1e8). ORDEM EXATA (S={campo.S}): {ac}. Comprar = devolver G+k. Uma acao por tick: para comprar duas coisas fique no raio (a politica e' chamada de novo no tick seguinte). A LOJA do posto vende comida e agua. Servico disponivel exige distancia < 6.
- m: m.fuel, m.agua, m.fome, m.fad, m.calor, m.vida, m.dinh, m.res, m.pd_ (>=0 carregando), m.hora(), m.noite_(), m.B (tensores (B,)).
- Proibido: importar alem de torch/math; ler m.px/m.pxd/m.serv/m.g/m.dest; os/sys/open/exec. Vetorizado (sem loop por ser).
- Constantes: fuel_passo .15/tick andando (tanque 100; preco_L .3 x pmul do distrito), agua_passo .08 (+.12 com calor), fome_passo .32 (REFEICAO 90, custa 2 x pmul), calor sobe .15 andando/desce .6 parado (92 = pane de calor, 6 de dano), pane de gasolina = 8 kcal da reserva + 6 de dano + guincho ate o posto com 15 L, tarifa 3 + .25/u x pmul, aluguel 4 x alug/dia, divida limite 60, oficina 10 (+25 vida, calor 25), hotel 8, dinh0 10, 10 dias = 2400 ticks."""
def contexto(lote):
    placar = ler(os.path.join(DA, 'placar.md'), 6000); dados = ler(os.path.join(DA, 'dados_campeao.md'), 6000); hip = ler(os.path.join(DA, 'hipoteses.md'), 5000)
    fb = ler(os.path.join(DA, 'lotes', f'L{lote-1}', 'feedback.md'), 6000) if lote > 1 else ''
    notas = ler(os.path.join(DA, 'notas_consolidador.md'), 5000)
    return f"# CONTEXTO (neuromod-lab, taxi na GPU — prova por construcao)\nTaxis com corpo sobrevivem 10 dias numa cidade com distritos, servicos e passageiros. O campeao EVOLUIDO morre 0.85. Politicas explicitas ja batem ele (0.73). Sua tarefa: uma politica MELHOR, mudando UMA alavanca.\n{api()}\n## DADOS MEDIDOS DO CAMPEAO E DA MELHOR POLITICA\n{dados}\n## PLACAR (melhores ate agora)\n{placar}\n## HIPOTESES JA TESTADAS (nao repita)\n{hip}\n## FEEDBACK DO LOTE ANTERIOR\n{fb}\n## NOTAS DO CONSOLIDADOR (leia: dados e ordens que valem para TODOS os lotes)\n{notas}\n"
def chama(prompt, model, timeout=900):
    try: r = subprocess.run([CLAUDE, '-p', prompt, '--model', model, '--output-format', 'json', '--no-session-persistence'], capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, env={**os.environ, 'CLAUDE_CONFIG_DIR': '/media/llm-data/universe-runs/neuromod-lab-taxi/agentes/claude-config'})   # config limpa (credenciais copiadas, SEM plugins): o hook do claude-mem bloqueava 75% das chamadas paralelas   # sem stdin: o hook do claude-mem esperava 3 s e falhava
    except subprocess.TimeoutExpired: return ''
    try: return json.loads(r.stdout).get('result', r.stdout)
    except Exception: return r.stdout or r.stderr
def bloco(txt, lang):
    if lang == 'python':   # tolerante: ```python, ```py ou ``` sem linguagem, desde que tenha def fabrica; pega o MAIOR bloco
        cands = [b for b in re.findall(r'```(?:python|py)?[ \t]*\n(.*?)```', txt, re.S) if 'def fabrica' in b]
        return cands[-1].strip() if cands else None   # o ULTIMO: respostas sujas pelo hook ecoam o prompt (com o codigo-base) antes da resposta
    m = re.search(r'```' + lang + r'\s*(.*?)```', txt, re.S); return m.group(1).strip() if m else None
def melhor_politica():
    pj = os.path.join(DA, 'placar.json'); P = json.load(open(pj)) if os.path.exists(pj) else []
    ok = sorted([p for p in P if 'mortos' in p], key=lambda p: p['mortos'])
    return ok[0]['politica'] if ok else os.path.join(REPO, 'src', 'politicas', 'campeao_explicito_r7_1.py')
def gerar(a):
    out = os.path.join(DA, 'lotes', f'L{a.lote}'); os.makedirs(out, exist_ok=True); base = a.base or melhor_politica(); ctx = contexto(a.lote); tarefa = ler(a.tarefa)
    def um(i):
        al = ALAVANCAS[(i - 1) % len(ALAVANCAS)]
        pr = f"{ctx}\n# SUA TAREFA (lote {a.lote}, agente {i})\n{tarefa}\nSUA ALAVANCA: **{al}**. Mude so isso na politica base abaixo (copie o resto). Justifique os numeros com os DADOS medidos.\nFORMATO: uma linha `PREDICAO: ...` e depois UM bloco ```python``` com o arquivo completo.\n\n```python\n{open(base).read()}\n```"
        open(os.path.join(out, f'p{i}.prompt.md'), 'w').write(pr)
        if a.dry_run: return i, 'dry', al
        txt = chama(pr, a.model); open(os.path.join(out, f'p{i}.resposta.md'), 'w').write(txt); py = bloco(txt, 'python'); pms = re.findall(r'PREDICAO:(.*)', txt); pm = pms[-1] if pms else ''
        if not py: return i, 'RECUSADO: sem bloco python', al
        if re.sub(r'\s+', '', py) == re.sub(r'\s+', '', open(base).read()): return i, 'RECUSADO: igual a base (sem mudanca)', al
        open(os.path.join(out, f'p{i}.politica.py'), 'w').write(py); json.dump({'alavanca': al, 'predicao': pm.strip()}, open(os.path.join(out, f'p{i}.meta.json'), 'w'), ensure_ascii=False)
        return i, 'ok', al
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.n) as ex: rs = list(ex.map(um, range(1, a.n + 1)))
    for i, st, al in rs: print(f'  p{i} [{al[:30]}]: {st}', flush=True)
    arqs = sorted(glob.glob(os.path.join(out, 'p*.politica.py'))); print(f'lote {a.lote}: {len(arqs)} politicas em {time.time()-t0:.0f}s', flush=True)
    if arqs and not a.dry_run:
        import nmd_cliente as c; c.pedir(f'l{a.lote}_lote', 'julga_lote', out='agentes', env=ENV, politicas=arqs, tag=f'_l{a.lote}', confirma=a.confirma, **({'cenario': a.cenario} if a.cenario else {}))
        print(f'  enfileirado l{a.lote}_lote', flush=True)
    return len(arqs)
def placar(a):
    out = os.path.join(DA, 'lotes', f'L{a.lote}'); lj = os.path.join(R, 'agentes', f'lote_l{a.lote}.json')
    if not os.path.exists(lj): print('sem resultado do juiz ainda'); return False
    L = json.load(open(lj)); pj = os.path.join(DA, 'placar.json'); P = json.load(open(pj)) if os.path.exists(pj) else []
    linhas = []
    for r in L['res']:
        meta = json.load(open(os.path.join(out, r['nome'] + '.meta.json'))) if os.path.exists(os.path.join(out, r['nome'] + '.meta.json')) else {}
        if 'med' in r:
            m = r['med']; e = dict(lote=a.lote, nome=r['nome'], politica=r['politica'], alavanca=meta.get('alavanca'), predicao=meta.get('predicao'), mortos=m['mortos'], ent=m['ent'], cor_dia=m['ent']/max(m['mortos']*m['dia_morte'] + (1 - m['mortos'])*10., 1e-6), rec=m['rec'], n_come=m['n_come'], n_posto=m['n_posto'], panes=m['panes'], dia=m['dia_morte'], c_fome=m['c_fome'], c_dano=m['c_dano'], c_sede=m['c_sede'], mortos5=(r.get('med5') or {}).get('mortos'))
            P.append(e); linhas.append(f"| L{a.lote} {r['nome']} | {meta.get('alavanca','')[:40]} | {m['mortos']:.2f} | {m['ent']:.1f} ({m['ent']/max(m['mortos']*m['dia_morte'] + (1 - m['mortos'])*10., 1e-6):.2f}/dia) | {m['n_come']:.1f} | {m['dia_morte']:.1f} | fome {100*m['c_fome']:.0f} % / dano {100*m['c_dano']:.0f} % / sede {100*m['c_sede']:.0f} % | {(meta.get('predicao') or '')[:70]} |")
        else: linhas.append(f"| L{a.lote} {r['nome']} | {meta.get('alavanca','')[:40]} | ERRO | | | | {r.get('erro','')[:60]} | |")
    json.dump(P, open(pj, 'w'), indent=1, ensure_ascii=False)
    ok = sorted([p for p in P if 'mortos' in p], key=lambda p: p['mortos'])[:15]
    md = ['# Placar (juiz: simulador; 3 sementes x 128 copias x 3 mapas; campeao evoluido = %.2f)' % L['baseline']['mortos'], '', '| lote/politica | alavanca | mortos | corridas (por dia vivo) | refeicoes | dia | causa | predicao do agente |', '|---|---|---|---|---|---|---|---|']
    md += [f"| L{p['lote']} {p['nome']} | {(p['alavanca'] or '')[:40]} | **{p['mortos']:.2f}** | {p['ent']:.1f} ({p.get('cor_dia', 0):.2f}/dia) | {p['n_come']:.1f} | {p['dia']:.1f} | fome {100*p['c_fome']:.0f} % / dano {100*p['c_dano']:.0f} % | {(p['predicao'] or '')[:60]} |" for p in ok]
    open(os.path.join(DA, 'placar.md'), 'w').write('\n'.join(md) + '\n')
    fb = [f"# Feedback do lote {a.lote} (medido pelo juiz; campeao {L['baseline']['mortos']:.2f}; melhor global {ok[0]['mortos']:.2f} = {ok[0]['nome']} L{ok[0]['lote']})", '', '| politica | alavanca | mortos | corridas (por dia vivo) | refeicoes | dia | causa | predicao |', '|---|---|---|---|---|---|---|---|'] + linhas
    open(os.path.join(out, 'feedback.md'), 'w').write('\n'.join(fb) + '\n'); print('\n'.join(fb), flush=True); return True
def consolidar(a):
    """Opus le placar + feedbacks dos ultimos K lotes e escreve a proxima tarefa (regras, numeros, o que nao repetir) + hipoteses novas"""
    fbs = '\n\n'.join(ler(os.path.join(DA, 'lotes', f'L{k}', 'feedback.md'), 5000) for k in range(max(1, a.lote - a.K + 1), a.lote + 1))
    notas = ler(os.path.join(DA, 'notas_consolidador.md'))
    pr = f"Voce e' o consolidador (Opus) de uma busca por politicas explicitas para taxis que sobrevivem 10 dias (juiz = simulador). ANTES DE TUDO leia as NOTAS DO SUPERVISOR (Fable), que corrigem erros seus de lotes anteriores e VALEM MAIS que a sua propria analise:\n{notas}\n\nLeia o placar, os dados medidos do campeao, as hipoteses ja testadas e os feedbacks dos ultimos {a.K} lotes. Escreva, em portugues, curto e concreto: (1) o que os dados dizem que ainda mata a melhor politica e qual alavanca tem mais chance (com numeros); (2) a TAREFA do proximo lote (texto de ate 12 linhas, com limiares numericos sugeridos por alavanca); (3) linhas novas para hipoteses.md (formato | # | hipotese | resultado | onde |). Responda com tres blocos: ```tarefa``` ```hipoteses``` e um paragrafo livre.\n\n## PLACAR\n{ler(os.path.join(DA,'placar.md'))}\n## DADOS DO CAMPEAO\n{ler(os.path.join(DA,'dados_campeao.md'))}\n## HIPOTESES\n{ler(os.path.join(DA,'hipoteses.md'))}\n## FEEDBACKS\n{fbs}"
    txt = chama(pr, 'opus', timeout=900); open(os.path.join(DA, 'lotes', f'L{a.lote}', 'consolidacao_opus.md'), 'w').write(txt)
    t = bloco(txt, 'tarefa'); h = bloco(txt, 'hipoteses')
    if t: open(os.path.join(DA, f'tarefa_L{a.lote+1}.md'), 'w').write(t + '\n'); print('tarefa da proxima escrita pelo Opus', flush=True)
    if h: open(os.path.join(DA, 'hipoteses.md'), 'a').write('\n' + h + '\n')
    return bool(t)
def espera(pid, tmax=3600):
    import nmd_cliente as c; t0 = time.time()
    while time.time() - t0 < tmax:
        if c.estado(pid).get('fase') == 'terminou': return True
        time.sleep(20)
    return False
def loop(a):
    for lote in range(a.de, a.ate + 1):
        a.lote = lote; existentes = [k for k in range(lote, 0, -1) if os.path.exists(os.path.join(DA, f'tarefa_L{k}.md'))]
        a.tarefa = (a.tarefa if lote == a.de and a.tarefa else None) or os.path.join(DA, f'tarefa_L{existentes[0]}.md')   # a mais recente que existe (bug: lote 6 rodou com tarefa vazia)
        print(f'===== LOTE {lote} ({time.strftime("%H:%M")}) tarefa {os.path.basename(a.tarefa)} =====', flush=True); a.base = None
        import nmd_cliente as c
        if c.estado(f'l{lote}_lote').get('fase') in ('rodando', 'terminou', 'na fila') or os.path.exists(os.path.join(R, 'agentes', f'lote_l{lote}.json')): print(f'lote {lote} ja gerado/julgado: pulando gerar', flush=True); n = 1
        else: n = gerar(a)
        if n == 0: print('lote vazio; seguindo'); continue
        if not espera(f'l{lote}_lote'): print('juiz nao terminou em 1 h; seguindo', flush=True); continue
        placar(a)
        if lote % a.K == 0: consolidar(a)
    print('===== FIM DO LACO =====', flush=True)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('fase', choices=['gerar', 'placar', 'consolidar', 'loop']); ap.add_argument('--lote', type=int, default=1); ap.add_argument('--de', type=int, default=1); ap.add_argument('--ate', type=int, default=6)
    ap.add_argument('--n', type=int, default=8); ap.add_argument('--K', type=int, default=3); ap.add_argument('--model', default='sonnet'); ap.add_argument('--tarefa', default=None); ap.add_argument('--base', default=None); ap.add_argument('--cenario', default=None)
    ap.add_argument('--confirma', type=int, default=2); ap.add_argument('--dry-run', action='store_true'); a = ap.parse_args()
    {'gerar': gerar, 'placar': placar, 'consolidar': consolidar, 'loop': loop}[a.fase](a)
