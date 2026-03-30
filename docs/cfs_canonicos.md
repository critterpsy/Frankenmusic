# CFs canónicos

Catálogo de cantus firmi canónicos reutilizables desde la CLI.

## Convenciones

- Formato interno del motor: enteros cromáticos (`C=0`, `D=2`, `E=4`, `F=5`, `G=7`, `A=9`, `B=11`).
- Alias textual en CLI: `R` se acepta como `RE` (`D`).

## Presets

### `d_f_re_e_g_f_a_g_f_e_d`

- Notas: `D, F, RE, E, G, F, A, G, F, E, D`
- Enteros: `2, 5, 2, 4, 7, 5, 9, 7, 5, 4, 2`
- Descripción: melodía solicitada para usar en especies desde CLI.

## Uso desde CLI

Listar CFs canónicos:

```bash
python3 generate_counterpoint.py --list_cfs
```

Usar preset por índice canónico:

```bash
python3 generate_counterpoint.py --species 2 --cf_index 1 --cp_disposition above
```

Usar preset en 2ª especie:

```bash
python3 generate_counterpoint.py --species 2 --cf_name d_f_re_e_g_f_a_g_f_e_d --cp_disposition above
```

Usar preset en 3ª especie:

```bash
python3 generate_counterpoint.py --species 3 --cf_name d_f_re_e_g_f_a_g_f_e_d --cp_disposition above
```
