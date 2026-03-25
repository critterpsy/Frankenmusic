# Frankenmusic — Motor de Generación de Contrapunto Renacentista

Frankenmusic es un **motor de generación automática de composiciones polifónicas** basado en búsqueda en árbol (depth-first search) que respeta las reglas estrictas del contrapunto renacentista según los principios de **Knud Jeppesen**.

## ¿Qué es?

Un sistema que genera **voces complementarias de contrapunto** (CP) que se ajustan a un *cantus firmus* (CF) existente, o genera cantus firmus válidos desde cero. Todas las composiciones generadas cumplen con:

- **~15 reglas melódicas**: tritono, saltos prohibidos, movimiento directo, repeticiones, etc.
- **~5 reglas armónicas**: quintas y octavas paralelas, consonancia, sensible en cadencias, etc.
- **Métricas de calidad**: variedad de notas, posición de clímax, discontinuidades controladas

## Características Principales

### Modos Soportados
Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian, incluyendo opción plagal.

### Especies de Contrapunto
- **1ª especie** (nota contra nota): implementada completamente
- **2ª–3ª especies** (estructura básica, sin soporte de disonancias aún)
- **4ª especie** (suspensiones): no implementado
- **5ª especie** (florida): no implementado

### Salida
- Secuencias de notas válidas almacenadas en memoria
- Exportación a archivos MIDI (notación moderna o período)
- Matrices de acordes multi-voz

## Estructura del Proyecto

```
.
├── src/                      # Núcleo del motor
│   ├── node.py              # Validación de reglas (15+ métodos)
│   ├── Note.py              # Utilidades musicales
│   ├── tree.py              # Serialización (minimal)
│   └── mathutils.py         # Helpers
├── treeSearch.py            # TreeSearch + Voice classes
├── tests/                   # Suite de pruebas
│   ├── test.py              # Tests ejecutables
│   └── Examples.py          # Ejemplos de validad/invalidez
├── docs/                    # Documentación de reglas
│   ├── backlog_reglas.md    # Comparación Jeppesen vs código
│   ├── jeppesen_contrapunto_reglas.md
│   └── jeppesen_contrapunto_especieN.md
├── notebooks/               # Ejemplos interactivos
│   └── play.ipynb           # (MIDI manipulation)
├── output/
│   └── midis/               # Archivos generados
└── README.md                # Este archivo
```

## Cómo Usar

### Generar un Cantus Firmus

```python
from treeSearch import TreeSearch, Voice
from src.Note import ScaleMode

# Inicializar búsqueda
ts = TreeSearch()

# Crear una voz en modo Dórico
voice = Voice(
    mode=ScaleMode.Dorian,
    index=0,
    length=8,
    range_bottom=60,  # MIDI note
    range_top=72
)

# Buscar secuencias válidas
voice.search(ts)

# Acceder a soluciones
for sequence in voice.pool:
    print(sequence)  # Lista de notas
```

### Validar Contrapunto contra Cantus Firmus

```python
from src.node import Node

# Crear nodo raíz para contrapunto
cp_node = Node(
    note=65,           # nota inicial CP
    parent=None,
    cf_sequence=[60, 62, 65, ...],  # CF conocido
    cp_index=0,
    mode=ScaleMode.Dorian,
    is_cf=False        # Es contrapunto, no CF
)

# Validar nota siguiente
next_note = 67
is_valid = cp_node.check_note(next_note)
```

## Reglas Implementadas

### Reglas Melódicas (Cantus Firmus)

| Regla | Estado | Función |
|-------|--------|---------|
| Inicio en tónica | ✅ | `check_note()` |
| Final en tónica | ✅ | `check_note()` |
| Cadencia: penúltima = 2º grado | ✅ | `check_note()` |
| Tritono melódico directo prohibido | ✅ | `checkTritoneInside()` |
| Tritono entre pivotes prohibido | ✅ | `checkTritoneIsolated()` |
| Saltos de 7ª prohibidos | ✅ | `check_jump()` |
| Salto de tritono prohibido | ✅ | `check_jump()` |
| Movimiento contrario obligatorio tras salto | ✅ | `check_movement()` |
| No repetición excesiva | ✅ | `check_repetition()` |
| Evitar secuencias melódicas repetidas | ✅ | `check_sequences()` |

### Reglas Armónicas (Contrapunto vs CF)

| Regla | Estado | Función |
|-------|--------|---------|
| Quintas directas prohibidas | ✅ | `check_direct5()` |
| Octavas directas prohibidas | ✅ | `check_direct8()` |
| Intervalos repetidos 4+ consecutivos | ✅ | `checkrepintervals()` |
| Cadencia: sensible → tónica (voz superior) | ✅ | `check_chord()` |

### Reglas No Implementadas

- ⏳ Paralelas de 5ª/8ª (vs directas)
- ⏳ Consonancia obligatoria en cada tiempo (1ª especie)
- ⏳ Disonancias preparadas/resueltas (2ª–3ª especies)
- ⏳ Suspensiones (4ª especie)
- ⏳ Mezcla de duraciones (5ª especie)

## Problemas Conocidos

### Bugs Activos
1. `check_sequences()` genera falsos positivos en ejemplos modales (Dorico, Frigio, Mixolidio)
2. `check_note()` rechaza cadencias válidas en modo Frigio (raíz en posición -3)
3. `check_jump()` rechaza 6ª menor descendente válida en CP

### Deuda Técnica
- Cientos de `print()` de debug distribuidos en paths críticos
- Documentación escasa (pocos docstrings)
- Método `Node.FromSequence()` roto e incompatible
- Generador `generate_second_species()` nunca completado

## Ejecución de Tests

```bash
cd /Users/daniel/Documents/Frankenmusic
python3 tests/test.py
```

Resultado esperado: **4 tests pasan**, documentados en `CF_KNOWN_BUGS` y `CP_KNOWN_BUGS`.

## Documentación Detallada

- **[backlog_reglas.md](docs/backlog_reglas.md)** — Comparación punto-a-punto entre teoría Jeppesen e implementación
- **[jeppesen_contrapunto_reglas.md](docs/jeppesen_contrapunto_reglas.md)** — Reglas generales
- **[jeppesen_contrapunto_especieN.md](docs/)** — Especificaciones por especie (1–5)

## Roadmap

- [ ] Eliminar/reemplazar `print()` por logging estructurado
- [ ] Arreglar falsos positivos en `check_sequences()`
- [ ] Arreglar validación de cadencias en Frigio
- [ ] Implementar disonancias de paso (2ª–3ª especies)
- [ ] Soporte de 4ª especie (suspensiones)
- [ ] Soporte de 5ª especie (florida)

## Autor

**Daniel** — Frankenmusic Project

---

*Última actualización: Marzo 2026*
