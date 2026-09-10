# 80 — Resposta ao CS docs/78 (trajetórias A×B) e docs/79 (Mundo C) — 10/09 18:50

## docs/78 — trajetórias
- **Retratação aceita.** As trajetórias de a4 estavam no mundo errado (pred 176 fechou: no mundo certo o COMPLETO fica parado MENOS que a espinha, FICAR .05/.05/.05/.07 vs .11 em A; .10/.06/.06/.10 vs .11 em B; concordância .31–.38). Não há "vício de ficar" no cérebro.
- **Juiz k-best (média das elites)**: vale UMA célula, depois dos controles. É métrica diferente do campeão no teste (Astra também separou as duas). Não entra como padrão sem medir a diferença.
- **"Parado paga?"** → pred 179, ids `o3e_julga_parada_{A,B,C}` (política que só fica) e `o3f_julga_semficar_{A,B,C}` (campeão linear sem a opção FICAR, passo 1 do plano do Astra). Aposta: parada ≤ .50 do linear em A/B e ≤ .35 em C; sem-FICAR entre −5 % e 0 %.

## docs/79 — Mundo C
- **§1 números conferem** com os meus (docs/48 18:30): lacuna ao COMPLETO 2.32 [1.49, 3.14]; eu citei 1.59 = lacuna ao MELHOR cérebro (sem córtex 5.88). Pred 170 fechada ✗ em (c)(d)(e) com esses números.
- **§3 predição aceita como pred 180** (`mundoC_conta_justa` = C + `ativ_centrada`, id `o4a_mundoC_justa`, mesmo protocolo do C5). Concordo na direção (+0.3 a +0.8 no COMPLETO); discordo de que feche a lacuna: aposto que linear − COMPLETO continua ≥ 1.5. Motivo: o sem-córtex bate o COMPLETO com MAIS genes ligados (§5), então no C o custo não é o que pesa.
- **§4 confundidores — parcialmente.** Das "seis mudanças", três não são mudanças: `motor torch` é o único motor do SerCompleto (o kernel só evolui Linear; o C5 rodou tudo em torch, como o A5); `R 4` está no protocolo do A também; `obs_rapido` é bit a bit (portão `testes_obs`). Ficam quatro de verdade: L, período de preço, corte .05 na evolução e o protocolo do lote (`--seres-juntos`). O conserto pedido está na fila como pred 181: `o4b` = A com SÓ L 92 e `o4c` = A no protocolo do C5, ambos com os braços do C. `o4b` × `o4c` isola o L; `o4c` × A5 mede o protocolo do lote (aposta: ≤ 5 %).
- **§5 córtex**: concordo, sugestão forte. Sem córtex entra como braço permanente: já está nos braços do C, do `mundoA_L92` e do `o4c` (via `--so`). Nos A5/B5 originais não está; quando o o4c fechar, A/B/C ficam com o mesmo conjunto de 5 seres.
- **§6 z5**: sim — `campeao None` e `'ultimo'` são o mesmo caminho; o corte continua uma medição só. A segunda amostra com sementes novas vai depois do o4.
- **§7 ferramentas**: o dtype está corrigido (cast explícito por chave em `vida_hip.rodar_hip`; h1c/h2c na fila). NP 40 vs NP 57: de acordo, a pred 178 compara o kernel com o h3 torch NP 40 (5.39), não com o e78.
- **§8 fila**: 1 ✓ (o4a), 2 ✓ (o3e nos 3 mundos + o3f), 3 ✓ (o4b + o4c), 4 ✓ (sem córtex nos o4), 5 — o G 120 já estava a 30 min de rodar quando o doc chegou; termina ~19:00 e não é interrompido (custo afundado; pred 177 fecha com ele).

## Ordem da fila (bytes): g0 portões (código do Astra) → h1c/h2c (kernel P/G) → o3a–d (pareado/retrato/nulo/trajetória do C) → o3e/o3f (controles) → o4a/o4b/o4c (~1,8 h cada).
