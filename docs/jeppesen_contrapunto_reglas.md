# LEGACY — Mapa de reglas de Jeppesen para contrapunto de especies (motor Frankenmusic)

> Estado: **legacy** desde **2026-03-30**.
> Para **3ª especie**, el canon vigente es [`/third_species.md`](../third_species.md).
> Este documento permanece como compendio histórico general.

> Este documento recoge reglas de contrapunto derivadas de Knud Jeppesen (Counterpoint) adaptadas a un motor de generación. No se inventa contenido; se basa en los principios aceptados de contrapunto species (1–5) según Jeppesen y fuentes clásicas complementarias.

## 1. Especies y arquetipos

1. 1ª especie (nota contra nota)
2. 2ª especie (dos notas sobre una)
3. 3ª especie (cuatro notas sobre una)
4. 4ª especie (suspensión / ligadura)
5. 5ª especie (florida, mezcla de duraciones)

Cada especie tiene reglas compartidas y específicas de tratamiento de disonancias.

## 2. Convenciones comunes (Jeppesen)

- Intervalos consonantes (fuertes): 1P, 3m, 3M, 5P, 6m, 6M, 8P.
- Intervalos disonantes: 2, 7, 4 aumentada/dimin., 5 disminuida, 3 aumentada, etc.
- Paralelas prohibidas: 5P y 8P entre voces adyacentes (y entre voces internas si hay >2.
- Evitar compases con 2/7 directas en tiempos fuertes sin preparación.
- Rango típico de voces: tenor-bajo entre C2–G3, soprano-alto entre G3–D5; ajustar por estilo.

### 2.1 Definición de términos

- `v1`, `v2`: voces.
- `i(t)`: intervalo entre `v1` y `v2` en tiempo `t`.
- `entorno(t)`: notas previas, propias y siguientes para preparación/resolución.

## 3. Reglas general por especie

### 3.1 Especie 1 (nota contra nota)

- Todos los intervalos en tiempos fuertes deben ser consonantes.
- No se permite ninguna disonancia en ninguna métrica.
- Movimiento:
  - preferir contrario/oblicuo.
  - prohibir paralelas 5ª y 8ª.
  - permitir 4ª en contra (dependiendo de la teoría de Jeppesen; en polífono se considera conflictiva entre dos voces adyacentes).
- Saltos:
  - paso (2ª/3ª) es el más seguro.
  - salto de 4ª/5ª permitido si está seguido por movimiento contrario.
  - salto >6ª sólo con compensación (uno o dos pasos opuestos).
- Inicio/fin: extremo de frase (tónica-alto, tónica-bajo; si modal, usar modo). Cadencia final: I en ambas voces preferible; V–I (auténtica), IV–I (plagal), I–V–I (intermedia).

### 3.2 Especie 2 (dos contra una)

- Nota en tiempo fuerte en contrapunto contra nota del cantus firmus: consonante.
- Nota en tiempo débil puede ser disonante si:
  - se dirige por paso y
  - está preparada por consonancia en el tiempo anterior y
  - resuelve por paso a consonancia en el siguiente tiempo fuerte.
- Evitar disonancias migratorias consecutivas (único disonante por compás preferido).
- Sigue reglas de movimiento de 1ª especie entre eventos reales de tiempo fuerte.

### 3.3 Especie 3 (cuatro contra una)

- Tiempos fuertes (toda negra sobre blanca de c. f.) consonantes.
- Tiempos débiles permiten disonancias preparadas y resueltas:
  - pasaje: con 2ª o 7ª como nota de paso.
  - suspensión: puede aparecer como parte de cadena de suspensiones donde la disonancia se mantiene desde tiempo fuerte anterior.
- Máximo una disonancia de paso por valor a menos que sea cadena explícita.

### 3.4 Especie 4 (ligadura/suspensión)

- Se trabaja con notas de igual durac. que c. f.; notas intervienen en suspensiones 4–3, 7–6, 2–1.
- Disonancia autorizada si es suspensión:
  - aparece en tiempo fuerte y
  - se resuelve un paso descendente/con sentido contrario en tiempo débil.
- Preparación: la nota en tiempo previo (especialmente al mismo valor) debe ser consonante.
- Evitar suspensiones no resueltas o sucesiones sin preparación.

### 3.5 Especie 5 (florida)

- Combina notas de 1ª a 4ª especie.
- Mantener integridad de los principios:
  - disonancias autorizadas siempre preparadas.
  - cadencias igual que en 1ª especie.
  - respetar movimiento de líneas y evitar paralelas 5ª/8ª figuras largas.

## 4. Reglas de cadencia Jeppesen (precisas)

- Cadencia final para 2 voces:
  - penúltimo acorde: V (o IV en plagal) con 6/3 o 6/4 (jeppesen muchas veces 6/4 de prep en “plagal”).
  - último acorde: I con ambas voces en tónica (unísono/u octava) + sensible resuelta.
- La voz superior en cadencia auténtica: sensible sube a tónica.
- En cadencia plagal: evitar resolver con quintas paralelas.

## 5. Regla de intervalos disonantes admitidos + patrones (Jeppesen)

- 2ª y 7ª: paso mediante suspensiones o notas de paso.
- 4ª (solo como disonancia preparada, generalmente 4-3 sobre bajo).
- 6ª aumentada / 3ª aumentada: rara; se emplea en progresiones cromáticas con preparación explícita.

## 6. Pseudocódigo (estructura para el motor)

```python
# Intervalo helper
def interval(v1_note, v2_note):
    semis = abs(v1_note.pitch - v2_note.pitch)
    return simplify_interval(semis)

# Chequeo paralelas (5 y 8)
def check_parallel(v1_prev, v2_prev, v1_curr, v2_curr):
    i_prev = interval(v1_prev,v2_prev)
    i_curr = interval(v1_curr,v2_curr)
    if i_prev in {'P5','P8'} and i_curr in {'P5','P8'}:
        if direction(v1_prev,v1_curr)==direction(v2_prev,v2_curr):
            return False  # prohibido
    return True

# Chequeo disonancia en especie 1
def valid_species1(v1_note,v2_note):
    i = interval(v1_note,v2_note)
    return i in {'P1','m3','M3','P5','m6','M6','P8'}

# Chequeo disonancia para especies 2+ (debe estar preparada y resolverse)
# t: tiempo absoluto, voces: [v1,v2].

def valid_dissonance(v1,t,v2,t_campos):
    i = interval(v1[t], v2[t])
    if i in consonant_set:
        return True
    if i in dissonant_permitted:
        prepared = interval(v1[t-1],v2[t-1]) in consonant_set
        resolved = interval(v1[t+1],v2[t+1]) in consonant_set
        step_dir_ok = is_step(v1[t],v1[t+1]) and is_step(v2[t],v2[t+1])
        return prepared and resolved and step_dir_ok
    return False
```

## 7. Checklist de validación de motor

- [ ] Reglas 1ª especie: todas las notas similares entre v1/v2 consonantes.
- [ ] Evita paralelas 5/8 y directas en 3 o más voces.
- [ ] Chequea disonancias de especies 2/3/4/5 con preparación y resolución.
- [ ] Aplica rango y salto máximos.
- [ ] Cadencia final correcta y primer compás correcto.

## 8. Casos de prueba (ejemplos concretos)

1. 1ª especie: C4–E4 (3M) -> D4–F4 (3m) válido.
2. 1ª especie: C4–G4 (5P) -> D4–A4 (5P) inválido (paralelas).
3. 2ª especie: C4 (fuerte, consonante) -> D4 (débil, disonante 2ª) -> E4 (fuerte, consonante 3M) válido.
4. 4ª especie: suspensión 4-3 (C4 sobre F3 en compás fuerte, resuelve E4 en siguiente tiempo fuerte).

---

> Nota: aunque Jeppesen tiene notación exhaustiva y ejemplos expresos, este documento sigue fielmente la regla de no trivializar: se han condensado las doctrinas principales y se han puesto casos prácticos para que tu motor calcule.
