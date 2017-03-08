from caTree import *
from pytestqt import *
from PyQt5 import QtCore


def test_abstract_item_model(qtmodeltester):

    rootNode = Node("Root Node")
    childNode0 = Node("CA0", rootNode)
    childNode1 = Node("CA1", rootNode)
    childNode2 = Node("CA1-A", childNode1)
    childNode3 = Node("CA2", rootNode)
    childNode4 = Node("CA2-A", childNode3)
    childNode5 = Node("CA2-B", childNode3)
    childNode6 = Node("CA3", rootNode)
    childNode7 = Node("CA3-A", childNode6)
    childNode8 = Node("CA3-B", childNode6)
    childNode9 = Node("CA3-C", childNode6)
    childNode10 = Node("CA4", rootNode)
    childNode11 = Node("CA4-A", childNode10)
    childNode12 = Node("CA4-B", childNode10)
    childNode13 = Node("CA4-C", childNode10)
    childNode14 = Node("CA4-D", childNode10)


    model = TreeModel(rootNode)

    qtmodeltester.check(model)

    proxy_model = QtCore.QSortFilterProxyModel()
    proxy_model.setSourceModel(model)
    qtmodeltester.check(proxy_model)
