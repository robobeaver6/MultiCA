from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import sys
import os
import caTree
import pickle
import crypto

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

        if os.path.exists('data.pkl'):
            self.load_data()

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
        self._proxyModel.sort(0, QtCore.Qt.AscendingOrder)

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
        self.btnGenerate.clicked.connect(self.on_click_generate_cert)

        # Menu Item Clicks
        self.actionSave.triggered.connect(self.save_data)

    def current_node(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        node = index.internalPointer()
        return node

    @pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, current, old):
        # print('selection Changed', current, old)
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
        self._model_list.dataChanged.disconnect()
        if current.internalPointer():
            self._model_list.setStringList(current.internalPointer().subject_alt_names)
        self._model_list.dataChanged.connect(lambda: self._subject_alt_names_data_changed(current))

    @pyqtSlot()
    def _subject_alt_names_data_changed(self, current):
        current.internalPointer().subject_alt_names = self._model_list.stringList()

    def clear_form(self):
        self.treeView.clearSelection()
        elements = [self.leCommonName,
                    self.leCountry,
                    self.leDescription,
                    self.leDomain,
                    self.leEmail,
                    self.leLocality,
                    self.leName,
                    self.leOrgUnit,
                    self.leOrganization,
                    self.leStateOrProvince,
                    self.leUID]
        for widget in elements:
            widget.setText(None)

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


    @pyqtSlot()
    def on_click_manage(self):
        self.treeView.resizeColumnsToContents()


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
                self.treeView.clearSelection()
                self._model.removeRow(index.row(), index.parent())
            self.clear_form()

    @pyqtSlot()
    def on_click_alt_name_add(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        node = index.internalPointer()
        if index.isValid():
            name, okPressed = QtWidgets.QInputDialog.getText(self, "Subject Alternate Name", "New Alt Name:", QtWidgets.QLineEdit.Normal, "")
            if okPressed and name != '':
                node.subject_alt_names_add(name)
                self._model_list.setStringList(node.subject_alt_names)

    @pyqtSlot()
    def on_click_alt_name_del(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        node = index.internalPointer()
        if self.lstSubjectAltName.currentIndex().isValid():
            print('Delete Subject Alt Name: ', node.name)
            node.subject_alt_names_del(self.lstSubjectAltName.currentIndex().row())
            self._model_list.setStringList(node.subject_alt_names)

    @pyqtSlot()
    def on_click_generate_cert(self):
        node = self.current_node()
        node.private_key = crypto.create_private_key(ec.SECP256R1, 'PassPhrase')
        if node.parent == self._root_node:
            node.certificate = crypto.create_root_certificate(node, node.private_key)
        else:
            node.cert_sign_req = crypto.create_cert_sign_req(node, node.private_key)


        print(node.private_key)

    @pyqtSlot()
    def save_data(self):
        with open('data.pkl', 'wb') as file_out:
            pickle.dump(self._root_node, file_out, protocol=pickle.HIGHEST_PROTOCOL)
            print('Data Saved')

    def load_data(self):
        with open('data.pkl', 'rb') as file_in:
            self._root_node = pickle.load(file_in)
            print('Data Loaded')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsVista")

    window = wndMain()
    window.show()

    sys.exit(app.exec_())
