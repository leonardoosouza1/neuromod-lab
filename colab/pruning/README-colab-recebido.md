# Neuromod Lab

Laboratório sobre **arquiteturas de memória em agentes com corpo**. Benchmark:
táxis com combustível, fome, fadiga, avarias e economia, num grafo urbano irregular.

> **Assumindo o projeto?** Leia `CLAUDE.md` primeiro. Ele tem o briefing completo,
> as regras de método e o que já foi refutado.

## Instalação

```bash
pip install numpy          # versão leve (src/taxi_np.py) — só isso
pip install torch          # opcional, para a versão GPU (src/lab.py)
```

## Uso

```bash
# exploração rápida (numpy, CPU, ~4 min por rodada)
python src/poda2.py podar 0

# versão GPU
python src/rodar.py --perito      # PORTÃO — obrigatório antes de qualquer bateria
python src/rodar.py --bateria -P 8192 -G 100 -R 8
```

## O portão

`--perito` roda a **mesma política** nas cinco arquiteturas com a memória zerada.
Elas têm que dar resultado idêntico:

```
PASSOU: as 5 batem (spread 0.000)
```

Se divergirem, há bug de porte. Este teste pegou cinco bugs silenciosos — todos
rodavam sem erro e produziam números plausíveis. Detalhes em `CLAUDE.md` §3.1.

## Achado mais recente

**Poda supera mutação livre** como operador de busca: fitness de treino +1,50
(p<0,00001, 18/20 sementes), melhor em 57 de 60 gerações, usando 35% das conexões.
A vantagem de generalização fica no limiar (p=0,053) e **não é afirmada**.

Cinco features são descartadas em 20/20 evoluções independentes — poda faz
seleção interpretável. Ver `docs/16-poda.md`.

## Estrutura

```
CLAUDE.md          briefing para assumir o projeto
src/
  taxi_np.py       simulação numpy (leve, para iterar)
  poda2.py         experimento de poda
  lab.py           simulação torch vetorizada (escala)
  rodar.py         CLI: --smoke, --perito, --bateria
docs/
  CONTEXTO.md      resumo executivo
  INDICE-MESTRE.md validados vs refutados + invariantes
  COLAB.md         VRAM, limpeza de GPU, armadilhas
  01..16           documentos temáticos
resultados/        dados brutos (jsonl)
notebooks/         versão Colab
```

## Regras do projeto

1. **Portão antes de bateria.** Sempre.
2. **Valide o mundo antes da política.** Perito à mão precisa bater aleatório por 10×.
3. **Valide cada dimensão que vai medir.** Uma bateria morreu porque a economia
   tinha margem negativa e ninguém percebeu.
4. **Resultado estranho é bug até prova em contrário.**
5. **Réplicas antes de população.** Fitness ruidoso seleciona sorte.
6. **≥10 sementes.** Um teste com 2 deu "+55%"; com 20 deu p=0,053.
