# Third Species Migration Matrix (Canon 2026-03-30)

Fuente normativa: [`/third_species.md`](../third_species.md)

Estado:
- `DONE`: implementado en validación/búsqueda/ranking.
- `PARTIAL`: cubierto de forma parcial o con heurística.
- `TODO`: pendiente.

| Regla canónica (`third_species.md`) | Estado | Implementación principal |
|---|---|---|
| Métrica 4:1 + compás final colapsado | DONE | `src/species/engine.py`, `src/species/plans.py`, `src/species/rules/third_species.py` |
| Apertura P5/P8 (arriba) y P8/P1 (abajo) | DONE | `src/species/rules/third_species.py`, `src/species/search_third.py` |
| Arranque opcional con silencio en q=1 | DONE | `src/species/config.py`, `src/species/rules/third_species.py`, `src/species/search_third.py` |
| q=1 y q=3 consonantes | DONE | `src/species/rules/third_species.py`, `src/species/search_third.py` |
| Disonancia solo en q=2/q=4 | DONE | `src/species/rules/third_species.py`, `src/species/rules/third_figures.py` |
| Figuras disonantes: passing/lower-neighbor/cambiata | DONE | `src/species/rules/third_figures.py`, `src/species/rules/third_species.py`, `src/species/search_third.py` |
| Upper neighbor disonante prohibida | DONE | `src/species/rules/third_species.py`, `src/species/search_third.py` |
| Unísono interior en q=1 prohibido | DONE | `src/species/rules/third_species.py`, `src/species/search_third.py` |
| Cadencia final a P1/P8, aproximación por paso | DONE | `src/species/rules/cadence.py`, `src/species/search_third.py` |
| Subtónica cadencial (semitono o tono frigio) | DONE | `src/species/rules/cadence.py`, `src/species/search_third.py` |
| Salto desde apoyo acentuado debe descender | DONE | `src/species/rules/third_melodic.py` |
| Salto desde débil normalmente asciende; excepción cambiata/tercera descendente controlada | DONE | `src/species/rules/third_melodic.py` |
| Salto solo entre verticalidades consonantes (excepto cambiata) | DONE | `src/species/rules/third_melodic.py` |
| Compensación después de salto amplio | DONE | `src/species/rules/third_melodic.py` |
| Evitar paralelas perfectas y directas a perfecta en apoyos estructurales | DONE | `src/species/rules/third_voice_independence.py` |
| Límite de series: perfectas/imperfectas repetidas en q=1 | DONE | `src/species/rules/third_voice_independence.py` |
| Restricciones extra de entrada a P5/P8 desde débiles del compás anterior | DONE | `src/species/rules/third_voice_independence.py` |
| Preferir consonancias imperfectas en apoyos | DONE | `src/species/ranking.py` |
| Penalizar secuencias/patrones mecánicos/reiteraciones | DONE | `src/species/ranking.py` |
| Clímax principal único y no coincidente con CF | PARTIAL | `src/species/ranking.py` |
| Evitar repetición cercana de cambiata | DONE | `src/species/ranking.py` |

Notas:
- Los docs `docs/jeppesen_contrapunto_especie3.md`, `docs/jeppesen_contrapunto_reglas.md` y `docs/dump_especies.md` quedan en estado **legacy**.
- La API pública (`validate_third_species`, `search_third_species`, `rank_third_species_solution`) se mantiene estable.
