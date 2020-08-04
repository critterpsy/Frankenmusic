import unittest
import random
from node import Node
from Note import Note, Diatonic
import sys
import os


standardSequence = [0, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0]
c = 0
d = 1
e = 2
f = 3
g = 4
a = 5
b = 6

cf_examples = []
cf_fail_examples = []

cp_examples = []
cp_fail_examples = []


def ToNote12(sequence):
    forexample:
        assert(e[1] is not None)
        '''check if cf is note7'''
        if e[0]:
            length = len(e[1])
            s = e[1]
            for i in range(0, length):
                s[i] = Note.diatonicScale(0, s[i])


class Example:
    def __init__(self, sequence, note7=True, failures):
        assert(seq is not None)
        if note7:
            self.sequence = []
            length = len(seq)
            for i in range(0, length):
                self.append(Note.diatonicScale(0, sequence[i]))
        else:
            self.sequence = sequence
        self.failures = failures


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

'''failure cases'''
f_parallel5 = 'p5'
f_direct5 = 'd5'
f_repeated_note = 'R'
f_tritone = 'ag4'
f_middle_tritone = 'mTR'
f_isolated_tritone = 'iTR'
f_bad_ending = 'E'
f_sixthM = '6M'
f_badJump = 'j'
f_seq = 'SQ'
f_pairs = 'ABAB'

note7, seq = True, [c, c]
failures = [(repeated_note, 1)]
repeatedNote = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(repeatedNote)

note7, seq = True, [f, b, f + 7, b, f, b - 7]
for in range(1, 6):
    fail.append(f_tritone, i)
tritone = Example(sequence=seq, note7=True, fail)
cf_fail_examples.append(tritone)

note7, seq = True, [4, 3, 4, 5, 6, 5]
failures = [(f_middle_tritone, 5)]
mTritone = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(mTritone)

note7, seq = True, [2, 3, 2, 1, 0, -1, 0]
failures = [(f_middle_tritone, 6)]
mTritone2 = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(mTritone2)

note7, seq = True, [0, 2, 1, 0, 3, 2, 4, 3, 2, -1, 0]
failures = [(f_bad_ending, len(seq) - 1)]
badEnding = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(badEnding)

note7, seq = False, [2, 7, 5, 9, 11, 12, 11, 12, 9, 4, 2]
failures = [(f_seq, 3), (f_seq)]
sequences = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(sequences)

note7, seq = False, [2, 9, 11, 2, 4, 2]
sixthM = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(sixthM)

note7, seq = False, [2, 4, 5, 4]
badJump = Example(sequence=seq, note7=True, failures)
cf_fail_examples.append(badJump)


''' example = D0, F0, E0, D0, G0, F0, A0, G0, F0, E0, RE'''
s = random.choice(cf_examples)[1].copy()
''' s[0] = D0# = s[0] + 1'''
s[0] = s[0] + 1
counterBadStart = NodeFromSequence(s, octaveShift=0, isCantus=False)
''' exampleCp = A0 , A0, G0, A0, B0, C1, C1, B0, D1, C1#, D1'''

''' quintas paralelas con la referencia '''
parallelFifth = []
parallelFifth.append(example[0] + 7)
parallelFifth.append(example[1] + 7)
parallel_5 = NodeFromSequence(parallelFifth, 0)


ToNote12(cf_examples)
ToNote12(cf_fail_examples)
ToNote12(cp_examples)
ToNote12(cp_fail_examples)


testNotes = testExample = testFailExample = testFailCounter = False


class TestCases(unittest.TestCase):
    print('testCases read!')
    print(testNotes)

    def testNotes(self):
        if testNotes:
            print('TESTING DIATONIC-CHROMATIC CORRESPONDANCE')
            print('TESTING CHROMATIC TO DIATONIC SCALE')
            for i in range(0, 15):
                note = Note.diatonicScale(0, -i)
                print('note :'+str(Note(note % 12)) + ' octave :' + str(int(note / 12)))
            for i in range(0, 12):
                if not Note.isWhite(i):
                    continue
                print('chromatic index :' + str(i))
                print('chromatitc name :' + str(Note(i)))
                d = Diatonic(Diatonic.index(Note(i).value)).name
                ch = Note(i).name
                print('diatonic name :' + d)
                assert(d == ch)
            for i in range(0, 24):
                print(Note(i % 12))
                print('dIndex : ' + str(Diatonic.index(i)))
            for i in range(0, 24):
                print(Note((-i) % 12))
                print('dIndex : ' + str(Diatonic.index(-i)))
            print('testing intervals')
            for i in range(0, 26):
                if not Note.isWhite(i):
                    continue
                print(Note(i % 12).name + str(i//12))
                print(Diatonic.interval(0, i))
            for i in range(0, 26):
                if not Note.isWhite(-i):
                    continue
                print(Note((-i) % 12).name + str(-i//12))
                print(Diatonic.interval(0, -i))

    def test_cf_examples(self):
        print('testing cf examples')
        for e in cf_examples:
            node = Node.FromSequence(sequence, 0, isCantus=False)
            s = node.sequence
            for i in range(0, len(s)):
                if node
                if i == 0:
                    node = Node(s[0])
                else:
                    node = Node(s[i], node)
                valid = node.validMelody(len(s))
                if not valid:
                    print('invalid ' + str(node.sequence))
                assert(valid)
                print('sequence passed')

    def testFail(self):
        print('testing cf fail examples')
        for e in cf_fail_examples:
            print('testing Fail')
            s = e[1]
            valid = True
            for i in range(0, len(s)):
                if i == 0:
                    node = Node(s[0])
                else:
                    node = Node(s[i], node)
                if not node.validMelody():
                    print('invalid')
                    print(s)
                    print
                    valid = False
                    break
            if not valid:
                print('sequence failed as intended')
            else:
                print('error :sequence should fail!!')
            node.printNotes()
            assert(not valid)

    # def testFailCantus(self, cantus, octaveShift, failures):
    #     print('testing bad counter to fail')
    #     length = len(cantus)
    #     if testFailCounter:
    #         s = failCounter
    #         s.reverse()
    #     cp = NodeFromSequence(cantus, octaveShift)
    #     for m in range(length):
    #         assert(cp.failures[m] == failures[m])
    #     print('ok, badExampleFailed in {}' + str(failures))


print('enter test module')
print(sys.argv)
if __name__ == '__main__':
    unittest.main()
