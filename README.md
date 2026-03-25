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
- **1st species** (note against note): fully implemented
- **2nd–3rd species** (basic structure): implemented without dissonance support
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
│   ├── tree.py              # Serialization
│   └── mathutils.py         # Helpers
├── treeSearch.py            # TreeSearch + Voice classes
├── tests/                   # Test suite
│   ├── test.py              # Executable tests
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
- ⏳ Prepared and resolved dissonances (2nd–3rd species)
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

Expected result: **4 tests pass**. Known edge cases are documented in `CF_KNOWN_BUGS` and `CP_KNOWN_BUGS` within the test file.

## Roadmap

- [ ] Replace debug `print()` statements with structured logging
- [ ] Fix false positives in `check_sequences()` for modal contexts
- [ ] Fix Phrygian cadence validation
- [ ] Implement passing dissonances (2nd–3rd species)
- [ ] Implement 4th species (suspensions)
- [ ] Implement 5th species (florid counterpoint)

## Author

**Daniel Ritter Miller**
[linkedin.com/in/daniel-ritter-miller-0368252a8](https://linkedin.com/in/daniel-ritter-miller-0368252a8)

---

*Last updated: March 2026*
