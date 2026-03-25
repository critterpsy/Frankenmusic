# Contrapunto 4ª especie (Jeppesen) - Mapa de reglas para Frankenmusic

Reglas de contrapunto de 4ª especie (suspensión) para motor de generación.

## 1. Objetivo
- Representar el uso de suspensiones (ligaduras) con disonancias en tiempos fuertes que se resuelven en tiempos débiles.
- Conservar consonancia estructural mientras se permiten disonancias articuladas.

## 2. Estructura rítmica
- CF: notas de blanca.
- CP: notas de blanca ligadas y aves con 4-3, 7-6, 2-1.
- En 4ª especie, cada nota de contrapunto se mantiene un tiempo y se suspende al entrar en tiempo fuerte.

## 3. Reglas de suspensiones
- Suspensión típica en 4ª especie:
  - t0: consonante (preparación)
  - t1: disonancia (suspensión)
  - t2: resolución por paso a consonancia
- Tipos comunes:
  - 4-3
  - 7-6
  - 2-1

## 4. Reglas específicas
- La nota disonante (en tiempo fuerte) debe estaré preparada por consonancia inmediata anterior.
- La resolución debe ser un paso descendente/converso opuesto idealmente.
- El intervalo de resolución debe ser consonante.
- Una suspensión no resuelta (disonancia persistente en tiempo fuerte siguiente) es un error.

## 5. Otras disonancias admitidas
- 2ª y 7ª en los tiempos de caída (suspensiones de prep) si siguen la preparación y resolución.
- Evitar cambios por salto directo en la resolución a menos que la suspensión sea explicita.

## 6. Movimiento y paralelas
- Paralelas 5ª/8ª prohibidas entre cualquier combinación de tiempos fuertes y resoluciones en dos voces.
- Priorizar contrario/oblicuo al resolver suspensiones.

## 7. Pseudocódigo
```python
CONSONANT = {'P1','m3','M3','P5','m6','M6','P8'}
SUSPENSIONS = {'4-3','7-6','2-1'}

for idx in range(1,len(contrapunto)):
    prev = contrapunto[idx-1]
    curr = contrapunto[idx]
    val_prev = interval(prev,cantus[idx-1])
    val_curr = interval(curr,cantus[idx])

    # Suspensión en 4ª especie asumimos ritmo 1 nota cada pulso:
    if is_strong(idx):
        if val_curr in DISSONANT:
            if val_prev not in CONSONANT:
                reject('suspensión no preparada')
            if not is_valid_suspension(val_prev,val_curr):
                reject('suspensión no taleado')
        else:
            # consonante en fuerte es posible tambien si no suspensión
            pass

    else:
        # resolver suspensiones
        if is_dissonant(val_prev) and val_curr in CONSONANT:
            if not is_step(prev,curr):
                reject('resolución de suspensión no por paso')

check_parallel_5_8(...)
check_cadence(...)
```

## 8. Casos de prueba
- C4->D4 (4-3 en altura con G3) debe pasar.
- C4->E4(7-6) debe pasar.
- Disonancia sin preparación o no resuelta debe fallar.

## 9. Checklist
- [ ] suspensiones preparadas de 4-3,7-6,2-1.
- [ ] resolución por paso a consonancia.
- [ ] no disonancias no suspendidas en tiempo fuerte.
- [ ] no paralelas 5/8.

---
> Jeppesen: 4ª especie es el primer estilo donde las disonancias actúan como articulación melódica, por eso eligió esquema de ligadura para mostrarlas como fenómenos regulares.
