# Backlog — Frankenmusic

## En progreso
_Ninguna tarea activa actualmente._

## Completadas
- [x] **Arreglar los 5 bugs críticos**
  - `tests/Examples.py:25` — variable `seq` → `sequence`, función `Note.diatonicScale` → `Note.white_scale`
  - `tests/Examples.py:3` — import `from src.Note import Note` → `from src import Note`
  - `src/Note.py:103` — `interval()` con `modulo12=False` devolvía `% 1` (siempre 0)
  - `src/Note.py:115` — `interval_table()` no retornaba el resultado
  - `src/Note.py:118` — `consonance()` llamaba a `interval_12()` inexistente → `interval()`
  - `src/node.py:341` — `self.reference` inexistente → `self.ref`

- [x] **Re-habilitar y reparar la suite de tests**
  - `tests/test.py` reescrito para usar la API actual de `Node` + `Voice`
  - 4 tests pasan: `TestCF::test_fail_examples`, `TestCF::test_valid_examples`, `TestCP::test_fail_examples`, `TestCP::test_valid_examples`
  - Bugs de validación documentados en `CF_KNOWN_BUGS` / `CP_KNOWN_BUGS` dentro del archivo

## Pendiente

- [x] **Eliminar o reemplazar los `print()` de debug por logging**
  - Cientos de `print()` en paths críticos de `node.py`, `treeSearch.py`, `src/Note.py`
  - Reemplazar por `logging.debug()` o eliminar según corresponda

- [x] **Eliminar código muerto**
  - `treeSearch.py` — método `generate_second_species()` comentado, nunca implementado
  - `src/node.py` — método `Node.FromSequence()` con API rota e incompatible
  - `tests/test.py` — comentarios de tests de APIs antiguas ya removidos en la reescritura

- [x] **Arreglar `check_sequences` (falsos positivos en ejemplos modales)**
  - Ejemplos afectados: `dorico`, `frigio3`, `mixo` (ver `CF_KNOWN_BUGS` en `tests/test.py`)
  - La función detecta como "secuencias prohibidas" cadencias modales válidas
  - Diagnóstico original: lógica extremadamente compleja, difícil de seguir

- [x] **Arreglar `check_note` para modo Frigio**
  - La regla prohíbe la raíz del modo en posición `length-3` para todos los modos
  - En Frigio, la cadencia natural lleva a E antes de la aproximación F→E final
  - Ejemplo afectado: `frigio` (ver `CF_KNOWN_BUGS` en `tests/test.py`)

- [x] **Arreglar `check_jump` (6ª menor descendente permitida en CP)**
  - La regla prohíbe saltos descendentes de exactamente 8 semitonos
  - Un ejemplo de contrapunto válido contiene C→E (−8 semitonos), que es rechazado
  - Ejemplo afectado: `cp_examples[1]` (ver `CP_KNOWN_BUGS` en `tests/test.py`)

- [x] **Arreglar `check_movement` (condición de salto ascendente invertida)** ✓ _arreglado_
  - `src/node.py:271` — `jump > 2 and lastJump > 0` debía ser `lastJump > 2 and jump > 0`
  - La condición original bloqueaba cualquier salto ascendente después de un paso ascendente
  - La regla correcta es simétrica: después de un salto grande ↑, no puedes seguir ↑

- [x] **Arreglar `note_range` (colisión de nombre con función `consonance`)** ✓ _arreglado_
  - `src/Note.py:241` — `consonance = filter.get('consonances')` pisaba la función del módulo
  - Si se pasaba `consonances=True`, llamar `consonance(root, note)` crasheaba con TypeError
  - Fix: renombrar variable a `filter_consonance`

- [x] **Arreglar `valid_chord` (muta el input y pisa builtin `min`)**
  - `src/Note.py:141` — `chord.sort()` modifica en-lugar la lista recibida del caller
  - `src/Note.py:142` — `min = chord[0]` oculta el builtin `min()`
  - Puede causar bugs sutiles en la validación de CP donde el orden del chord importa

- [x] **Revisar `check_jump` (chequeo diatónico probablemente código muerto)**
  - `src/node.py:224` — `if jump == 4 and abs(diat) == 3` nunca se cumple con notas blancas + Bb
  - En la escala generada por `note_range`, todos los saltos de 4 semitonos son 3ras mayores (diat=2)
  - Confirmar si la condición tiene algún caso de uso real o eliminarla

- [x] **Revisar `checkTritoneIsolated` (pivot inicializado en 0, no None)** ✓ _correcto_
  - `self.pivot = 0` es intencional: la nota inicial actúa como primer pivot implícito
  - Cambiar a `None` abriría un hueco: el arco inicio→primer giro no se chequearía

- [ ] **Arreglar `Node.FromSequence` (API rota)**
  - `src/node.py:484` — llama `sequence.reverse()` sobre `*args` (tupla, no lista) → AttributeError
  - Constructor de Node dentro del método usa API antigua incompatible con la actual
  - Eliminar o reescribir si se necesita validar secuencias directamente
