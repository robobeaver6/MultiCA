from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import sys
import caTree

base, form = uic.loadUiType("MultiCA.ui")
baseNewCA, formNewCA = uic.loadUiType("NewCA_Dialog.ui")

class wndNewCA(baseNewCA, formNewCA):
    def __init__(self, parent=None, name='Untitled', description=None):
        super(baseNewCA, self).__init__(parent)
        self.setupUi(self)

        # self.buttonBox.accepted.connect(self.on_click_create_root)

        @pyqtSlot()
        def on_click_create_root(self):
            print('OK Pressed')
            # index = self._selectionModel.currentIndex()
            # index = self._proxyModel.mapToSource(index)
            # while index.isValid():
            #     # print(index.internalPointer().name)
            #     index = index.parent()
            # end_of_list = self._model._rootNode.child_count
            # self._model.insertRow(end_of_list, index)

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

        self.treeView.setModel(self._proxyModel)
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
        self.btnDelete.clicked.connect(self.on_click_delete)

    def __connect_data_mapper(self):
        self._dataMapper.setModel(self._proxyModel.sourceModel())
        # self._dataMapper.setModel(self._model)
        self._dataMapper.addMapping(self.leName, 0)
        self._dataMapper.addMapping(self.leDescription, 1)
        self._dataMapper.addMapping(self.leUID, 2)
        self._dataMapper.addMapping(self.leCommonName, 3)
        self._dataMapper.addMapping(self.leOrgUnit, 4)
        self._dataMapper.addMapping(self.leOrganization, 5)
        self._dataMapper.addMapping(self.leLocality, 6)
        self._dataMapper.addMapping(self.leStateOrProvince, 7)
        self._dataMapper.addMapping(self.leCountry, 8)
        self._dataMapper.addMapping(self.leEmail, 9)
        self._dataMapper.addMapping(self.leDomain, 10)

    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, current, old):
        current = self._proxyModel.mapToSource(current)
        parent = current.parent()
        self.__connect_data_mapper()
        self._dataMapper.addMapping(self.leName, 0)
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)

    @pyqtSlot()
    def on_click_manage(self):
        self.treeView.resizeColumnsToContents()

    @pyqtSlot()
    def on_click_create_root(self):
        name, okPressed = QtWidgets.QInputDialog.getText(self, "New CA", "CA Name:", QtWidgets.QLineEdit.Normal, "")
        if okPressed and name != '':
            index = self._selectionModel.currentIndex()
            index = self._proxyModel.mapToSource(index)
            while index.isValid():
                index = index.parent()
            end_of_list = self._model._rootNode.child_count
            self._model.insertRow(end_of_list, index, name=name)

    @pyqtSlot()
    def on_click_create_sub(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        if index.isValid():
            name, okPressed = QtWidgets.QInputDialog.getText(self, "New Sub CA", "Sub CA Name:",
                                                             QtWidgets.QLineEdit.Normal, "")
            if okPressed and name != '':
                end_of_list = index.internalPointer().child_count
                self._model.insertRow(end_of_list, index, name=name)

    def on_click_delete(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        if index.isValid():
            node = index.internalPointer()
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
            msg.setText("!!!Delete CA!!!")
            msg.setInformativeText("This will delete {}, {} Sub CA's and all associated Keys".format(node.name,
                                                                                                     node.child_count))
            msg.setWindowTitle("DELETE CA")
            return_val = msg.exec()
            if return_val == QtWidgets.QMessageBox.Ok:
                self._model.removeRow(index.row(), index.parent())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsVista")

    window = wndMain()
    window.show()

    sys.exit(app.exec_())
