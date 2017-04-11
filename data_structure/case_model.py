"""@package data_structure.case_model

File that contains the class CaseModel that creates a model for the Case treeview list.

"""
from PyQt4 import QtCore, QtGui
from occ_modules.shape_properties import shape_colorlist, shape_colordictionary, shape_colordictionaryhex

class CaseModel(QtCore.QAbstractItemModel):
    """
    This is a creation of a model for the tree view list.

    It inherits the basic QAbstractItemModel classThe QAbstractItemModel class defines the standard interface that
    item models must use to be able to inter-operate with other components in the model/view architecture. It is not
    supposed to be instantiated directly. Instead, you should subclass it to create new models. This model will be
    the one used by a a data_structure.case_node.CaseNode object.

    When subclassing QAbstractItemModel, at the very least you must implement index(), parent(), rowCount(),
    columnCount(), and data(). These functions are used in all read-only models, and form the basis of editable
    models. More info: http://doc.qt.io/qt-5/qabstractitemmodel.html#details

    """

    def __init__(self, root, parent=None):
        super(CaseModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        """
        Returns the number of rows under the given parent. When the parent is valid it means that rowCount is returning
        the number of children of parent.

        """
        if not parent.isValid():
            parent_node = self._rootNode
        else:
            parent_node = parent.internalPointer()

        return parent_node.childCount()

    def columnCount(self, parent):
        """
        Returns the number of columns for the children of the given parent.
        ref: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#columncount

        """
        return 2

    def data(self, index, role):
        """
        Returns the data stored under the given role for the item referred to by the index.
        """
        if not index.isValid():
            return None

        node = index.internalPointer()


        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()

            if index.column() == 1:
                if node.tecplotIsVisible():
                    return node.tecplotMode()
                else:
                    return "hidden"

            if index.column() == 3:
                return node.shapeQuality()

            if index.column() == 4:
                return node.shapeTransparency()

            if index.column() == 5:
                return node.shapeColor()

            if index.column() == 6:
                return node.shapeTransformation()[0]

            if index.column() == 7:
                return node.shapeTransformation()[1]

            if index.column() == 8:
                return node.shapeTransformation()[2]

            if index.column() == 9:
                return node.shapeTransformation()[3]

            if index.column() == 10:
                return node.shapeTransformation()[4]




        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                pixmap = QtGui.QPixmap(26, 26)
                pixmap.fill(shape_colordictionaryhex[shape_colorlist[node.shapeColor()]])
                icon = QtGui.QIcon(pixmap)
                return icon


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Sets the role data for the item at index to value.
        ref: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#setdata

        """
        if index.isValid():

            node = index.internalPointer()

            if role == QtCore.Qt.EditRole:

                if index.column() == 0:
                    node.setName(value)
                if index.column() == 3:
                    node.setShapeQuality(value)
                if index.column() == 4:
                    node.setShapeTransparency(value)
                if index.column() == 5:
                    node.setShapeColor(value)
                if index.column() == 6:
                    node.setShapeTransformation(value, 0)
                if index.column() == 7:
                    node.setShapeTransformation(value, 1)
                if index.column() == 8:
                    node.setShapeTransformation(value, 2)
                if index.column() == 9:
                    node.setShapeTransformation(value, 3)
                if index.column() == 10:
                    node.setShapeTransformation(value, 4)

                self.dataChanged.emit(index, index)
                return True

        return False

    def headerData(self, section, orientation, role):
        """
        Returns the data for the given role and section in the header with the specified orientation.
        http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#headerdata
        """
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Case"
            else:
                return "TecPlot Disp."

    def flags(self, index):
        """
        Returns the item flags for the given index.
        ref: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#flags

        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def parent(self, index):
        """
        Returns the parent of the model item with the given index.
        ref: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#parent

        """

        node = self.getNode(index)
        parent_node = node.parent()

        if parent_node == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        """
        Returns the index of the item in the model specified by the given row, column and parent index.
        ref: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#index

        """

        parent_node = self.getNode(parent)
        child_item = parent_node.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):

        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Method for removing rows from the data structure
        ref: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemmodel.html#removeows

        """
        parent_node = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parent_node.removeChild(position)

        self.endRemoveRows()

        return success