# Contrapunto 1ª especie (Jeppesen) - Mapa de reglas para Frankenmusic

Este documento recoge reglas de Jeppesen para contrapunto de 1ª especie (nota contra nota) con un formato de motor.

## 1. Objetivo

- Generar y validar líneas contrapuntísticas de dos voces en 1ª especie.
- Aplicar reglas estrictas de consonancia y movimiento de voces.
- Evitar errores típicos: quintas/octavas paralelas, disonancias, saltos no compensados.

## 2. Filosofía Jeppesen

- 1ª especie: un compás/nota de la voz exterior coincidiendo con un compás/nota de la voz principal.
- Todo evento armónico debe ser consonante (3ª, 6ª, 5ª, 8ª, 1ª).
- Las disonancias no están permitidas en 1ª especie, salvo contextualizaciones muy raras (evitables).

## 3. Intervalos permitidos

```
Intervalos permitidos:
- Perfectos: 1P, 5P, 8P.
- Imperfectos: 3m, 3M, 6m, 6M.

Intervalos prohibidos:
- 2da (m/M), 7ma (m/M), 4ª justa en consonancia directa (solo 4-3 transición en especies posteriores), 5ª disminuida, 8ª aumentada, cualquier intervalos aumentados/diminuidos.
```

## 4. Regla de paralelas

- `i(t-1)` y `i(t)` no pueden ser ambos 5P o ambos 8P si:
  - `direccion(v1(t-1)->v1(t)) == direccion(v2(t-1)->v2(t))`.

- Evaluar para voz superior/voz inferior y, en extensiones, para todas las pares adyacentes en 3+ voces.

## 5. Movimiento recomendado

- priorizar: contrario > oblicuo > similar.
- permitir similar solo si no deriva en quinta/octava cercana.
- evitar grandes saltos seguidos.

### 5.1 Saltos permitidos

- 2ª y 3ª: oregulares, naturales
- 4ª y 5ª: permitidos con compensación (paso contrario inmediato)
- 6ª: permitidos, preferir resolución por paso en dirección opuesta
- >6ª: rara, solo con compensación y un paso contrario después

## 6. Reglas de inicio y cierre

### 6.1 Inicio
- voz inferior: tonalidad tónica (C en Do mayor) o modo correspondiente.
- voz superior: tónica, tercera o quinta.

### 6.2 Cierre
- cadencia final básica: V -> I (para voz principal) con v1 capaz de resolver sensible a tónica.
- cierre de dos voces: tratar como progresión a unísono/u octava final.

## 7. Chequeo semántico de consonancia

- `isConsonant(interval) -> bool`
- `isPerfectConsonance(interval)` etc.

## 8. Pseudocódigo de validación 1ª especie

```python
CONSONANT = {'P1','m3','M3','P5','m6','M6','P8'}
FOR pos in range(1,len(list)):
    i_prev = interval(v1[pos-1],v2[pos-1])
    i_curr = interval(v1[pos], v2[pos])

    if i_curr not in CONSONANT:
        reject('disonancia en especie 1')

    if i_prev in {'P5','P8'} and i_curr in {'P5','P8'}:
        if direction(v1[pos-1],v1[pos]) == direction(v2[pos-1],v2[pos]):
            reject('paralelas prohibidas')

    if abs(step(v1[pos-1],v1[pos])) > 7 and not compensating_step(v1,pos):
        reject('salto excesivo sin compensar')

    # cadencia comprobada en final

validate_start_end(v1,v2)
```

## 9. Casos de prueba breves

- Válido: C4/G3 -> D4/A3 -> E4/C4 (paralelo 5 detectado) - debe fallar.
- Válido: C4/E3 -> D4/F3 -> E4/G3 (3r/6th pasos, no paralelas directas) - debe pasar.
- Válido: G4/E4 -> F4/D4 -> E4/C4 (cadencia V–I)

## 10. Checklist de implementación

1. Test de intervalos consonantes
2. Test de paralelas 5/8
3. Test de rango de salto
4. Test de cadencia final
5. Test de movimiento contrario/preferido

---

> Nota: este `.md` se focaliza exclusivamente en 1ª especie con precisión mecanizable para tu motor. Para especies 2–5 queda el documento previo con generalidades y transición.
