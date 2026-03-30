#!/usr/bin/env python3
"""
Script para generar contrapuntos desde la consola.
Uso:
  python3 generate_counterpoint.py --species 1 --modo C --length 8 --num_voices 2
  python3 generate_counterpoint.py --species 2 --cf 0,2,4 --cp_disposition above
  python3 generate_counterpoint.py --species 2 --cf 0,2,4 --cp_disposition above --random_top_k 5
  python3 generate_counterpoint.py --species 3 --cf 0,2,4 --cp_disposition above
  python3 generate_counterpoint.py --species 2 --cf_name d_f_re_e_g_f_a_g_f_e_d
  python3 generate_counterpoint.py --species 2 --cf_index 1
"""

import argparse
import sys
import os
import random
import subprocess
import shutil
from datetime import datetime

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from treeSearch import TreeSearch
from Note import Notes, interval as note_interval
from src.species.canonical_cfs import (
    CANONICAL_CFS,
    canonical_cf_names,
    canonical_cf_sequence,
)
from src.species.config import CPDisposition, SearchMode, SpeciesEngineConfig
from src.species.engine import search_second_species, search_third_species

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("Advertencia: mido no está instalado. No se puede exportar a MIDI. Instala con: pip install mido")

SEPARATOR = "─" * 60
DISPLAY_SOLUTIONS = 3
SECOND_SPECIES_CF_CANDIDATES = 10
SECOND_SPECIES_CF_ATTEMPTS = 12
NOTE_TOKEN_TO_PITCH = {
    "C": 0,
    "DO": 0,
    "D": 2,
    "RE": 2,
    "R": 2,
    "E": 4,
    "MI": 4,
    "F": 5,
    "FA": 5,
    "G": 7,
    "SOL": 7,
    "SO": 7,
    "A": 9,
    "LA": 9,
    "B": 11,
    "SI": 11,
    "TI": 11,
}


def extract_sequence(entry):
    """Normaliza nodos/containers del árbol a una lista de enteros."""
    return entry.sequence if hasattr(entry, 'sequence') else entry

def note_name(note_num):
    """Convierte número de nota a nombre legible (e.g., 0 -> C0, 12 -> C1).

    Convención de alturas interna:
      - Los enteros internos empiezan en 0 = C (octava 0).
      - Fórmula: pitch_class = note_num % 12, octave = note_num // 12
      - Ejemplos: 0=C0, 2=D0, 4=E0, 9=A0, 12=C1, 21=A1
      - Exportación MIDI: se añaden +60 al entero interno, por lo que
        el entero 0 corresponde a MIDI 60 (Do central / C4 en notación estándar).
    """
    octave = note_num // 12
    note = Notes(note_num % 12).name
    return f"{note}{octave}"

def format_note_value(note_num):
    if note_num is None:
        return "R"
    return str(note_num)

def format_note_label(note_num):
    if note_num is None:
        return "Rest"
    return note_name(note_num)

def format_pitch_cell(note_num):
    if note_num is None:
        return "Rest (R)"
    return f"{note_name(note_num):>4} ({note_num:>3})"

def parse_cf_sequence(raw_value):
    """Parsea una secuencia de CF por enteros o nombres de nota separados por comas."""
    if not raw_value or not raw_value.strip():
        raise ValueError("La secuencia CF no puede estar vacía.")

    values = []
    for chunk in raw_value.split(','):
        token = chunk.strip()
        if not token:
            raise ValueError("La secuencia CF contiene valores vacíos.")
        try:
            values.append(int(token))
        except ValueError as exc:
            named = NOTE_TOKEN_TO_PITCH.get(token.upper())
            if named is None:
                raise ValueError(
                    f"Valor inválido en --cf: '{token}'. Usa enteros o notas "
                    "C,D,E,F,G,A,B (también DO,RE,MI,FA,SOL,LA,SI)."
                ) from exc
            values.append(named)

    if len(values) < 2:
        raise ValueError("La especie seleccionada requiere un CF de al menos 2 notas.")

    return values


def parse_canonical_cf(raw_name):
    try:
        return canonical_cf_sequence(raw_name)
    except KeyError as exc:
        available = ", ".join(canonical_cf_names())
        raise ValueError(
            f"CF canónico desconocido: '{raw_name}'. Disponibles: {available}"
        ) from exc


def parse_canonical_cf_index(index_value):
    names = canonical_cf_names()
    if not names:
        raise ValueError("No hay CFs canónicos registrados.")
    if index_value is None:
        raise ValueError("Índice canónico vacío.")
    if index_value < 1 or index_value > len(names):
        raise ValueError(
            f"Índice de CF canónico fuera de rango: {index_value}. "
            f"Rango válido: 1..{len(names)}."
        )
    selected_name = names[index_value - 1]
    return canonical_cf_sequence(selected_name)


def print_canonical_cfs():
    print(f"\n{SEPARATOR}")
    print("  CFs canónicos")
    print(SEPARATOR)
    for idx, name in enumerate(canonical_cf_names(), start=1):
        preset = CANONICAL_CFS[name]
        notes = ", ".join(preset.notes)
        ints = ", ".join(str(value) for value in preset.sequence)
        print(f"  [{idx}] {name}")
        if preset.description:
            print(f"      {preset.description}")
        print(f"      notas : {notes}")
        print(f"      enteros: {ints}")
    print(f"\n{SEPARATOR}")

def _append_timed_notes(track, timed_notes):
    pending_time = 0
    for note, duration in timed_notes:
        if note is None:
            pending_time += duration
            continue
        track.append(Message('note_on', note=note + 60, velocity=64, time=pending_time))
        track.append(Message('note_off', note=note + 60, velocity=64, time=duration))
        pending_time = 0

def export_to_midi(voices, filename):
    """Exporta las voces a un archivo MIDI"""
    if not MIDI_AVAILABLE:
        print("No se puede exportar: mido no disponible.")
        return None

    mid = MidiFile()

    for i, voice in enumerate(voices):
        if not voice.pool:
            continue
        track = MidiTrack()
        mid.tracks.append(track)

        track.append(MetaMessage('track_name', name=f'Voz {i}', time=0))

        # pool[0] is the best-scored result (pool is sorted by score_node after search)
        seq = voice.pool[0].sequence if hasattr(voice.pool[0], 'sequence') else voice.pool[0]

        for note in seq:
            track.append(Message('note_on', note=note + 60, velocity=64, time=0))
            track.append(Message('note_off', note=note + 60, velocity=64, time=480))

    mid.save(filename)
    return filename

def export_second_species_to_midi(cf_sequence, cp_line, filename):
    """Exporta una solución de segunda especie con dos tracks: CF y CP."""
    if not MIDI_AVAILABLE:
        print("No se puede exportar: mido no disponible.")
        return None

    ticks_per_beat = 480
    mid = MidiFile()

    cf_track = MidiTrack()
    cp_track = MidiTrack()
    mid.tracks.extend([cf_track, cp_track])

    cf_track.append(MetaMessage('track_name', name='Cantus Firmus', time=0))
    cp_track.append(MetaMessage('track_name', name='Contrapunto 2a especie', time=0))

    _append_timed_notes(
        cf_track,
        [(note, ticks_per_beat * 2) for note in cf_sequence],
    )

    timed_cp = []
    for i, measure in enumerate(cp_line.measures):
        is_final = i == len(cp_line.measures) - 1
        if is_final:
            timed_cp.append((measure.beat1, ticks_per_beat * 2))
        else:
            timed_cp.append((measure.beat1, ticks_per_beat))
            timed_cp.append((measure.beat2, ticks_per_beat))
    _append_timed_notes(cp_track, timed_cp)

    mid.save(filename)
    return filename

def export_third_species_to_midi(cf_sequence, cp_line, filename):
    """Exporta una solución de tercera especie con dos tracks: CF y CP."""
    if not MIDI_AVAILABLE:
        print("No se puede exportar: mido no disponible.")
        return None

    ticks_per_beat = 480
    cf_duration = ticks_per_beat * 2
    cp_quarter = cf_duration // 4

    mid = MidiFile()

    cf_track = MidiTrack()
    cp_track = MidiTrack()
    mid.tracks.extend([cf_track, cp_track])

    cf_track.append(MetaMessage('track_name', name='Cantus Firmus', time=0))
    cp_track.append(MetaMessage('track_name', name='Contrapunto 3a especie', time=0))

    _append_timed_notes(
        cf_track,
        [(note, cf_duration) for note in cf_sequence],
    )

    timed_cp = []
    for i, measure in enumerate(cp_line.measures):
        is_final = i == len(cp_line.measures) - 1
        if is_final:
            timed_cp.append((measure.beat1, cf_duration))
        else:
            timed_cp.append((measure.beat1, cp_quarter))
            timed_cp.append((measure.beat2, cp_quarter))
            timed_cp.append((measure.beat3, cp_quarter))
            timed_cp.append((measure.beat4, cp_quarter))
    _append_timed_notes(cp_track, timed_cp)

    mid.save(filename)
    return filename

def find_mscore():
    """Busca el ejecutable de MuseScore en el sistema."""
    for cmd in ['mscore4', 'mscore3', 'mscore', 'musescore4', 'musescore3', 'musescore']:
        if shutil.which(cmd):
            return cmd
    # macOS app bundle paths
    for path in [
        '/Applications/MuseScore 4.app/Contents/MacOS/mscore',
        '/Applications/MuseScore 3.app/Contents/MacOS/mscore',
    ]:
        if os.path.exists(path):
            return path
    return None

def open_in_musescore(midi_path):
    """Abre el archivo MIDI en MuseScore."""
    abs_path = os.path.abspath(midi_path)

    if sys.platform == "darwin" and os.path.exists("/Applications/MuseScore 4.app"):
        print(f"\n  Abriendo en MuseScore vía LaunchServices: \"{abs_path}\"")
        try:
            subprocess.Popen(["open", "-a", "MuseScore 4", abs_path])
            return
        except OSError as e:
            print(f"\n  [!] Falló apertura vía LaunchServices: {e}")

    mscore = find_mscore()
    if not mscore:
        print("\n  [!] MuseScore no encontrado. Instálalo desde https://musescore.org")
        return

    print(f"\n  Abriendo en MuseScore: {mscore} \"{abs_path}\"")
    try:
        subprocess.Popen([mscore, abs_path])
    except OSError as e:
        print(f"\n  [!] No se pudo lanzar MuseScore: {e}")

def print_header(args, length):
    print(f"\n{SEPARATOR}")
    print(f"  Frankenmusic — Generador de Contrapunto")
    print(SEPARATOR)
    print(f"  Especie    : {args.species}")
    print(f"  Modo       : {args.modo}")
    print(f"  Longitud   : {length}")
    print(f"  Voces      : {args.num_voices}")
    print(f"  Plagal     : {'Sí' if args.plagal else 'No'}")
    print(f"  Debug      : {'Sí' if args.debug else 'No'}")
    if args.species in {2, 3}:
        print(f"  Disposición: {args.cp_disposition}")
    print(SEPARATOR)

_INTERVAL_NAMES = {
    0: 'U', 1: 'm2', 2: 'M2', 3: 'm3', 4: 'M3',
    5: 'P4', 6: 'TT', 7: 'P5', 8: 'm6', 9: 'M6',
    10: 'm7', 11: 'M7',
}

def _interval_label(semitones):
    return _INTERVAL_NAMES.get(abs(semitones) % 12, '?')

def _melodic_intervals(seq):
    """Signed semitones + interval name between consecutive notes. First cell blank."""
    parts = [f"{'':>7}"]
    for k in range(1, len(seq)):
        diff = seq[k] - seq[k - 1]
        parts.append(f"{diff:>+3}/{_interval_label(diff):<3}")
    return "  ".join(parts)

def _harmonic_intervals(cf_seq, cp_seq):
    """Harmonic intervals (semitones + name) between CF and CP at each timestep."""
    return "  ".join(
        f"{note_interval(cf_seq[k], cp_seq[k]):>2}/{_interval_label(note_interval(cf_seq[k], cp_seq[k])):<3}"
        for k in range(len(cp_seq))
    )

def print_results(ts, modo_str, length):
    """Muestra los resultados ordenados por score (mejor primero).

    ts.voices[i].pool está ordenado por score_node() descendente tras la búsqueda,
    por lo que el primer resultado ([1]) es siempre el de mayor calidad.
    """
    voices = ts.voices
    cf_seq = (voices[0].pool[0].sequence
              if voices and voices[0].pool
              else None)

    print(f"\n{SEPARATOR}")
    print(f"  RESULTADO  |  Modo: {modo_str}  |  Longitud: {length}")
    print(SEPARATOR)

    for i, voice in enumerate(voices):
        label = "Cantus Firmus" if voice.is_cantus() else f"Contrapunto {i}"
        count = len(voice.pool)
        print(f"\n  Voz {i} — {label}  ({count} secuencia{'s' if count != 1 else ''} encontrada{'s' if count != 1 else ''})")

        if not voice.pool:
            print("    (ninguna secuencia válida)")
            continue

        for j, seq in enumerate(voice.pool[:3]):
            seq_list = seq.sequence if hasattr(seq, 'sequence') else seq
            note_names = [note_name(n) for n in seq_list]
            nums   = "  ".join(f"{n:>3}" for n in seq_list)
            names  = "  ".join(f"{n:>4}" for n in note_names)
            score  = ts.score_node(seq)
            marker = "►" if j == 0 else " "
            print(f"    {marker} [{j+1}]  score:{score:>3}  nums : {nums}")
            print(f"         notas: {names}")
            if j == 0:
                if voice.is_cantus():
                    print(f"         mvmt : {_melodic_intervals(seq_list)}")
                elif cf_seq is not None:
                    print(f"         ivls : {_harmonic_intervals(cf_seq, seq_list)}")

    print(f"\n{SEPARATOR}")

def print_second_species_results(
    cf_sequence,
    ranked,
    selected_cf_index=None,
    cf_candidate_count=1,
    selected_rank=1,
    selected_top_k=1,
    requested_top_k=1,
):
    print(f"\n{SEPARATOR}")
    print("  RESULTADO  |  Especie: 2")
    print(SEPARATOR)

    if selected_cf_index is not None and cf_candidate_count > 1:
        print(f"  CF candidato usado : {selected_cf_index}")

    print(f"  Candidatos explorados: {ranked.explored_candidates}")
    print(f"  Soluciones válidas   : {len(ranked.solutions)}")

    if not ranked.solutions:
        print("\n  (ninguna solución válida encontrada)")
        print(f"\n{SEPARATOR}")
        return

    if requested_top_k > 1:
        print(
            f"  Contrapunto elegido : puesto {selected_rank} al azar dentro "
            f"del top {selected_top_k}"
        )
        if requested_top_k > selected_top_k:
            print(f"  Top solicitado      : {requested_top_k} (disponibles: {selected_top_k})")

    display_limit = max(DISPLAY_SOLUTIONS, selected_rank)
    for i, solution in enumerate(ranked.solutions[:display_limit], start=1):
        measures = solution.cp.measures
        marker = "►" if i == selected_rank else " "
        print(f"\n  {marker} Solución {i}  score:{solution.score.total_score:>7.2f}")
        print("    Compás | CF           | CP beat1     | CP beat2")
        print("    -------+--------------+--------------+--------------")
        for measure_index, (cf_note, measure) in enumerate(zip(cf_sequence, measures), start=1):
            print(
                f"    {measure_index:>6} | "
                f"{format_pitch_cell(cf_note):<12} | "
                f"{format_pitch_cell(measure.beat1):<12} | "
                f"{format_pitch_cell(measure.beat2):<12}"
            )

    print(f"\n{SEPARATOR}")

def print_third_species_results(
    cf_sequence,
    ranked,
    selected_cf_index=None,
    cf_candidate_count=1,
    selected_rank=1,
    selected_top_k=1,
    requested_top_k=1,
):
    print(f"\n{SEPARATOR}")
    print("  RESULTADO  |  Especie: 3")
    print(SEPARATOR)

    if selected_cf_index is not None and cf_candidate_count > 1:
        print(f"  CF candidato usado : {selected_cf_index}")

    print(f"  Candidatos explorados: {ranked.explored_candidates}")
    print(f"  Soluciones válidas   : {len(ranked.solutions)}")

    if not ranked.solutions:
        print("\n  (ninguna solución válida encontrada)")
        print(f"\n{SEPARATOR}")
        return

    if requested_top_k > 1:
        print(
            f"  Contrapunto elegido : puesto {selected_rank} al azar dentro "
            f"del top {selected_top_k}"
        )
        if requested_top_k > selected_top_k:
            print(f"  Top solicitado      : {requested_top_k} (disponibles: {selected_top_k})")

    display_limit = max(DISPLAY_SOLUTIONS, selected_rank)
    for i, solution in enumerate(ranked.solutions[:display_limit], start=1):
        measures = solution.cp.measures
        marker = "►" if i == selected_rank else " "
        print(f"\n  {marker} Solución {i}  score:{solution.score.total_score:>7.2f}")
        print("    Compás | CF           | CP beat1     | CP beat2     | CP beat3     | CP beat4")
        print("    -------+--------------+--------------+--------------+--------------+--------------")
        for measure_index, (cf_note, measure) in enumerate(zip(cf_sequence, measures), start=1):
            print(
                f"    {measure_index:>6} | "
                f"{format_pitch_cell(cf_note):<12} | "
                f"{format_pitch_cell(measure.beat1):<12} | "
                f"{format_pitch_cell(measure.beat2):<12} | "
                f"{format_pitch_cell(measure.beat3):<12} | "
                f"{format_pitch_cell(measure.beat4):<12}"
            )

    print(f"\n{SEPARATOR}")

def build_second_species_config(args):
    mode = SearchMode.EXHAUSTIVE if args.exhaustive_species else SearchMode.EAGER
    random_top_k = getattr(args, "random_top_k", 1)
    return SpeciesEngineConfig(
        cp_disposition=CPDisposition(args.cp_disposition),
        search_mode=mode,
        max_solutions=max(args.max_solutions, random_top_k),
    )

def build_third_species_config(args):
    mode = SearchMode.EXHAUSTIVE if args.exhaustive_species else SearchMode.EAGER
    random_top_k = getattr(args, "random_top_k", 1)
    return SpeciesEngineConfig(
        cp_disposition=CPDisposition(args.cp_disposition),
        search_mode=mode,
        max_solutions=max(args.max_solutions, random_top_k),
    )


def choose_ranked_solution(ranked, top_k, seed=None):
    if top_k < 1:
        raise ValueError("--random_top_k debe ser >= 1.")
    if not ranked.solutions:
        return None, None, 0

    available_top_k = min(top_k, len(ranked.solutions))
    if available_top_k == 1:
        return ranked.solutions[0], 1, available_top_k

    rng = random.Random(seed) if seed is not None else random
    selected_index = rng.randrange(available_top_k)
    return ranked.solutions[selected_index], selected_index + 1, available_top_k

def collect_cf_candidates(args, modo):
    selectors_used = int(bool(args.cf)) + int(bool(args.cf_name)) + int(bool(args.cf_index))
    if selectors_used > 1:
        raise ValueError("Usa solo uno entre --cf, --cf_name y --cf_index.")

    if args.cf_name:
        return [parse_canonical_cf(args.cf_name)]

    if args.cf_index:
        return [parse_canonical_cf_index(args.cf_index)]

    if args.cf:
        return [parse_cf_sequence(args.cf)]

    print("\n  Buscando cantus firmi base compatibles...")

    unique_candidates = {}

    def _add_candidates(pool):
        for entry in pool:
            sequence = extract_sequence(entry)
            unique_candidates.setdefault(tuple(sequence), sequence)
            if len(unique_candidates) >= SECOND_SPECIES_CF_CANDIDATES:
                break

    def _run_cf_search(exhaustive):
        ts = TreeSearch(
            modo=modo,
            length=args.length,
            plagal=args.plagal,
            num_voices=1,
            debug=args.debug,
            sequential=args.sequential,
            exhaustive_search=exhaustive,
        )
        ts.generate_voices()
        if ts.voices and ts.voices[0].pool:
            return ts.voices[0].pool
        return []

    if args.exhaustive_search:
        _add_candidates(_run_cf_search(exhaustive=True))
    else:
        for _ in range(SECOND_SPECIES_CF_ATTEMPTS):
            pool = _run_cf_search(exhaustive=False)
            if pool:
                _add_candidates(pool[:1])
            if len(unique_candidates) >= SECOND_SPECIES_CF_CANDIDATES:
                break

        if not unique_candidates:
            _add_candidates(_run_cf_search(exhaustive=True))

    candidates = list(unique_candidates.values())
    if not candidates:
        if args.species == 3:
            raise RuntimeError("No se pudo generar un cantus firmus base para tercera especie.")
        raise RuntimeError("No se pudo generar un cantus firmus base para segunda especie.")

    return candidates

def search_second_species_from_cli(args, modo):
    config = build_second_species_config(args)
    cf_candidates = collect_cf_candidates(args, modo)

    def _evaluate(candidates):
        fallback = None
        for idx, cf_sequence in enumerate(candidates, start=1):
            ranked = search_second_species(cf_sequence, config)
            if fallback is None:
                fallback = (cf_sequence, ranked, idx, len(candidates))
            if ranked.solutions:
                return (cf_sequence, ranked, idx, len(candidates)), fallback
        return None, fallback

    selected, fallback = _evaluate(cf_candidates)

    if selected is None and not args.cf and not args.exhaustive_search:
        expanded_args = argparse.Namespace(**vars(args))
        expanded_args.exhaustive_search = True
        expanded_candidates = collect_cf_candidates(expanded_args, modo)
        seen = {tuple(cf) for cf in cf_candidates}
        for cf in expanded_candidates:
            if tuple(cf) not in seen:
                cf_candidates.append(cf)
        selected, fallback = _evaluate(cf_candidates)

    if selected is not None:
        cf_sequence, ranked, idx, candidate_count = selected
        return cf_sequence, ranked, idx, candidate_count

    assert fallback is not None
    cf_sequence, ranked, _, candidate_count = fallback
    return cf_sequence, ranked, None, candidate_count

def search_third_species_from_cli(args, modo):
    config = build_third_species_config(args)
    cf_candidates = collect_cf_candidates(args, modo)

    def _evaluate(candidates):
        fallback = None
        for idx, cf_sequence in enumerate(candidates, start=1):
            ranked = search_third_species(cf_sequence, config)
            if fallback is None:
                fallback = (cf_sequence, ranked, idx, len(candidates))
            if ranked.solutions:
                return (cf_sequence, ranked, idx, len(candidates)), fallback
        return None, fallback

    selected, fallback = _evaluate(cf_candidates)

    if selected is None and not args.cf and not args.exhaustive_search:
        expanded_args = argparse.Namespace(**vars(args))
        expanded_args.exhaustive_search = True
        expanded_candidates = collect_cf_candidates(expanded_args, modo)
        seen = {tuple(cf) for cf in cf_candidates}
        for cf in expanded_candidates:
            if tuple(cf) not in seen:
                cf_candidates.append(cf)
        selected, fallback = _evaluate(cf_candidates)

    if selected is not None:
        cf_sequence, ranked, idx, candidate_count = selected
        return cf_sequence, ranked, idx, candidate_count

    assert fallback is not None
    cf_sequence, ranked, _, candidate_count = fallback
    return cf_sequence, ranked, None, candidate_count

def build_midi_filename(args, length):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (
        f"output/midis/counterpoint_s{args.species}_{args.modo}_"
        f"{length}n_{args.num_voices}v_{timestamp}.mid"
    )

def run_first_species(args, modo):
    print_header(args, args.length)

    ts = TreeSearch(modo=modo, length=args.length, plagal=args.plagal,
                    num_voices=args.num_voices, debug=args.debug,
                    sequential=args.sequential, exhaustive_search=args.exhaustive_search)

    print("\n  Buscando secuencias...")
    ts.generate_voices()

    print_results(ts, args.modo, args.length)

    midi_path = None
    if args.export_midi or args.open_score:
        if not args.midi_filename:
            args.midi_filename = build_midi_filename(args, args.length)
        dirname = os.path.dirname(args.midi_filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        midi_path = export_to_midi(ts.voices, args.midi_filename)
        if midi_path:
            abs_path = os.path.abspath(midi_path)
            print(f"  MIDI guardado en : {abs_path}")
            print(f"\n  Para abrir manualmente:")
            mscore = find_mscore() or "mscore3"
            print(f"    {mscore} \"{abs_path}\"")

    if args.open_score:
        if midi_path:
            open_in_musescore(midi_path)
        else:
            print("\n  [!] No se generó MIDI, no se puede abrir el score.")

    if not (args.export_midi or args.open_score) and MIDI_AVAILABLE:
        print(f"  Tip: usa --export_midi para guardar el MIDI")
        print(f"       usa --export_midi --open_score para abrirlo directamente en MuseScore")

def run_second_species(args, modo):
    if args.num_voices != 2:
        raise ValueError("La integración CLI de segunda especie genera exactamente 2 voces (--num_voices 2).")

    cf_sequence, ranked, selected_cf_index, cf_candidate_count = search_second_species_from_cli(args, modo)
    selected_solution, selected_rank, selected_top_k = choose_ranked_solution(
        ranked,
        getattr(args, "random_top_k", 1),
        seed=getattr(args, "random_seed", None),
    )
    print_header(args, len(cf_sequence))
    print_second_species_results(
        cf_sequence,
        ranked,
        selected_cf_index=selected_cf_index,
        cf_candidate_count=cf_candidate_count,
        selected_rank=selected_rank or 1,
        selected_top_k=selected_top_k,
        requested_top_k=getattr(args, "random_top_k", 1),
    )

    midi_path = None
    if ranked.solutions and (args.export_midi or args.open_score):
        if not args.midi_filename:
            args.midi_filename = build_midi_filename(args, len(cf_sequence))
        dirname = os.path.dirname(args.midi_filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        midi_path = export_second_species_to_midi(
            cf_sequence,
            selected_solution.cp,
            args.midi_filename,
        )
        if midi_path:
            abs_path = os.path.abspath(midi_path)
            print(f"  MIDI guardado en : {abs_path}")
            print(f"\n  Para abrir manualmente:")
            mscore = find_mscore() or "mscore3"
            print(f"    {mscore} \"{abs_path}\"")

    if args.open_score:
        if midi_path:
            open_in_musescore(midi_path)
        else:
            print("\n  [!] No se generó MIDI, no se puede abrir el score.")

    if not ranked.solutions:
        print("  Sugerencia: prueba otro CF con --cf o usa --exhaustive_search para ampliar el CF base.")
    elif not (args.export_midi or args.open_score) and MIDI_AVAILABLE:
        print(f"  Tip: usa --export_midi para guardar el MIDI")
        print(f"       usa --export_midi --open_score para abrirlo directamente en MuseScore")

def run_third_species(args, modo):
    if args.num_voices != 2:
        raise ValueError("La integración CLI de tercera especie genera exactamente 2 voces (--num_voices 2).")

    cf_sequence, ranked, selected_cf_index, cf_candidate_count = search_third_species_from_cli(args, modo)
    selected_solution, selected_rank, selected_top_k = choose_ranked_solution(
        ranked,
        getattr(args, "random_top_k", 1),
        seed=getattr(args, "random_seed", None),
    )
    print_header(args, len(cf_sequence))
    print_third_species_results(
        cf_sequence,
        ranked,
        selected_cf_index=selected_cf_index,
        cf_candidate_count=cf_candidate_count,
        selected_rank=selected_rank or 1,
        selected_top_k=selected_top_k,
        requested_top_k=getattr(args, "random_top_k", 1),
    )

    midi_path = None
    if ranked.solutions and (args.export_midi or args.open_score):
        if not args.midi_filename:
            args.midi_filename = build_midi_filename(args, len(cf_sequence))
        dirname = os.path.dirname(args.midi_filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        midi_path = export_third_species_to_midi(
            cf_sequence,
            selected_solution.cp,
            args.midi_filename,
        )
        if midi_path:
            abs_path = os.path.abspath(midi_path)
            print(f"  MIDI guardado en : {abs_path}")
            print(f"\n  Para abrir manualmente:")
            mscore = find_mscore() or "mscore3"
            print(f"    {mscore} \"{abs_path}\"")

    if args.open_score:
        if midi_path:
            open_in_musescore(midi_path)
        else:
            print("\n  [!] No se generó MIDI, no se puede abrir el score.")

    if not ranked.solutions:
        print("  Sugerencia: prueba otro CF con --cf o usa --exhaustive_search para ampliar el CF base.")
    elif not (args.export_midi or args.open_score) and MIDI_AVAILABLE:
        print(f"  Tip: usa --export_midi para guardar el MIDI")
        print(f"       usa --export_midi --open_score para abrirlo directamente en MuseScore")

def main():
    parser = argparse.ArgumentParser(description='Generar contrapuntos con Frankenmusic')
    parser.add_argument('--species', type=int, default=1, choices=[1, 2, 3],
                        help='Especie de contrapunto: 1, 2 o 3 (default: 1)')
    parser.add_argument('--modo', type=str, default='C', choices=['C', 'D', 'E', 'F', 'G', 'A', 'B'],
                        help='Nota base del modo (default: C)')
    parser.add_argument('--length', type=int, default=4,
                        help='Longitud de la secuencia (default: 4)')
    parser.add_argument('--num_voices', type=int, default=2,
                        help='Número de voces (default: 2)')
    parser.add_argument('--plagal', action='store_true',
                        help='Modo plagal (default: False)')
    parser.add_argument('--debug', action='store_true',
                        help='Modo debug (default: False)')
    parser.add_argument('--sequential', action='store_true',
                        help='Búsqueda secuencial (default: False)')
    parser.add_argument('--exhaustive_search', action='store_true',
                        help='Continuar buscando más allá del primer resultado (default: False)')
    parser.add_argument('--export_midi', action='store_true',
                        help='Exportar a archivo MIDI (requiere mido)')
    parser.add_argument('--midi_filename', type=str, default='',
                        help='Nombre del archivo MIDI (default: auto-generado)')
    parser.add_argument('--open_score', action='store_true',
                        help='Abrir el MIDI en MuseScore tras exportar')
    parser.add_argument('--cp_disposition', type=str, default='above', choices=['above', 'below'],
                        help='Solo 2ª/3ª especie: contrapunto por encima o por debajo del CF')
    parser.add_argument('--cf', type=str, default='',
                        help='Solo 2ª/3ª especie: CF explícito por enteros o notas, e.g. 0,2,4,5 o D,F,E,D')
    parser.add_argument('--cf_name', type=str, default='',
                        help='Solo 2ª/3ª especie: nombre de CF canónico para reutilizar presets')
    parser.add_argument('--cf_index', type=int, default=0,
                        help='Solo 2ª/3ª especie: índice 1-based del CF canónico (ver --list_cfs)')
    parser.add_argument('--list_cfs', action='store_true',
                        help='Listar CFs canónicos disponibles y salir')
    parser.add_argument('--max_solutions', type=int, default=1,
                        help='Solo 2ª/3ª especie: máximo de soluciones a conservar y mostrar (default: 1)')
    parser.add_argument('--random_top_k', type=int, default=1,
                        help='Solo 2ª/3ª especie: elige al azar una solución dentro de las primeras k rankeadas (default: 1 = la mejor)')
    parser.add_argument('--random_seed', type=int, default=None,
                        help='Solo 2ª/3ª especie: semilla opcional para hacer reproducible la elección aleatoria')
    parser.add_argument('--exhaustive_species', action='store_true',
                        help='Solo 2ª/3ª especie: explorar todo el espacio de búsqueda (más lento)')

    args = parser.parse_args()

    if args.max_solutions < 1:
        parser.error("--max_solutions debe ser >= 1")
    if args.random_top_k < 1:
        parser.error("--random_top_k debe ser >= 1")

    if args.list_cfs:
        print_canonical_cfs()
        return

    modo_map = {
        'C': Notes.C, 'D': Notes.D, 'E': Notes.E, 'F': Notes.F,
        'G': Notes.G, 'A': Notes.A, 'B': Notes.B
    }
    modo = modo_map.get(args.modo.upper(), Notes.C)

    try:
        if args.species == 1:
            run_first_species(args, modo)
        elif args.species == 2:
            run_second_species(args, modo)
        else:
            run_third_species(args, modo)

        print()

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
