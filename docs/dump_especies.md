# Dump completo — Reglas de todas las especies (Jeppesen / Frankenmusic)

> Compilación de `especie1.md` a `especie5.md` y `jeppesen_contrapunto_reglas.md`. Fuente única para referencia del motor.

---

## Convenciones comunes (todas las especies)

- Intervalos **consonantes**: P1, m3, M3, P5, m6, M6, P8.
- Intervalos **disonantes**: m2, M2, m7, M7, A4/d5, A3, etc.
- **Paralelas prohibidas**: 5P y 8P en movimiento similar entre voces adyacentes.
- **Quintas/octavas directas** prohibidas (movimiento similar hacia P5/P8).
- Movimiento preferido: contrario > oblicuo > similar.
- Rango típico: tenor-bajo C2–G3, soprano-alto G3–D5.

### Términos

- `v1`, `v2`: voces.
- `i(t)`: intervalo entre `v1` y `v2` en tiempo `t`.
- `is_strong(t)`: tiempo fuerte según especie.
- `is_step(a, b)`: movimiento por grado conjunto (2ª).

---

## 1ª especie — Nota contra nota

### Objetivo
Generar y validar líneas de dos voces donde cada nota del contrapunto (CP) coincide con una nota del cantus firmus (CF). Todo evento armónico debe ser consonante.

### Intervalos permitidos

| Tipo | Intervalos |
|------|-----------|
| Consonancias perfectas | P1, P5, P8 |
| Consonancias imperfectas | m3, M3, m6, M6 |
| **Prohibidos** | m2, M2, m7, M7, d5, A4, A3, cualquier aumentado/disminuido |

> La 4ª justa es conflictiva en contrapunto a dos voces; se evita como consonancia directa (se usa solo en transición 4-3 en especies posteriores).

### Paralelas

- `i(t-1)` y `i(t)` **no pueden** ser ambos P5 o P8 si `dirección(v1) == dirección(v2)`.
- Evaluar entre todos los pares adyacentes en 3+ voces.

### Movimiento recomendado

- Prioridad: contrario > oblicuo > similar.
- Similar solo si no deriva en 5ª/8ª.

### Saltos permitidos

| Intervalo | Regla |
|-----------|-------|
| 2ª y 3ª | Naturales, sin restricción |
| 4ª y 5ª | Permitidos con paso contrario inmediato |
| 6ª | Permitido, preferir resolución por paso en dirección opuesta |
| > 6ª | Muy raro; exige uno o dos pasos contrarios después |

### Inicio y cierre

- **Inicio**: voz inferior en tónica; voz superior en tónica, 3ª o 5ª.
- **Cierre**: cadencia V→I (auténtica), IV→I (plagal). Ambas voces en tónica (unísono/octava). Sensible resuelve a tónica en voz superior.

### Pseudocódigo

```python
CONSONANT = {'P1','m3','M3','P5','m6','M6','P8'}

for pos in range(1, len(notes)):
    i_prev = interval(v1[pos-1], v2[pos-1])
    i_curr = interval(v1[pos],   v2[pos])

    if i_curr not in CONSONANT:
        reject('disonancia en especie 1')

    if i_prev in {'P5','P8'} and i_curr in {'P5','P8'}:
        if direction(v1[pos-1], v1[pos]) == direction(v2[pos-1], v2[pos]):
            reject('paralelas prohibidas')

    if abs(leap(v1[pos-1], v1[pos])) > 7 and not compensating_step(v1, pos):
        reject('salto excesivo sin compensar')

validate_start_end(v1, v2)
```

### Casos de prueba

| Caso | Resultado |
|------|-----------|
| C4/G3 → D4/A3 → E4/C4 (P5 paralela) | Falla |
| C4/E3 → D4/F3 → E4/G3 (3ª/6ª, sin paralelas) | Pasa |
| G4/E4 → F4/D4 → E4/C4 (cadencia V–I) | Pasa |

### Checklist

- [ ] Todos los intervalos consonantes
- [ ] Sin paralelas P5/P8
- [ ] Saltos compensados
- [ ] Cadencia final correcta
- [ ] Movimiento contrario preferido

---

## 2ª especie — Dos notas contra una

### Objetivo
Dos negras en CP por cada blanca en CF. Tiempos fuertes consonantes; tiempos débiles pueden ser disonantes con preparación y resolución.

### Estructura de pulsos (4/4 como referencia)
- **Fuertes**: índices pares (0, 2, 4…)
- **Débiles**: índices impares (1, 3, 5…)

### Reglas de intervalos

- **Tiempo fuerte**: consonancia estricta (P1, m3, M3, P5, m6, M6, P8).
- **Tiempo débil**: puede ser consonante O disonante si:
  1. El tiempo fuerte anterior es consonante (preparación).
  2. El tiempo fuerte siguiente es consonante (resolución).
  3. La resolución es por paso (`is_step`).
- Disonancias débiles permitidas: m2, M2, m7, M7.
- **No** se permiten disonancias en dos tiempos fuertes seguidos.

### Suspensión en 2ª especie

```
t0 (fuerte): consonante
t1 (débil):  disonancia (7-6, 4-3 como paso)
t2 (fuerte): consonante
```

### Movimiento y paralelas

- Paralelas P5/P8 prohibidas entre tiempos fuertes adyacentes.
- Prioridad: contrario > oblicuo > similar.

### Saltos

- Pasos 2ª/3ª recomendados.
- 4ª/5ª en salto único con compensación (movimiento contrario).
- > 6ª excepcional; probable rechazo si no hay paso contrario.

### Inicio/fin

- Inicio: CP en tónica, 3ª o 5ª respecto al CF.
- Fin: cadencia V→I; última negra fuerte consonante en ambas voces.

### Pseudocódigo

```python
CONSONANT        = {'P1','m3','M3','P5','m6','M6','P8'}
ALLOWED_DISS     = {'m2','M2','m7','M7'}

def is_strong(index):
    return index % 2 == 0

for i in range(len(contrapunto)):
    iv = interval(contrapunto[i], cantus[i])

    if is_strong(i):
        if iv not in CONSONANT:
            reject('tiempo fuerte no consonante')
    else:
        if iv not in CONSONANT:
            if iv not in ALLOWED_DISS:
                reject('disonancia inválida en débil')
            prev_iv = interval(contrapunto[i-1], cantus[i-1])
            next_iv = interval(contrapunto[i+1], cantus[i+1])
            if prev_iv not in CONSONANT or next_iv not in CONSONANT:
                reject('disonancia sin preparación/resolución')
            if not is_step(contrapunto[i], contrapunto[i+1]):
                reject('disonancia no resuelta por paso')

check_no_parallel_5_8(contrapunto, cantus)
check_cadence(contrapunto, cantus)
```

### Casos de prueba

| Caso | Resultado |
|------|-----------|
| CF C D E F; CP E D F E | Pasa |
| CF C(f) D(d) E(f); CP E(f) F(d sus 2) E(f) | Pasa (suspensión) |

### Checklist

- [ ] Tiempos fuertes consonantes
- [ ] Disonancia débil con preparación y resolución
- [ ] Sin paralelas P5/P8 entre tiempos fuertes
- [ ] Cadencia final correcta
- [ ] Rango y saltos por voz

---

## 3ª especie — Cuatro notas contra una

### Objetivo
Cuatro negras en CP por cada blanca en CF. Tiempos fuertes consonantes; tiempos débiles permiten disonancias de paso con preparación/resolución. Carácter de flujo melódico continuo.

### Estructura de pulsos por compás

```
t0 (fuerte)  t1 (débil)  t2 (fuerte)  t3 (débil)
```

- **Fuertes**: t0, t2 → consonancias estrictas.
- **Débiles**: t1, t3 → disonancias de paso permitidas.

### Reglas de intervalos

- **t0, t2**: P1, m3, M3, P5, m6, M6, P8.
- **t1, t3**: m2, M2, m7, M7 permitidas si:
  1. Preparadas por consonancia en el tiempo fuerte anterior.
  2. Resueltas por paso en el tiempo fuerte siguiente.
- No disonancias en dos tiempos fuertes consecutivos.
- Máximo una disonancia de paso por valor salvo cadena explícita.

### Paralelas

- Prohibidas entre fuertes adyacentes: (t0, t2), (t2, t0 del siguiente compás).
- También entre fuertes y débiles si generan efecto paralelo inmediato.

### Saltos

- Pasos cortos en negras preferibles.
- Saltos > 5ª deben compensarse con paso contrario directo.
- No más de un salto > 5ª por compás salvo excepción controlada.

### Cadencia

- t0 final = tónica (P8 o P1).
- Entrada: V→I, IV→I o I→V→I.
- Sensible resuelve a tónica en voz superior.

### Pseudocódigo

```python
CONSONANT     = {'P1','m3','M3','P5','m6','M6','P8'}
DISSONANT_W   = {'m2','M2','m7','M7'}

def is_strong(offset):
    return offset % 2 == 0

for t in range(len(cantus)):
    base = cantus[t]
    for offset in range(4):
        idx = t * 4 + offset
        cp  = contrapunto[idx]
        iv  = interval(cp, base)

        if is_strong(offset):
            if iv not in CONSONANT:
                reject('tiempo fuerte no consonante')
        else:
            if iv not in CONSONANT:
                if iv not in DISSONANT_W:
                    reject('disonancia débil no permitida')
                prev_iv = interval(contrapunto[idx-1], base)
                next_iv = interval(contrapunto[idx+1], base)
                if prev_iv not in CONSONANT or next_iv not in CONSONANT:
                    reject('disonancia sin preparación/resolución')
                if not is_step(cp, contrapunto[idx+1]):
                    reject('disonancia no resuelta por paso')

check_parallel_5_8(...)
check_cadence(...)
```

### Casos de prueba

| Caso | Resultado |
|------|-----------|
| CF C3; CP G4 F4 E4 D4 (f d f d) con preparación | Pasa |
| CF C; CP E D C B (f d f d) con prep/resolución | Pasa |
| CF con C-G en t0 + D-A en t2 misma dirección | Falla (P5 paralela) |

### Checklist

- [ ] Tiempos fuertes consonantes
- [ ] Disonancias débiles solo m2/M2/m7/M7 con prep y resolución
- [ ] Sin paralelas P5/P8 en eventos relevantes
- [ ] Cadencia final correcta
- [ ] Rango y saltos

---

## 4ª especie — Ligadura / Suspensión

### Objetivo
Notas del CP de igual duración que el CF, articuladas mediante ligaduras que crean suspensiones en tiempos fuertes. Las disonancias aparecen en tiempo fuerte y se resuelven en tiempo débil por paso.

### Estructura rítmica

```
t0 (fuerte): consonante — preparación
t1 (débil):  disonancia — suspensión
t2 (fuerte): consonante — resolución
```

La nota de t1 es la misma que la de t0 del compás anterior (ligada).

### Suspensiones admitidas

| Patrón | Descripción |
|--------|-------------|
| 4-3 | Cuarta suspendida → tercera |
| 7-6 | Séptima suspendida → sexta |
| 2-1 | Segunda suspendida → unísono |

### Reglas específicas

1. La nota disonante (suspensión) **debe estar preparada** por consonancia inmediata anterior.
2. La resolución es un **paso descendente** (idealmente).
3. El intervalo de resolución debe ser **consonante**.
4. Una suspensión no resuelta (disonancia persistente en tiempo fuerte siguiente) es error.
5. La 2ª y 7ª son admitidas en tiempos de caída si siguen el esquema preparación→resolución.
6. No cambiar por salto directo en la resolución salvo que la suspensión sea explícita.

### Paralelas

- P5/P8 prohibidas entre cualquier combinación de tiempos fuertes y resoluciones.
- Priorizar contrario/oblicuo al resolver suspensiones.

### Pseudocódigo

```python
CONSONANT = {'P1','m3','M3','P5','m6','M6','P8'}
DISSONANT = {'m2','M2','m7','M7','P4'}  # P4 disonante en 4ª especie

for idx in range(1, len(contrapunto)):
    prev = contrapunto[idx-1]
    curr = contrapunto[idx]
    iv_prev = interval(prev, cantus[idx-1])
    iv_curr = interval(curr, cantus[idx])

    if is_strong(idx):
        if iv_curr in DISSONANT:
            if iv_prev not in CONSONANT:
                reject('suspensión no preparada')
            if not is_valid_suspension_type(iv_prev, iv_curr):
                reject('tipo de suspensión no válido')
    else:
        # resolución de suspensión
        if iv_prev in DISSONANT and iv_curr in CONSONANT:
            if not is_step(prev, curr):
                reject('resolución de suspensión no por paso')

check_parallel_5_8(...)
check_cadence(...)
```

### Casos de prueba

| Caso | Resultado |
|------|-----------|
| C4→D4 (4-3 sobre G3) | Pasa |
| C4→E4 (7-6) | Pasa |
| Disonancia sin preparación | Falla |
| Disonancia no resuelta | Falla |

### Checklist

- [ ] Suspensiones preparadas (4-3, 7-6, 2-1)
- [ ] Resolución por paso a consonancia
- [ ] Sin disonancias no suspendidas en tiempo fuerte
- [ ] Sin paralelas P5/P8
- [ ] Cadencia final correcta

---

## 5ª especie — Florido (mezcla de especies)

### Objetivo
Combinar libremente notas de 1ª a 4ª especie en un solo flujo melódico. Es el "estilo completo" que sintetiza todas las otras especies.

### Principios centrales

- Inicio y final de frase consonantes con cadencia clásica.
- Cada segmento de un compás se valida según la especie que representa.
- Disonancias siempre preparadas y resueltas.
- Evitar disonancias largas o sin propósito (máx. 1-2 por compás, 2-4 por frase).

### Material rítmico

- Blancas → aplica reglas de 1ª especie.
- Dos negras por compás → aplica reglas de 2ª especie.
- Cuatro negras por compás → aplica reglas de 3ª especie.
- Notas ligadas → aplica reglas de 4ª especie (suspensión).
- Corcheas y silencios ligeros permitidos para ornamentación.

### Reglas de disonancia

- Solo en posición débil o de preparación.
- Preparada por consonancia en el pulso anterior.
- Resuelta por paso en el siguiente pulso fuerte apropiado.

### Cadencia y clausura

- Preparar el V con una sexta (submediant u otra) antes de la cadencia.
- Final: I con tónica en ambas voces y sensible resuelta.
- Evitar llegar al final con salto de P5/P8 paralelo en las dos últimas notas.
- "Media cadencia" a mitad de la frase; "cadencia plena" al final.

### Pseudocódigo

```python
for i, event in enumerate(cantus_events):
    pattern = detect_species_pattern(contrapunto_segment(i))

    if pattern == 1:
        validate_species1(contrapunto_segment(i), event)
    elif pattern == 2:
        validate_species2(contrapunto_segment(i), event)
    elif pattern == 3:
        validate_species3(contrapunto_segment(i), event)
    elif pattern == 4:
        validate_species4(contrapunto_segment(i), event)

    remember_resolved_dissonance(...)  # check global

validate_cadence(contrapunto)
check_parallel_5_8(contrapunto, cantus)
```

### Casos de prueba

| Caso | Resultado esperado |
|------|-------------------|
| (1ª especie) → (2ª especie) → (4ª especie) → cadencia | Pasa si cada segmento cumple su especie |
| Compás con patrón de 3ª especie con disonancia en fuerte | Falla |
| Suspensión 4-3 dentro del flujo de 5ª especie | Pasa si preparada y resuelta |

### Checklist

- [ ] Detección correcta del patrón de especie por segmento
- [ ] Integración de validadores 1-4 en un solo flujo
- [ ] Disonancias preparadas y resueltas en todos los segmentos
- [ ] Cadencia final correcta
- [ ] Sin paralelas P5/P8 en cualquier transición de especie

---

## Pseudocódigo general compartido

```python
# Intervalo entre dos notas
def interval(v1_note, v2_note):
    semis = abs(v1_note.pitch - v2_note.pitch)
    return simplify_interval(semis)

# Chequeo de paralelas (P5 y P8)
def check_parallel(v1_prev, v2_prev, v1_curr, v2_curr):
    i_prev = interval(v1_prev, v2_prev)
    i_curr = interval(v1_curr, v2_curr)
    if i_prev in {'P5','P8'} and i_curr in {'P5','P8'}:
        if direction(v1_prev, v1_curr) == direction(v2_prev, v2_curr):
            return False  # prohibido
    return True

# Disonancia preparada y resuelta (especies 2+)
def valid_dissonance(v1, t, v2):
    iv = interval(v1[t], v2[t])
    if iv in CONSONANT:
        return True
    if iv in DISSONANT_PERMITTED:
        prepared = interval(v1[t-1], v2[t-1]) in CONSONANT
        resolved = interval(v1[t+1], v2[t+1]) in CONSONANT
        step_ok  = is_step(v1[t], v1[t+1]) and is_step(v2[t], v2[t+1])
        return prepared and resolved and step_ok
    return False
```

---

## Tabla resumen por especie

| Especie | Ritmo CP/CF | Disonancia en fuerte | Disonancia en débil | Suspensión |
|---------|------------|---------------------|---------------------|-----------|
| 1ª | 1:1 | No | No | No |
| 2ª | 2:1 | No | Sí (preparada+resuelta) | No |
| 3ª | 4:1 | No | Sí (paso) | Parcial |
| 4ª | 1:1 (ligada) | Sí (suspensión) | No (es resolución) | Sí (4-3, 7-6, 2-1) |
| 5ª | Mixto | Solo si suspensión (4ª) | Sí (según especie) | Sí |

---

*Fuente: `especie1.md`, `especie2.md`, `especie3.md`, `especie4.md`, `especie5.md`, `jeppesen_contrapunto_reglas.md`*
