from node import Node
from collections import Counter
from Note import Note

container = []
maxDepth = 11
counterP = []
cantus = [1, 3, 2, 1, 4, 3, 5, 4, 3, 2, 1]
testCounter = [5, 5, 4, 5, 6, 7, 7, 6, 8, 7, 8]


def Search(note, depth, maxDepth, plagal, lastNode=None):

    if depth == 0:
        # print('starting from: '+str(note))
        new_node = Node(note)
    else:
        new_node = Node(note, lastNode)
    if not new_node.isValid():
        return
    else:
        pass
    if depth + 1 == maxDepth:
        container.append(new_node)
        return
    shift = 5 if plagal else 0
    root = new_node.root
    for i in range(root - shift, root + 12 - shift):
        newNote = Note.diatonicScale(root - shift, i)
        Search(newNote, depth + 1, maxDepth, plagal, new_node)


def SearchCantus(initial, length, plagal):
    step = 0
    Search(initial, step, length, plagal, lastNode=None)


def pruneCantus(cArray, hiIndex, discontinuities, variety, modeRepetitions):
    length = len(cArray)
    hiIndex = 11 - hiIndex
    for i in range(0, length):
        if i > length - 1:
            break
        s = container[i].sequence
        # setBreak = False
        # for k in range(0,11):
        #     if TerminalNode[i].sequence[k] != cTest[k]:
        #         setBreak = True
        #         break
        # if setBreak:print('abc , a+x b+x c+x')
        #     continue
        # else:
        #     print('found')
        if cArray[i].disc > discontinuities:
            # print(1)
            # break
            continue
        if cArray[i].hiIndex > hiIndex:
            # print(2)
            # break
            continue
        if len(Counter(cArray[i].sequence).keys()) < 5:
            # print(3)
            # break
            continue
        if cArray[i].modeRep < 1:
            # print(4)
            # break
            continue

        interval = []
        TerminalNode[i].printNotes()
        # for j in range(0,11):
        #     if j == 0:
        #         continue
        #     interval.append(Note.interval(s[j-1], s[j]))
        print(s)
        print(str(interval) + '\n')


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
    if not newNode.isValid(True, mode):
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
    for i in range(mode - shift, mode + 7 - shift):
        interval = i - cantus[depth + 1]
        print('index'+str(i))
        print('step '+str(depth))
        print('cantus '+str(cantus[depth]))
        print('diatonic interval' + str(Note.diatonic(interval)))
        interval = Note.diatonic(interval) % 12
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
        searchCounter(mode, i, cantus, depth + 1, plagal, newNode)


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


def testCounter(seq, cantus):
    for m in range(0, 11):
        if m == 0:
            cp = Node(seq[0])
            previous = cp
        else:
            cp = Node(seq[m], previous)
            if not cp.isValid(True, cantus[0]+7):
                print('invalid movement from counterpoint '+str(cp.index))
                break
            previous = cp
        if not cp.validateVoice1(cantus):
            print('invalid counter point '+str(cp.index))
            Note.printSequence(cp.sequence, True)
            Note.printSequence(cantus[0:len(cp.sequence)], True)
            Note.printIntervales(cantus[0:len(cp.sequence)], cp.sequence, True)
            break
            # print('validated '+str(seq[m]) + ' at :' + str(cp.index))
    if len(cp.sequence) == 11:
        print('valid counter point')

    return cp
