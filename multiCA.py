from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import sys
import caTree

base, form = uic.loadUiType("MultiCA.ui")


class wndMain(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
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

        # Proxy Model for sorting
        """VIEW <------> PROXY MODEL <------> DATA MODEL"""
        self._proxyModel = QtCore.QSortFilterProxyModel()
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # self.treeView.setModel(self._proxyModel.sourceModel())
        self.treeView.setModel(self._proxyModel)
        # self.treeView.setModel(self._model)
        self.treeView.expandAll()
        self.treeView.setSortingEnabled(True)

        # Setup selection model for data mapper
        self._selectionModel = self.treeView.selectionModel()
        self._selectionModel.currentChanged.connect(self.selection_changed)

        self._dataMapper = QtWidgets.QDataWidgetMapper()

        # Button actions
        self.btnManage.clicked.connect(self.on_click_manage)
        self.btnCreateRoot.clicked.connect(self.on_click_create_root)
        self.btnCreateSub.clicked.connect(self.on_click_create_sub)

    def __connect_data_mapper(self):
        pass
        # Setup data mapper for GUI editing and updates
        self._dataMapper.setModel(self._proxyModel.sourceModel())
        # self._dataMapper.setModel(self._proxyModel)
        self._dataMapper.setModel(self._model)
        self._dataMapper.addMapping(self.leName, 0)
        self._dataMapper.addMapping(self.leDescription, 1)
        self._dataMapper.addMapping(self.leUID, 2)

    def __clear_form(self):
        self.leName.setText(None)
        self.leDescription.setText(None)
        self.leUID.setText(None)

    @pyqtSlot()
    def on_click_manage(self):
        pass

    @pyqtSlot()
    def on_click_create_root(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        while index.isValid():
            # print(index.internalPointer().name)
            index = index.parent()
        end_of_list = self._model._rootNode.child_count
        self._model.insertRow(end_of_list, index)

    @pyqtSlot()
    def on_click_create_sub(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        end_of_list = index.internalPointer().child_count
        self._model.insertRow(end_of_list, index)

    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, current, old):
        current = self._proxyModel.mapToSource(current)
        parent = current.parent()
        self.__connect_data_mapper()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsVista")

    window = wndMain()
    window.show()

    sys.exit(app.exec_())
