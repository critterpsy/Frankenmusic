import json
from json import JSONEncoder


class SNode:

    def __init__(self, value=1, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        print(parent)
        if parent is not None:
            self.parent.children.append(self)

    def toJson(self):
        serialized = json.dumps(self, indent=4, cls=TreeEncoder)
        return serialized


# subclass JSONEncoder
class TreeEncoder(JSONEncoder):
    def default(self, o):
        attrs = o.__dict__
        print(o)
        if attrs['parent'] is not None:
            attrs['parent'] = o.parent.value
        return attrs


def serialize_node(node, reverse=False):
    s = node.sequence.copy()
    if reverse:
        s.reverse()
    length = len(node)
    s_node = SNode(s[0])
    for i in range(1, length):
        s_node = SNode(s[i], s_node)


if __name__ == '__main__':
    a = SNode()
    b = SNode(parent=a)
    c = SNode(parent=b)
    # a_json = json.dumps(a, indent=4, cls=TreeEncoder)
    print(a.toJson())
