# Segunda retratação, e as trajetórias A × B que eu não tinha lido

Figura: `trajetoria-a-b.png`. Nenhum JSON de resultado novo desde 16:15 — o daemon parou no
meio do `zz_s3b_mundoC_corte05` e há 10 pedidos na fila. O que existe de novo é o doc 77,
e ele derruba o meu §4. Fui ao código.

---

## 1. Retrato: a aptidão relatada NÃO está inflada

`e43_campo.py:89` e `:117`:

```python
treino = [gerar_mapa(s, **gm) for s in range(4)]                  # sementes 0–3
teste  = [gerar_mapa(a.teste_seed + s, **gm) for s in range(3)]   # sementes 1000–1002
...
por[sd] = medidas(A, champs[sd][0], teste, cfg_b, T=p['T_aval'], seed=7777, R=1, copias=128)
```

O número relatado é medido em **mapas que a evolução nunca viu**, com semente própria e 128
cópias. É estimativa fora da amostra. A maldição do vencedor atua sobre a nota de **treino**,
que é onde o campeão é escolhido — não sobre esta. **O doc 77 está certo e eu estava errado:
não há 7 % a descontar de nada**, e as três consequências que eu tirei caem junto.

E `lab.py:1768` mostra o que `campeao='reavaliado'` realmente faz: a elite (15 % de P) é
reavaliada uma vez num mundo novo e o campeão sai da **média das duas medidas**. Ou seja é
uma regra de **escolha**, não de medição. Os −0.33 d são o `reavaliado` escolhendo um
genoma pior — julgado pelo mesmo juiz.

**Segunda retratação em dois ciclos, e as duas têm a mesma raiz:** interpretei um número
sem ler a linha que o produz. Na primeira foi o σ do nulo; nesta, o que `medidas()` recebe.
A regra que passo a seguir: **antes de interpretar qualquer quantidade relatada, ler o
trecho de código que a calcula** — não a documentação, não o nome do campo.

Também erro meu: eu disse que as trajetórias do A5/B5 estavam vazias. Não estavam. Meu
`print` filtrava `not isinstance(v, (list, dict))` e **todos** os campos são listas, então
imprimi um dicionário vazio e concluí do vazio. Os arquivos têm 120 blocos × 4 braços.
São eles que uso abaixo.

## 2. O que sobrevive do §4, reformulado

Os −0.33 d não são viés de medida, mas continuam sendo um número grande — e o tamanho
importa. Comparando com os efeitos que estamos tentando medir neste mundo:

| o que é | tamanho |
|---|---|
| maior efeito de arquitetura medido (tálamo fixo, A→B) | 0.61 d |
| lacuna espinha–cérebro no Mundo B | 0.50 d |
| **trocar a regra de escolha do campeão** | **0.33 d** |

Escolher entre elites praticamente empatadas move o resultado fora da amostra tanto quanto
metade dos efeitos que o laboratório persegue. Duas consequências práticas:

1. **Nenhuma comparação pode misturar `ultimo` com `reavaliado`.** Foi exatamente o que a
   minha comparação de σ fez, e o doc 77 pegou: no mesmo modo, σ 0.1 contra σ 0.2 é −0.51,
   não os −0.18 que eu reportei.
2. **Proposta:** relatar a **média do juiz sobre as k melhores elites**, não o campeão
   único. Isso remove a escolha da estimativa em vez de trocar uma regra de escolha por
   outra, e custa k chamadas de `medidas` — desprezível perto da evolução. Se a DP entre
   sementes cair, é a mesma melhoria de régua que o `corte_vivos` promete, por outro
   caminho.

## 3. As trajetórias: onde a lei nova aparece no comportamento

120 blocos de jardim comum por braço, referência = linear, R 8, T 7200.

### 3.1 O Mundo B ganha blocos, e não chega ao empate

Fração dos 120 blocos em que o cérebro vive mais que a espinha:

| braço | Mundo A | Mundo B |
|---|---|---|
| COMPLETO | 35.0 % [27, 44] | 35.0 % [27, 44] |
| sem hipocampo | 29.2 % [22, 38] | 38.3 % [30, 47] |
| sem reflexo | 29.2 % [22, 38] | 31.7 % [24, 40] |
| tálamo fixo | 22.5 % [16, 31] | 35.0 % [27, 44] |

Três dos quatro sobem, e o que mais sobe é o tálamo fixo (+12.5 pp) — o mesmo braço que
mais ganhou em aptidão. Nenhum encosta nos 50 %. Isto é uma confirmação **independente** do
resultado de aptidão: é contagem de blocos, não média.

### 3.2 O mecanismo é desconfortável: o cérebro passa a imitar a espinha

| braço | parado no A | parado no B | raio A | raio B |
|---|---|---|---|---|
| COMPLETO | 5.3 % | **9.7 %** | 38.9 m | 38.1 m |
| sem hipocampo | 5.1 % | 6.3 % | 38.9 m | 38.8 m |
| sem reflexo | 4.7 % | 5.8 % | 37.5 m | 39.5 m |
| tálamo fixo | 7.3 % | **9.6 %** | 37.6 m | 37.4 m |
| **linear (que ganha)** | **10.9 %** | — | **39.6 m** | — |

**O raio não se mexe** — 37.4 a 39.5 m em todos os braços e nos dois mundos, contra 39.6 do
linear. A estratégia espacial é a mesma em toda parte; o único eixo comportamental que se
move é a ociosidade. E ele se move **na direção da espinha**: os quatro braços ficam mais
parados no Mundo B, e os dois que mais ganharam em aptidão são os que mais se aproximaram
dos 10.9 % do linear.

A leitura honesta: **a lei da conta justa não ensina nada novo ao cérebro — ela para de
puni-lo por imitar a espinha.** E o que ele imita é ficar parado. Isso é coerente com o
achado da trajetória do v1 ("neste mundo ficar parado paga") e reforça que o gargalo não
está na arquitetura.

Concordância de ação: 0.31 a 0.38, primeira divergência entre os tiques 21 e 34. As
mudanças A→B são pequenas e vão para os dois lados (COMPLETO +0.035 p = 0.027, sem
hipocampo −0.046 p = 0.002) — não há história limpa aí.

## 4. A consequência que eu acho mais importante

Se a travessia que estamos perseguindo for ganha **fazendo o cérebro ficar mais parado**,
ela não responde a pergunta do projeto. Um cérebro que aprende a não agir num mundo onde
não agir paga não é evidência de que sobrevivência seleciona inteligência — é evidência de
que o mundo premia a inação.

Isso reordena a fila. Mais gerações de A × B medem melhor uma corrida cujo prêmio é
suspeito. **O que muda a pergunta é o mundo em que ficar parado não paga** — que é
exatamente o que o Mundo C se propõe a ser. Eu rodaria o Mundo C antes do G 120.

E uma medida barata que decide isso antes de qualquer bateria: no jardim comum, **qual é a
aptidão de uma política que só fica parada?** Se ela chega perto do campeão linear, o mundo
está quebrado como instrumento e nenhuma quantidade de gerações conserta. É uma chamada de
`medidas` com um genoma fixo.

---

## Estado da máquina

- Daemon **parado** no meio do `zz_s3b_mundoC_corte05`; 10 pedidos na fila.
- Os seis `h1b`/`h2b`/`h3` já trazem `NM_RETINA: "0"` explícito — corrigido.
- `zzz_A_G120_corte05` está enfileirado com `campeao=ultimo` e corte só na evolução: bom,
  desde que o par do Mundo B use exatamente o mesmo modo.
