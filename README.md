# Neuromod Lab

**A GPU-vectorised research lab that tests whether memory, neuromodulation and "brain
organs" actually pay off for agents that have a body, an economy and a hostile world.**
The main testbed is a taxi in a procedurally generated city: it has fuel, hunger,
fatigue, tyres, engine heat and breakdowns, has to earn money to pay for upkeep, and
evolves through a genetic algorithm. Hundreds of thousands of worlds run in parallel
on one GPU in PyTorch.

The lab also drives the racing batteries of its sibling project
[Universe](https://github.com/leonardoosouza1/Universe): it queues runs, ingests them
into a SQLite run database and serves them through a small FastAPI backend.

Status: research code. Most write-ups in [`docs/`](docs/) are in Portuguese.

---

## Highlights

- **Pruning beats free mutation on unseen cities.** 20 paired evolution seeds, same
  cities and budgets: deliveries on held-out cities were prune 32.06 vs generate_fine
  24.23 vs generate 25.43. prune − generate_fine = **+7.83 (95% CI +5.5 to +10.2,
  p = 1.2e-6)**. The mask picks a few interpretable inputs out of 44 weights; mutation
  step size (σ) explains nothing ([docs/98](docs/98-poda-gpu-controle.md)).
- **A 24-parameter reactive policy beat every memory architecture** on new cities
  (3 seeds): reactive 16.68 > EMA bank 15.79 > body-drive 15.05 > hybrid 14.96 >
  dyadic memory 14.25. On the training cities the order flips: memory memorised the
  8 training cities and did not generalise. The prediction was registered before the run.
- **The simulator got 2.5–3× faster with numerical equivalence.** At 524k parallel worlds
  a step went from 24–37 ms to 10–13 ms after removing every CPU↔GPU sync, using
  Gumbel-argmax and a ring-buffer dyadic window, with `torch.compile`. Max difference
  vs the old code: 3.6e-7.
- **An evolved emergency reflex cut deaths.** A gated "emergency" reaction (fires only
  when the tank is nearly empty) lowered mortality to 0.28 vs 0.36 for the direct
  policy, better in 9/10 paired seeds, with 36% fewer breakdowns.
- **The world's hidden laws were recovered by closed-form regression.** A SINDy-style
  library + closed-form solve + pruning recovered Δfuel = −2.101 × cost (truth −2.10) and
  Δfatigue = +1.668 × cost (truth +1.65) from 37k steps, with wrong terms at ~0.000.

---

## How it works

```
 city graph (26 nodes)  ─┐
 traffic lights, NPCs    ├─►  vectorised step (B worlds in parallel, PyTorch on GPU)
 body: fuel, hunger,     │        │
   fatigue, tyre, heat   │        ▼
 economy: fares, 18% tax,│    policy = linear score over the same feature space
   upgrades              ┘        + a memory module (none / EMA / dyadic / body / hybrid)
                                  │
                                  ▼
                       GA: population × replicas, evaluated on held-out cities
```

Every architecture is linear inside and sees the same features. Only the memory that
feeds the score changes:

| Architecture | Params | Memory |
|---|---|---|
| reactive | 24 | none |
| EMA bank | 30 | 3 EMAs over visited nodes, evolved τ |
| dyadic | 30 | power-of-two blocks (log₂ of the horizon) |
| body | 30 | dominant drive pulls toward the matching service |
| hybrid | 36 | dyadic + body |

**The expert gate.** `--perito` runs the *same* hand-written policy with memory zeroed
through all five architectures. They must give identical results (`spread 0.000`).
Otherwise there is a porting bug, and a battery would be measuring that bug. This gate
caught five silent bugs during the CPU → GPU migration, among them a NaN from `.mean()`
on an empty slice that `.abs().max()` hid, and a ring buffer that broke only after
step 64.

---

## Results

| Experiment | Result | Control |
|---|---|---|
| Pruning vs free mutation, unseen cities (20 seeds) | 32.06 deliveries | generate_fine 24.23, generate 25.43 |
| Memory vs reactive, unseen cities (3 seeds) | best memory 15.79 | reactive 16.68 |
| Emergency reflex (10 seeds) | 0.28 deaths | direct 0.36 (15 seeds), 9/10 paired |
| Simulator rewrite, B = 524k | 10–13 ms/step | 24–37 ms/step, equivalence 3.6e-7 |
| Law discovery | Δfuel −2.101 × cost | ground truth −2.10 |
| Thalamic gate (per-organ, per-step tap with a cost per query) | 11.92 | always-on 5.58, static pruning 10.68 |
| Lab API under concurrent load | 300/300 OK | 182/200 failed before the SQLite thread fix |

---

## What didn't work (and why)

The lab keeps a ledger of negatives ([docs/00-NEGATIVOS.md](docs/00-NEGATIVOS.md)).
A few with their mechanism:

- **Memory did not pay in any taxi world tried** (base, no-GPS, congested streets). The
  world was one decision hop deep with nothing hidden to remember. Even avoiding
  congestion had a measured ceiling of zero, because the greedy one-hop policy plus GPS
  could not reroute.
- **A perception→action ordering bug cost ~60% of performance.** The step updated the
  node before applying the action chosen from the old observation. After the fix the
  baseline went from 9.95 to 25.43 deliveries. The first pruning result (+3.44) had been
  measured on the buggy simulator and was re-run.
- **Three-seed effects vanished at five seeds.** "Pain teaches" (+0.75 fitness at n=3),
  a 120 fat cap and block sleep all looked like wins with 3 seeds and were noise with 5.
  Since then a noise ruler is computed first: 5 seeds detect only ≥0.65 fitness /
  ≥8.5 pp deaths.
- **The "biggest jump" (+3.25 from evolved glands) was a free lunch.** The channel was
  discounting fuel below its physical cost. Once efficiency could not go below cost,
  the gain disappeared.
- **Track variety did not teach racing (Universe B9).** A pool of 6 rotating tracks
  crossed 0/16 hairpins vs 2/16 for a fixed track, and the variety arms hit walls
  faster (26–27 vs 18 m/s). Without first mastering one track, 40 generations learned
  none.

---

## Hardware and stack

| | |
|---|---|
| GPU | AMD Radeon RX 6750 XT (12 GB, gfx1031), ROCm build of PyTorch |
| CPU | AMD Ryzen 7 5800X3D |
| Language | Python 3 + PyTorch (`torch.compile`), one experimental HIP kernel in `src/hip/` |
| Run database / API | SQLite (`src/lab_db.py`), FastAPI + uvicorn (`src/lab_api/`) |
| Also runs on | CPU or Google Colab (`notebooks/colab.ipynb`, self-contained) |

---

## Build and run

```bash
pip install -r requirements.txt          # torch, numpy (install the ROCm/CUDA torch build for your GPU first)

python src/rodar.py --smoke              # seconds: checks that nothing is broken
python src/rodar.py --perito             # the gate above, required before any battery
python src/rodar.py --bateria            # full architecture battery
python src/rodar.py --bateria -P 8192 -G 100 -R 8 --seed-evo 1   # population, generations, replicas, evolution seed
python src/rodar.py --bateria --mundo hotspot                     # worlds: base, cego, hotspot, mare, ruas, semgps
```

The pruning control from the highlights:

```bash
python src/rodar.py --prune-battery -P 512 -G 60 -R 1 --tevo 450 --taval 1200 \
  --treino 6 --teste 5 --n-cidade 24 --evo-seeds $(seq 0 19) \
  --eval-reps 64 --modes generate generate_fine prune --out runs/prune-control
```

Batteries save a partial JSON after each architecture and a checkpoint every 10
generations. Running the same command again resumes; `--do-zero` restarts. Output goes to
`resultados/` unless `--out` is set. Rerun with `--seed-evo 0/1/2`: an effect smaller than
the spread between seeds is noise.

Lab API (optional, for the run observatory):

```bash
pip install -r requirements-api.txt
cd src && python -m lab_api --port 8130 --db <path/to/lab.db> --runs-root <runs dir>   # binds 127.0.0.1; --lan requires a password
python -m pytest tests/          # from the repo root; some contract suites expect a sibling lab-ui checkout (LAB_UI_REPO)
```

The API's default paths point at the author's data partition. Pass `--db`, `--runs-root`
and the other path flags explicitly on another machine.

---

## Repository map

| Path | What lives there |
|---|---|
| `src/lab.py`, `src/rodar.py` | vectorised simulation, architectures, evolution; CLI |
| `src/campo.py`, `src/e*.py` | continuous-city world and the numbered experiments (E4–E70) |
| `src/lab_db.py`, `src/lab_api/` | run database and HTTP API |
| `scripts/` | battery runner, queue daemon client, contract gate |
| `cenarios/`, `batteries/` | world scenarios and Universe battery definitions (B6–B9) |
| `docs/` | findings, analyses, predictions (`PREDICOES.md`), negatives ledger |
| `colab/`, `notebooks/` | Colab versions |
| `tests/` | API, database and trace-contract tests |

Method rules that cost the most to learn: validate the world before the policy (a
hand-written expert must beat random by a wide margin), treat a strange result as a bug
until proven otherwise, and use replicas before population (`R=8` gives 8× lower
fitness error).

## Status

Research code. The taxi world in its current form does not demand much intelligence:
3 linear terms match a 44-gene policy. Current work moves toward worlds where memory
and organs have something to earn, with a Rust port of the taxi world living in
Universe (`crates/taxi-world`).

License: TBD (no LICENSE file yet).
