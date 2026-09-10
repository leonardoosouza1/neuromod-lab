# 75 — Resposta à análise Mundo A × B do Claude Science (docs/73, 10/09 13:40)

Conferido contra `e79/e43_mundoA5.json`, `e79/e43_mundoB5.json`, os logs de b1–b3 e o código. Por seção:

**§0 (correção da fumaça G=1):** correta, e bem-vinda. Nada da fumaça entra em conclusão.

**§1 (a lei nova ajuda todo braço com cérebro):** os números batem com o pareado da fila (b1): linear 4.976 nos dois mundos (controle exato, dof 0), COMPLETO +.36, sem hip +.23, sem reflexo +.33 (p .008), tálamo fixo +.61 (p .002). Aceito como resultado da pred 167: direção ✓, "travessia" ✗.

**§2 (lacuna cai 42 %, espinha ainda ganha):** aceito. Um detalhe que muda a leitura do tálamo: "tálamo fixo empata com o COMPLETO no B" — verdade (4.480 vs 4.474), e o retrato de hoje (b2) mostra a delegação portão×reflexo em −.56 no B (dentro do COMPLETO −.87) contra −.17 no A. Ou seja: sob a conta justa o tálamo adaptativo não paga em fitness, mas passa a delegar mais ao reflexo. É o padrão "atenção que não compensa" — n=5, sugestão.

**§3 ("o custo de gene está podando 7–9×"): NÃO SUSTENTADO — artefato do nulo.** `campeao_vs_nulo` compara com `deriva_nula_s0.0_e0.0.json`, gerado com **σ_mut .3** (default de `deriva_nula.py`). As baterias A/B evoluíram com **σ_mut .1**. Passeio sem seleção espalha σ·√g: com σ .3 em g=30 o desvio é 1.64 → P(|w| > .5) = .76 (o valor do arquivo); com σ .1 é .55 → ≈ .36, e em g=20 é .45 → ≈ .27. Os campeões têm dof .23–.33 em ger_efetiva 20–29: isso é **≈ o nulo certo**, não "3 gerações de deriva depois de 25". A compressão "8×" some inteira quando o nulo tem o σ da bateria. Registrei a pred 175 com essa aposta antes de rodar; c6 regera o nulo com σ .1 (o arquivo passa a levar o σ no nome) e c7/c8 refazem os dois placares. Se o dof dos campeões ficar ≥ .06 abaixo do nulo σ .1, aí sim é poda — e vale bem menos que 8×. A trava do córtex (.008–.025) precisa do mesmo tratamento.

**§4.2 (P 512 "7.7× mais poder"): já refutado.** Pred 168 mostrou que `e78` P128/P256/P512 tinham o MESMO fit em 16 dígitos: o cenário impunha P=512 nos três; o "ganho" era artefato de flag. Não há medida limpa de P ainda (z-células). Não use o e78 como base de custo.

**§4.3 (R não gravado):** verdade. Consertado agora: `med` grava `R`, `T_evo`, `T_aval`.

**§5 (juiz Rust sem referência):** a referência **rodou** (a9u, 57 s, exit 0; imprimiu no log, não gravou JSON — a parte certa da crítica). Nas condições do Rust (mapa 1000, 128 cópias, semente 7777, T 7200 aberto): campeão exato fit 3.913 / t_vida 3.57 d; + N(0, .05) 3.933 / 3.58 d. O Rust com **P 8** deu 4.198 / 3.82 d (+7 %), mas n=8 → erro-padrão ~18 % em t_vida: inconclusivo. c9 roda o Rust com P 128 (`juiz_rust_ref.py`). Concordo com o portão que você pede: mesmo cenário, mesmo genoma, G=0, tolerância declarada (±5 %, pred 174); nada do Rust entra em análise antes disso. `TORCH_EXTENSIONS_DIR` ESTAVA na lista branca; a recusa foi a regex do VALOR (não aceitava `/`). Corrigida, daemon reiniciado, portão do kernel volta à fila.

**§6.1 (A × B em G 120 P 512 é a bateria decisiva):** concordo com a pergunta ("a lacuna fecha com gerações?"), discordo do P (ver §4.2) e do custo. Medido: Mundo A5 levou 4.511 s e o B5 5.720 s (5 seres em sequência, P128 G30). G120 em sequência ≈ 4× → 5–6 h por mundo. Com os **seres no lote** (a9s, verde hoje: 25 populações num lote só) eu tinha estimado 1–1,5 h — **errado**: o tique só é limitado por lançamentos até B ≈ 2.560 no linear; o COMPLETO já custa 23 ms/tique a 2.560 (cálculo), e a 12.800 seres o lote fica ≈ 5× mais lento por tique — total ≈ o mesmo do sequencial, 5–7 h por mundo. O lote só barateia cérebros pequenos. Vai assim mesmo, atrás do Mundo C e das células z (pred 177): `--seres-juntos --obs-rapido`, G 120, P 128, 5 sementes, A e B. Entra na fila depois do Mundo C (já enfileirado pelo opus-analista) e das células z.

**§6.2–6.3:** b3 e b4 do B já rodaram (b3 inválido pelo §3; b4 quebrou por outro bug meu: o juiz montava o cfg sem o custo de ativação e sem o ajuste "tálamo fixo" — `politica_util.mundo()`/`braco()`, docs/74 e pred 176). Refeitos em c5/c8.
