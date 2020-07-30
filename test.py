import unittest
from node import Node
from Note import Note, Diatonic
import sys

standardSequence = [0, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0]
c = 0
d = 1
e = 2
f = 3
g = 4
a = 5
b = 6

standard = [0, 2, 1, 0, 3, 2, 4, 3, 2, 1, 0]
repeatedNote = [c, c]
tritone = [f, b, f + 7, b, f, b - 7]
mTritone = [4, 3, 4, 5, 6, 5]
mTritone2 = [2, 3, 2, 1, 0, -1, 0]
badEnding = [0, 2, 1, 0, 3, 2, 4, 3, 2, -1, 0]


example = standard
failExample = badEnding


'''convertimos de note12 a note7'''
for i in range(0, len(example)):
    value = example[i]
    example[i] = Note.diatonicScale(0, value)

for i in range(0, len(failExample)):
    value = failExample[i]
    failExample[i] = Note.diatonicScale(0, value)
    value = failExample[i]
    print(Note(value % 12))

print(Note.diatonicScale(0, -1))


class TestMelody(unittest.TestCase):

    def testNotes(self):
        print('testing notes')
        for i in range(0, 12):
            if not Note.isWhite(i):
                continue
            print('chromatic index :' + str(i))
            print('chromatitc name :' + str(Note(i)))
            d = Diatonic(Diatonic.index(Note(i).value)).name
            ch = Note(i).name
            print('diatonic name :' + d)
            assert(d == ch)

    def testPass(self):
        print('testing cf')
        s = example
        s.reverse()
        for i in range(0, 11):
            if i == 0:
                node = Node(s[0])
            else:
                node = Node(s[i], node)
            assert(node.validMelody())
        print('sequence passed')

    def testFail(self):
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
                valid = False
        if not valid:
            print('sequence failed as intended')
        assert(not valid)


if __name__ == '__main__':
    unittest.main()
    print('caca')
