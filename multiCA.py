from PyQt5 import uic, QtWidgets, QtCore, QtGui, QtTest
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import sys
import os
import caTree
import pickle
import logging
import crypto
from pprint import pprint
from PyQt5.QtCore import qInstallMessageHandler, QMessageLogContext
from PyQt5.Qt import QtMsgType
import utils.debug as debug


def myQtMsgHandler(msg_type, msg_log_context, msg_string):
    # Convert Qt msg type to logging level
    log_level = [logging.DEBUG,
                 logging.WARN,
                 logging.ERROR,
                 logging.FATAL][int(msg_type)]
    logging.log(logging.DEBUG,
                'Qt context file is ' + msg_log_context.file
                )
    logging.log(logging.DEBUG,
                'Qt context line and function: {0} {1}'.format(
                    msg_log_context.line, msg_log_context.function)
                )
    logging.log(log_level, 'Qt message: ' + msg_string)


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
        self.btnCreateEndEntiy.clicked.connect(self.on_click_create_end_entity)
        self.btnDelete.clicked.connect(self.on_click_delete)
        self.btnAltNameAdd.clicked.connect(self.on_click_alt_name_add)
        self.btnAltNameDel.clicked.connect(self.on_click_alt_name_del)
        self.btnGenKey.clicked.connect(self.on_click_generate_key)
        self.btnGenCSR.clicked.connect(self.on_click_generate_csr)
        self.btnGenCert.clicked.connect(self.on_click_generate_certificate)


        # Menu Item Clicks
        self.actionSave.triggered.connect(self.save_data)

        # Check Box clicks
        # self.CA.stateChanged.connect(self.cb_basic_constraint_ca_changed)
        # self._spy = QtTest.QSignalSpy(self.contentCommitment.toggled)
        # debug.log_signals(self.contentCommitment)
        # debug.log_signals(self.contentCommitment)
        self.CA.stateChanged.connect(self.cb_stateChanged_basic_constraint_ca)
        self.digitalSignature.stateChanged.connect(self.cb_stateChanged_digital_signature)
        self.contentCommitment.stateChanged.connect(self.cb_stateChanged_content_commitment)
        self.keyEncipherment.stateChanged.connect(self.cb_stateChanged_key_encipherment)
        self.dataEncipherment.stateChanged.connect(self.cb_stateChanged_data_encipherment)
        self.keyAgreement.stateChanged.connect(self.cb_stateChanged_key_agreement)
        self.keyCertSign.stateChanged.connect(self.cb_stateChanged_key_cert_sign)
        self.cRLSign.stateChanged.connect(self.cb_stateChanged_crl_sign)
        self.encipherOnly.stateChanged.connect(self.cb_stateChanged_encipher_only)
        self.decipherOnly.stateChanged.connect(self.cb_stateChanged_decipher_only)


        # RFC5759 Compliance Radio Buttons
        # self.rbCertAuth.setChecked(True)
        # self.rbKeyEstablishment.toggled.connect(lambda: self.cb_basic_constraint_ca_changed(rfc_usage='KeyEstablishment'))
        # self.rbDigitalSig.toggled.connect(lambda: self.cb_basic_constraint_ca_changed(rfc_usage='DigitalSignature'))
        # self.rbNonCompliant.toggled.connect(lambda: self.cb_basic_constraint_ca_changed(rfc_usage='NonCompliant'))

        # Set Validators
        reg_ex = QtCore.QRegExp("[A-Z]{2}")
        input_validator = QtGui.QRegExpValidator(reg_ex, self.leCountry)
        self.leCountry.setValidator(input_validator)

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
        node = current.internalPointer()
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
        # self._dataMapper.addMapping(self.CA, 11)
        # self._dataMapper.addMapping(self.digitalSignature, 12)
        # self._dataMapper.addMapping(self.contentCommitment, 13)
        # self._dataMapper.addMapping(self.keyEncipherment, 14)
        # self._dataMapper.addMapping(self.dataEncipherment, 15)
        # self._dataMapper.addMapping(self.keyAgreement, 16)
        # self._dataMapper.addMapping(self.keyCertSign, 17)
        # self._dataMapper.addMapping(self.cRLSign, 18)
        # self._dataMapper.addMapping(self.encipherOnly, 19)
        # self._dataMapper.addMapping(self.decipherOnly, 20)
        self._dataMapper.addMapping(self.PrivateKey, 21)
        self._dataMapper.addMapping(self.CertSignReq, 22)
        self._dataMapper.addMapping(self.Certificate, 23)
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        # Setup Subject Alt Name list view
        self.lstSubjectAltName.setModel(self._model_list)
        self._model_list.dataChanged.disconnect()
        if current.internalPointer():
            self._model_list.setStringList(current.internalPointer().subject_alt_names)
        self._model_list.dataChanged.connect(lambda: self._subject_alt_names_data_changed(current))

        self.get_basic_constraints(node)
        # Radio Buttons to control Key usage Extensions
        if self.CA.isChecked():
            pass
        else:
            if node.rfc_usage == 'KeyEstablishment':
                self.rbKeyEstablishment.setChecked(True)
            elif node.rfc_usage == 'DigitalSignature':
                self.rbDigitalSig.setChecked(True)
            elif node.rfc_usage == 'NonCompliant':
                self.rbNonCompliant.setChecked(True)

        # Make Key, CSR and Cert window read only if cert data already generated
        if node.key.private_key_exists:
            self.PrivateKey.setReadOnly(True)
        else:
            self.PrivateKey.setReadOnly(False)
        if node.key.csr is None:
            self.CertSignReq.setReadOnly(False)
        else:
            self.CertSignReq.setReadOnly(True)
        if node.key.certificate is None:
            self.Certificate.setReadOnly(False)
        else:
            self.Certificate.setReadOnly(True)

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

    # Button Functions

    @pyqtSlot()
    def on_click_create_root(self):
        name, okPressed = QtWidgets.QInputDialog.getText(self, "New CA", "CA Name:", QtWidgets.QLineEdit.Normal, "")
        if okPressed and name != '':
            index = self._selectionModel.currentIndex()
            index = self._proxyModel.mapToSource(index)
            while index.isValid():
                index = index.parent()
            end_of_list = self._model._rootNode.child_count
            self._model.insertRow(end_of_list, index, name=name, ca=True)
        self.treeView.resizeColumnToContents(0)

    @pyqtSlot()
    def on_click_create_sub(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        if index.isValid():
            name, okPressed = QtWidgets.QInputDialog.getText(self, "New Sub CA", "Sub CA Name:",
                                                             QtWidgets.QLineEdit.Normal, "")
            if okPressed and name != '':
                end_of_list = index.internalPointer().child_count
                self._model.insertRow(end_of_list, index, name=name, ca=True)
        self.treeView.resizeColumnToContents(0)

    @pyqtSlot()
    def on_click_create_end_entity(self):
        index = self._selectionModel.currentIndex()
        index = self._proxyModel.mapToSource(index)
        if index.isValid():
            name, okPressed = QtWidgets.QInputDialog.getText(self, "End Entity", "End Entity Name:",
                                                             QtWidgets.QLineEdit.Normal, "")
            if okPressed and name != '':
                end_of_list = index.internalPointer().child_count
                self._model.insertRow(end_of_list, index, name=name, ca=False)
        self.treeView.resizeColumnToContents(0)
        # TODO: Ensure not CA.
        # TODO: Make fields non editable after cert creation
        # TODO: impliment date fields
        # TODO: Key Usage

    @pyqtSlot()
    def on_click_manage(self):
        # node = self.current_node()
        # if self.contentCommitment.isChecked():
        #     self.contentCommitment.setChecked(False)
        # else:
        #     self.contentCommitment.setChecked(True)
        self._dataMapper.submit()
        # print(self._spy)


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
    def on_click_generate_key(self):
        index = self._selectionModel.currentIndex()
        # index = self._proxyModel.mapToSource(index)
        node = self.current_node()
        pass_phrase = self.get_pass_phrase(node)
        node.key.create_private_key(int(self.KeyLength.currentText()), pass_phrase)
        self.PrivateKey.setReadOnly(True)


    def on_click_generate_certificate(self):
        node = self.current_node()
        # pass_phrase = self.get_pass_phrase(node)
        if node.key.certificate_exists:
            return
        if node.key.private_key_exists:
            if node.parent == self._root_node:
                node.key.create_root_certificate(self.get_pass_phrase(node))
                return
            elif not node.key.csr_exists:
                node.key.create_cert_sign_req(self.get_pass_phrase(node))

        if node.key.csr_exists and node.parent.key.ready:
            node.key.certificate = node.parent.key.sign_csr(node.key.csr, self.get_pass_phrase(node.parent))


        # if not node.key.ready:
        #     if node.parent == self._root_node:
        #         node.key.create_root_certificate(pass_phrase)
        #         break
        #     if not node.key.csr_exists:
        #         node.key.create_cert_sign_req(pass_phrase)
        #
        #     node.key.certificate = node.parent.key.sign_csr(node.key.csr, self.get_pass_phrase(node.parent))


    def on_click_generate_csr(self):
        node = self.current_node()
        pass_phrase = self.get_pass_phrase(node)
        if node.parent == self._root_node:
            node.key.create_root_certificate(pass_phrase)
        else:
            if node.parent.key.ready:
                node.key.create_cert_sign_req(pass_phrase)
                # node.key.certificate = node.parent.key.sign_csr(node.key.csr, self.get_pass_phrase(node.parent))
                # print(node.key)

    @pyqtSlot()
    def cb_basic_constraint_ca_changed(self, *args, **kwargs):
        node = self.current_node()
        if self.CA.isChecked():
            self.rfcUsage.setEnabled(False)
            node.rfc_usage = 'CertificateAuth'
            # self.digitalSignature.setChecked(False)
            # self.contentCommitment.setChecked(False)
            self.keyEncipherment.setChecked(False)
            self.dataEncipherment.setChecked(False)
            self.dataEncipherment.setChecked(False)
            self.keyAgreement.setChecked(False)
            self.keyCertSign.setChecked(True)
            self.cRLSign.setChecked(True)
            self.encipherOnly.setChecked(False)
            self.decipherOnly.setChecked(False)
            self.rfcUsage.setEnabled(False)
            self.digitalSignature.setEnabled(True)
            self.contentCommitment.setEnabled(True)
            self.keyEncipherment.setEnabled(False)
            self.dataEncipherment.setEnabled(False)
            self.keyAgreement.setEnabled(False)
            self.keyCertSign.setEnabled(False)
            self.cRLSign.setEnabled(False)
            self.encipherOnly.setEnabled(False)
            self.decipherOnly.setEnabled(False)
            self._dataMapper.submit()

        else:
            self.rfcUsage.setEnabled(True)
            self.digitalSignature.setEnabled(True)
            self.contentCommitment.setEnabled(True)
            self.keyEncipherment.setEnabled(True)
            self.dataEncipherment.setEnabled(True)
            self.keyAgreement.setEnabled(True)
            self.keyCertSign.setEnabled(False)
            self.cRLSign.setEnabled(False)
            self.encipherOnly.setEnabled(True)
            self.decipherOnly.setEnabled(True)

            self.keyCertSign.setChecked(False)
            self.cRLSign.setChecked(False)
            self._dataMapper.submit()
            # self.rfcUsage.setEnabled(True)
            # if 'rfc_usage' not in kwargs.keys():
            #     kwargs['rfc_usage'] = node.rfc_usage
            #
            # if kwargs['rfc_usage'] == 'DigitalSignature':
            #     print('Digital Sig')
            #     node.rfc_usage = 'DigitalSignature'
            #     self.digitalSignature.setChecked(True)
            #     self.digitalSignature.setEnabled(False)
            #     # self.contentCommitment.setChecked(False)
            #     self.contentCommitment.setEnabled(True)
            #     self.keyEncipherment.setChecked(False)
            #     self.keyEncipherment.setEnabled(False)
            #     self.dataEncipherment.setChecked(False)
            #     self.dataEncipherment.setEnabled(False)
            #     self.keyAgreement.setChecked(False)
            #     self.keyAgreement.setEnabled(False)
            #     self.keyCertSign.setChecked(False)
            #     self.keyCertSign.setEnabled(False)
            #     self.cRLSign.setChecked(False)
            #     self.cRLSign.setEnabled(False)
            #     self.encipherOnly.setChecked(False)
            #     self.encipherOnly.setEnabled(False)
            #     self.decipherOnly.setChecked(False)
            #     self.decipherOnly.setEnabled(False)
            # elif kwargs['rfc_usage'] == 'KeyEstablishment':
            #     print('Key Establishment')
            #     node.rfc_usage = 'KeyEstablishment'
            #     self.digitalSignature.setChecked(False)
            #     self.digitalSignature.setEnabled(False)
            #     self.contentCommitment.setChecked(False)
            #     self.contentCommitment.setEnabled(False)
            #     self.keyEncipherment.setChecked(False)
            #     self.keyEncipherment.setEnabled(False)
            #     self.dataEncipherment.setChecked(False)
            #     self.dataEncipherment.setEnabled(False)
            #     self.keyAgreement.setChecked(True)
            #     self.keyAgreement.setEnabled(False)
            #     self.keyCertSign.setChecked(False)
            #     self.keyCertSign.setEnabled(False)
            #     self.cRLSign.setChecked(False)
            #     self.cRLSign.setEnabled(False)
            #     # self.encipherOnly.setChecked(True)
            #     self.encipherOnly.setEnabled(True)
            #     # self.decipherOnly.setChecked(False)
            #     self.decipherOnly.setEnabled(True)
            # elif kwargs['rfc_usage'] == 'NonCompliant':
            #     print('Non Compliant')
            #     node.rfc_usage = 'NonCompliant'
            #     # self.digitalSignature.setChecked(True)
            #     self.digitalSignature.setEnabled(True)
            #     # self.contentCommitment.setChecked(False)
            #     self.contentCommitment.setEnabled(True)
            #     # self.keyEncipherment.setChecked(False)
            #     self.keyEncipherment.setEnabled(True)
            #     # self.dataEncipherment.setChecked(False)
            #     self.dataEncipherment.setEnabled(True)
            #     # self.keyAgreement.setChecked(False)
            #     self.keyAgreement.setEnabled(True)
            #     self.keyCertSign.setChecked(False)
            #     self.keyCertSign.setEnabled(False)
            #     self.cRLSign.setChecked(False)
            #     self.cRLSign.setEnabled(False)
            #     # self.encipherOnly.setChecked(False)
            #     self.encipherOnly.setEnabled(True)
            #     # self.decipherOnly.setChecked(False)
            #     self.decipherOnly.setEnabled(True)



    @pyqtSlot()
    def cb_stateChanged_basic_constraint_ca(self):
        node = self.current_node()
        node.basic_constraint_ca = self.CA.isChecked()
        if self.CA.isChecked():
            self.keyEncipherment.setChecked(False)
            self.dataEncipherment.setChecked(False)
            self.dataEncipherment.setChecked(False)
            self.keyAgreement.setChecked(False)
            self.keyCertSign.setChecked(True)
            self.cRLSign.setChecked(True)
            self.encipherOnly.setChecked(False)
            self.decipherOnly.setChecked(False)
            self.rfcUsage.setEnabled(False)
            self.digitalSignature.setEnabled(True)
            self.contentCommitment.setEnabled(True)
            self.keyEncipherment.setEnabled(False)
            self.dataEncipherment.setEnabled(False)
            self.keyAgreement.setEnabled(False)
            self.keyCertSign.setEnabled(False)
            self.cRLSign.setEnabled(False)
            self.encipherOnly.setEnabled(False)
            self.decipherOnly.setEnabled(False)
        else:
            # self.keyEncipherment.setChecked(False)
            # self.dataEncipherment.setChecked(False)
            # self.dataEncipherment.setChecked(False)
            # self.keyAgreement.setChecked(False)
            self.keyCertSign.setChecked(False)
            self.cRLSign.setChecked(False)
            # self.encipherOnly.setChecked(False)
            # self.decipherOnly.setChecked(False)
            self.rfcUsage.setEnabled(True)
            self.digitalSignature.setEnabled(True)
            self.contentCommitment.setEnabled(True)
            self.keyEncipherment.setEnabled(True)
            self.dataEncipherment.setEnabled(True)
            self.keyAgreement.setEnabled(True)
            self.keyCertSign.setEnabled(False)
            self.cRLSign.setEnabled(False)
            self.encipherOnly.setEnabled(True)
            self.decipherOnly.setEnabled(True)

    @pyqtSlot()
    def cb_stateChanged_digital_signature(self):
        node = self.current_node()
        node.digital_signature = self.digitalSignature.isChecked()

    @pyqtSlot()
    def cb_stateChanged_content_commitment(self):
        node = self.current_node()
        node.content_commitment = self.contentCommitment.isChecked()

    @pyqtSlot()
    def cb_stateChanged_key_encipherment(self):
        node = self.current_node()
        node.key_encipherment = self.keyEncipherment.isChecked()

    @pyqtSlot()
    def cb_stateChanged_data_encipherment(self):
        node = self.current_node()
        node.key_encipherment = self.keyEncipherment.isChecked()

    @pyqtSlot()
    def cb_stateChanged_key_agreement(self):
        node = self.current_node()
        node.key_agreement = self.keyAgreement.isChecked()

    @pyqtSlot()
    def cb_stateChanged_key_cert_sign(self):
        node = self.current_node()
        node.key_cert_sign = self.keyCertSign.isChecked()

    @pyqtSlot()
    def cb_stateChanged_crl_sign(self):
        node = self.current_node()
        node.crl_sign = self.cRLSign.isChecked()

    @pyqtSlot()
    def cb_stateChanged_encipher_only(self):
        node = self.current_node()
        node.encipher_only = self.encipherOnly.isChecked()

    @pyqtSlot()
    def cb_stateChanged_decipher_only(self):
        node = self.current_node()
        node.decipher_only = self.decipherOnly.isChecked()

    
    def get_basic_constraints(self, node):
        self.CA.setChecked(node.basic_constraint_ca)
        self.digitalSignature.setChecked(node.digital_signature)
        self.contentCommitment.setChecked(node.content_commitment)
        self.keyEncipherment.setChecked(node.key_encipherment)
        self.dataEncipherment.setChecked(node.data_encipherment)
        self.keyAgreement.setChecked(node.key_agreement)
        self.keyCertSign.setChecked(node.key_cert_sign)
        self.cRLSign.setChecked(node.crl_sign)
        self.encipherOnly.setChecked(node.encipher_only)
        self.decipherOnly.setChecked(node.decipher_only)

    def get_pass_phrase(self, node):
        private_key = None
        pass_phrase = None
        ok_pressed = False
        while not isinstance(private_key, ec.EllipticCurvePrivateKey):
            pass_phrase, ok_pressed = QtWidgets.QInputDialog.getText(self,
                                                                     "Pass Phrase",
                                                                     "Pass Phrase for {}:".format(node.name),
                                                                     QtWidgets.QLineEdit.Normal)
            # TODO: Fix cancel button still generates cert
            if pass_phrase == '':
                pass_phrase = None
            if ok_pressed:
                # check if password was valid if node key exists
                if node.key.private_key_exists:
                    private_key = node.key.private_key(pass_phrase)
                else:
                    return pass_phrase
            else:
                break
        return pass_phrase

    @pyqtSlot()
    def save_data(self):
        with open('data.pkl', 'wb') as file_out:
            pickle.dump(self._root_node, file_out, protocol=pickle.HIGHEST_PROTOCOL)
            print('Data Saved')

    def load_data(self):
        if os.path.exists('data.pkl'):
            try:
                with open('data.pkl', 'rb') as file_in:
                    self._root_node = pickle.load(file_in)
                    print('Data Loaded')
            except EOFError as e:
                logging.error('Failed to Load' + e)
                print(e)


    def debug_key_usage(self):
        node = self.current_node()
        output = []
        for key, value in node.key_usage.items():
            output.append('{} - {}'.format(key, value))
        pprint(output)

if __name__ == "__main__":

    logging.basicConfig(filename='logfile.txt', level=logging.DEBUG)
    logging.info('--------- New Session Started ---------')
    qInstallMessageHandler(myQtMsgHandler)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("windowsVista")

    window = wndMain()
    window.show()

    sys.exit(app.exec_())
