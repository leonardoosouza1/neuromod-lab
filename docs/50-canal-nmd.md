# nmd — o canal entre a sessão e a GPU

Você tinha razão no desenho, só não no transporte. HTTP não serve: meu sandbox tem
namespace de rede próprio (`localhost` aqui é o meu, não o seu) e endereço privado do
host não é liberável. **Disco compartilhado serve**, nas duas direções — é como eu já
li os JSONs que sua fila gravou às 12:52. E é o padrão que você já usa: `fila.sh
--depois-de` espera um `.done` aparecer.

Então: uma **fila em disco** e um daemon do lado da GPU. Eu deposito o pedido,
ele executa, escreve estado e resultado, eu leio. Sem porta, sem token, sem rede.

## Subir (uma vez)

```bash
cp nmd.py /home/leonardo/projects/LLM/neuromod-lab/scripts/
python3 /home/leonardo/projects/LLM/neuromod-lab/scripts/nmd.py       # em primeiro plano, para ver
```
Permanente:
```bash
cp nmd.service ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now nmd
journalctl --user -u nmd -f
```
Parar de aceitar (termina o job atual e sai):
`touch /media/llm-data/universe-runs/neuromod-lab-taxi/_nmd/PARE`

## O que ele NÃO faz (o ponto importante)

O spool é um diretório em disco: quem escreve nele manda trabalho para a sua GPU.
Por isso o daemon **nunca executa string de comando**. Recebe pedido declarativo
(script + argumentos tipados), valida contra lista branca e **reconstrói o argv ele
mesmo**, com `subprocess` sem shell. Testado aqui, quatro pedidos:

| pedido | resultado |
|---|---|
| bateria legítima (`e43_campo`, fumaça) | rodou, exit 0, 8 s, resultado gravado |
| `"script":"os.system"` | **recusado** — script fora da lista branca |
| `"so":["--out /etc"]` (injeção de flag) | **recusado** — valor parece flag |
| `"env":{"LD_PRELOAD":"..."}` | **recusado** — env fora da lista branca |

Mais: um job por vez (`pgrep` antes de subir — nunca dois na GPU); `--out` só aceita
nome de subpasta dentro da base; nenhum caminho absoluto vindo do pedido; recusa vai
para `recusados/` com o motivo; escrita de estado é atômica (`os.replace`), então eu
nunca leio meio arquivo. A lista branca de scripts e de env está no topo do `nmd.py` —
edite à vontade, é a sua política de segurança, não a minha.

## Como eu mando e como eu vejo

```python
import nmd_cliente as nmd
nmd.pedir('e63c', 'e43_campo', out='e63', env={'NM_RISCO':'1'},
          preset='honesto', G=120, R=8, seeds=[0,1,2,3,4], L=200, dias=15,
          fitness='riqueza', mundo='distinto', nevoa=25,
          so=['linear','bilinear risco (esc 3)'], tag='_e63_nev_25')
nmd.estado('e63c')     # {'fase':'rodando','geracao':45,'melhor_por_semente':[...],'bracos_prontos':[...]}
nmd.resultado('e63c')  # os JSONs de resultado já carregados
```

**Como eu quero ver o resultado** — você perguntou. Três coisas, em ordem de valor:

1. **Heartbeat com a curva** (`estado/<id>.json`, já implementado): geração corrente e
   melhor fitness **por semente**. Com isso eu vejo na geração 30 que o braço virou
   pedra e te aviso para matar, em vez de descobrir 6 h depois.
2. **Por-semente para TODAS as medidas** no JSON de resultado. Hoje só `fit` e `mortos`
   têm `_por_semente`; panes, entregas, fome e dinheiro vêm só como média, e sem eles
   metade da régua pareada fica inacessível. São três linhas em `e43_campo.py` — é a
   mudança de maior retorno por linha em todo o repositório, e eu faço quando você
   quiser.
3. O `log/<id>.log`, que eu leio só quando algo quebra.

Nada de novo formato: o JSON da bateria continua sendo a fonte da verdade, e o
`analise_campo.py` já lê ele.

## O caminho preto no branco

```
eu escrevo:  _nmd/pedidos/e63c.json
daemon:      valida -> pgrep -> roda na GPU -> _nmd/estado/e63c.json (a cada 20 s)
                                            -> _nmd/log/e63c.log
                                            -> e63/e43_e63_nev_25.json
eu leio:     nmd.estado('e63c') / nmd.resultado('e63c') -> analise_campo.py -> painel
```
