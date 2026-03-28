"""Legacy first-species search engine.

The musical behavior of this module is intentionally preserved: the goal of
this refactor is to make the old engine readable and maintainable, not to
change its doctrine. Public method names are kept for compatibility with the
CLI, tests, and older exploratory scripts.
"""

import logging
import random

from src import Note
from src.node import Node


logger = logging.getLogger("treeSearch")
Notes = Note.Notes


class Voice:
    """Single voice configuration and result pool for the legacy search engine."""

    def __init__(
        self,
        modo,
        octave,
        index=0,
        _range=1,
        length=11,
        plagal=False,
        debug=False,
    ):
        self.index = index
        self.length = length
        self.is_cantus_firmus = index == 0
        self.modo = modo % 12 + 12 * octave
        self.floor = self.modo if not plagal else self.modo - 7
        self.ceiling = self.floor + _range * 12
        self.plagal = plagal
        self.pool = []

    def is_cantus(self):
        return self.index == 0

    def pitch_domain(self):
        """Return the legacy search domain for this voice."""
        octaves = (self.ceiling - self.floor) // 12
        return Note.note_range(
            self.floor,
            octaves,
            **{"add_sib": True, "whites": True},
        )

    def range(self):
        """Compatibility wrapper for the historical API."""
        return self.pitch_domain()

    def found(self):
        return bool(self.pool)

    def opening_notes(self):
        """Return allowed starting pitches for this voice."""
        if self.is_cantus():
            return [self.modo]
        return Note.degree(self.modo, 1, self.ceiling - 1, **{"3rd": True})

    def start(self):
        """Compatibility wrapper for the historical API."""
        return self.opening_notes()

    def penultimate_candidates(self):
        """Return allowed penultimate-note candidates for cadential closure."""
        if self.is_cantus():
            return [Note.white_scale(self.modo, 1)]
        if self.index == 1:
            return [self.modo - 1, self.modo + 12]
        return Note.degree(note=self.modo, n=7, ceiling=self.ceiling, **{"ag": self.modo - 2})

    def cadence(self):
        """Compatibility wrapper for the historical API."""
        return self.penultimate_candidates()

    def final_candidates(self):
        """Return allowed final-note candidates for this voice."""
        if self.is_cantus():
            return [self.modo]
        return Note.degree(self.modo, n=1, ceiling=self.ceiling, **{"major": True})

    def endings(self):
        """Compatibility wrapper for the historical API."""
        return self.final_candidates()

    def add(self, node):
        self.pool.append(node)

    def size(self):
        return len(self.pool)

    def get_notes(self, index=None):
        """Return a stored solution; default to the best-ranked solution."""
        assert self.pool is not None
        return self.pool[0 if index is None else index]

    def __str__(self):
        index = "cf" if self.index == 0 else self.index
        string = "modo: {}, value {}".format(Notes(self.modo % 12), self.modo)
        string += "\n\tindex: {}".format(index)
        string += "\n\tlength: {}".format(self.length)
        string += "\n\tplagal: {}".format(self.plagal)
        return string


class TreeSearch:
    """Legacy depth-first search generator for first-species counterpoint."""

    # Stable scope: 2 voices / first species.
    # Support for 3+ voices is experimental: incremental generation works, but
    # global inter-voice validation is not guaranteed during search.
    # Future direction: a PolyphonicState architecture would support true
    # simultaneous multi-voice generation with global validation at each step.
    STABLE_NUM_VOICES = 2

    class Parameters:
        """Historical search parameters kept for compatibility."""

        def __init__(self, instance, **kwargs):
            kwargs["hiIndex"] = kwargs.get("hiIndex", instance.length // 2)
            kwargs["disc"] = kwargs.get("disc", 3)
            kwargs["modeRep"] = kwargs.get("modeRep", 3)
            kwargs["variety"] = kwargs.get("variety", 5)
            logger.debug("init parameters: %s", kwargs)
            self.high_index = kwargs.get("hiIndex")
            self.discontinuities = kwargs.get("disc")
            self.modeRep = kwargs.get("modeRep")
            self.variety = kwargs.get("variety")

    def __init__(
        self,
        modo=Notes.D,
        length=11,
        plagal=False,
        num_voices=1,
        debug=False,
        sequential=False,
        exhaustive_search=False,
    ):
        self.modo = modo.value
        self.length = length
        self.plagal = plagal
        self.num_voices = num_voices
        self.voices = []
        self.sequential = sequential
        self.exhaustive_search = exhaustive_search
        self.debug = debug
        self.parameters = self.Parameters(self)
        logger.debug("%s", self)

        for index in range(num_voices):
            self.add_voice(index, _range=1, octave=index)

    def _best_sequence_for_voice(self, voice):
        if not voice.found():
            return []
        return voice.get_notes().sequence

    def _note_name(self, num):
        octave = num // 12
        name = Notes(num % 12).name
        return f"{name}{octave}"

    def _format_note_sequence(self, sequence):
        return "  ".join(f"{self._note_name(note):>4}" for note in sequence)

    def _candidate_pool_for_depth(self, voice, depth, pitch_domain, cadence_candidates, final_candidates):
        """Select the correct note domain for the next recursive step."""
        next_depth = depth + 1
        if next_depth == self.length - 2:
            return cadence_candidates
        if next_depth == self.length - 1:
            return final_candidates
        return pitch_domain

    def _ordered_candidates(self, candidate_pool):
        """Return candidates in deterministic or randomized search order."""
        if self.sequential:
            return list(candidate_pool)
        return random.sample(candidate_pool, len(candidate_pool))

    def _record_solution(self, voice_index, node):
        """Store a complete valid solution if it survives conservative pruning."""
        if not self.prune_node(node):
            return False
        logger.debug("PUSHING NODE")
        self.push_node(voice_index, node)
        return True

    def _build_search_node(self, voice, note, depth, last_node, reference_chords):
        """Build the current search node and its previous vertical snapshot."""
        if depth == 0:
            return Node(voice, note, debug=self.debug, ref=reference_chords), None
        node = last_node.create_child(note)
        last_chord = reference_chords[depth - 1] + [last_node.note]
        return node, last_chord

    def _sort_voice_pool(self, voice):
        if len(voice.pool) > 1:
            voice.pool.sort(key=self.score_node, reverse=True)

    def _iter_found_voice_pairs(self, sequences):
        for left in range(len(sequences)):
            for right in range(left + 1, len(sequences)):
                yield left, right

    def add_voice(self, index, _range, octave):
        voice = Voice(
            modo=self.modo,
            octave=octave,
            index=index,
            _range=_range,
            length=self.length,
        )
        logger.debug("adding voice %s", voice)
        if index < len(self.voices):
            self.voices[index] = voice
        else:
            self.voices.append(voice)

    def push_node(self, index, node):
        """Commit a node object to the selected voice pool."""
        self.voices[index].add(node)

    def to_chord(self, *args, omit=None):
        """Build a vertical reference snapshot from all found voices.

        For each voice at index ``i``, ``args[i]`` selects an explicit pool item.
        When no explicit index is passed, the best-ranked sequence is used
        (`pool[0]`, after post-search sorting).

        Voices that have not yet produced any result are skipped.
        ``omit`` excludes a specific voice index while building the reference
        used during search.
        """
        selected_sequences = []
        for index, voice in enumerate(self.voices):
            if omit == index or not voice.found():
                continue
            selected_index = args[index] if index < len(args) else None
            selected_sequences.append(voice.get_notes(index=selected_index))

        return [
            [selected_sequences[k].sequence[time_index] for k in range(len(selected_sequences))]
            for time_index in range(self.length)
        ]

    def generate_voices(self):
        """Generate each voice sequentially, using prior voices as reference.

        Stable scope: 2 voices / first species (STABLE_NUM_VOICES = 2).
        For 3+ voices the generation is experimental: each new voice is
        validated against all already-found voices at each step, but there
        is no simultaneous global revision of the full polyphonic fabric.
        After generation, validate_polyphonic_set() performs a post-hoc
        global check and logs any violations found.
        """
        for index in range(len(self.voices)):
            self.search_voice(self.voices[index], cf=self.voices[0:index])

        for violation in self.validate_polyphonic_set():
            logger.warning("polyphonic violation: %s", violation)

    def display_voice_found(self, voice_index):
        """Print the best sequence found for one voice."""
        voice = self.voices[voice_index]
        label = "CF" if voice.is_cantus() else f"CP{voice_index}"
        best_sequence = self._best_sequence_for_voice(voice)
        print(f"  [{label}] {voice.size()} secuencia(s) → {self._format_note_sequence(best_sequence)}")

        if voice_index > 0 and self.voices[0].found():
            cf_sequence = self._best_sequence_for_voice(self.voices[0])
            print(f"  CF  →  {self._format_note_sequence(cf_sequence)}")
            print(f"  CP  →  {self._format_note_sequence(best_sequence)}")

    def display_voices(self, tree=False, size=3):
        """Display stored results for interactive inspection."""
        if not tree:
            for voice in self.voices:
                if voice.found():
                    print(voice.get_notes())
            return

        for voice in self.voices:
            max_items = min(size, len(voice.pool))
            for index in range(max_items):
                print(voice.pool[index])

    def search_voice(self, voice, cf=None):
        """Search all valid sequences for one voice against prior references."""
        del cf  # historical argument kept for compatibility with older call sites

        voice_index = voice.index
        opening_notes = voice.opening_notes()
        pitch_domain = voice.pitch_domain()
        cadence_candidates = voice.penultimate_candidates()
        final_candidates = voice.final_candidates()
        stop_on_first = not self.exhaustive_search
        reference_chords = self.to_chord(omit=voice_index)

        logger.debug("sequential: %s", self.sequential)

        def search_branch(note, depth=0, last_node=None):
            node, last_chord = self._build_search_node(
                voice,
                note,
                depth,
                last_node,
                reference_chords,
            )
            current_chord = reference_chords[depth] + [node.note]

            if not node.is_valid(self.num_voices, current_chord, last_chord):
                return False

            if depth + 1 == self.length:
                solution_recorded = self._record_solution(voice_index, node)
                return solution_recorded and stop_on_first

            candidate_pool = self._candidate_pool_for_depth(
                voice,
                depth,
                pitch_domain,
                cadence_candidates,
                final_candidates,
            )

            for candidate in self._ordered_candidates(candidate_pool):
                if candidate == node.note and voice_index == 0:
                    continue
                found = search_branch(candidate, depth=depth + 1, last_node=node)
                if found and stop_on_first:
                    return True
            return False

        for note in opening_notes:
            logger.debug("voice %d search start", voice_index)
            found = search_branch(note)
            logger.debug("%d node(s) found for voice %d", voice.size(), voice_index)
            if found:
                break

        self._sort_voice_pool(voice)
        self.display_voice_found(voice_index)

    def __str__(self):
        return (
            "search info \n\t modo {}   \n\t sequential {} "
            "\n\t exhaustive_search {}".format(
                self.modo,
                self.sequential,
                self.exhaustive_search,
            )
        )

    def validate_polyphonic_set(self):
        """Post-hoc global validator for the assembled polyphonic result.

        Checks all voice pairs at every time step for:
        - Vertical consonance (each pair must form a consonant interval)
        - Parallel perfect 5ths (arriving at P5 by similar motion)
        - Parallel octaves / unisons (arriving at 0 mod 12 by similar motion)

        Returns a list of violation strings. An empty list means no violations
        were found. Runs only when at least 2 voices have produced results.
        """
        found_voices = [voice for voice in self.voices if voice.found()]
        if len(found_voices) < 2:
            return []

        sequences = [voice.get_notes().sequence for voice in found_voices]
        violations = []

        for time_index in range(len(sequences[0])):
            for left, right in self._iter_found_voice_pairs(sequences):
                if not Note.consonance(sequences[left][time_index], sequences[right][time_index]):
                    name_left = Notes(sequences[left][time_index] % 12).name
                    name_right = Notes(sequences[right][time_index] % 12).name
                    violations.append(
                        f"Dissonance at t={time_index}: voice {left} ({name_left}) "
                        f"vs voice {right} ({name_right})"
                    )

        for time_index in range(1, len(sequences[0])):
            for left, right in self._iter_found_voice_pairs(sequences):
                left_move = sequences[left][time_index] - sequences[left][time_index - 1]
                right_move = sequences[right][time_index] - sequences[right][time_index - 1]
                if left_move == 0 or right_move == 0:
                    continue
                if (left_move > 0) != (right_move > 0):
                    continue

                current_interval = Note.interval(sequences[left][time_index], sequences[right][time_index])
                if current_interval == 7:
                    violations.append(
                        f"Parallel 5th at t={time_index}: voice {left} vs voice {right}"
                    )
                if current_interval == 0:
                    violations.append(
                        f"Parallel octave/unison at t={time_index}: voice {left} vs voice {right}"
                    )

        return violations

    def prune_node(self, node):
        """Conservative viability filter for complete sequences.

        Only rejects sequences with too many leaps (disc), which makes a
        melody genuinely unsingable regardless of stylistic preference.
        All other quality metrics (hiIndex, variety, modeRep) are handled
        by score_node() and reflected in pool ordering instead.
        """
        return node.disc <= self.parameters.discontinuities

    def score_node(self, node):
        """Quality score for a complete sequence. Higher is better.

        Components:
        - disc_score: fewer leaps larger than a step
        - hi_score: climax closer to the sequence center
        - variety_score: more distinct pitches
        - mode_score: more returns to the modal final
        """
        center = self.length // 2
        disc_score = max(0, 6 - node.disc)
        hi_score = max(0, self.length - abs(node.hiIndex - center))
        variety_score = len(set(node.sequence))
        mode_score = node.modeRep
        return disc_score + hi_score + variety_score + mode_score
