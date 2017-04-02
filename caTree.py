import re
from PyQt5 import QtCore, QtWidgets, QtGui
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import uuid
import crypto
import logging


class Node (object):
    def __init__(self, name, parent=None, ca=True):
        # Tree Specific Variables
        self._name = name
        self._parent = parent
        self._children = []
        # Certificate Variables
        self._description = ''
        self._uid = uuid.uuid4()
        self._common_name = None
        self._organization_name = None
        self._locality_name = None
        self._state_or_province_name = None
        self._country_name = None
        self._email_address = None
        self._domain_component = None
        self._organizational_unit_name = None
        self._date_start = None
        self._date_end = None
        self._key_length = 256
        self._key = crypto.Key(self)
        self._subject_alt_names = []
        self._rfc_usage = 'KeyEstablishment'
        if ca is True:
            self._basic_constraint_ca = True
            self._basic_constraint_path_length = None
            self._key_usage = {'digital_signature': True,
                                    'content_commitment': True,
                                    'key_encipherment': False,
                                    'data_encipherment': False,
                                    'key_agreement': False,
                                    'key_cert_sign': True,
                                    'crl_sign': True,
                                    'encipher_only': False,
                                    'decipher_only': False}
        else:
            self._basic_constraint_ca = False
            self._basic_constraint_path_length = None
            self._key_usage = {'digital_signature': False,
                                    'content_commitment': False,
                                    'key_encipherment': False,
                                    'data_encipherment': False,
                                    'key_agreement': True,
                                    'key_cert_sign': False,
                                    'crl_sign': False,
                                    'encipher_only': True,
                                    'decipher_only': True}
        # self._basic_constraint_ca = False
        # self._basic_constraint_path_length = None
        # self._key_usage = {'digital_signature': True,
        #                    'content_commitment': True,
        #                    'key_encipherment': False,
        #                    'data_encipherment': False,
        #                    'key_agreement': False,
        #                    'key_cert_sign': True,
        #                    'crl_sign': True,
        #                    'encipher_only': False,
        #                    'decipher_only': False}

        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        else:
            self._children.insert(position, child)
            child._parent = self
            return True

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        else:
            child = self._children.pop(position)
            child._parent = None
            return False

    def child(self, row):
        # print("{} Row:{}  :  Children{}".format(self._name, row, len(self._children)-1))
        if 0 <= row < len(self._children):
            return self._children[row]

    @property
    def child_count(self):
        return len(self._children)

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    # Setters and Getters
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def uid(self):
        return str(self._uid)

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def common_name(self):
        return self._common_name

    @common_name.setter
    def common_name(self, value):
        self._common_name = value

    @property
    def organizational_unit_name(self):
        return self._organizational_unit_name

    @organizational_unit_name.setter
    def organizational_unit_name(self, value):
        self._organizational_unit_name = value

    @property
    def organization_name(self):
        return self._organization_name

    @organization_name.setter
    def organization_name(self, value):
        self._organization_name = value

    @property
    def locality_name(self):
        return self._locality_name

    @locality_name.setter
    def locality_name(self, value):
        self._locality_name = value

    @property
    def state_or_province_name(self):
        return self._state_or_province_name

    @state_or_province_name.setter
    def state_or_province_name(self, value):
        self._state_or_province_name = value

    @property
    def country_name(self):
        return self._country_name

    @country_name.setter
    def country_name(self, value):
        self._country_name = value

    @property
    def email_address(self):
        return self._email_address

    @email_address.setter
    def email_address(self, value):
        self._email_address = value

    @property
    def domain_component(self):
        return self._domain_component

    @domain_component.setter
    def domain_component(self, value):
        self._domain_component = value

    @property
    def date_start(self):
        return self._date_start

    @date_start.setter
    def date_start(self, value):
        self._date_start = value

    @property
    def date_end(self):
        return self._date_end

    @date_end.setter
    def date_end(self, value):
        self._date_end = value

    @property
    def subject_alt_names(self):
        return self._subject_alt_names

    @subject_alt_names.setter
    def subject_alt_names(self, value: list()):
        for i, v in enumerate(value):
            value[i] = v.strip()
        self._subject_alt_names = value

    def subject_alt_names_add(self, value):
        self._subject_alt_names.append(value)

    def subject_alt_names_del(self, row):
        del self._subject_alt_names[row]

    @property
    def basic_constraint_ca(self):
        if self._basic_constraint_ca is not None:
            return self._basic_constraint_ca

    @basic_constraint_ca.setter
    def basic_constraint_ca(self, value):
        self._basic_constraint_ca = value

    @property
    def key_usage(self):
        return self._key_usage

    @key_usage.setter
    def key_usage(self, value):
        self._key_usage = value

    # KeyUsage getters and Setters

    @property
    def digital_signature(self):
        return self._key_usage['digital_signature']

    @digital_signature.setter
    def digital_signature(self, value):
        self._key_usage['digital_signature'] = value

    @property
    def content_commitment(self):
        return self._key_usage['content_commitment']

    @content_commitment.setter
    def content_commitment(self, value):
        self._key_usage['content_commitment'] = value

    @property
    def key_encipherment(self):
        return self._key_usage['key_encipherment']

    @key_encipherment.setter
    def key_encipherment(self, value):
        self._key_usage['key_encipherment'] = value

    @property
    def data_encipherment(self):
        return self._key_usage['data_encipherment']

    @data_encipherment.setter
    def data_encipherment(self, value):
        self._key_usage['data_encipherment'] = value

    @property
    def key_agreement(self):
        return self._key_usage['key_agreement']

    @key_agreement.setter
    def key_agreement(self, value):
        self._key_usage['key_agreement'] = value

    @property
    def key_cert_sign(self):
        return self._key_usage['key_cert_sign']

    @key_cert_sign.setter
    def key_cert_sign(self, value):
        self._key_usage['key_cert_sign'] = value

    @property
    def crl_sign(self):
        return self._key_usage['crl_sign']

    @crl_sign.setter
    def crl_sign(self, value):
        self._key_usage['crl_sign'] = value

    @property
    def encipher_only(self):
        return self._key_usage['encipher_only']

    @encipher_only.setter
    def encipher_only(self, value):
        self._key_usage['encipher_only'] = value

    @property
    def decipher_only(self):
        return self._key_usage['decipher_only']

    @decipher_only.setter
    def decipher_only(self, value):
        self._key_usage['decipher_only'] = value

    @property
    def rfc_usage(self):
        return self._rfc_usage

    @rfc_usage.setter
    def rfc_usage(self, value):
        self._rfc_usage = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    def key_create(self, passphrase=''):
        self._key = crypto.Key(self._key_length, passphrase)

    def __str__(self):
        if self.parent is None:
            return 'name={} : Parent={} : Keys_Gen={}'.format(self.name, 'None', self.key is not None)
        else:
            return 'name={} : Parent={} : Keys_Gen={}'.format(self.name, self.parent.name, self.key is not None)


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        """ rowCount(self, parent: QModelIndex = QModelIndex()) -> int """
        if not parent.isValid():
            parent_node = self._rootNode
        elif parent.column() > 0:
            return 0
        else:
            parent_node = parent.internalPointer()

        return parent_node.child_count

    @property
    def root(self):
        return self._rootNode

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return 2

    def data(self, index, role=None):
        if not index.isValid():
            return None
        node = index.internalPointer()
        # print ("Role = {} : Column = {} : Row = {}".format(role, index.column(), index.row()))
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name
            if index.column() == 1:
                return node.description
            if index.column() == 2:
                return node.uid
            if index.column() == 3:
                return node.common_name
            if index.column() == 4:
                return node.organizational_unit_name
            if index.column() == 5:
                return node.organization_name
            if index.column() == 6:
                return node.locality_name
            if index.column() == 7:
                return node.state_or_province_name
            if index.column() == 8:
                return node.country_name
            if index.column() == 9:
                return node.email_address
            if index.column() == 10:
                return node.domain_component
            if index.column() == 11:
                return node.basic_constraint_ca
            if index.column() == 12:
                return node.digital_signature
            if index.column() == 13:
                return node.content_commitment
            if index.column() == 14:
                return node.key_encipherment
            if index.column() == 15:
                return node.data_encipherment
            if index.column() == 16:
                return node.key_agreement
            if index.column() == 17:
                return node.key_cert_sign
            if index.column() == 18:
                return node.crl_sign
            if index.column() == 19:
                return node.encipher_only
            if index.column() == 20:
                return node.decipher_only
            if index.column() == 21:
                if node.key:
                    if node.key._str_key:
                        return node.key._str_key.decode()
            if index.column() == 22:
                if node.key:
                    if node.key._str_csr:
                        return node.key._str_csr.decode()
            if index.column() == 23:
                if node.key:
                    if node.key._str_certificate:
                        return node.key._str_certificate.decode()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                if index.column() == 0:
                    node.name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 1:
                    node.description = value
                    self.dataChanged.emit(index, index)
                if index.column() == 2:
                    node.uid = value
                    self.dataChanged.emit(index, index)
                if index.column() == 3:
                    node.common_name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 4:
                    node.organizational_unit_name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 5:
                    node.organization_name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 6:
                    node.locality_name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 7:
                    node.state_or_province_name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 8:
                    node.country_name = value
                    self.dataChanged.emit(index, index)
                if index.column() == 9:
                    node.email_address = value
                    self.dataChanged.emit(index, index)
                if index.column() == 10:
                    node.domain_component = value
                    self.dataChanged.emit(index, index)
                if index.column() == 11:
                    node.basic_constraint_ca = value
                    self.dataChanged.emit(index, index)
                if index.column() == 12:
                    node.digital_signature = value
                    self.dataChanged.emit(index, index)
                if index.column() == 13:
                    node.content_commitment = value
                    self.dataChanged.emit(index, index)
                if index.column() == 14:
                    node.key_encipherment = value
                    self.dataChanged.emit(index, index)
                if index.column() == 15:
                    node.data_encipherment = value
                    self.dataChanged.emit(index, index)
                if index.column() == 16:
                    node.key_agreement = value
                    self.dataChanged.emit(index, index)
                if index.column() == 17:
                    node.key_cert_sign = value
                    self.dataChanged.emit(index, index)
                if index.column() == 18:
                    node.crl_sign = value
                    self.dataChanged.emit(index, index)
                if index.column() == 19:
                    node.encipher_only = value
                    self.dataChanged.emit(index, index)
                if index.column() == 20:
                    node.decipher_only = value
                    self.dataChanged.emit(index, index)
                if index.column() == 21:
                    node.key._str_key = value.encode()
                    self.dataChanged.emit(index, index)
                if index.column() == 22:
                    if value.startswith('-----BEGIN CERTIFICATE REQUEST-----'):
                        node.key._str_csr = value.encode()
                    else:
                        value = '-----BEGIN CERTIFICATE REQUEST-----\n' + value
                        value += '-----END CERTIFICATE REQUEST-----\n'
                        # remove white space and blank lines
                        new_value = ''
                        for line in value.split('\n'):
                            if re.match(r'^\s*$', line):
                                pass
                            else:
                                new_value += line + '\n'
                        node.key._str_csr = new_value.encode()
                    self.dataChanged.emit(index, index)
                if index.column() == 23:
                    node.key._str_certificate = value.encode()
                    self.dataChanged.emit(index, index)

                return True
        return False

    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Name"
            else:
                return ""

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.NoItemFlags

    def parent(self, index=QtCore.QModelIndex()):
        """
                parent(self, QModelIndex) -> QModelIndex
                parent(self) -> QObject
        """
        if index.isValid():
            node = self.getNode(index)
            if node is not None:
                parent_node = node.parent
                # print('          S={}\n        P={}'.format(node.name, parent_node.name))
            else:
                return QtCore.QModelIndex()

            if parent_node == self._rootNode:
                return QtCore.QModelIndex()

            return self.createIndex(parent_node.row(), 0, parent_node)
        else:
            return QtCore.QModelIndex()

    def index(self, row, column, parent=None, *args, **kwargs):
        """ index(self, int, int, parent: QModelIndex = QModelIndex()) -> QModelIndex """
        if row < 0 or column < 0:
            return QtCore.QModelIndex()
        parent_node = self.getNode(parent)
        child_item = parent_node.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def insertRow(self, row, parent=None, name='untitled', ca=True):
        return self.insertRows(row, 1, parent, **kwargs)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), *args, **kwargs):
        success = None
        parent_node = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            child_node = Node(kwargs['name'], ca=kwargs['ca'])
            child_node.organizational_unit_name = parent_node.organizational_unit_name
            child_node.organization_name = parent_node.organization_name
            child_node.locality_name = parent_node.locality_name
            child_node.state_or_province_name = parent_node.state_or_province_name
            child_node.country_name = parent_node.country_name
            child_node.email_address = parent_node.email_address
            child_node.domain_component = parent_node.domain_component
            success = parent_node.insertChild(position, child_node)
        self.endInsertRows()
        return success

    def removeRow(self, row, parent=None, *args, **kwargs):
        return self.removeRows(row, 1, parent, **kwargs)

    def removeRows(self, position, rows, parent=QtCore.QModelIndex(), *args, **kwargs):
        success = None
        parent_node = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            success = parent_node.removeChild(position)

        self.endRemoveRows()
        return success

    def getNode(self, index):
        if index:
            if index.isValid():
                node = index.internalPointer()
                if node:
                    return node
        return self._rootNode


if __name__ == "__main__":
    pass
