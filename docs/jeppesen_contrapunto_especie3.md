# LEGACY — Contrapunto 3ª especie (Jeppesen) — Motor Frankenmusic

> Estado: **legacy** desde **2026-03-30**.
> Canon vigente para implementación: [`/third_species.md`](../third_species.md).
> Este archivo se conserva solo como referencia histórica de la versión `v1`.

Este documento separa explícitamente:

- **Doctrina jeppeseniana operable**
- **Restricciones de implementación v1**

## API pública

- `validate_third_species(cf, cp, config=None)`
- `search_third_species(cf, config=None)`
- `rank_third_species_solution(cf, cp, config=None)`

Representación:

- `ThirdSpeciesMeasure(beat1, beat2, beat3, beat4)`
- `ThirdSpeciesLine(measures=[...])`
- Grid canónico del cuerpo: `4*N - 3` slots.
- Compás final colapsado a nota larga final (`beat2/beat3/beat4 = None`).
- Apertura doctrinal opcional con `quarter rest` en `beat1` del primer compás (`allow_half_rest_start=True`).

## Doctrina jeppeseniana implementada

### Métrica y consonancia

- `beat1` y `beat3` deben ser consonantes.
- `beat2` y `beat4` pueden ser consonantes o disonantes.
- Disonancias solo en `beat2` o `beat4`.

### Figuras disonantes permitidas

Solo se aceptan estas tres clases:

1. `passing tone`
2. `lower neighbor`
3. `cambiata` (forma canónica descendente)

No se admite:

- `upper neighbor` disonante
- semántica de 4ª especie (ligaduras/suspensiones)

### Unísono y repeticiones

- Unísono prohibido en `beat1` interior.
- Unísono permitido en cuartos no iniciales si no rompe independencia.
- Repeticiones inmediatas: error duro.
- Repetición trivial `beat2 == beat4`: error duro.
- Reutilizar la misma nota de lower-neighbor dos veces seguidas: error duro.
- Otras reiteraciones no inmediatas: degradación estilística en ranking.

### Cadencia

- Último ataque: `P1` o `P8` con el CF.
- Aproximación final por paso.
- Subtónica cadencial obligatoria (semitono, o tono en frigio).

## Reglas formales de figuras (operables)

### Passing Tone

Ventana mínima: `strong_prev, weak, strong_next`

- `weak` en `beat2` o `beat4`
- `weak` disonante
- `strong_prev` y `strong_next` consonantes
- entrada por paso, salida por paso
- misma dirección en entrada y salida

### Lower Neighbor

Ventana mínima: `strong_prev, weak, strong_next`

- `weak` en `beat2` o `beat4`
- `weak` disonante
- `strong_prev == strong_next`
- `weak` un grado por debajo de `strong_prev`
- entrada/salida por paso en direcciones opuestas

### Cambiata (nota cambiata)

Ventana mínima: `n1, n2, n3, n4, n5`

- `n2` única disonancia de la figura
- `n2` en `beat2` o `beat4`
- `n1, n3, n4, n5` consonantes en sus posiciones
- `n1 -> n2`: paso
- `n2 -> n3`: salto de tercera en la misma dirección
- `n3 -> n4 -> n5`: dos pasos en dirección opuesta
- se reconoce también al cruzar barra
- v1 acepta solo forma canónica descendente

## Restricciones v1 (no declarar como doctrina)

- Solver dedicado por compás con pruning local y validación global; no cubre todavía todas las variantes rítmicas editoriales del penúltimo compás reportadas en otras síntesis.
- El compás final se mantiene colapsado por diseño de representación.
- La ruta CLI principal sigue priorizando especie 1 y 2; la especie 3 está expuesta y probada a nivel de API/engine.

## Tests mínimos implementados

- `cambiata` válida
- casi-`cambiata` inválida
- apertura con `quarter-rest` inicial
- unísono permitido en cuarto no inicial
- unísono inválido en `beat1` interior
- repetición trivial `beat2 == beat4` rechazada
- reutilización de same lower-neighbor rechazada
- reiteración no trivial conservada y penalizada en ranking
