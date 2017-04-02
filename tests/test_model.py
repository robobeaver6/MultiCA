from caTree import Node, TreeModel
from pytestqt import *
from PyQt5 import QtCore

def build_tree(width=1, depth=1, parent=None):
    if width < 0:
        raise ValueError
    if depth < 0:
        raise ValueError

    for n in range(width):
        if depth > 1:
            child = Node('Child-{}-{}'.format(depth, n), parent)
            # print('Create {}'.format(child.name))
            build_tree(width, depth - 1, child)
        else:
            child = Node('Child-{}-{}'.format(depth, n), parent)
            # print('Create {}'.format(child.name))

    return parent

def test_build_tree():
    print('Test build_tree 0,0')
    root_node = build_tree(0,0, Node('root'))
    assert root_node.child_count == 0
    print('test buid_tree width 5')
    root_node2 = build_tree(5,1, Node('root'))
    assert root_node2.child_count == 5
    print('Test build_tree Depth 3')
    root_node3 = build_tree(1, 3, Node('RootNode'))
    assert root_node3.child_count == 1
    assert root_node3.child(0).child_count == 1
    assert root_node3.child(0).child(0).child_count == 1
    assert root_node3.child(0).child(0).child(0).child_count == 0


def test_abstract_item_model(qtmodeltester):
    rootNode = build_tree(3,2, Node('Root'))
    model = TreeModel(rootNode)
    qtmodeltester.check(model)
    proxy_model = QtCore.QSortFilterProxyModel()
    proxy_model.setSourceModel(model)
    qtmodeltester.check(proxy_model)


def test_add_child():
    root_node = Node('Root')
    child_node = Node('Child 0', root_node)

    assert root_node.child(0) == child_node

def test_insert_child():
    root_node = build_tree(3, 3, Node('Root Insert Child Test'))
    new_child = Node('TestChild')
    insert_node = root_node.child(1).child(1)
    assert insert_node.insertChild(1, new_child)
    assert new_child.parent == insert_node
    assert insert_node.child(1) == new_child

def test_remove_child():
    root_node = build_tree(3, 2, Node('root'))
    node_before = root_node.child(0)
    node_to_remove = root_node.child(1)
    node_after = root_node.child(2)
    root_node.removeChild(1)
    assert root_node.child_count == 2
    assert root_node.child(0) == node_before
    assert root_node.child(1) == node_after

def test_node_child():
    root_node = build_tree(3, 2, Node('root'))
    assert root_node.child(1) == root_node._children[1]
