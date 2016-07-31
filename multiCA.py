from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import sys
import caTree

base, form = uic.loadUiType("MultiCA.ui")

class wndMain(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)



        rootNode = caTree.Node("Root Node")
        childNode1 = caTree.Node("CA1", rootNode)
        childNode2 = caTree.Node("CA1-A", childNode1)
        childNode3 = caTree.Node("CA1-B", childNode1)
        childNode4 = caTree.Node("CA2", rootNode)
        childNode5 = caTree.Node("CA2-A", childNode4)
        childNode6 = caTree.Node("CA2-B", childNode4)
        childNode7 = caTree.Node("CA2-A-1", childNode5)
        childNode8 = caTree.Node("CA3", rootNode)
        childNode9 = caTree.Node("CA4", rootNode)

        self._model = caTree.TreeModel(rootNode)


        self.treeView.setModel(self._model)
        self._selectionModel = self.treeView.selectionModel()


        self._dataMapper = QtWidgets.QDataWidgetMapper()
        self._dataMapper.setModel(self._model)
        self._dataMapper.addMapping(self.leName, 0)
        self._dataMapper.addMapping(self.leUID, 1)
        #self._dataMapper.toFirst()
        print (self._dataMapper)

        self.leName.editingFinished.connect(self.test)
        self.btnManage.clicked.connect(self.on_click)
        self._selectionModel.currentChanged.connect(self.setSelection)

    def test(self):
        #node = self.treeView.sel
        #print (node)
        #self._model.dataChanged()
        pass

    @pyqtSlot()
    def on_click(self):
        selModel = self.treeView.selectionModel()
        index = selModel.selectedRows()[0]
        node = self._model.getNode(index)
        print (node.name())
        self.leName.setText(node.name())

    @pyqtSlot()
    def selChanged(self):
        index = self._selectionModel.selectedRows()[0]
        node = self._model.getNode(index)
        print(node.name())
        #self.leName.setText(node.name())

    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def setSelection(self, current, old):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)

        self._dataMapper.setCurrentModelIndex(current)
        node = self._model.getNode(current)
        print ("Changed: {}".format(node.name()))

class testSignal(QObject):
    trigger = pyqtSignal()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsVista")

    window = wndMain()
    window.show()


    sys.exit(app.exec_())