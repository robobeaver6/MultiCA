from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import sys
import caTree

base, form = uic.loadUiType("MultiCA.ui")


class wndMain(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self._dataMapper = QtWidgets.QDataWidgetMapper()

        self.setupUi(self)

        self._root_node = caTree.Node("Root Node")
        childNode0 = caTree.Node("CA0", self._root_node)
        childNode1 = caTree.Node("CA1", self._root_node)
        childNode2 = caTree.Node("CA1-A", childNode1)
        childNode3 = caTree.Node("CA2", self._root_node)
        childNode4 = caTree.Node("CA2-A", childNode3)
        childNode5 = caTree.Node("CA2-B", childNode3)
        childNode6 = caTree.Node("CA3", self._root_node)
        childNode7 = caTree.Node("CA3-A", childNode6)
        childNode8 = caTree.Node("CA3-B", childNode6)
        childNode9 = caTree.Node("CA3-C", childNode6)
        childNode10 = caTree.Node("CA4", self._root_node)
        childNode11 = caTree.Node("CA4-A", childNode10)
        childNode12 = caTree.Node("CA4-B", childNode10)
        childNode13 = caTree.Node("CA4-C", childNode10)
        childNode14 = caTree.Node("CA4-D", childNode10)

        self._model = caTree.TreeModel(self._root_node)

        self.treeView.setModel(self._model)

        # Setup selection model for data mapper
        self._selectionModel = self.treeView.selectionModel()
        self._selectionModel.currentChanged.connect(self.selection_changed)

        # self.leName.editingFinished.connect(self.test_function)

        # Button actions
        self.btnManage.clicked.connect(self.on_click_manage)
        self.btnCreateRoot.clicked.connect(self.on_click_create_root)
        self.btnCreateSub.clicked.connect(self.on_click_create_sub)

    def __connect_data_mapper(self):
        # Setup data maper for GUI editing and updates
        self._dataMapper.setModel(self._model)
        self._dataMapper.addMapping(self.leName, 0)
        self._dataMapper.addMapping(self.leDescription, 1)
        self._dataMapper.addMapping(self.leUID, 2)
        # self._dataMapper.toFirst()

    def __clear_form(self):
        self.leName.setText(None)
        self.leDescription.setText(None)
        self.leUID.setText(None)

    @pyqtSlot()
    def on_click_manage(self):
        sel_model = self.treeView.selectionModel()
        index = sel_model.selectedRows()[0]
        node = self._model.getNode(index)
        print(node.name())
        self.leName.setText(node.name())

    @pyqtSlot()
    def on_click_create_root(self):
        # Clear existing data and connections
        self.treeView.clearSelection()
        self._dataMapper.clearMapping()
        self.__clear_form()

        # Create New Node
        # new_node = caTree.Node("New Node", rootNode)
        root_node_index = self._model.createIndex(0, 0, self._root_node)
        # root_child_count = self._root_node.childCount()
        root_child_count = 1
        self._model.insertRow(root_child_count - 1, root_node_index)

        #self.TreeView.setSelection()



    @pyqtSlot()
    def on_click_create_sub(self):
        sel_model = self.treeView.selectionModel()
        index = sel_model.selectedRows()[0]
        node = self._model.getNode(index)
        print (node.name())
        self.leName.setText(node.name())

    @pyqtSlot()
    def selection_changed(self):
        index = self._selectionModel.selectedRows()[0]
        node = self._model.getNode(index)
        print(node.name())
        # self.leName.setText(node.name())

    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, current, old):
        parent = current.parent()
        self.__connect_data_mapper()
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