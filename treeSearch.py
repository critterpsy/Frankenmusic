from node import Node
from collections import Counter
from Note import Note
import sys

container = []
maxDepth = 11
counterP = []


def Search(note, depth, maxDepth, plagal, lastNode=None):
    if depth == 0:
        new_node = Node(note)
    else:
        new_node = Node(note, lastNode)
    if not new_node.validMelody(size=11, counter=False, mode=new_node.root):
        
        return
    if depth + 1 == maxDepth:
        container.append(new_node)
        return
    shift = 5 if plagal else 0
    root = new_node.root
    if depth + 2 == maxDepth:
        Search(new_node.root, depth + 1, maxDepth, plagal, new_node)
        return
    for i in range(0, 7):
        newNote = Note.diatonicScale(root - shift, i)
        Search(newNote, depth + 1, maxDepth, plagal, new_node)


def SearchCantus(initial, length, plagal):
    step = 0
    print('search called')
    Search(initial, step, length, plagal, lastNode=None)


def pruneCantus(arr, hi, disc, variety, modeRep, cTest=None):
    length = len(arr)
    size = 0
    for i in range(0, length):
        if i > length - 1:
            break
        s = arr[i].sequence
        if arr[i].disc > disc:
            continue
        if arr[i].hiIndex > 11 - hi:
            continue
        if len(Counter(arr[i].sequence).keys()) < variety:
            continue
        if arr[i].modeRep < modeRep:
            continue
        if cTest:
            setBreak = False
            for k in range(0, 11):
                if s[k] != cTest[k]:
                    setBreak = True
                    break
            if setBreak:
                continue
            print('found')
            print('cf found :'+str(size))
            arr[i].printNotes()
            # return
        interval = []
        size = size + 1
        arr[i].printNotes()
        print(s)
        print(str(interval) + '\n')
        print(i)
    print(size)
    if cTest:
        print('notFound')


def searchCounter(mode, note, cantus, depth, plagal, lastNode=None):
    # print('starting serch counter '+str(note))
    # print(depth)
    print('\n start search '+str(depth))
    print('sequence '+str(note))
    if depth == 0:
        # print('generating counter '+str(note))
        newNode = Node(note)
    else:
        # print('constructing child '+str(note) + ' from :'+str(lastNode.note))
        newNode = Node(note, lastNode)
    if not newNode.validMelody(11, True, mode):
        print('---invalid melody '+str(newNode.sequence))
        # print(str(note)+' invalid melody')
        return
    else:
        print('---valid melody')
        print(newNode.sequence)
    if not newNode.validateVoice1(cantus):
        # print(str(note)+' invalid counter')
        print('---invalid counter')
        return False
    else:
        print('---valid counterpoint')
    if depth + 1 == maxDepth:

        counterP.append(newNode)
        return
    shift = 4 if plagal else 0
    # print('generating children')
    if depth == 0:
        print('mode is '+str(Note(mode).name))
        searchCounter(mode, mode-1, cantus, 1, plagal, newNode)
        return
    if depth + 2 == maxDepth:
        searchCounter(mode, mode, cantus, depth + 1, plagal, newNode)
        searchCounter(mode, mode + 4, cantus, depth + 1, plagal, newNode)
        return
    for i in range(0, 7):
        interval = (mode - shift + i) - cantus[depth + 1]
        interval = abs(interval)
        print('index'+str(i))
        print('step '+str(depth))
        print('cantus '+str(cantus[depth]))
        print('interval' + str(interval))

        if interval == 1:
            continue
        if interval == 2:
            continue
        if interval == 5:
            continue
        if interval == 6:
            continue
        if interval == 10:
            continue
        if interval == 11:
            continue
        searchCounter(mode, mode - shift + i, cantus, depth + 1, plagal, newNode)


def GenerateCounter(cantus):
    searchCounter(cantus[0]+7, cantus[0] + 7, cantus, 0, False)
    print('counter found '+str(len(counterP)))
    for c in counterP:
        # if pruneCounter(cantus, c):
        #     continue
        print('\n')
        c.printNotes()
        # print(c.sequence)
        for i in range(0, 11):
            if i == 0:
                new_node = Node(cantus[0])
                previous = new_node
            else:
                new_node = Node(cantus[i], previous)
                previous = new_node
        new_node.printNotes()
        c.sequence.reverse()
        print(c.sequence)
        intervals = []
        for i in range(0, 11):
            intervals.append(Note.nInterval(
                                            new_node.sequence[i],
                                            c.sequence[i]))
        intervals.reverse()
        print(intervals)


def testCounter(seq, cantus, octave=0):
    for m in range(0, 11):
        if m == 0:
            cp = Node(seq[0] + 12*octave)
            previous = cp
        else:
            cp = Node(seq[m]+12*octave, previous)
            if not cp.validMelody(11, True, cantus[0]+12*1):
                print('invalid movement from counterpoint '+str(cp.index))
                break
            previous = cp
        if not cp.validateVoice1(cantus):
            print('invalid counter point '+str(cp.index))
            print('note : '+str(cp.note))
            Note.printSequence(cp.sequence, True)
            Note.printSequence(cantus[0:len(cp.sequence)], True)
            Note.printIntervales(cantus[0:len(cp.sequence)], cp.sequence, True)
            break
            # print('validated '+str(seq[m]) + ' at :' + str(cp.index))
    if len(cp.sequence) == 11:
        print('valid counter point')

    return cp


s = [2, 5, 4, 2, 7, 5, 9, 7, 5, 4, 2]
cantus = [1, 3, 2, 1, 4, 3, 5, 4, 3, 2, 1]
counterDiat = [5, 5, 4, 5, 6, 7, 7, 6, 8, 7, 8]
counter = [9, 9, 7, 9, 11, 12, 12, 11, 14, 13, 14]

if sys.argv[1] == 'scf':
    SearchCantus(2, 11, False)
    s.reverse()
    pruneCantus(container, hi=6, disc=3, variety=5, modeRep=3, cTest=s)
    print(len(container))
if sys.argv[1] == 'scp':
    s.reverse()
    GenerateCounter(s)
if sys.argv[1] == 'tcp':
    s.reverse()
    counter.reverse()
    testCounter(counter, s, octave=1)
    print('testCounter')
if sys.argv[1] == 'tcf':
    print('testing cf')
    s.reverse()
    for i in range(0, len(s)):
        if i == 0:
            node = Node(s[0])
        else:
            node = Node(s[i], node)
        valid = node.validMelody(len(s))
    if not valid:
        print('invalid ' + str(node.sequence))
    if node.disc > 3:
        print('disc :' + str(node.disc))
    if node.hiIndex > 11 - 6:
        print('invalid hiIndex ' + str(node.hiIndex))
    if len(Counter(node.sequence).keys()) < 5:
        print('variety ' + str(len(Counter(node.sequence).keys())))
    if node.modeRep < 3:
        print('modeRep :' + str(node.modeRep))
# for c in container:
    #     print(c.printNotes())
