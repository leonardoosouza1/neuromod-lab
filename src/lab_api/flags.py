"""Derives the arm-flag allow-list from `gpu_evolve`'s own canonical registry.

lab-ui PRD S1, Launcher/queue delivery: "arm flags only from an allow-list you
derive from `Universe/src/bin/gpu_evolve/cli_flags.rs` -- read it, do not invent."

`cli_flags.rs` is itself the single source of truth `gpu_evolve`'s argument loop
matches against (its own docstring: "the names live here, once"). This module
regex-parses that Rust file's `FLAGS` table -- rather than hand-copying the ~130
flag names into Python, which would silently drift the day someone adds or
renames a flag in Rust and not here. It is deliberately a narrow parser (one
`flag(...)` call per line, `#[rustfmt::skip]`-preserved -- see that file's own
comment on why it is kept one row per line) and raises if it parses zero flags,
so a format change is loud rather than silently producing an empty allow-list.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

# Matches one `flag("--name", &[...aliases...], VALUE|SWITCH, "help")` call.
# `[^)]*?` for the help text would be simpler but risks matching past a `)` inside
# a string; the help column is not needed here, so the pattern stops at the
# VALUE/SWITCH token and ignores the rest of the line.
_FLAG_RE = re.compile(
    r'flag\(\s*"(?P<name>--[A-Za-z0-9-]+)"\s*,\s*&\[(?P<aliases>[^\]]*)\]\s*,\s*'
    r'(?P<takes_value>VALUE|SWITCH)\s*,'
)
_ALIAS_RE = re.compile(r'"(--[A-Za-z0-9-]+)"')


@dataclass(frozen=True)
class FlagSpec:
    canonical: str        # e.g. "--no-neuron-memory", WITH leading dashes
    aliases: tuple[str, ...]
    takes_value: bool


class FlagRegistryError(ValueError):
    """Raised when cli_flags.rs cannot be found or parses to zero flags."""


@lru_cache(maxsize=8)
def load_flag_registry(cli_flags_path: str) -> dict[str, FlagSpec]:
    """Parses the `FLAGS` table of `cli_flags.rs`.

    Returns a dict keyed by flag name WITHOUT leading dashes, both canonical
    and every deprecated alias mapping to the same `FlagSpec` -- so a caller
    can look up whichever spelling a request used. Cached (`lru_cache`) since
    the file only changes when Universe is rebuilt, not per-request.
    """
    path = Path(cli_flags_path)
    if not path.is_file():
        raise FlagRegistryError(f"cli_flags.rs not found at {path}")
    text = path.read_text()
    registry: dict[str, FlagSpec] = {}
    for m in _FLAG_RE.finditer(text):
        name = m.group("name")
        aliases = tuple(_ALIAS_RE.findall(m.group("aliases")))
        spec = FlagSpec(canonical=name, aliases=aliases, takes_value=m.group("takes_value") == "VALUE")
        registry[name.lstrip("-")] = spec
        for alias in aliases:
            registry[alias.lstrip("-")] = spec
    if not registry:
        raise FlagRegistryError(
            f"parsed zero flags from {path} -- has the FLAGS table's format changed?"
        )
    return registry


# Flags the queue schema already exposes as dedicated, typed fields (bin, gens,
# ticks, beings, width, seed, tracks, cost/gate, trace profile/cadence) or that
# control process plumbing the API itself owns (--out, --resume, --panel*).
# Submitting one of these as an "arm flag" would either duplicate or fight the
# value the dedicated field already sets, so they are excluded from the
# arm-flag allow-list rather than left for `args` to silently collide on.
RESERVED_FLAG_NAMES = frozenset({
    "beings", "seres", "ticks", "gens", "seed", "width",
    "tracks", "pistas", "track-held-out", "pista-held-out", "held-out-every", "held-out-cada",
    "wall-cost", "impact-cost", "cost-gate-progress",
    "driving-diagnostics", "vision-being", "vision-every", "same-start",
    "out", "resume", "retomar", "panel", "painel", "panel-port", "painel-porta",
    "replay-every", "replay-cada",
})


def arm_flag_allow_list(cli_flags_path: str) -> dict[str, FlagSpec]:
    """The registry minus `RESERVED_FLAG_NAMES` -- what `routes/queue.py` actually
    validates a request's `arm_flags` entries against."""
    registry = load_flag_registry(cli_flags_path)
    return {name: spec for name, spec in registry.items() if name not in RESERVED_FLAG_NAMES}
