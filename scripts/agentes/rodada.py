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
"""
API_POL = """## Contrato politica.py (agente escreve; o juiz executa em GPU com 3 mundos de teste x 128 copias x 5 sementes)
Defina `fabrica()` que devolve uma CLASSE com: reset(s, m, W) ; extra(s, m, W, F) -> torch.zeros(m.B, G) (guarde s.F = F) ; decidir(s, tudo, m) -> LongTensor (m.B,) ; atualizar(s, m).
- F (B, G=9, NF) = observacao: para cada opcao de movimento g (8 direcoes + ficar = g 8), colunas 0..9 = NOMES_OP = ['d_alvo','d_posto','d_comida','d_agua','d_oficina','d_descanso','custo_frente','preco_frente','aliq_frente','casa_frente']
  (distancias em unidades andadas APOS a opcao; d_alvo = passageiro mais perto ou destino se carrega) e colunas 10.. = NOMES_CORPO (iguais nas 9 opcoes):
  ['e_fuel','e_agua','e_fome','e_fadiga','e_calor','e_vida','e_dinheiro','e_reserva','e_tem_pax','h_sin','h_cos','e_noite','custo_aqui','bias','e_consumo','e_autonomia','e_risco','e_demanda','e_espera'] (escalas 0..1; dinheiro /150; autonomia = (tanque/consumo - d_posto)/100).
- tudo (B, G+S): colunas 0..G-1 = notas de movimento (ignore), G.. = servicos DISPONIVEIS e pagos (> -1e8) na ordem ACOES = [posto 25L, posto 50L, posto encher, comida, agua, hotel, oficina, ...] — use `tudo[:, G:] > -1e8` para saber o que pode comprar AQUI e AGORA.
- Corpo em m (tensores (B,)): m.fuel, m.agua, m.fome, m.fad, m.calor, m.vida, m.dinh, m.res, m.pd_ (>=0 carregando), m.hora() (0..24), m.noite_(), m.B.
- Devolva por ser: um indice de movimento 0..8 (use argmin de uma coluna de F para 'ir ao alvo'), ou G + indice do servico para comprar.
- Proibido: importar alem de torch/math, ler m.px/m.pxd/m.serv/m.g/m.dest, chamar os/sys/open/exec. Tudo vetorizado em torch (sem loop por ser).
- Exemplo minimo (o oraculo que morreu 1.00): ir ao passageiro; se e_fuel < .4 ir ao posto e encher quando disponivel; se fome > .8 comer. Faca melhor: margem de alcance (autonomia), comer quando ja esta no posto, evitar centro caro sem dinheiro, descansar de madrugada."""
def prompt_de(grupo, g, i, rod):
    base = contexto(); saida = ('Responda com UM bloco ```json``` contendo o cenario.json completo (campo "predicao" obrigatorio, com numeros e mecanismo) e nada mais.' if g['tipo'] == 'cenario'
             else API_POL + '\nResponda com UM bloco ```python``` com o politica.py completo, e antes dele UMA linha `PREDICAO: ...` com mortos, entregas e o que mata.')
    return f"{base}\n# SUA TAREFA (grupo '{grupo}', agente {i}, rodada {rod})\n{g['tarefa']}\nSeja diferente dos outros agentes do grupo: agente {i} deve escolher uma abordagem distinta (variacao {i}).\n{saida}"
def chama(prompt, model, timeout=420):
    r = subprocess.run([CLAUDE, '-p', prompt, '--model', model, '--output-format', 'json', '--no-session-persistence'], capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout).get('result', r.stdout)
    except Exception: return r.stdout or r.stderr
def bloco(txt, lang):
    m = re.search(r'```' + lang + r'\s*(.*?)```', txt, re.S); return m.group(1).strip() if m else None
def gerar(a):
    grupos = json.load(open(os.path.join(REPO, 'scripts', 'agentes', a.grupos))); out = os.path.join(REPO, 'docs', 'agentes', f'r{a.rodada}'); os.makedirs(out, exist_ok=True)
    import nmd_cliente as c; pedidos = []
    for nome, g in grupos.items():
        if a.so and nome not in a.so: continue
        for i in range(1, a.n + 1):
            pr = prompt_de(nome, g, i, a.rodada); open(os.path.join(out, f'{nome}_{i}.prompt.md'), 'w').write(pr)
            if a.dry_run: print(f'[dry] {nome}_{i}: prompt {len(pr)} chars'); continue
            t0 = time.time(); txt = chama(pr, a.model); open(os.path.join(out, f'{nome}_{i}.resposta.md'), 'w').write(txt); print(f'{nome}_{i}: resposta {len(txt)} chars em {time.time()-t0:.0f}s', flush=True)
            env = {'NM_RISCO': '1', 'NM_PONTO': '1'}; pid = f'r{a.rodada}_{nome}{i}'
            if g['tipo'] == 'cenario':
                js = bloco(txt, 'json')
                try: cen = json.loads(js)
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
    json.dump(pedidos, open(os.path.join(out, 'pedidos.json'), 'w')); print('pedidos:', pedidos)
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
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('fase', choices=['gerar', 'consolidar']); ap.add_argument('--rodada', type=int, default=1); ap.add_argument('--n', type=int, default=2); ap.add_argument('--model', default='sonnet')
    ap.add_argument('--grupos', default='grupos.json'); ap.add_argument('--so', nargs='*', default=None); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--triagem', action='store_true', help='forca protocolo P512 G60 pac30 nos cenarios'); a = ap.parse_args()
    gerar(a) if a.fase == 'gerar' else consolidar(a)
