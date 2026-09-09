"""Orquestrador por FASES (doc 53). gerar: chama Sonnet por grupo (claude -p, assinatura), valida a saida, salva em docs/agentes/r<N>/ e enfileira
no nmd. consolidar: le os resultados julgados, chama Opus para 3 insights + tarefas da proxima rodada. Sem processo longo: cada fase termina."""
import sys, os, json, re, subprocess, argparse, glob, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(REPO, 'scripts'))
CLAUDE = '/home/leonardo/.local/bin/claude'; R = '/media/llm-data/universe-runs/neuromod-lab-taxi'
BRACOS = ['linear', 'COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', 'bilinear risco+demanda+espera (esc 1)', 'bilinear risco (esc 3)', 'bilinear (corpo x opcao)', 'reflexo', 'minimo 3 (d_alvo, d_posto, e_fuel)']
def ler(p, n=None):
    s = open(os.path.join(REPO, p)).read(); return s if n is None else s[-n:]
def contexto():
    preds = [l for l in ler('PREDICOES.md').split('\n') if l.startswith('| 9')][-8:]
    return f"""# CONTEXTO (neuromod-lab, taxi na GPU)
Seres = taxis com corpo (gasolina, agua, fome, fadiga, calor, vida, dinheiro, reserva) que precisam sobreviver 10 dias (2400 ticks; 1 tick = 6 min)
numa cidade continua 200x200 com distritos (perfis centro/industrial/residencial/periferia), ruas (custo 1 na rua, 3 fora), servicos (posto, comida,
agua, descanso, oficina) e passageiros. Cerebros evoluidos por selecao. Achados: (84) no Linear os sentidos do corpo sao invisiveis na direcao;
(E64-E67) o campeao linear e' um pico local da regua 'riqueza 10 dias' (busca x4, gradiente e ruido nao mudam; morre 0.82); (E68, pred 95) o campeao
anda 82% do tempo, 67% com passageiro, espera livre 3%: no mundo antigo o passageiro nascia perto do taxi, entao lugar nao tinha preco;
(E70, rodando) passageiro agora nasce NA CIDADE (pax_cidade). Regra da casa: negativo com mecanismo e' resultado; predicao ANTES de rodar; sem portao desenhado a mao no cerebro.
## Ultimas predicoes (ledger)
{chr(10).join(preds)}
## Contrato cenario.json e regras (doc 53)
{ler('docs/53-agentes-cenarios.md')}
## cenarios/base.json (mundo de hoje; tudo que voce nao mudar fica assim)
{ler('cenarios/base.json')}
## Constantes do corpo (CfgCampo): fuel_passo .15/tick andando (tanque 100, posto vende a preco_L .3/L x pmul do distrito), agua_passo .08, fome_passo .32 (REFEICAO 90 por 2 x pmul),
fad_passo .15, calor sobe .15 andando e desce .6 parado (CALOR_MAX 92 = pane de calor), pane de gasolina = KCAL_PANE 8 de reserva + reboque ate o posto com 15 L,
tarifa 3 + .25 por unidade x pmul do distrito de origem, aluguel 4 x alug do distrito-casa por dia, LIMITE_DIVIDA 60, HOTEL 8, oficina 10 (REPARO 25 de vida), dinh0 10.
## Bracos disponiveis: {BRACOS}
## CALIBRACAO MEDIDA (rodada 1) — leia antes de escolher numeros
linear e' o controle e TEM de ficar com mortos entre 0.40 e 0.80, senao a regua crava e o cenario e' recusado. Medidas: passageiro perto do taxi (pax_cidade false, npx 12) -> linear 0.83, 18 entregas, renda 165;
cidade (pax_cidade true, npx 12, respawn 20) -> linear 0.93, 11 entregas, renda ~110, COMPLETO 0.91 (piso: todos morrem igual); cidade + npx 5 + respawn 80 + periferia dem .05 -> 1.00 e 3 entregas (letal).
Politicas explicitas da rodada 1 (2 agentes) morreram 1.00 de FOME com 2-4 entregas: estacionaram e nunca compraram comida (refeicoes 0). O oraculo a mao tambem morre 1.00. O campeao evoluido, medido pelo mesmo juiz: 0.85, 17.7 entregas, 6.8 panes.
"""
API_POL = """## Contrato politica.py (agente escreve; o juiz executa em GPU com 3 mundos de teste x 128 copias x 5 sementes)
Defina `fabrica()` que devolve uma CLASSE (nao instancia) com EXATAMENTE estes metodos e assinaturas Python (self e' o objeto, como sempre): `def reset(self, m, W)`, `def extra(self, m, W, F)` -> devolve torch.zeros(m.B, G) e guarda self.F = F, `def decidir(self, tudo, m)` -> LongTensor (m.B,), `def atualizar(self, m)`. NAO acrescente parametros extras (na rodada 3 os agentes escreveram `def reset(self, s, m, W)` e crasharam).
- F (B, G=9, NF) = observacao: para cada opcao de movimento g (8 direcoes + ficar = g 8), colunas 0..9 = NOMES_OP = ['d_alvo','d_posto','d_comida','d_agua','d_oficina','d_descanso','custo_frente','preco_frente','aliq_frente','casa_frente']
  (distancias em unidades andadas APOS a opcao; d_alvo = passageiro mais perto ou destino se carrega) e colunas 10.. = NOMES_CORPO (iguais nas 9 opcoes):
  ['e_fuel','e_agua','e_fome','e_fadiga','e_calor','e_vida','e_dinheiro','e_reserva','e_tem_pax','h_sin','h_cos','e_noite','custo_aqui','bias','e_consumo','e_autonomia','e_risco','e_demanda','e_espera'] (escalas 0..1; dinheiro /150; autonomia = (tanque/consumo - d_posto)/100).
- tudo (B, G+S): colunas 0..G-1 = notas de movimento (ignore), G+k = servico k DISPONIVEL e pago (> -1e8). ORDEM EXATA (S=10), indice k -> acao: ['0: posto 25', '1: posto 50', '2: posto 75', '3: posto 100', '4: posto 150', '5: agua 50', '6: agua 100', '7: comida', '8: descanso', '9: oficina']. Ex.: comprar 'comida' = devolver G + 7; 'posto 100' = G + 3. Use `tudo[:, G+k] > -1e8` para saber se a acao k pode ser comprada AQUI e AGORA (esta no raio 6 do servico e tem dinheiro). A LOJA do posto vende comida e agua (loja_no_posto): no posto, comida/agua tambem ficam disponiveis. Distancias F[:, :, 1..5] sao ate posto/comida/agua/oficina/descanso; servico 'disponivel' exige d < 6.
- Corpo em m (tensores (B,)): m.fuel, m.agua, m.fome, m.fad, m.calor, m.vida, m.dinh, m.res, m.pd_ (>=0 carregando), m.hora() (0..24), m.noite_(), m.B.
- Devolva por ser: um indice de movimento 0..8 (use argmin de uma coluna de F para 'ir ao alvo'), ou G + indice do servico para comprar.
- Proibido: importar alem de torch/math, ler m.px/m.pxd/m.serv/m.g/m.dest, chamar os/sys/open/exec. Tudo vetorizado em torch (sem loop por ser).
- RODADAS 1-2 MORRERAM POR CULPA DO CONTRATO: a ordem de ACOES estava errada no prompt (comida era indexada como posto 100 L). Agora a ordem acima e' a do codigo. Nao invente indices: use a tabela.
- Exemplo minimo (o oraculo que morreu 1.00): ir ao passageiro; se e_fuel < .4 ir ao posto e encher quando disponivel; se fome > .8 comer. Faca melhor: margem de alcance (autonomia), comer quando ja esta no posto, evitar centro caro sem dinheiro, descansar de madrugada."""
def prompt_de(grupo, g, i, rod):
    base = contexto(); saida = ('Responda com UM bloco ```json``` contendo o cenario.json completo (campo "predicao" obrigatorio, com numeros e mecanismo) e nada mais.' if g['tipo'] == 'cenario'
             else API_POL + '\nResponda com UM bloco ```python``` com o politica.py completo, e antes dele UMA linha `PREDICAO: ...` com mortos, entregas e o que mata.')
    return f"{base}\n# SUA TAREFA (grupo '{grupo}', agente {i}, rodada {rod})\n{g['tarefa']}\nSeja diferente dos outros agentes do grupo: agente {i} deve escolher uma abordagem distinta (variacao {i}).\n{saida}"
def chama(prompt, model, timeout=900):
    try: r = subprocess.run([CLAUDE, '-p', prompt, '--model', model, '--output-format', 'json', '--no-session-persistence'], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired: return ''   # agente lento demais: vira RECUSADO, o laco segue
    try: return json.loads(r.stdout).get('result', r.stdout)
    except Exception: return r.stdout or r.stderr
def bloco(txt, lang):
    m = re.search(r'```' + lang + r'\s*(.*?)```', txt, re.S); return m.group(1).strip() if m else None
def json_tolerante(js):
    """agente escreve JSON com comentarios // e virgula sobrando: limpa antes de recusar"""
    js = re.sub(r'//[^\n]*', '', js); js = re.sub(r'/\*.*?\*/', '', js, flags=re.S); js = re.sub(r',(\s*[}\]])', r'\1', js); return json.loads(js)
def gerar(a):
    grupos = json.load(open(os.path.join(REPO, 'scripts', 'agentes', a.grupos))); out = os.path.join(REPO, 'docs', 'agentes', f'r{a.rodada}'); os.makedirs(out, exist_ok=True)
    import nmd_cliente as c; pedidos = []
    for nome, g in grupos.items():
        if a.so and nome not in a.so: continue
        for i in (a.agentes or range(1, a.n + 1)):
            pr = prompt_de(nome, g, i, a.rodada); open(os.path.join(out, f'{nome}_{i}.prompt.md'), 'w').write(pr)
            if a.dry_run: print(f'[dry] {nome}_{i}: prompt {len(pr)} chars'); continue
            t0 = time.time(); txt = chama(pr, a.model); open(os.path.join(out, f'{nome}_{i}.resposta.md'), 'w').write(txt); print(f'{nome}_{i}: resposta {len(txt)} chars em {time.time()-t0:.0f}s', flush=True)
            if not txt: print('  RECUSADO: sem resposta (timeout)', flush=True); continue
            env = {'NM_RISCO': '1', 'NM_PONTO': '1'}; pid = f'r{a.rodada}_{nome}{i}'
            if g['tipo'] == 'cenario':
                js = bloco(txt, 'json')
                try: cen = json_tolerante(js)
                except Exception as e: print(f'  RECUSADO (json): {e}'); continue
                if not cen.get('predicao'): print('  RECUSADO: sem predicao'); continue
                if a.triagem: cen['protocolo'] = {'P': 512, 'G': 60, 'paciencia': 30, 'R': 4, 'seeds': [0, 1, 2, 3, 4]}   # juiz rapido (~10 min por cenario de 4 bracos); a rodada final usa o protocolo cheio
                cp = os.path.join(out, f'{nome}_{i}.cenario.json'); json.dump(cen, open(cp, 'w'), indent=1)
                c.pedir(pid, 'e43_campo', out=f'agentes_r{a.rodada}', env=env, preset='fumaca', cenario=cp, tag=f'_{pid}', **{'init-from': [R + '/e64/e43_busca8x_L200.json', 'linear'], 'sigma-espinha': 0.05})
            else:
                py = bloco(txt, 'python'); pm = re.search(r'PREDICAO:(.*)', txt)
                if not py or not pm: print('  RECUSADO: sem bloco python ou sem PREDICAO'); continue
                pp = os.path.join(out, f'{nome}_{i}.politica.py'); open(pp, 'w').write(py); json.dump({'predicao': pm.group(1).strip()}, open(os.path.join(out, f'{nome}_{i}.cenario.json'), 'w'))
                c.pedir(pid, 'julga_politica', out=f'agentes_r{a.rodada}', env=env, politica=pp, tag=f'_{pid}')
            pedidos.append(pid); print(f'  enfileirado {pid}', flush=True)
    pp = os.path.join(out, 'pedidos.json'); antigos = json.load(open(pp)) if os.path.exists(pp) else []
    todos = antigos + [x for x in pedidos if x not in antigos]; json.dump(todos, open(pp, 'w')); print('pedidos desta chamada:', pedidos, '| todos da rodada:', todos)
def consolidar(a):
    out = os.path.join(REPO, 'docs', 'agentes', f'r{a.rodada}'); pedidos = json.load(open(os.path.join(out, 'pedidos.json'))); import nmd_cliente as c
    partes = []
    for pid in pedidos:
        est = c.estado(pid); log = ''
        try: log = open(os.path.join(R, '_nmd', 'log', pid + '.log')).read()
        except Exception: pass
        log = '\n'.join(l for l in log.split('\n') if not ('Warn' in l or 'W0908' in l))[-4000:]
        nome = pid.split('_', 1)[1]; pred = json.load(open(os.path.join(out, f'{nome[:-1]}_{nome[-1]}.cenario.json'))).get('predicao')
        partes.append(f'## {pid} (fase {est.get("fase")})\nPREDICAO DO AGENTE: {pred}\nRESULTADO (log do juiz):\n{log}\n')
    pr = f"""Voce e' o consolidador (Opus) de uma rodada de agentes que criaram cenarios/politicas para o taxi (doc 53). Abaixo, a predicao de cada agente e o resultado JULGADO pelo simulador.
Escreva em portugues, direto: (1) para cada item: acertou/errou a predicao e POR QUE (mecanismo, com os numeros do log); (2) 3 insights transferiveis entre grupos;
(3) tarefas da proxima rodada por grupo, como JSON no formato de grupos.json (bloco ```json```), mais especificas que as atuais; (4) o que NAO repetir.
{chr(10).join(partes)}"""
    open(os.path.join(out, 'consolidacao.prompt.md'), 'w').write(pr)
    if a.dry_run: print(f'[dry] consolidacao: {len(pr)} chars'); return
    txt = chama(pr, 'opus', timeout=600); open(os.path.join(out, 'consolidacao.md'), 'w').write(txt); js = bloco(txt, 'json')
    if js:
        try: json.dump(json.loads(js), open(os.path.join(REPO, 'scripts', 'agentes', f'grupos_r{a.rodada+1}.json'), 'w'), indent=1); print('grupos da proxima rodada gravados')
        except Exception as e: print('json das tarefas invalido:', e)
    print(txt[:1500])
def reenviar(a):
    """recria os pedidos de uma rodada a partir dos arquivos em docs/agentes/r<N>/ (apos desligamento da maquina); so os que NAO tem estado 'terminou'"""
    import nmd_cliente as c; out = os.path.join(REPO, 'docs', 'agentes', f'r{a.rodada}'); env = {'NM_RISCO': '1', 'NM_PONTO': '1'}; feitos = []
    for f in sorted(glob.glob(os.path.join(out, '*.cenario.json'))):
        nome = os.path.basename(f).replace('.cenario.json', ''); grupo, i = nome.rsplit('_', 1); pid = f'r{a.rodada}_{grupo}{i}'
        if c.estado(pid).get('fase') == 'terminou' and not a.forca: continue
        pol = os.path.join(out, f'{nome}.politica.py')
        if os.path.exists(pol): c.pedir(pid, 'julga_politica', out=f'agentes_r{a.rodada}', env=env, politica=pol, tag=f'_{pid}')
        else:
            cen = json.load(open(f))
            if a.triagem: cen['protocolo'] = {'P': 512, 'G': 60, 'paciencia': 30, 'R': 4, 'seeds': [0, 1, 2, 3, 4]}; json.dump(cen, open(f, 'w'), indent=1)
            c.pedir(pid, 'e43_campo', out=f'agentes_r{a.rodada}', env=env, preset='fumaca', cenario=f, tag=f'_{pid}', **{'init-from': [R + '/e64/e43_busca8x_L200.json', 'linear'], 'sigma-espinha': 0.05})
        feitos.append(pid)
    pp = os.path.join(out, 'pedidos.json'); antigos = json.load(open(pp)) if os.path.exists(pp) else []
    json.dump(antigos + [x for x in feitos if x not in antigos], open(pp, 'w')); print('reenviados:', feitos)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('fase', choices=['gerar', 'consolidar', 'reenviar']); ap.add_argument('--forca', action='store_true', help='reenviar mesmo os que ja terminaram'); ap.add_argument('--rodada', type=int, default=1); ap.add_argument('--n', type=int, default=2); ap.add_argument('--model', default='sonnet')
    ap.add_argument('--grupos', default='grupos.json'); ap.add_argument('--so', nargs='*', default=None); ap.add_argument('--agentes', type=int, nargs='*', default=None, help='so estes indices de agente (ex.: 2)'); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--triagem', action='store_true', help='forca protocolo P512 G60 pac30 nos cenarios'); a = ap.parse_args()
    {'gerar': gerar, 'consolidar': consolidar, 'reenviar': reenviar}[a.fase](a)
