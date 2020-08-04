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

note7, seq = True, [0, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0]
standard = (note7, seq)
cf_examples.append(standard)
note7, seq = True, [1, 5, 4, 3, 2, 1, 3, 2, 1]
dorico = (note7, seq)
cf_examples.append(dorico)
note7, seq = True, [2, 0, 1, 0, -2, 5, 2, 3, 2]
frigio = (note7, seq)
cf_examples.append(frigio)
note7, seq = True, [2, -2, 5, 4, 3, 2, 0, 3, 2]
frigio2 = (note7, 7)
cf_examples.append(frigio2)
note7, seq = True, [2, -2, -1, 0, 1, 2, 3, 1, 4, 3, 2]
frigio3 = (note7, seq)
cf_examples.append(frigio3)
note7, seq = True, [-3, 1, 0, -2, -1, 0, -1, -2, -3]
mixo = (note7, seq)
cf_examples.append(mixo)
note7, seq = True, [c, c]
repeatedNote = (note7, seq)
cf_fail_examples.append(repeatedNote)
note7, seq = True, [f, b, f + 7, b, f, b - 7]
tritone = (note7, seq)
cf_fail_examples.append(tritone)
note7, seq = True, [4, 3, 4, 5, 6, 5]
mTritone = (note7, seq)
cf_fail_examples.append(mTritone)
note7, seq = True, [2, 3, 2, 1, 0, -1, 0]
mTritone2 = (note7, seq)
cf_fail_examples.append(mTritone2)
note7, seq = True, [0, 2, 1, 0, 3, 2, 4, 3, 2, -1, 0]
badEnding = (note7, seq)
cf_fail_examples.append(badEnding)
note7, seq = False, [2, 7, 5, 9, 11, 12, 11, 12, 9, 4, 2]
sequences = (note7, seq)
cf_fail_examples.append(sequences)
note7, seq = False, [2, 9, 11, 2, 4, 2]
sixthM = (note7, seq)
cf_fail_examples.append(sixthM)
badJump = (False, [2, 4, 5, 4])
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








def ToNote12(examples):
    for e in examples:
        assert(e[1] is not None)
        '''check if cf is note7'''
        if e[0]:
            length = len(e[1])
            s = e[1]
            for i in range(0, length):
                s[i] = Note.diatonicScale(0, s[i])
        e.reverse()


ToNote12(cf_examples)
ToNote12(cf_fail_examples)
ToNote12(cp_examples)
ToNote12(cp_fail_examples)




if cf_reference[1] == 7:
    '''convertimos de note7 a note12'''
    cf = cf_reference[0]
    for i in range(0, len(example)):
        value = example[i]
        example[i] = Note.diatonicScale(0, value)





def NodeFromSequence(sequence, octaveShift, reverse=True, isCantus=False):
    failures = ''
    if reverse:
        sequence.reverse()
    for i in range(0, len(sequence)):
        valid = True
        if i == 0:
            node = Node(sequence[0] + 12*octaveShift)
        else:
            print(node)
            node = Node(sequence[i], node)
            valid = node.validMelody(size=len(sequence), counter=not isCantus, mode=node.root)
        if not valid:
            failures = failures + node.failures[i]
    print(failures)
    return node

#

#


#
# for i in range(0, len(failExample)):
#     value = failExample[i]
#     failExample[i] = Note.diatonicScale(0, value)
#     value = failExample[i]
    # print(Note(value % 12))


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

    def test_example(self):
        print('testing cf')
        s = example
        s.reverse()
        for i in range(0, len(s)):
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
        if testFailExample:
            print('testing Fail')
            s = failExample
            s.reverse()
            print(failExample)

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
