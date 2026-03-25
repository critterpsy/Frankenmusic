# Contrapunto 3ª especie (Jeppesen) - Mapa de reglas para Frankenmusic

Este documento describe reglas de Jeppesen para contrapunto de 3ª especie (cuatro negras sobre una blanca) para motor.

## 1. Objetivo
- Generación y validación de contrapunto 3ª especie con dos voces.
- Garantizar consonancias en fuertes y disonancias con preparación en débiles.
- Mantener articulación melódica y evitar anomalías.

## 2. Posiciones de pulso y duraciones
- C. F. (cantus firmus) en blancas.
- Contrapunto en negras: t0, t1, t2, t3 dentro de cada compás.
- Fuerza: t0 y t2 son fuertes; t1 y t3 débiles.

## 3. Reglas de intervalos
- Fuerte (t0,t2): consonantes estrictas: P1, m3, M3, P5, m6, M6, P8.
- Débil (t1,t3): disonancias permitidas con preparación/resolución:
  - notas de paso (2,7) o suspensiones enlazadas.
- No disonancias en dos tiempos fuertes consecutivos.

## 4. Reglas disonancias 3ª especie (Jeppesen)
- Dissonancia en tiempo débil debe ser:
  - paso por grado conjuncto (2ª o 7ª) o suspensión prolongada.
  - preparada por consonancia (tiempo previo t0 o t2).
  - resuelta por paso en t2 o t0 siguiente.
- `notas_de_paso` o `vecindad` se representan en t1 o t3.

## 5. Movimiento y paralelas
- Paralelas de 5ª/8ª prohibidas entre fuertes adyacentes: (t0,t2), (t2,t0 siguiente) y entre fuertes y débiles si generan effecto paralelo inmediato.
- Contrario > oblicuo > similar en fuertes.
- En débiles, el movimiento puede ser paso contiguo (conjunctus) libre.

## 6. Saltos de voz
- Pasos cortos en contrapunto negro preferibles.
- Saltos mayores a 5ª deben compensarse con paso contrario directo.
- No más de un salto mayor a 5ª por compás salvo excepciones muy controladas.

## 7. Reglas de cadencia
- En la última blanca:
  - t0 final debe ser la tónica (consonante perfecta 8va/u1).
  - Entrada a t0 final: V->I, IV->I o I->V->I (si se extiende).
- Resolver sensible en la voz superior hacia tónica.

## 8. Pseudocódigo
```python
CONSONANT = {'P1','m3','M3','P5','m6','M6','P8'}
DISSONANT_WEAK = {'m2','M2','m7','M7'}

def is_strong(i):
    return i % 2 == 0

for t in range(len(cantus)):
    base = cantus[t]
    for offset in range(4):
        idx = t*4 + offset
        cp = contrapunto[idx]
        i = interval(cp, base)

        if is_strong(offset):
            if i not in CONSONANT:
                reject('fuerte no consonante')
        else:
            if i not in CONSONANT:
                if i not in DISSONANT_WEAK:
                    reject('dissonancia debil no permitida')
                prev = interval(contrapunto[idx-1], base)
                next = interval(contrapunto[idx+1], base)
                if prev not in CONSONANT or next not in CONSONANT:
                    reject('disonancia sin preparación/resolución')
                if not is_step(cp, contrapunto[idx+1]):
                    reject('disonancia no resuelta por paso')

# parametros de direccion y paralelas
check_parallel_5_8(...)
check_cadence(...)
```

## 9. Casos de prueba
- CP: G4 F4 E4 D4 contra CF: C3 (t0,t1,t2,t3) correspond. Debe pasar si C3->G4 (P5), etc.
- Disonancia válida: CF C, CP E D C B sobre tiempos (f,d,f,d) con preparación/resolución.
- Paralelas: detecta C-G en t0 + D-A en t2, reject (5ª paralela con mismo direction).

## 10. Checklist
- [ ] Tiempos fuertes consonantes
- [ ] Dissonancias débiles solo 2/7 con preparación y resolución
- [ ] No paralelas 5/8 en eventos relevantes
- [ ] Cadencia final correcta
- [ ] Rango y saltos

---
> Basado en Jeppesen: 3ª especie mantiene el “carácter de flujo” de la melodía, usando disonancias móviles mediante notas de paso y suspensiones ligadas con naturalezas tonales.
