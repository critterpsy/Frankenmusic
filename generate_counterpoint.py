#!/usr/bin/env python3
"""
Script para generar contrapuntos desde la consola.
Uso: python3 generate_counterpoint.py --modo C --length 8 --num_voices 2
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
from Note import Notes

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("Advertencia: mido no está instalado. No se puede exportar a MIDI. Instala con: pip install mido")

SEPARATOR = "─" * 60

def note_name(note_num):
    """Convierte número de nota a nombre (e.g., 0 -> C4)"""
    octave = note_num // 12
    note = Notes(note_num % 12).name
    return f"{note}{octave}"

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

        seq = voice.pool[0].sequence if hasattr(voice.pool[0], 'sequence') else voice.pool[0]

        for note in seq:
            track.append(Message('note_on', note=note + 60, velocity=64, time=0))
            track.append(Message('note_off', note=note + 60, velocity=64, time=480))

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
    mscore = find_mscore()
    if not mscore:
        print("\n  [!] MuseScore no encontrado. Instálalo desde https://musescore.org")
        return
    abs_path = os.path.abspath(midi_path)
    print(f"\n  Abriendo en MuseScore: {mscore} \"{abs_path}\"")
    subprocess.Popen([mscore, abs_path])

def print_results(voices, modo_str, length):
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
            marker = "►" if j == 0 else " "
            print(f"    {marker} [{j+1}]  nums : {nums}")
            print(f"         notas: {names}")

    print(f"\n{SEPARATOR}")

def main():
    parser = argparse.ArgumentParser(description='Generar contrapuntos con Frankenmusic')
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

    args = parser.parse_args()

    modo_map = {
        'C': Notes.C, 'D': Notes.D, 'E': Notes.E, 'F': Notes.F,
        'G': Notes.G, 'A': Notes.A, 'B': Notes.B
    }
    modo = modo_map.get(args.modo.upper(), Notes.C)

    print(f"\n{SEPARATOR}")
    print(f"  Frankenmusic — Generador de Contrapunto")
    print(SEPARATOR)
    print(f"  Modo       : {args.modo}")
    print(f"  Longitud   : {args.length}")
    print(f"  Voces      : {args.num_voices}")
    print(f"  Plagal     : {'Sí' if args.plagal else 'No'}")
    print(f"  Debug      : {'Sí' if args.debug else 'No'}")
    print(SEPARATOR)

    try:
        ts = TreeSearch(modo=modo, length=args.length, plagal=args.plagal,
                        num_voices=args.num_voices, debug=args.debug,
                        sequential=args.sequential, exhaustive_search=args.exhaustive_search)

        print("\n  Buscando secuencias...")
        ts.generate_voices()

        print_results(ts.voices, args.modo, args.length)

        midi_path = None
        if args.export_midi or args.open_score:
            if not args.midi_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                args.midi_filename = f"output/midis/counterpoint_{args.modo}_{args.length}n_{args.num_voices}v_{timestamp}.mid"
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suggested = f"output/midis/counterpoint_{args.modo}_{args.length}n_{args.num_voices}v_{timestamp}.mid"
            mscore = find_mscore() or "mscore3"
            print(f"  Tip: usa --export_midi para guardar el MIDI")
            print(f"       usa --export_midi --open_score para abrirlo directamente en MuseScore")

        print()

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
