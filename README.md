# Frankenmusic — Renaissance Counterpoint Generation Engine

Frankenmusic is an **automatic polyphonic composition engine** based on depth-first tree search, implementing the strict rules of Renaissance counterpoint as defined by **Knud Jeppesen**.

## Overview

The system generates valid **counterpoint voices (CP)** against an existing *cantus firmus* (CF), or generates valid cantus firmi from scratch. All compositions comply with:

- **~15 melodic rules**: tritone avoidance, forbidden leaps, contrary motion, repetition limits, etc.
- **~5 harmonic rules**: parallel fifths/octaves, consonance requirements, leading tone resolution, etc.
- **Quality metrics**: note variety, climax placement, controlled melodic discontinuities

## Features

### Supported Modes
Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian — including plagal variants.

### Counterpoint Species
- **1st species** (note against note): fully implemented in the legacy `TreeSearch` engine
- **2nd species** (2:1 against a cantus firmus): implemented in `src/species/` with validation, exhaustive search, ranking, weak-beat passing dissonances, and CLI support
- **3rd species** (4:1): planned
- **4th species** (suspensions): planned
- **5th species** (florid): planned

### Output
- Valid note sequences stored in memory
- MIDI file export (modern or period notation)
- Multi-voice chord matrices

## Project Structure

```
.
├── src/                      # Engine core
│   ├── node.py              # Rule validation (15+ methods)
│   ├── Note.py              # Music theory utilities
│   ├── species/             # Dedicated engine for 2nd species
│   ├── tree.py              # Serialization
│   └── mathutils.py         # Helpers
├── treeSearch.py            # TreeSearch + Voice classes
├── tests/                   # Test suite
│   ├── test.py              # Executable tests
│   ├── species/             # 2nd-species engine and CLI tests
│   └── Examples.py          # Valid/invalid sequence examples
├── docs/                    # Rule documentation
│   ├── backlog_reglas.md    # Jeppesen theory vs. implementation comparison
│   ├── jeppesen_contrapunto_reglas.md
│   └── jeppesen_contrapunto_especieN.md
├── notebooks/               # Interactive examples
│   └── play.ipynb
├── output/
│   └── midis/               # Generated MIDI files
└── README.md
```

## Usage

### CLI

#### Generate 1st-Species Counterpoint

```bash
python3 generate_counterpoint.py --species 1 --modo C --length 8 --num_voices 2
```

#### Generate 2nd-Species Counterpoint from an Explicit CF

```bash
python3 generate_counterpoint.py --species 2 --cf 0,2,4,5 --cp_disposition above
```

Notes:

- `--cf` expects internal pitch integers separated by commas
- `--cp_disposition` accepts `above` or `below`
- `--species 2` currently generates exactly 2 voices: CF + CP
- `--export_midi` and `--open_score` work for both species routes

#### Generate 2nd-Species Counterpoint from an Auto-Generated CF

```bash
python3 generate_counterpoint.py --species 2 --modo D --length 6 --cp_disposition below
```

In this mode, the script generates several candidate cantus firmi with the legacy engine, tries them automatically against the new `src/species/` engine, and keeps the first CF that admits a valid 2nd-species line. If the quick passes fail, it widens the CF search automatically before giving up.

### Generate a Cantus Firmus

```python
from treeSearch import TreeSearch, Voice
from src.Note import ScaleMode

ts = TreeSearch()

voice = Voice(
    mode=ScaleMode.Dorian,
    index=0,
    length=8,
    range_bottom=60,  # MIDI note number
    range_top=72
)

voice.search(ts)

for sequence in voice.pool:
    print(sequence)
```

### Validate Counterpoint Against a Cantus Firmus

```python
from src.node import Node

cp_node = Node(
    note=65,
    parent=None,
    cf_sequence=[60, 62, 65, ...],
    cp_index=0,
    mode=ScaleMode.Dorian,
    is_cf=False
)

next_note = 67
is_valid = cp_node.check_note(next_note)
```

## Implemented Rules

### Melodic Rules (Cantus Firmus)

| Rule | Status | Function |
|------|--------|----------|
| Start on tonic | ✅ | `check_note()` |
| End on tonic | ✅ | `check_note()` |
| Penultimate = 2nd degree | ✅ | `check_note()` |
| Direct tritone forbidden | ✅ | `checkTritoneInside()` |
| Outlined tritone forbidden | ✅ | `checkTritoneIsolated()` |
| Seventh leaps forbidden | ✅ | `check_jump()` |
| Tritone leap forbidden | ✅ | `check_jump()` |
| Contrary motion required after leap | ✅ | `check_movement()` |
| No excessive repetition | ✅ | `check_repetition()` |
| No repeated melodic sequences | ✅ | `check_sequences()` |

### Harmonic Rules (Counterpoint vs CF)

| Rule | Status | Function |
|------|--------|----------|
| Direct fifths forbidden | ✅ | `check_direct5()` |
| Direct octaves forbidden | ✅ | `check_direct8()` |
| 4+ consecutive repeated intervals | ✅ | `checkrepintervals()` |
| Leading tone → tonic resolution | ✅ | `check_chord()` |

### Planned Rules

- ⏳ Parallel fifths/octaves (vs. direct)
- ⏳ Mandatory consonance on each beat (1st species)
- ⏳ 3rd-species rhythmic and dissonance handling
- ⏳ Suspensions (4th species)
- ⏳ Mixed note values (5th species)

## Known Limitations

- `check_sequences()` produces false positives in certain modal contexts (Dorian, Phrygian, Mixolydian)
- Cadence validation in Phrygian mode rejects some valid progressions
- `check_jump()` incorrectly rejects valid descending minor sixths in CP

## Running Tests

```bash
python3 tests/test.py
```

Legacy engine regression suite.

```bash
python3 -m unittest tests.species.test_second_species_engine tests.species.test_generate_counterpoint_cli
```

Second-species engine validation, search, ranking, and CLI integration suite.

## Roadmap

- [ ] Replace debug `print()` statements with structured logging
- [ ] Fix false positives in `check_sequences()` for modal contexts
- [ ] Fix Phrygian cadence validation
- [ ] Extend the dedicated species engine to 3rd species
- [ ] Unify the legacy `TreeSearch` and `src/species/` workflows behind one shared interface
- [ ] Implement 4th species (suspensions)
- [ ] Implement 5th species (florid counterpoint)

## Author

**Daniel Ritter Miller**
[linkedin.com/in/daniel-ritter-miller-0368252a8](https://linkedin.com/in/daniel-ritter-miller-0368252a8)

---

*Last updated: March 2026*
