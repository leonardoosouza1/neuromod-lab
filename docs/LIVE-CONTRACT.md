# Live contract (slice S6)

Live view = 1–4 Hz population snapshots of a run in flight. Tick-by-tick data and neural
stages exist only in replay (trace-v1); the relay never polls `/api/activation`.

## Producer

`gpu_evolve --panel --panel-port <3200..3299>` serves `/api/status` and `/api/beings`
(`src/bin/gpu_evolve/painel.rs`, frozen binary `gpu_evolve-f5d203b`). Field names come from
the producer and are passed through unchanged (several are Portuguese); the UI maps them.

## Discovery

`GET /api/live/runs` → `[{"run": "s6smoke_panel", "port": 3290, "battery": null}]`: nmd spool
`estado/*.json` with `fase == "rodando"`, a live pid and a panel port in argv.

## Stream

`WS /ws/live?port=N&hz=H` — `N` in 3200..3299 on 127.0.0.1 only (else close 1008);
`H` clamped to 1..4 (default 2). Under `--lan` a session cookie is required before
`accept()` (else close 1008). Payloads are never logged.

Snapshot frame (real, captured 16/09 19:25 from `s6smoke_panel`, 8 beings; lists trimmed):

```json
{"type": "snapshot", "port": 3290, "run": "s6smoke_panel", "t": "2026-09-16T22:25:10+00:00",
 "status": {"geracao": 0, "tick": 192, "vivos": 8, "mediana_m": 0.0, "elite_m": 0.0,
            "mortos_pct": 0.0, "obediencia_pct": 0.0, "setores": [], "slope": 0.0,
            "vel_mediana": 0.0, "life_mediana": 0.449, "fuel_mediana": 0.781,
            "activation_alarms": [], "dead_pct_l1": 0.0, "saturated_pct_l1": 0.0,
            "spectral_radius": 0.0, "snr_i8": 0.0,
            "waypoints": [[623.32, 716.93], [602.17, 709.16], "..."]},
 "beings": [{"id": 0, "x": 612.75, "z": 713.04, "vel": 0.0, "life": 0.166, "vivo": true}, "..."]}
```

| field | meaning |
|---|---|
| `status.geracao`, `status.tick` | generation and tick inside it (the tick advances ~64 per frame at 2 Hz on a busy GPU; frames may repeat a tick) |
| `status.vivos`, `mortos_pct` | alive beings; percentage dead |
| `status.mediana_m`, `elite_m` | median and best progress of the generation so far (m) |
| `status.vel_mediana`, `life_mediana`, `fuel_mediana` | medians over alive beings |
| `status.waypoints` | track axis `[x, z]` in world metres — draw the track from this |
| `beings[i]` | `id`, world position `x`/`z` (m), `vel` (m/s), `life` (0..1), `vivo` |

Error frame, sent when the panel port is down, refuses, or returns non-JSON/non-2xx; the
relay keeps retrying at 1 Hz:

```json
{"type": "error", "port": 3290, "error": "connection refused"}
```

Sample of 20 real frames: `/media/llm-data/scratch/s6/frames.jsonl`.
