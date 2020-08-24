from node import Node
from collections import Counter
from Note import Note
import sys
from tree import SNode
from Examples import cf_examples



searched_cf = []
serialized_cf = []
js = []
pruned_cf = []
maxDepth = 11
counterP = []
debug_mode = True
debug_break_search = True


def search(note, depth, maxDepth, plagal, lastNode=None, serializable=None):
    debug = debugMode
    if depth == 0:
        new_node = Node(note, debug=debug)
        # nodeS = SNode(value=Note, parent=None)
        # js.append(nodeS)
    else:
        new_node = Node(note, lastNode=lastNode, debug=debug)
        # nodeS = SNode(value=note, parent=serializable)
    if not new_node.validMelody(size=11, counter=False, mode=new_node.root):
        return
    if depth + 1 == maxDepth:
        searched_cf.append(new_node)
        return
    shift = 5 if plagal else 0
    root = new_node.root
    if depth + 2 == maxDepth:
        search(
               note=new_node.root,
               depth=depth + 1,
               maxDepth=maxDepth,
               plagal=plagal,
               lastNode=new_node,
               serializable=None)
        return

    for i in range(0, 7):
        newNote = Note.diatonicScale(root - shift, i)
        search(
                note=newNote,
                depth=depth + 1,
                maxDepth=maxDepth,
                plagal=plagal,
                lastNode=new_node,
                serializable=None)


def search_cantus(initial, length, plagal):
    step = 0
    print('search called')
    search(initial, step, length, plagal, lastNode=None, serializable=None)
    print('search halt')


def searchCounter(mode, note, cantus, depth, plagal, lastNode=None, filter=None):
    if debug_break_search:
        input("Press enter to continue :\n")
    print('new note {}'.format(note) + ' thread :{}'.format(lastNode.sequence if lastNode else ''))
    if filter:
        print('step {}'.format(depth))
        print('filter {}'.format(filter))
    if depth == 0:
        newNode = Node(note, debug=debug_mode)
    else:
        newNode = Node(note, lastNode,  debug=debug_mode)
    if not newNode.validMelody(11, True, mode):
        # print('---invalid melody '+str(newNode.sequence))
        return
    if not newNode.valid_cp(cantus):
        # print('---invalid counter')
        return
    else:
        print('valid {}'.format(note))
    if depth + 1 == maxDepth:
        counterP.append(newNode)
        return
    shift = 4 if plagal else 0
    # if filter:
    #     print('trying')
    #     try:
    #         next_node = filter[depth + 1]
    #         searchCounter(mode, next_node, cantus, depth + 1, plagal, newNode, filter)
    #         return
    #     except Exception:
    #         pass

    if depth == 0:
        print('mode is '+str(Note(mode).name))
        searchCounter(mode, mode-1, cantus, 1, plagal, newNode)
        searchCounter(mode, mode-1 + 12, cantus, 1, plagal, newNode)
        return
    for i in range(0, 12):
        next_note = (mode - shift + i)
        interval = abs(next_note - cantus[depth + 1])
        # if interval == 1:
        #     continue
        # if interval == 2:
        #     continue
        # if interval == 5:
        #     continue
        # if interval == 6:
        #     continue
        # if interval == 10:
        #     continue
        # if interval == 11:
        #     continue
        if filter and filter[depth + 1] != next_note:
            continue

        searchCounter(mode, mode - shift + i, cantus, depth + 1, plagal, newNode)


def prune_sequence(arr, hi, disc, variety, modeRep, cTest=None):
    length = len(arr)
    size = 0
    setBreak = False
    for i in range(0, length):
        s = arr[i].sequence
        node = arr[i]
        # if node.disc > disc:
        #     continue
        # if node.hiIndex > len(s) - 1 - hi:
        #     continue
        # if len(Counter(s).keys()) < variety:
        #     continue
        # if node.modeRep < modeRep:
        #     continue
        size = size + 1
        if cTest:
            setBreak = False
            if len(s) != len(cTest):
                raise Exception('Test sequence does not correpond to tree depth')
            for k in range(0, len(s)):
                if s[k] != cTest[k]:
                    setBreak = True
                    break
            if setBreak:
                continue
            pruned_cf.append(node)
            print('found')
            break
            # return
        pruned_cf.append(node)
        node.printNotes()
    print('pruned found {}'.format(len(pruned_cf)))
    print(setBreak)
    if cTest and setBreak:
        print('notFound')


def generate_counter(cantus, reverse=True, log=True, filter_debug=None):
    cantus = cantus.copy()
    if filter_debug:
        filter_debug = filter_debug.copy()
        filter_debug.reverse()
    if reverse:
        cantus.reverse()
    searchCounter(cantus[0], cantus[0] + 12, cantus, 0, False, filter=(filter_debug))
    print('counter found '+str(len(counterP)))
    cantus_node = Node.FromSequence(cantus,
                                    octaveShift=0,
                                    reverse=False,
                                    is_cantus=(True))
    if log:
        for c in counterP:
            # if pruneCounter(cantus, c):
            #     continue
            print('\n')
            print('scale mode {}'.format(c.get_scale_mode()))
            c.printNotes()
            cantus_node.printNotes()
            # print(c.sequence)
            intervals = []
            for i in range(0, 11):
                intervals.append(Note.nInterval(
                                                cantus_node.sequence[i],
                                                c.sequence[i]))
            intervals.reverse()
            print(intervals)


def test_sequence(seq, cantus, octave=0):
    length = len(seq)
    for m in range(0, length):
        if m == 0:
            cp = Node(seq[0] + 12*octave, debug=True)
        else:
            cp = Node(seq[m]+12*octave, lastNode=cp, debug=True)
        if not cp.validMelody(length, True, cp.get_scale_mode()):
            break
        if not cp.valid_cp(cantus):
            break
            # print('validated '+str(seq[m]) + ' at :' + str(cp.index))
    if len(cp.sequence) == length:
        print('valid counter point')
    else:
        print(cp)
        print('counter is {} \n'.format(seq))
    return cp


def main():

    s = [2, 5, 4, 2, 7, 5, 9, 7, 5, 4, 2]
    counter = [9, 9, 7, 9, 11, 12, 12, 11, 14, 13, 14]
    if sys.argv[1] == 'scf':
        try:
            if sys.argv[2] == 'prune':
                prune = True
        except Exception:
            prune = False
        search_cantus(2, 11, False)
        # print(serializable_cf_root)
        # print(serializable_cf_root.toJson())
        s.reverse()
        if prune:
            prune_sequence(searched_cf, hi=1, disc=3, variety=5, modeRep=3, cTest=s)
        print('examples found ' + str(len(searched_cf)))
        print('examples serialized {}'.format(len(serialized_cf)))
        print('searched sequence : {}'.format(s))
        print('after prune :' + str(len(pruned_cf)))
    if sys.argv[1] == 'scp':
        filter = counter
        # filter = None
        generate_counter(s, log=(True), filter_debug=filter)
        prune_sequence(counterP, 4, 2, 5, 1, counter)
    if sys.argv[1] == 'tcp':
        s.reverse()
        counter.reverse()
        test_sequence(counter, s, octave=0)
        print('testCounter')
    if sys.argv[1] == 'tcf':
        print('testing cf {}')
        s.reverse()
        debug = debugMode
        for i in range(0, len(s)):
            if i == 0:
                print('start node')
                node = Node(s[0], debug=debug)
            else:
                print('node from parent')
                node = Node(s[i], lastNode=node, debug=debug)
            valid = node.validMelody(len(s))
            print('{} is valid {}'.format(node.sequence, valid))
            if not valid:
                print(node.failures)
                break
        if not valid:
            print('invalid ' + str(node.sequence))


if __name__ == '__main__':
    main()
