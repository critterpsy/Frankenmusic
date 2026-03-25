# Backlog — Reglas de contrapunto (Jeppesen vs. código)

## Reglas melódicas del Cantus Firmus

- [x] **Inicio en tónica** — `check_note`: primera nota == `modo`
- [x] **Final en tónica** — `check_note`: última nota == `modo`
- [x] **Cadencia: penúltima = 2º grado** — `check_note`: antepenúltima debe ser el 2º grado diatónico
- [x] **Tritono melódico directo prohibido** — `checkTritoneInside`: intervalo == 6 st entre notas adyacentes
- [x] **Tritono entre pivotes prohibido** — `checkTritoneIsolated`: tritono entre cambios de dirección
- [x] **Salto de 7ª (mayor y menor) prohibido** — `check_jump`: `jump == 11` y `jump == 10`
- [x] **Salto de tritono prohibido** — `check_jump`: `jump == 6`
- [x] **Salto >8ª prohibido** — `check_jump`: `jump > 12`
- [x] **6ª menor descendente permitida, ascendente no** — `check_jump`: `jump == 8 and note < parent`
- [x] **Movimiento contrario obligatorio tras salto** — `check_movement`: tras salto > 2ª, el siguiente paso debe ser contrario
- [x] **No repetición excesiva** — `check_repetition`: 3 notas iguales consecutivas prohibidas; CF no permite ninguna repetición directa
- [x] **Evitar secuencias melódicas repetidas** — `check_sequences`: detecta patrones de intervalos diatónicos repetidos en grupos de 3–6 notas
- [ ] **TODO: Salto >6ª requiere compensación por paso** — Jeppesen exige uno o dos pasos contrarios tras 6ª/7ª; el código prohíbe la 7ª pero no verifica la compensación posterior
- [ ] **TODO: Sib permitido en modos que lo requieren** — el código lo prohíbe absolutamente en CF; Jeppesen lo permite en modos con Bb (F, Bb)

## Reglas armónicas (CP contra CF)

- [x] **Quintas directas prohibidas** — `check_direct5`: movimiento similar hacia 5ª
- [x] **Octavas directas prohibidas** — `check_direct8`: movimiento similar hacia 8ª
- [x] **Unísono en medio prohibido (2 voces)** — `cp_valid_generator` con `twovoices`
- [x] **Intervalos repetidos CP/CF** — `checkrepintervals`: 4 intervalos diatónicos idénticos consecutivos entre voces
- [x] **Cadencia: sensible → tónica en voz superior** — `check_chord` para `index == length - 2`
- [ ] **TODO: Paralelas de 5ª prohibidas** — el código detecta 5ª *directas* pero no 5ª *paralelas* (5P → 5P en movimiento similar); son reglas distintas
- [ ] **TODO: Paralelas de 8ª prohibidas** — igual que el punto anterior para octavas
- [ ] **TODO: Consonancia obligatoria en cada tiempo (1ª especie)** — `check_chord` solo valida inicio, penúltima y final; los tiempos intermedios no se verifican
- [ ] **TODO: Disonancias de paso preparadas y resueltas (2ª–3ª especie)** — no existe lógica de preparación/resolución; todas las notas se tratan como iguales
- [ ] **TODO: Suspensiones 4-3, 7-6, 2-1 (4ª especie)** — no hay implementación de ligaduras ni suspensiones
- [ ] **TODO: 5ª especie (florida)** — no hay soporte para mezcla de duraciones

## Métricas de calidad (propias del motor, no Jeppesen)

- [x] **Discontinuidades máximas** — `prune_node`: `disc` cuenta saltos > tono; límite configurable
- [x] **Posición del clímax** — `prune_node`: `hiIndex` debe aparecer después de cierto índice
- [x] **Variedad mínima de notas** — `prune_node`: mínimo de notas distintas en la secuencia
- [x] **Repeticiones de tónica mínimas** — `prune_node`: mínimo de apariciones del modo
