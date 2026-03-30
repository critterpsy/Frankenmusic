"""Canonical cantus-firmus presets shared by CLI species workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalCF:
    name: str
    sequence: tuple[int, ...]
    notes: tuple[str, ...]
    description: str = ""


_USER_MELODY_KEY = "d_f_re_e_g_f_a_g_f_e_d"

CANONICAL_CFS: dict[str, CanonicalCF] = {
    _USER_MELODY_KEY: CanonicalCF(
        name=_USER_MELODY_KEY,
        sequence=(2, 5, 2, 4, 7, 5, 9, 7, 5, 4, 2),
        notes=("D", "F", "RE", "E", "G", "F", "A", "G", "F", "E", "D"),
        description="Melodia solicitada: D, F, R/RE, E, G, F, A, G, F, E, D",
    ),
}

CANONICAL_CF_ALIASES: dict[str, str] = {
    "dfregfagfed": _USER_MELODY_KEY,
    "d-f-r-e-g-f-a-g-f-e-d": _USER_MELODY_KEY,
    "d_f_r_e_g_f_a_g_f_e_d": _USER_MELODY_KEY,
}


def canonical_cf_names() -> list[str]:
    """Return canonical names in deterministic order."""
    return sorted(CANONICAL_CFS.keys())


def resolve_canonical_cf_name(raw_name: str) -> str:
    """Resolve a canonical CF name or alias to the canonical key."""
    if not raw_name:
        raise KeyError("Nombre de CF canónico vacío.")
    key = raw_name.strip().lower()
    if key in CANONICAL_CFS:
        return key
    if key in CANONICAL_CF_ALIASES:
        return CANONICAL_CF_ALIASES[key]
    raise KeyError(raw_name)


def canonical_cf_sequence(raw_name: str) -> list[int]:
    """Return canonical CF sequence by name/alias as a mutable list."""
    canonical_name = resolve_canonical_cf_name(raw_name)
    return list(CANONICAL_CFS[canonical_name].sequence)
