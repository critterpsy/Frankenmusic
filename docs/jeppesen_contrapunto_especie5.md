# Contrapunto 5ª especie (Jeppesen) - Mapa de reglas para Frankenmusic

Reglas para contrapunto florido (5ª especie) en motor Frankenmusic.

## 1. Objetivo
- Combinar 1ª a 4ª especie en un solo flujo melódico.
- Mantener control sobre consonancia/disonancia y finalizar con cadencia clásica.

## 2. Principios centrales
- Base: todo inicio y final de frase deben ser consonantes y respetar cadencias.
- Fluir hacia y desde disonancias preparadas/resueltas dentro de la estructura.
- Evitar disonancias largas o sin propósito.

## 3. Material rítmico
- Alternar ritmos: negras, corcheas, blancas, ligaduras y silencios ligeros.
- Cada segmento de 1 medida puede seguir reglas de especie 1-4 según el contenido.

## 4. Reglas específicas (Jeppesen)
- 5ª especie acepta note over note y nota prolongada.
- Se pueden incluir:
  - 1ª especie para notas largas
  - 2ª especie para literalmente dos notas por compás
  - 3ª especie para grupos de cuatro notas
  - 4ª especie para suspensiones efectivas
- Disonancias en 5ª especie deben siempre: 
  - aparecer en posición débil o tiempo de preparación,
  - estar preparadas por consonancia en el pulso anterior,
  - resolverse por paso en un pulso fuerte apropiado.

## 5. Cadencia y clausura
- Antes de la cadencia, preparar el V con una sexta (submediant etc.)
- Al final, establecer I con tónica en ambas voces y sensible resuelta.
- Evitar llegar a la final usando salto de 5ª/8ª paralelo en las dos últimas notas.

## 6. Pseudocódigo semiestructurado
```python
for i, event in enumerate(cantus_events):
    pattern = detect_species_pattern(contrapunto_segment(i))
    if pattern == 1:
        validate_species1(...)
    elif pattern == 2:
        validate_species2(...)
    elif pattern == 3:
        validate_species3(...)
    elif pattern == 4:
        validate_species4(...)

    remember_resolved_dissonance(...) # para check global

validate_cadence(contrapunto)
check_parallel_5_8(...)
```

## 7. Valores de guía
- 2-4 disonancias por frase (si es un bit largo), no más de 1-2 en compás.
- Aplicar “media cadencia” en la mitad y “cadencia plena” al final.

## 8. Casos de prueba
- Caso mixto: (1ª especie breve) -> (2ª especie) -> (4ª especie) -> cadencia.
- Asegurar que en una medida con 3ª especie no aparezcan disonancias en tiempos fuertes.
- Validar suspensión 4-3 en 4ª especie dentro del flujo de 5ª especie.

## 9. Checklist
- [ ] integración de especies (1-4) en una sola línea
- [ ] disonancias preparadas / resueltas
- [ ] cadencia final correcta
- [ ] evitar paralelas 5/8 en cualquier transición de especie

---
> Nota: Jeppesen considera la 5ª especie como el “estilo completo” que sintetiza todas las otras especies en una frase musical. En el motor, esto implica un controlador de contexto y un validador hibrido.
