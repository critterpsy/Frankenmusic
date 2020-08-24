import unittest
import Examples
import random
from node import Node
from Note import Note, Diatonic
import sys

cf_examples = Examples.cf_examples
cf_fail_examples = Examples.cf_fail_examples

cp_examples = Examples.cp_examples
cp_fail_examples = Examples.cp_fail_examples


class TestCases(unittest.TestCase):

    # def testNotes(self):
    #     c = 0
    #     d = 2
    #     e = 4
    #     f = 5
    #     g = 7
    #     a = 9
    #     b = 11
    #     equals = Note.equals
    #     for i in range(0, 48):
    #         is_white = False
    #         if equals(i, c):
    #             is_white = True
    #         elif equals(i, d):
    #             is_white = True
    #         elif equals(i, e):
    #             is_white = True
    #         elif equals(i, f):
    #             is_white = True
    #         elif equals(i, g):
    #             is_white = True
    #         elif equals(i, a):
    #             is_white = True
    #         elif equals(i, b):
    #             is_white = True
    #         if is_white:
    #             assert(Note.isWhite(i))
    #         else:
    #             assert(not Note.isWhite(i))
    #
    # def test_cf_examples(self):
    #     print('testing {} cantus firmus'.format(len(cf_examples)))
    #     for e in cf_examples:
    #         node = Node.FromSequence(e.sequence, 0, is_cantus=True)
    #         s = node.sequence
    #         ''' failure log is contained in terminalNode.failures string arr'''
    #         for i in range(0, len(s)):
    #             assert(node.failures[i] == '')

    def test_cp_examples(self):
        print('testing {} counterpoints'.format(len(cp_examples)))
        for e in cp_examples:
            node = Node.debug_cp(
                                input_sequence=e.sequence,
                                is_cantus=False,
                                cantus_firmus=e.reference)
            s = node.sequence
            ''' failure log is contained in terminalNode.failures string arr'''
            for i in range(0, len(s)):
                assert(node.failures[i] == '')

    # def test_cf_failes(self):
    #     print('testing {} cf fail examples  :'.format(len(cf_fail_examples)))
    #     fail_example = cf_fail_examples[0]
    #     print('inspecting sequence ' + str(fail_example.sequence))
    #     node = Node.FromSequence(cf_fail_examples[0].sequence,
    #                              is_cantus=(True))
    #     print(node.failures)
    #     for f in cf_fail_examples:
    #         node = Node.FromSequence(f.sequence, 0, is_cantus=(True))
    #         assert(len(node.sequence) == len(f.sequence))
    #         failures = f.failures
    #         print('node sequence :' + str(node.sequence))
    #         print('example sequence :' + str(f.sequence))
    #         s_ = node.failures
    #         # if f.straight:
    #         #     s_.reverse()
    #         print('example failures :' + str(failures))
    #         print('tree_node_failures :' + str(s_))
    #         for item in failures:
    #             length = len(node.sequence)
    #             intended_failure = item[0]
    #             index = item[1]
    #             print('length :' + str((length)))
    #             print('index searched :' + str(index))
    #             print('node failure detected :' + str(node.failures[index]))
    #             print('example failure :' + str(intended_failure))
    #             assert((intended_failure) in node.failures[index])
    #
    #
    # def test_cp_failes(self):
    #     print('\n testing {} cp fail examples  :'.format(len(cp_fail_examples)))
    #     cantus_firmus = cf_examples[0].sequence
    #     print('cantus firmus :{}'.format(cf_examples[0].sequence))
    #     print(cp_fail_examples[0])
    #     for f in cp_fail_examples:
    #         node = Node.debug_cp(input_sequence=f.sequence,
    #                              octave_shift=0,
    #                              is_cantus=(False),
    #                              cantus_firmus=(cantus_firmus))
    #         assert(len(node.sequence) == len(f.sequence))
    #         failures = f.failures
    #         # print('example failures :' + str(failures))
    #         # print('tree_node_failures :' + str(s_))
    #         # print('{} failures found:'.format(len(failures)))
    #         for item in failures:
    #             length = len(node.sequence)
    #             intended_failure = item[0]
    #             index = item[1]
    #             print(node)
    #             print('length :' + str((length)))
    #             print('index searched :' + str(index))
    #             print('node failure detected :' + str(node.failures[index]))
    #             print('example failure :' + str(intended_failure))
    #             assert((intended_failure) in node.failures[index])
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


if __name__ == '__main__':
    unittest.main()
