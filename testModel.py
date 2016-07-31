from caTree import *
from pytestqt import *

def test_abstract_item_model(qtmodeltester):

    rootNode = Node("Root Node")
    childNode1 = Node("CA1", rootNode)
    childNode2 = Node("CA1-A", childNode1)
    childNode3 = Node("CA1-B", childNode2)
    childNode4 = Node("CA2", rootNode)
    childNode5 = Node("CA2-A", childNode4)
    childNode6 = Node("CA2-B", childNode5)

    model = TreeModel(rootNode)

    qtmodeltester.check(model)

    print (childNode1.name())