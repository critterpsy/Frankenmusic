import failureCases
import random
from Note import Note

f_ = failureCases


standardSequence = [0, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0]
c = 0
d = 1
e = 2
f = 3
g = 4
a = 5
b = 6


class Example:
    def __init__(self, sequence, note7=True, failures=None, reference=None, straight=True):
        assert(seq is not None)
        if note7:
            self.sequence = []
            length = len(seq)
            for i in range(0, length):
                self.sequence.append(Note.diatonicScale(0, sequence[i]))
        else:
            self.sequence = sequence
        self.failures = failures



cf_examples = []
cf_fail_examples = []

cp_examples = []
cp_fail_examples = []

note7, seq = True, [0, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0]
standard = Example(sequence=seq, note7=True, failures=None)
cf_examples.append(standard)

note7, seq = True, [1, 5, 4, 3, 2, 1, 3, 2, 1]
dorico = Example(sequence=seq, note7=True, failures=None)
cf_examples.append(dorico)

note7, seq = True, [2, 0, 1, 0, -2, 5, 2, 3, 2]
frigio = Example(sequence=seq, note7=True, failures=None)
cf_examples.append(frigio)

note7, seq = True, [2, -2, 5, 4, 3, 2, 0, 3, 2]
frigio2 = Example(sequence=seq, note7=True, failures=None)
cf_examples.append(frigio2)

note7, seq = True, [2, -2, -1, 0, 1, 2, 3, 1, 4, 3, 2]
frigio3 = Example(sequence=seq, note7=True, failures=None)
cf_examples.append(frigio3)

note7, seq = True, [-3, 1, 0, -2, -1, 0, -1, -2, -3]
mixo = Example(sequence=seq, note7=True, failures=None)
cf_examples.append(mixo)


'''failure examples '''

note7, seq = True, [c, c]
failures = [(f_.repeated_note, 1)]
repeatedNote = Example(sequence=seq, note7=True, failures=failures)
cf_fail_examples.append(repeatedNote)

note7, seq = True, [f, b, f + 7, b, f, b - 7]
fail = []
for i in range(1, 6):
    fail.append((f_.tritone, i))
tritone = Example(sequence=seq, note7=True, failures=fail)
cf_fail_examples.append(tritone)

note7, seq = True, [4, 3, 4, 5, 6, 5]
failures = [(f_.isolated_tritone, 5)]
mTritone = Example(sequence=seq, note7=True, failures=failures)
cf_fail_examples.append(mTritone)

note7, seq = True, [2, 3, 2, 1, 0, -1, 0]
failures = [(f_.isolated_tritone, 6)]
mTritone2 = Example(sequence=seq, note7=True, failures=failures)
cf_fail_examples.append(mTritone2)

note7, seq = True, [0, 2, 1, 0, 3, 2, 4, 3, 2, -1, 0]
failures = [(f_.bad_ending, len(seq) - 2)]
badEnding = Example(sequence=seq, note7=True, failures=failures)
cf_fail_examples.append(badEnding)

note7, seq = False, [2, 7, 5, 9, 11, 12, 11, 12, 9, 4, 2]
failures = [(f_.seq, 3), (f_.seq)]
sequences = Example(sequence=seq, note7=True, failures=failures)
cf_fail_examples.append(sequences)

note7, seq = False, [2, 9, 11, 2, 4, 2]
failures = [(f_.sixthM, 3)]
sixthM = Example(sequence=seq, note7=False, failures=failures)
cf_fail_examples.append(sixthM)

note7, seq = False, [2, 4, 7, 4]
failures = [(f_.badJump, 2)]
badJump = Example(sequence=seq, note7=True, failures=failures)
cf_fail_examples.append(badJump)


''' example = D0, F0, E0, D0, G0, F0, A0, G0, F0, E0, RE'''
reference_cf = random.choice(cf_examples).sequence
sequence_cp = reference_cf.copy()
sequence_cp[0] = sequence_cp[0] + 1
counterBadStart = Example(sequence=sequence_cp,
                          note7=False,
                          failures=[(f_.dissonance)],
                          reference=(reference_cf)
                          )
cp_fail_examples.append(counterBadStart)
''' s[0] = D0# = s[0] + 1'''
# counterBadStart = Node.FromSequence(cf, octaveShift=0, isCantus=False)
# ''' exampleCp = A0 , A0, G0, A0, B0, C1, C1, B0, D1, C1#, D1'''
#
# ''' quintas paralelas con la referencia '''
# parallelFifth = []
# parallelFifth.append(example[0] + 7)
# parallelFifth.append(example[1] + 7)
# parallel_5 = NodeFromSequence(parallelFifth, 0)
