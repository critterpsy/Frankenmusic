#!/usr/bin/env python3
"""
Script para generar contrapuntos desde la consola.
Uso:
  python3 generate_counterpoint.py --species 1 --modo C --length 8 --num_voices 2
  python3 generate_counterpoint.py --species 2 --cf 0,2,4 --cp_disposition above
"""

import argparse
import sys
import os
import subprocess
import shutil
from datetime import datetime

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from treeSearch import TreeSearch
from Note import Notes, interval as note_interval
from src.species.config import CPDisposition, SearchMode, SpeciesEngineConfig
from src.species.engine import search_second_species

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
    """Parsea una secuencia de CF en enteros separados por comas."""
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
            raise ValueError(
                f"Valor inválido en --cf: '{token}'. Usa enteros separados por comas."
            ) from exc

    if len(values) < 2:
        raise ValueError("Segunda especie requiere un CF de al menos 2 notas.")

    return values

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
    if args.species == 2:
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

def print_second_species_results(cf_sequence, ranked, selected_cf_index=None, cf_candidate_count=1):
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

    for i, solution in enumerate(ranked.solutions[:DISPLAY_SOLUTIONS], start=1):
        measures = solution.cp.measures
        print(f"\n  ► Solución {i}  score:{solution.score.total_score:>7.2f}")
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

def build_second_species_config(args):
    mode = SearchMode.EXHAUSTIVE if args.exhaustive_species else SearchMode.EAGER
    return SpeciesEngineConfig(
        cp_disposition=CPDisposition(args.cp_disposition),
        search_mode=mode,
        max_solutions=args.max_solutions,
    )

def collect_cf_candidates(args, modo):
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
    print_header(args, len(cf_sequence))
    print_second_species_results(
        cf_sequence,
        ranked,
        selected_cf_index=selected_cf_index,
        cf_candidate_count=cf_candidate_count,
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
            ranked.solutions[0].cp,
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
    parser.add_argument('--species', type=int, default=1, choices=[1, 2],
                        help='Especie de contrapunto: 1 o 2 (default: 1)')
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
                        help='Solo 2ª especie: contrapunto por encima o por debajo del CF')
    parser.add_argument('--cf', type=str, default='',
                        help='Solo 2ª especie: CF explícito como enteros separados por comas, e.g. 0,2,4,5')
    parser.add_argument('--max_solutions', type=int, default=1,
                        help='Solo 2ª especie: máximo de soluciones a conservar y mostrar (default: 1)')
    parser.add_argument('--exhaustive_species', action='store_true',
                        help='Solo 2ª especie: explorar todo el espacio de búsqueda (más lento)')

    args = parser.parse_args()

    modo_map = {
        'C': Notes.C, 'D': Notes.D, 'E': Notes.E, 'F': Notes.F,
        'G': Notes.G, 'A': Notes.A, 'B': Notes.B
    }
    modo = modo_map.get(args.modo.upper(), Notes.C)

    try:
        if args.species == 1:
            run_first_species(args, modo)
        else:
            run_second_species(args, modo)

        print()

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
