from caTree import *
from pytestqt import *


def test_abstract_item_model(qtmodeltester):

    rootNode = Node("Root Node")
    childNode1 = Node("CA1", rootNode)
    childNode2 = Node("CA1-A", childNode1)
    childNode3 = Node("CA1-B", childNode1)
    childNode4 = Node("CA2", rootNode)
    childNode5 = Node("CA2-A", childNode4)
    childNode6 = Node("CA2-B", childNode4)
    childNode7 = Node("CA3", rootNode)
    childNode8 = Node("CA3-A", childNode7)
    childNode9 = Node("CA3-B", childNode7)
    childNode10 = Node("CA3-C", childNode7)
    childNode11 = Node("CA4", rootNode)
    childNode12 = Node("CA4-A", childNode11)
    childNode13 = Node("CA4-B", childNode11)
    childNode14 = Node("CA4-C", childNode11)
    childNode15 = Node("CA4-D", childNode11)

    model = TreeModel(rootNode)

    qtmodeltester.check(model)

    print(childNode1.name())
