"""dimensiona.py — [reprojeto CS docs/70 3.1] as constantes do mundo como RAZAO contra a vida do ser.

So stdlib e so LEITURA: le um cenario JSON, devolve as razoes e um veredito. Nao roda mundo nenhum e nao
importa torch nem campo — por isso as constantes do codigo ficam ESPELHADAS aqui e sao conferidas contra o
codigo no portao `testes_import` (sem isso viram indice cravado que envelhece em silencio).

TRES RAZOES (docs/70 3.1; o minimo utilizavel e o que o CS declarou la):
  cidade_ao_alcance   fracao do mapa dentro do raio de acao do ser = min(1, pi*raio^2/L^2)   >= .50
  amostras_por_caixa  entregas por vida / caixas de memoria que o MUNDO instancia            >= 5
  ciclos_por_vida     vida do ser / periodo do ciclo mais lento do mundo                     >= 3

AVISOS (nao reprovam; sao constantes em unidade ABSOLUTA que nao acompanham L, ou limites do ser):
  caixas_mortas   DMAX - K: linhas do cortex e caixas do hipocampo que o mundo nunca instancia
  tau_max_vida    o estado mais lento que o ser PODE ter (201 ticks) em fracao de vida
  retina_por_L    raio da retina de dia / L: em cidade pequena o ser ve o mapa inteiro de uma vez
  anel_pax_por_L  anel de nascimento do passageiro (raio_px, absoluto) / L

USO:
  python dimensiona.py --cenario cenarios/mundoC_cidade_da_vida.json [--vida 4.589 --entregas 13.02 --raio 37] [--exigir]
  from dimensiona import razoes; r = razoes(json.load(open(cen)))
"""
import argparse, json, math, os, sys

CAIXAS_MAX = 12       # espelha completo.DMAX (linhas do cortex e caixas do hipocampo)
TICKS_DIA = 240       # espelha CfgCampo.dia
TAU_MAX_TICKS = 201   # espelha campo: tau = 1. + 200.*sigmoid(.) — o estado mais lento que existe no ser
RETINA_R_DIA = 60.    # espelha RETINA_PADRAO['R_dia'] (usado so quando o cenario nao declara retina)
RAIO_PX = 45.         # espelha CfgCampo.raio_px: anel onde o passageiro nasce, em metros ABSOLUTOS

MIN_CIDADE = .50      # docs/70 3.1: o ser tem de conhecer metade do mapa
MIN_AMOSTRAS = 5.     # docs/70 3.1: 5 visitas por caixa antes de a caixa valer alguma coisa
MIN_CICLOS = 3.       # docs/70 3.1: o ciclo tem de se repetir 3 vezes numa vida

# medidas do Mundo A (e79/e43_mundoA5.json, braco linear, 5 sementes) e do retrato de vida (docs/69)
VIDA_D = 4.589        # t_vida_media do linear
ENTREGAS = 13.02      # ent do linear por vida
RAIO_M = 37.          # raio de acao medido nos campeoes (docs/69: 28 / 41 / 43 m)

ORDEM = ('cidade_ao_alcance', 'amostras_por_caixa', 'ciclos_por_vida')


def constantes(cen):
    """le do cenario as constantes de mundo que entram nas razoes (com o mesmo default do codigo)."""
    m = cen.get('mundo') or {}
    L = float(m.get('L') or 200.)
    K = int(m.get('K') or max(3, round(6*L/200.)))
    reg = m.get('regime') if isinstance(m.get('regime'), dict) else None
    per = float(reg['periodo_dias']) if reg and reg.get('periodo_dias') else None
    fonte = 'regime.periodo_dias'
    if per is None:
        pr = m.get('precos') or {}
        per = float(pr['periodo']) if pr.get('periodo') else None
        fonte = 'precos.periodo'
    ret = m.get('retina') if isinstance(m.get('retina'), dict) else None
    R_dia = float(ret['R_dia']) if ret and ret.get('R_dia') else RETINA_R_DIA
    return dict(L=L, K=K, periodo_d=per, periodo_fonte=(fonte if per else None), R_dia=R_dia)


def razoes(cen, vida_d=VIDA_D, entregas=ENTREGAS, raio_m=RAIO_M):
    """as tres razoes + avisos. `fora` lista, na ordem de ORDEM, as razoes abaixo do minimo."""
    c = constantes(cen)
    L, K, per = c['L'], c['K'], c['periodo_d']
    caixas = min(CAIXAS_MAX, K)
    r = {}
    v = min(1., math.pi*raio_m*raio_m/(L*L))
    r['cidade_ao_alcance'] = dict(valor=v, minimo=MIN_CIDADE, ok=v >= MIN_CIDADE,
                                  atual=f'raio {raio_m:.0f} m em L {L:.0f}',
                                  sugestao=f'L <= {raio_m*math.sqrt(math.pi/MIN_CIDADE):.0f}')
    v = entregas/max(1, caixas)
    r['amostras_por_caixa'] = dict(valor=v, minimo=MIN_AMOSTRAS, ok=v >= MIN_AMOSTRAS,
                                   atual=f'{entregas:.1f} entregas em {caixas} caixas (K {K}, DMAX {CAIXAS_MAX})',
                                   sugestao=f'K <= {max(3, int(entregas/MIN_AMOSTRAS))} ou entregas por vida >= {MIN_AMOSTRAS*caixas:.0f}')
    v = (vida_d/per) if per else 0.
    r['ciclos_por_vida'] = dict(valor=v, minimo=MIN_CICLOS, ok=v >= MIN_CICLOS,
                                atual=(f'vida {vida_d:.2f} d / {c["periodo_fonte"]} {per:.2f} d' if per else 'o mundo nao tem ciclo lento'),
                                sugestao=(f'periodo <= {vida_d/MIN_CICLOS:.2f} d' if per else f'declarar um ciclo de <= {vida_d/MIN_CICLOS:.2f} d'))
    av = dict(caixas_mortas=CAIXAS_MAX - min(CAIXAS_MAX, K),
              tau_max_vida=TAU_MAX_TICKS/(vida_d*TICKS_DIA),
              retina_por_L=c['R_dia']/L, anel_pax_por_L=RAIO_PX/L)
    fora = [k for k in ORDEM if not r[k]['ok']]
    return dict(nome=cen.get('nome'), constantes=c, razoes=r, avisos=av, fora=fora, ok=not fora,
                medido=dict(vida_d=vida_d, entregas=entregas, raio_m=raio_m))


def linhas(res):
    out = [f'dimensiona: {res["nome"]} | L {res["constantes"]["L"]:.0f} K {res["constantes"]["K"]} | '
           f'medido: vida {res["medido"]["vida_d"]:.2f} d, {res["medido"]["entregas"]:.1f} entregas, raio {res["medido"]["raio_m"]:.0f} m']
    for k in ORDEM:
        d = res['razoes'][k]
        out.append(f'  {k:<19} {d["valor"]:7.2f}  minimo {d["minimo"]:.2f}  {"ok" if d["ok"] else "FORA"}  ({d["atual"]}; para entrar: {d["sugestao"]})')
    a = res['avisos']
    out.append(f'  avisos: caixas mortas {a["caixas_mortas"]} de {CAIXAS_MAX} | estado mais lento do ser = {a["tau_max_vida"]*100:.0f} % de uma vida | '
               f'retina/L {a["retina_por_L"]:.2f} | anel do passageiro/L {a["anel_pax_por_L"]:.2f}')
    out.append('  VEREDITO: ' + ('todas as razoes na faixa' if res['ok'] else 'fora da faixa: ' + ', '.join(res['fora'])))
    return out


def main(a):
    cen = json.load(open(a.cenario))
    res = razoes(cen, vida_d=a.vida, entregas=a.entregas, raio_m=a.raio)
    print('\n'.join(linhas(res)), flush=True)
    if a.json: print(json.dumps(res, ensure_ascii=False, indent=1), flush=True)
    if a.exigir and not res['ok']: sys.exit(1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--cenario', required=True)
    ap.add_argument('--vida', type=float, default=VIDA_D, help='vida media medida do ser (dias)')
    ap.add_argument('--entregas', type=float, default=ENTREGAS, help='entregas por vida medidas')
    ap.add_argument('--raio', type=float, default=RAIO_M, help='raio de acao medido (m)')
    ap.add_argument('--exigir', action='store_true', help='sai com codigo 1 se alguma razao estiver fora da faixa')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--out', default=None, help='ignorado (a fila sempre acrescenta --out)')
    main(ap.parse_args())
