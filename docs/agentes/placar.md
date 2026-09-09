# Placar (juiz: simulador; 3 sementes x 128 copias x 3 mapas; campeao evoluido = 0.85)

| lote/politica | alavanca | mortos | corridas | refeicoes | dia | causa | predicao do agente |
|---|---|---|---|---|---|---|---|
| L2 p6 | NOITE: descanso/fadiga (hoje ignorado) | **0.73** | 16.4 | 7.3 | 5.6 | fome 46 % / dano 53 % | mortos 0.63–0.66 (meta ≤0.65), corridas ~15.8, refeições ~8. |
| L2 p8 | LIVRE: qualquer coisa que os dados do ca | **0.73** | 16.0 | 7.3 | 5.7 | fome 53 % / dano 46 % | mortos ≈0.69 (de 0.74); corridas ≈16.1 (leve queda vs 16.3,  |
| L1 p5 | ORDEM das compras no posto e quantos tic | **0.74** | 16.3 | 7.4 | 5.7 | fome 50 % / dano 48 % | mortos 0.69 (de 0.73), corridas 16.4, refeições 7.4, morre d |
| L1 p4 | GASOLINA: quantos litros por parada conf | **0.75** | 16.0 | 7.1 | 5.7 | fome 55 % / dano 44 % | mortos 0.62 (vs base 0.73), corridas 17.0, refeições 7.4, mo |
| L1 p8 | LIVRE: qualquer coisa que os dados do ca | **0.75** | 15.8 | 7.1 | 5.6 | fome 57 % / dano 42 % | alavanca = detour proativo ao posto ANTES do fechar (posto f |
| L1 p2 | AGUA: quando e quanto comprar | **0.76** | 16.3 | 7.1 | 5.7 | fome 51 % / dano 44 % | mortos ≈0.62 (de 0.73), corridas ≈17.4, refeições ≈7.8, abas |
| L1 p1 | limiar de COMIDA no posto e fora (fome) | **0.78** | 13.4 | 7.8 | 5.6 | fome 74 % / dano 25 % | mortos ≈0.60 (de 0.73), corridas ≈15.8, refeições ≈8.8, dia  |
| L1 p6 | NOITE: descanso/fadiga (hoje ignorado) | **0.79** | 15.4 | 6.8 | 5.7 | fome 53 % / dano 46 % | mortos ~0.62 (corridas ~15.2, refeições ~7.0, oficinas ~1.9, |
| L1 p3 | REPARO na oficina: limiar de vida e de c | **0.84** | 12.4 | 5.6 | 5.3 | fome 74 % / dano 25 % | mortos 0.66, corridas 15.8, refeicoes 7.0, dia medio morte 6 |
| L1 p7 | RUA: penalizar sair da rua (custo_frente | **0.99** | 1.7 | 1.3 | 4.3 | fome 97 % / dano 1 % | mortos=0.63 (baseline 0.73), corridas=16.0 (baseline 16.5, l |
