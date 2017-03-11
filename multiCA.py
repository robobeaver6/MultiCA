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
        child_node0 = caTree.Node("CA0", self._root_node)
        child_node1 = caTree.Node("CA1", self._root_node)
        child_node2 = caTree.Node("CA1-A", child_node1)
        child_node3 = caTree.Node("CA2", self._root_node)
        child_node4 = caTree.Node("CA2-A", child_node3)
        child_node5 = caTree.Node("CA2-B", child_node3)
        child_node6 = caTree.Node("CA3", self._root_node)
        child_node7 = caTree.Node("CA3-A", child_node6)
        child_node8 = caTree.Node("CA3-B", child_node6)
        child_node9 = caTree.Node("CA3-C", child_node6)
        child_node10 = caTree.Node("CA4", self._root_node)
        child_node11 = caTree.Node("CA4-A", child_node10)
        child_node12 = caTree.Node("CA4-B", child_node10)
        child_node13 = caTree.Node("CA4-C", child_node10)
        child_node14 = caTree.Node("CA4-D", child_node10)

        self._model = caTree.TreeModel(self._root_node)
        self._model_list = QtCore.QStringListModel()

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
        self._selectionModel_list = self.lstSubjectAltName.selectionModel()

        self._dataMapper = QtWidgets.QDataWidgetMapper()

        # Button actions
        self.btnManage.clicked.connect(self.on_click_manage)
        self.btnCreateRoot.clicked.connect(self.on_click_create_root)
        self.btnCreateSub.clicked.connect(self.on_click_create_sub)
        self.btnDelete.clicked.connect(self.on_click_delete)
        self.btnAltNameAdd.clicked.connect(self.on_click_alt_name_add)
        self.btnAltNameDel.clicked.connect(self.on_click_alt_name_del)


    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, current, old):
        current = self._proxyModel.mapToSource(current)
        parent = current.parent()
        # Connect up dataMapper to List boxes
        self._dataMapper.setModel(self._proxyModel.sourceModel())
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
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        # Setup Subject Alt Name list view
        self.lstSubjectAltName.setModel(self._model_list)
        self._model_list.setStringList(current.internalPointer().subject_alt_names)
        self._model_list.dataChanged.connect(lambda: self._subject_alt_names_data_changed(current))

    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed_list(self, current, old):
        current = self._proxyModel.mapToSource(current)
        parent = current.parent()
        print('List Selection Changed', current.row())

    @pyqtSlot()
    def _subject_alt_names_data_changed(self, current, *args, **kwargs):
        current.internalPointer().subject_alt_names = self._model_list.stringList()
        print(' Data Changed ', current.internalPointer().name, args, kwargs)




    @pyqtSlot()
    def on_click_manage(self):
        # self.treeView.resizeColumnsToContents()
        file = QtCore.QFile("save.txt")
        file.open(QtCore.QIODevice.WriteOnly)
        # open data stream
        out = QtCore.QDataStream(file)
        # recursively write model item into the datastream
        self.save_item(self._model.root, out)

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

    @pyqtSlot()
    def on_click_alt_name_add(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        node = index.internalPointer()
        if index.isValid():
            name, okPressed = QtWidgets.QInputDialog.getText(self, "Subject Alternate Name", "New Alt Name:", QtWidgets.QLineEdit.Normal, "")
            if okPressed and name != '':
                # self._model_list.beginInsertRows(index.parent(), index.row(), index.row()+1)
                # self._model_list.insertRows(index.row()+1, 1)
                # self._model_list.setData(index.sibling(index.row()+1, 0), name)
                # self._model_list.endInsertRows()
                node.subject_alt_names_add(name)
                self._model_list.setStringList(node.subject_alt_names)


    @pyqtSlot()
    def on_click_alt_name_del(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        node = self._selectionModel.internalPointer()
        print('Delete Subject Alt Name: ')
        node.subject_alt_names_del(index.row())
        self._model_list.setStringList(node.subject_alt_names)

    def save_data(self, item, out):
        # TODO Write data to file
        for i in range(0, item.rowCount()):
            child = item.child(i)
            child.write(out)
            self.save_item(child, out)

    def load_data(self):
        # TODO Restore Data
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsVista")

    window = wndMain()
    window.show()

    sys.exit(app.exec_())
