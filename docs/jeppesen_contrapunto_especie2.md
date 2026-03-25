# Contrapunto 2ª especie (Jeppesen) - Mapa de reglas para Frankenmusic

Este documento desarrolla un mapa de reglas precisas para contrapunto de 2ª especie (dos negras sobre una blanca de cantus) siguiendo a Jeppesen.

## 1. Objetivo
- Modelar generación/validación de 2ª especie en dos voces, acorde al método de Jeppesen.
- Asegurar consonancias en tiempos fuertes.
- Controlar disonancias en tiempos débiles con preparación y resolución.

## 2. Reglas básicas de consonancia
- En cada tiempo fuerte (las negras en pulso 1 y 3 en compás 4/4) la armonía contra el CF debe ser consonante plena:
  - P1, m3, M3, P5, m6, M6, P8.
- En tiempos débiles (2 y 4) la nota en contrapunto puede ser:
  - consonante, o
  - disonante permitida (normalmente 2ª o 7ª) si se sigue la regla de suspensión/paso.

## 3. Dissonancias permitidas en tiempos débiles
- La disonancia debe:
  - estar preparada en el tiempo fuerte anterior por consonancia;
  - resolverse por paso en el siguiente tiempo fuerte en consonancia.
- Ejemplo típico: C (fuerte consonante) -> D (débil disonante 2ª) -> E (fuerte consonante 3M).

## 4. Suspensión en 2ª especie (cómo modelarla)
- El contrapunto puede usar suspensiones 7-6, 4-3 sobre CF conectando tiempos fuertes y débiles:
  - t0 (fuerte): consonante
  - t1 (débil): disonancia (suspensión/paso)
  - t2 (fuerte): consonante
- No se permiten disonancias en dos tiempos fuertes seguidos.

## 5. Movimiento y paralelas
- Paralelas 5ª/8ª prohibidas entre todos los pares de tiempos fuertes, y cada tiempo fuerte con el siguiente tiempo fuerte.
- Preferir:
  - contrario > oblicuo > similar
- Similar solo con distancias pequeñas y evitando salto paralelo en 5/8.

## 6. Saltos por voz
- En la voz en 2ª especie, las transiciones deben obedecer:
  - pasos 2/3 recomendados;
  - 4/5 en salto único con compensación (contra movimiento); 
  - >6 de forma excepcional y probable rechazo si no hay paso contrario.

## 7. Reglas de inicio/fin (adaptadas a 2ª especie)
- Inicio: voz inferior (cantus) tiene tónica; contrapunto suele empezar en tónica, 3a o 5a con respecto al CF.
- Fin: como 1ª especie, cadencia V–I preferida.
- Requiere que la última negra fuerte sea consonante en ambas voces y que no quiebre la secuencia de tensiones.

## 8. Pseudocódigo BÁSICO
```python
CONSONANT = {'P1','m3','M3','P5','m6','M6','P8'}
ALLOWED_DISSONANCE = {'m2','M2','m7','M7'}  # solo en débil

def is_strong_beat(index):
    return index % 2 == 0  # 0-based: 0,2 son fuertes

for i in range(len(cantus)-1):
    curr_cp = contrapunto[i]
    curr_cf = cantus[i]
    interval_curr = interval(curr_cp,curr_cf)

    if is_strong_beat(i):
        if interval_curr not in CONSONANT:
            reject('fuerte no consonante')

    else:
        if interval_curr not in CONSONANT:
            if interval_curr not in ALLOWED_DISSONANCE:
                reject('dissonancia inválida en débil')
            prev_interval = interval(contrapunto[i-1],cantus[i-1])
            next_interval = interval(contrapunto[i+1],cantus[i+1])
            if prev_interval not in CONSONANT or next_interval not in CONSONANT:
                reject('disonancia sin preparación/resolución')
            if not is_step(contrapunto[i],contrapunto[i+1]):
                reject('disonancia no resuelta por paso')

# Reglas de paralelas + cadencia al final
check_no_parallel_5_8(contrapunto,cantus)
check_cadence(contrapunto,cantus)
```

## 9. Ejemplos de test
- Fallar: CF C D E F; CP E F G A (strong: E-G=3M, A vs F no es consonante fuerte? etc) revisar.
- Pasar: CF C D E F, CP E D F E.
- Suspensión: CF C (f) D (d) E (f), CP E (f) F (d sus 2) E (f)

## 10. Checklist de implementación
- [ ] verificación de intervalos fuertes
- [ ] disonancia débil con preparación y resolución
- [ ] no paralelas en 5/8 entre tiempos fuertes
- [ ] cadencia final correcta
- [ ] rango/salto por voz

---

> Referencias Jeppesen (2007/2ª edición y versión original) sobre 2ª especie: “las disonancias participan en articulación melódica y requieren el mismo principio de preparación y resolución que en 3ª especie”.
