import json
from json import JSONEncoder


class TreeNode:

    def __init__(self, value=1, parent=None):
        self.value = value
        self.parent = parent
        self.children = []

        if parent is not None:
            self.parent.children.append(self)


# subclass JSONEncoder
class TreeEncoder(JSONEncoder):
    def default(self, o):
        attrs = o.__dict__
        if attrs['parent'] is not None:
            attrs['parent'] = o.parent.value
        return attrs


if __name__ == '__main__':
    a = TreeNode()
    b = TreeNode(parent=a)
    a_json = json.dumps(a, indent=4, cls=TreeEncoder)
    a_json
