import unittest
import Examples
import random
from node import Node
from Note import Note, Diatonic
import sys
import os
from treeSearch import Search

cf_examples = Examples.cf_examples
cf_fail_examples = Examples.cf_fail_examples

cp_examples = []
cp_fail_examples = Examples.cp_fail_examples


class TestCases(unittest.TestCase):
    print('testCases read!')

    # def testNotes(self):
    #     if testNotes:
    #         print('TESTING DIATONIC-CHROMATIC CORRESPONDANCE')
    #         print('TESTING CHROMATIC TO DIATONIC SCALE')
    #         for i in range(0, 15):
    #             note = Note.diatonicScale(0, -i)
    #             print('note :'+str(Note(note % 12)) + ' octave :' + str(int(note / 12)))
    #         for i in range(0, 12):
    #             if not Note.isWhite(i):
    #                 continue
    #             print('chromatic index :' + str(i))
    #             print('chromatitc name :' + str(Note(i)))
    #             d = Diatonic(Diatonic.index(Note(i).value)).name
    #             ch = Note(i).name
    #             print('diatonic name :' + d)
    #             assert(d == ch)
    #         for i in range(0, 24):
    #             print(Note(i % 12))
    #             print('dIndex : ' + str(Diatonic.index(i)))
    #         for i in range(0, 24):
    #             print(Note((-i) % 12))
    #             print('dIndex : ' + str(Diatonic.index(-i)))
    #         print('testing intervals')
    #         for i in range(0, 26):
    #             if not Note.isWhite(i):
    #                 continue
    #             print(Note(i % 12).name + str(i//12))
    #             print(Diatonic.interval(0, i))
    #         for i in range(0, 26):
    #             if not Note.isWhite(-i):
    #                 continue
    #             print(Note((-i) % 12).name + str(-i//12))
    #             print(Diatonic.interval(0, -i))

    def test_cf_examples(self):
        print('testing {} cantus firmus'.format(len(cf_examples)))
        for e in cf_examples:
            node = Node.FromSequence(e.sequence, 0, isCantus=True)
            s = node.sequence
            ''' failure log is contained in terminalNode.failures string arr'''
            for i in range(0, len(s)):
                assert(node.failures[i] == '')

    def test_cf_failes(self):
        print('testing {} cf fail examples  :'.format(len(cf_fail_examples)))
        i = 0
        fail_example = cf_fail_examples[0]
        print('inspecting sequence ' + str(fail_example.sequence))
        node = Node.FromSequence(cf_fail_examples[0].sequence, isCantus=(True))
        print(node.failures)
        for f in cf_fail_examples:
            node = Node.FromSequence(f.sequence, 0, isCantus=(True))
            assert(len(node.sequence) == len(f.sequence))
            failures = f.failures
            print('node sequence :' + str(node.sequence))
            print('example sequence :' + str(f.sequence))
            s_ = node.failures
            # if f.straight:
            #     s_.reverse()
            print('example failures :' + str(failures))
            print('tree_node_failures :' + str(s_))
            for item in failures:
                length = len(node.sequence)
                intended_failure = item[0]
                index = item[1]
                print('length :' + str((length)))
                print('index searched :' + str(index))
                print('node failure detected :' + str(node.failures[index]))
                print('example failure :' + str(intended_failure))
                assert((intended_failure) in node.failures[index])
    #
    #     def test_cp_failes(self):
    #         print('testing {} cf fail examples  :'.format(len(cp_fail_examples)))
    #         i = 0
    #         fail_example = cp_fail_examples[0]
    #         print('inspecting sequence ' + str(fail_example.sequence))
    #         node = Node.FromSequence(cp_fail_examples[0].sequence, isCantus=(False))
    #         print(node.failures)
    #         for f in cf_fail_examples:
    #             if i > 1:
    #                 break
    #             node = Node.FromSequence(f.sequence, 0, isCantus=(True))
    #             assert(len(node.sequence) == len(f.sequence))
    #             failures = f.failures
    #             print('node sequence :' + str(node.sequence))
    #             print('example sequence :' + str(f.sequence))
    #             s_ = node.failures
    #             s_.reverse()
    #             print('example failures :' + str(failures))
    #             print('tree_node_failures :' + str(s_))
    #             for item in failures:
    #                 length = len(node.sequence)
    #                 intended_failure = item[0]
    #                 index = item[1]
    #                 print('failures :' + str(node.failures))
    #                 print('length :' + str((length)))
    #                 print('index searched :' + str(index))
    #                 print('node failure detected :' + str(node.failures[index]))
    #                 print('example failure :' + str(intended_failure))
    #                 print('ag4' in 'R E ag4')
    #                 assert((intended_failure) in node.failures[index])
                    # i = i + 1
    # def testFail(self):
    #     print('testing cf fail examples')
    #     for e in cf_fail_examples:
    #         print('testing Fail')
    #         s = e[1]
    #         valid = True
    #         for i in range(0, len(s)):
    #             if i == 0:
    #                 node = Node(s[0])
    #             else:
    #                 node = Node(s[i], node)
    #             if not node.validMelody():
    #                 print('invalid')
    #                 print(s)
    #                 print
    #                 valid = False
    #                 break
    #         if not valid:
    #             print('sequence failed as intended')
    #         else:
    #             print('error :sequence should fail!!')
    #         node.printNotes()
    #         assert(not valid)

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
