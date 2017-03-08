from PyQt5 import QtCore, QtWidgets, QtGui
import uuid
import json


class Node (object):
    def __init__(self, name, parent=None):
        self._name = name
        self._description = ''
        self._children = []
        self._parent = parent
        self._uid = uuid.uuid4()
        self._commonName = "Test"
        self._organization = None
        self._locality = None
        self._stateOrProvince = None
        self._country = None
        self._privateKey = None
        self._certificate = None
        self._certSignReq = None
        self._dateStart = None
        self._dateEnd = None

        if parent is not None:
            parent.addChild(self)

        # print ("Created  {} : {}".format(self._name, self._uid))

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
    @property
    def name(self):
        return self._name

    def child(self, row):
        # print("{} Row:{}  :  Children{}".format(self._name, row, len(self._children)-1))
        if 0 <= row < len(self._children):
            return self._children[row]

    @property
    def child_count(self):
        return len(self._children)

    @property
    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            # print (self._parent._children.index(self))
            return self._parent._children.index(self)

    def save_data(self, filename):
        with open(filename, 'w') as f:
            json.dumps(self)

    # setters
    def setName(self, value):
        self._name = value

    def setUID(self, value):
        self._uid = value

    def setDescription(self, value):
        self._description = value

    def setCommonName(self, value):
        self._commonName = value

    def setOrganization(self, value):
        self._organization = value

    def setLocality(self, value):
        self._locality = value

    def setStateOrProvince(self, value):
        self._stateOrProvince = value

    def setCountry(self, value):
        self._country = value

    def setPrivateKey(self, value):
        self._privateKey = value

    def setCertificate(self, value):
        self._certificate = value

    def setCertSignReq(self, value):
        self._certSignReq = value

    def setDateStart(self, value):
        self._dateStart = value

    def setDateEnd(self, value):
        self._dateEnd = value

    # getters
    def get_root(self):
        return str(self._root)

    def getName(self):
        return str(self._name)

    def getUID(self):
        return str(self._uid)

    def getDescription(self):
        return str(self._description)

    def getCommonName(self):
        return self._commonName

    def getOrganization(self):
        return self._organization

    def getLocality(self):
        return self._locality

    def getStateOrProvince(self):
        return self._stateOrProvince

    def getCountry(self):
        return self._country

    def getPrivateKey(self):
        return self._privateKey

    def getCertificate(self):
        return self._certificate

    def getCertSignReq(self):
        return self._certSignReq

    def getDateStart(self):
        return self._dateStart

    def getDateEnd(self):
        return self._dateEnd


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(TreeModel,self).__init__(parent)
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

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return 3

    def data(self, index, role=None):
        if not index.isValid():
            return None
        node = index.internalPointer()
        # print ("Role = {} : Column = {} : Row = {}".format(role, index.column(), index.row()))
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                # print ("Col0 = {}".format(node.name()))
                # return node.name()
                return node.name
            if index.column() == 1:
                # print("Col1 = {}".format(node.name()))
                return node.getDescription()
                # return str(index + node.parent)
            if index.column() == 2:
                # print("Col1 = {}".format(node.name()))
                return node.getUID()
                # return str(index + node.parent)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                if index.column() == 0:
                    node.setName(value)
                    self.dataChanged.emit(index, index)
                if index.column() == 1:
                    node.setDescription(value)
                    self.dataChanged.emit(index, index)
                if index.column() == 2:
                    node.setUID(value)
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

    def insertRow(self, row, parent=None, *args, **kwargs):
        return self.insertRows(row, 1, parent, **kwargs)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), *args, **kwargs):
        parent_node = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            if 'name' in kwargs.keys():
                child_node = Node(kwargs['name'])
            else:
                child_node = Node('Untitled')
            success = parent_node.insertChild(position, child_node)
            # self.layoutChanged.emit()
        self.endInsertRows()
        # self.dataChanged.emit(parent, parent)
        return success

    def removeRow(self, row, parent=None, *args, **kwargs):
        return self.removeRows(row, 1, parent, **kwargs)

    def removeRows(self, position, rows, parent=QtCore.QModelIndex(), *args, **kwargs):
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
                    # print("getNode Returned Node")
                    return node
        # print("getNode Returned Root Node")
        return self._rootNode


if __name__ == "__main__":
    pass
