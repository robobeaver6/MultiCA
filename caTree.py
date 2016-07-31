from PyQt5 import QtCore, QtWidgets, QtGui
import uuid


class Node (object):
    def __init__(self, name, parent=None):
        self._name = name
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

        #print ("Created  {} : {}".format(self._name, self._uid))

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        else:
            self._children.insert(position, child)
            child._parent = self

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        else:
            child = self._children.pop(position)
            child._parent = None

    def name(self):
        return self._name

    def child(self, row):
        print("Row: {}  :  {}".format(row, len(self._children)-1))
        if row < len(self._children) and row >= 0:
            return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            #print (self._parent._children.index(self))
            return self._parent._children.index(self)

    ## setters
    def setName(self, value):
        self._name = value

    def setUID(self, value):
        self._uid = value

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

    ##getters
    def getUID(self):
        return str(self._uid)

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

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role=None):
        if not index.isValid():
            return None

        node = index.internalPointer()
        #print ("Role = {} : Column = {} : Row = {}".format(role, index.column(), index.row()))
        if role == QtCore.Qt.DisplayRole or QtCore.Qt.EditRole:
            if index.column() == 0:
                #print ("Col0 = {}".format(node.name()))
                return node.name()
            if index.column() == 1:
                #print("Col1 = {}".format(node.name()))
                return node.getUID()



    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                if index.column() == 0:
                    node.setName(value)
                    # noinspection PyUnresolvedReferences
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
            #return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index=QtCore.QModelIndex()):
        if index.isValid():
            node = self.getNode(index)
            parentNode = node.parent()
            row = parentNode.row()
            print("   {}   {}  ".format(row, index.column()))
            if parentNode == self._rootNode or row == None:
                return QtCore.QModelIndex()

            newIndex = self.createIndex(row, 0, parentNode)

            return newIndex
        print("INVALID Index in Parent func")
        return QtCore.QModelIndex()

    def index(self, row, column, parent=None, *args, **kwargs):
        if row<0 or column <0:
            return QtCore.QModelIndex()

        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()


    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), *args, **kwargs):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            childNode = Node("Untitled")
            success = parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex(), *args, **kwargs):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            success = parentNode.removeChild(position)

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
