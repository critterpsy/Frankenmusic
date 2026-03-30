Contrapunto de 3ª especieFormalización jeppeseniana para implementación algorítmica
Documento técnico en español
Propósito: Este documento traduce la 3ª especie a 2 voces al lenguaje de reglas verificables por máquina, manteniendo el contenido musical de Jeppesen y separando con claridad lo que es regla doctrinal de lo que aquí se fija sólo como convención de formalización.

Campo
Contenido
Alcance
Contrapunto estricto a 2 voces, 3ª especie pura 4:1, una voz contra cantus firmus en redondas.
Base doctrinal
Knud Jeppesen, Counterpoint: The Polyphonic Vocal Style of the Sixteenth Century; apoyado por resúmenes pedagógicos explícitamente basados en Jeppesen.
Uso previsto
Diseño de validador, motor de búsqueda, tests y documentación de reglas.
Criterio editorial
Las ambigüedades pedagógicas se resuelven aquí con lectura conservadora y formalización explícita.


1. Alcance exacto
Se modela un cantus firmus (CF) en redondas y una voz contrapuntística (CP) en negras: cuatro ataques del CP por cada compás del CF.
El último compás concluye con una redonda final en el CP. El penúltimo compás contiene la preparación cadencial normal de 3ª especie.
Se asume un entorno modal/diatónico al estilo del contrapunto estricto renacentista. Las alteraciones cromáticas no forman parte del núcleo de este documento salvo la sensible cadencial cuando el modo y la clausula lo exigen.
No se incluyen síncopas de 4ª especie, mezcla de especies, floreo libre, imitación ni libertades tardías. Cuando Jeppesen menciona una excepción que depende de valores rítmicos distintos de la 3ª especie pura, se documenta como nota histórica pero no se incorpora al validador puro 4:1.
Lectura doctrinal: En 3ª especie el pulso interno del compás queda jerarquizado como fuerte - débil - relativamente fuerte - débil. La disonancia queda desterrada del tiempo 1 y restringida a figuras controladas en los tiempos débiles; Jeppesen acentúa especialmente la linealidad, la cantabilidad y el predominio del movimiento conjunto.

2. Convenciones formales
Indexación temporal: cada compás m tiene cuatro subdivisiones q = 1,2,3,4. La nota CP[m,q] suena contra CF[m].
Tiempo fuerte principal: q=1. Tiempo relativamente fuerte: q=3. Tiempos débiles: q=2 y q=4.
Consonancias armónicas admitidas en el estilo estricto: 3ª, 5ª, 6ª, 8ª, 10ª, 12ª y sus equivalentes compuestos. La 4ª cuenta como disonancia cuando se mide desde la voz inferior real.
Unísono: restringido. No se admite en q=1 dentro del curso ordinario; puede aparecer en tiempos débiles por necesidad contrapuntística, con mucha moderación.
Salto melódico: intervalo melódico de 3ª o mayor. Paso: 2ª diatónica.
Compensación: tras un salto amplio, la línea debe reaccionar en dirección contraria por grado conjunto.
3. Reglas estructurales del comienzo y del final
3.1 Apertura
CP arriba del CF: la primera altura estructural debe formar 5ª u 8ª con el CF.
CP abajo del CF: la primera altura estructural debe formar 8ª o unísono con el CF; en la práctica de especie pura se privilegia la 8ª.
Jeppesen admite que la 3ª especie puede arrancar con cuatro negras o con silencio de negra seguido de tres negras. Si se usa anacrusa interna, la primera altura real debe respetar igualmente la regla intervalar de apertura.
En un validador puro 4:1 es razonable aceptar dos perfiles de arranque: (a) compás completo de cuatro negras; (b) silencio en q=1 y notas en q=2-4. Todo otro arranque queda fuera del alcance.
3.2 Cadencia
La nota final del CP es siempre la final modal, escrita como redonda.
La penúltima nota real del CP es la última negra del penúltimo compás.
Cadencia superior típica: el CP realiza 7-8 sobre el 2-1 del CF.
Cadencia inferior típica: el CP realiza 2-1 bajo el 7-1 del CF.
La aproximación final debe producir clausula vera: convergencia por movimiento contrario hacia octava o unísono perfectos.
Caso
Penúltima del CF
Penúltima del CP
Final vertical
CP arriba
2
7
8ª
CP abajo
7
2
8ª o 1ª

4. Jerarquía métrica y régimen vertical
Posición
Fuerza métrica
Estado vertical permitido
q=1
fuerte
sólo consonancia; no unísono salvo inicio/final
q=2
débil
consonancia o disonancia controlada
q=3
relativamente fuerte
lectura conservadora jeppeseniana: consonancia estructural
q=4
débil
consonancia o disonancia controlada

Decisión de formalización: Para implementación estricta estilo Jeppesen conviene exigir consonancia en q=1 y q=3. Algunos resúmenes modernos permiten casos especiales más flexibles en q=3, pero la lectura conservadora usada aquí trata q=3 como apoyo estructural consonante. Esto mantiene la solución alineada con el uso pedagógico más severo.

5. Reglas de disonancia
Toda disonancia debe quedar en tiempo débil: q=2 o q=4.
En 3ª especie jeppeseniana pura sólo se admiten tres clases de disonancia: nota de paso, cambiata y vecina inferior. Otras categorías modernas (appoggiatura, escapada, vecina superior libre, bordadura libre, etc.) quedan excluidas.
La vecina superior aparece en un comentario excepcional de Jeppesen cuando el contexto rítmico ya no es el de 3ª especie pura; por eso aquí no se habilita en el validador 4:1.
5.1 Nota de paso disonante
Patrón local: consonancia - disonancia - consonancia.
Entrada y salida por paso en la misma dirección.
La disonancia rellena el espacio de una 3ª melódica.
Puede encadenarse un par de disonancias de paso sucesivas si ambas permanecen fuera del tiempo fuerte y la línea sigue íntegramente por grado conjunto en una sola dirección.
5.2 Vecina inferior disonante
Patrón local: X - X-1 - X, todo por paso.
La nota disonante baja por paso desde una consonancia y regresa por paso a la misma consonancia.
La forma típica es inferior, no superior. Repetir la misma vecina dos veces seguidas empobrece la línea y debe rechazarse o penalizarse severamente según el nivel de rigidez buscado.
5.3 Cambiata
La cambiata es la única figura regular en la que una disonancia puede ir seguida de salto.
Núcleo local de cuatro notas dentro del compás: descenso por paso hacia la disonancia en tiempo débil, salto descendente de 3ª hacia consonancia, y corrección posterior por paso ascendente.
La segunda nota del patrón es la disonancia; la tercera y la cuarta deben ser consonantes.
La figura completa debe sentirse como una sola inflexión lineal controlada, no como salto libre desde una nota extraña.
Patrones abstractos válidos de disonanciaPASSING(q):  harmonic(q) = DISSONANT  q in {2,4}  melodic(cp[q-1], cp[q]) = step  melodic(cp[q], cp[q+1]) = step  direction(cp[q-1]->cp[q]) = direction(cp[q]->cp[q+1])  harmonic(q-1) = CONSONANT  harmonic(q+1) = CONSONANTLOWER_NEIGHBOR(q):  harmonic(q) = DISSONANT  q in {2,4}  cp[q] = cp[q-1] - step  cp[q+1] = cp[q-1]  harmonic(q-1) = CONSONANT  harmonic(q+1) = CONSONANTCAMBIATA(m, q=2):  harmonic(m,2) = DISSONANT  cp[m,1] -> cp[m,2] = step down  cp[m,2] -> cp[m,3] = third down  cp[m,3] -> cp[m,4] = step up  harmonic(m,1) = CONSONANT  harmonic(m,3) = CONSONANT  harmonic(m,4) = CONSONANT

6. Reglas melódicas del CP
La línea debe ser primordialmente conjunta. En la práctica jeppeseniana de 3ª especie la proporción de pasos frente a saltos es mucho mayor que en 1ª y 2ª especie.
Los saltos deben ser pocos, pequeños y preferentemente internos al compás.
Todo salto ha de ocurrir entre dos verticalidades consonantes, salvo la excepción de la cambiata.
Los saltos tienden a quedar contenidos o compensados a ambos lados; la línea rápida no debe sentirse acrobática.
No se permiten sucesiones que esbocen acordes por arpegio, secuencias obvias, balanceos repetitivos tipo “trino lento” ni reiteración excesiva del mismo motivo.
6.1 Dirección permitida de los saltos
Situación
Regla
Salto desde tiempo acentuado (q=1 o q=3)
sólo descendente
Salto desde tiempo débil
normalmente ascendente
Excepción desde tiempo débil
puede bajar sólo por 3ª si el contexto es cambiata o si el salto queda corregido de inmediato por paso ascendente
Dos apoyos acentuados consecutivos con salto
muy desfavorable; evitar

6.2 Compensación y contención
Después de un salto amplio, la nota siguiente debe cambiar de dirección y moverse por paso.
Los saltos no deben encadenarse libremente en la misma dirección.
Un patrón 3ª seguida por 2ª en la misma dirección sólo es aceptable en formas muy concretas donde el salto queda encuadrado por cambio de dirección en uno de los lados.
6.3 Perfil global
Debe existir un clímax principal único, preferentemente no coincidente con el clímax del CF.
Jeppesen valora especialmente las líneas cuyo punto más alto llega hacia el final por una cadena suave y natural de pequeñas ascensiones y descensos.
Se evitan cambios bruscos de registro, meandros sin dirección y reutilización mecánica del mismo contorno.
7. Reglas contrapuntísticas entre compases
Los apoyos de q=1 a q=1 entre compases consecutivos obedecen las reglas generales del contrapunto estricto: evitar paralelos perfectos y evitar que la llegada a perfecta por movimiento similar destruya la independencia de voces.
No deben aparecer tres compases seguidos con la misma consonancia perfecta en el arranque; dos pueden tolerarse, tres no.
No deben aparecer más de tres compases seguidos con la misma consonancia imperfecta en el arranque.
Si el nuevo q=1 forma 5ª, ni q=3 ni q=4 del compás anterior deben formar 5ª con el CF. Si el nuevo q=1 forma 8ª, tampoco q=2, q=3 ni q=4 del compás anterior deben formar 8ª.
La transición q=4 -> siguiente q=1 debe respetar las restricciones de entrada a apoyo fuerte; añadir notas intermedias no “disimula” una falsa relación de quintas u octavas.
8. Catálogo operacional de patrones válidos por compás
Esquema del compás
Descripción
Estado
C C C C
las cuatro notas consonantes
válido
C D C C
paso o vecina inferior en q=2
válido
C C C D
disonancia final sólo si resuelve por paso al q=1 siguiente
válido
C D C D
dos débiles disonantes separados por consonancias
válido si cada una clasifica
C D C C con salto 2->3
cambiata
válido sólo en la forma prescrita
C C D C
q=3 disonante
rechazado en lectura estricta
C D D C
dos disonancias internas sin figura compuesta válida
rechazado
D ...
disonancia en q=1
rechazado

9. Pseudocódigo matemático del validador
function validate_third_species(cf, cp, placement):    assert len(cp) = 4*(len(cf)-1) + 1_final_whole    check_mode_and_range(cf, cp)    check_opening(cf, cp, placement)    check_final_cadence(cf, cp, placement)    for each measure m in 1 .. N-1:        for q in {1,2,3,4}:            iv = harmonic_interval(cf[m], cp[m,q], placement)            if q in {1,3}:                require consonant(iv)                if q == 1 and m not in {1,N}: require iv != unison            else:                if dissonant(iv):                    require classify_dissonance(cf, cp, m, q) in {PASSING, LOWER_NEIGHBOR, CAMBIATA}        check_measure_internal_melody(cf, cp, m)        check_crossbar_motion(cf, cp, m)    check_global_melodic_shape(cp)    return VALID

function check_measure_internal_melody(cf, cp, m):    notes = [cp[m,1], cp[m,2], cp[m,3], cp[m,4]]    for each adjacent pair a->b in notes plus crossbar pair cp[m,4]->cp[m+1,1]:        if is_leap(a,b):            require harmonic_at(a) consonant and harmonic_at(b) consonant            require leap_size(a,b) <= allowed_melodic_limit            if beat_of(a) in {1,3}: require direction(a,b) = DOWN            if beat_of(a) in {2,4}: require direction(a,b) = UP or cambiata_exception(a,b)    for each leap a->b:        if is_large_leap(a,b):            require next_motion(b) = step opposite_direction    reject repeated_motive_excess(cp)    reject upper_neighbor_in_pure_third_species(cp)    reject same_neighbor_twice_in_a_row(cp)    reject accented_arpeggiation(cp)

function classify_dissonance(cf, cp, m, q):    if q not in {2,4}: return NONE    if step(cp[m,q-1], cp[m,q]) and step(cp[m,q], next_note(m,q)):        if same_direction(cp[m,q-1], cp[m,q], next_note(m,q)):            if harmonic_consonant(prev) and harmonic_consonant(next):                return PASSING        if cp[m,q+1] == cp[m,q-1] and cp[m,q] is lower_neighbor_of cp[m,q-1]:            return LOWER_NEIGHBOR    if q == 2:        if step_down(cp[m,1], cp[m,2]) and third_down(cp[m,2], cp[m,3]) and step_up(cp[m,3], cp[m,4]):            if harmonic(m,1), harmonic(m,3), harmonic(m,4) are consonant:                return CAMBIATA    return NONE

10. Lista de rechazo duro
Disonancia en q=1.
q=3 disonante bajo la lectura estricta aquí adoptada.
Disonancia en q=2 o q=4 que no clasifica exactamente como paso, vecina inferior o cambiata.
Vecina superior en 3ª especie pura 4:1.
Salto desde verticalidad disonante, salvo el salto característico de la cambiata.
Salto ascendente desde apoyo acentuado o salto descendente desde tiempo débil fuera de la excepción prescrita.
Entrada a perfecta estructural que produzca paralelo/directo prohibido con el apoyo estructural anterior.
Más de dos apoyos perfectos idénticos seguidos al inicio de compases o exceso de misma imperfecta en serie.
Arpegiación evidente del acorde, secuencia mecánica, repetición insistente del mismo dibujo o línea sin clímax reconocible.
11. Lista de preferencias de estilo (no siempre rechazo absoluto)
Preferir consonancias imperfectas en q=1 y q=3.
Preferir saltos dentro del compás y no a través de la barra.
Favorecer fragmentos escalares amplios y mezclados con pocas figuras idiomáticas bien espaciadas.
Hacer que el punto culminante del CP no coincida con el del CF.
Evitar que la misma figura de cambiata aparezca repetida a corta distancia.
Implementación práctica: Estas preferencias son buenas candidatas para el motor de ranking de un searcher: no tienen por qué podar todas las soluciones, pero sí ordenar las más “jeppesenianas” por encima de las meramente válidas.

12. Resumen ejecutivo para código
Tema
Regla ejecutable
Ritmo
4 notas del CP por compás, salvo la nota final larga
Apertura
CP arriba: P5/P8; CP abajo: P8/P1
Apoyos estructurales
q=1 y q=3 consonantes
Disonancias
sólo en q=2/q=4
Tipos de disonancia
paso, vecina inferior, cambiata
Vecina superior
no en 3ª especie pura
Saltos
pocos, entre consonancias, preferentemente pequeños
Dirección del salto
desde acento baja; desde débil sube; excepción de 3ª descendente controlada
Cadencia
penúltima negra del CP realiza 7-8 o 2-1 según colocación
Control global
clímax único, predominio conjunto, sin secuencias ni arpegios

13. Fuentes doctrinales usadas
Knud Jeppesen, Counterpoint: The Polyphonic Vocal Style of the Sixteenth Century. Referencia principal para el contenido musical.
Clark Ross, “Rules by Species” y “Third Species: Skips, Dissonances, and Stylistic Summary”, resúmenes pedagógicos explícitamente basados en Jeppesen.
Open Music Theory, “Third-Species Counterpoint”, usado sólo como apoyo comparativo moderno para la explicitación de categorías y terminología.
Cierre editorial: El documento busca maximizar fidelidad estilística y utilidad de implementación. Donde Jeppesen enseña con ejemplos y formulaciones verbales, aquí se fijan predicados y desempates concretos para que el comportamiento del motor sea estable, auditable y cercano al ideal jeppeseniano.

