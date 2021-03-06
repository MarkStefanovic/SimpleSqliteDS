from PyQt4 import QtCore, QtGui


def convert_to_bool(val):
    if 'true' in str(val).lower():
        return True
    elif 'false' in str(val).lower():
        return False
    elif isinstance(val, int):
        if val == 0:
            return False
        return True
    else:
        return val


class CheckBoxDelegate(QtGui.QStyledItemDelegate):
    """A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent) -> None:
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index) -> None:
        return None

    def paint(self, painter, option, index) -> None:
        """Paint the checkbox."""
        checked = convert_to_bool(index.data())
        check_box_style_option = QtGui.QStyleOptionButton()

        if QtCore.Qt.ItemIsEditable:
            check_box_style_option.state |= QtGui.QStyle.State_Enabled
        else:
            check_box_style_option.state |= QtGui.QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtGui.QStyle.State_On
        else:
            check_box_style_option.state |= QtGui.QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)

        check_box_style_option.state |= QtGui.QStyle.State_Enabled
        QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index) -> bool:
        """Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        """
        if not QtCore.Qt.ItemIsEditable:
            return False
        elif event.type() == QtCore.QEvent.MouseButtonPress:
            return False
        elif event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() != QtCore.Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QtCore.QEvent.KeyPress:
            return False
        self.setModelData(None, model, index)
        return True

    def setModelData (self, editor, model, index) -> None:
        """Save the changes to the model."""
        new_value = not convert_to_bool(index.data())
        model.setData(index, new_value, QtCore.Qt.EditRole)

    def getCheckBoxRect(self, option):
        check_box_style_option = QtGui.QStyleOptionButton()
        check_box_rect = QtGui.QApplication.style().subElementRect(QtGui.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint(
            option.rect.x() + option.rect.width()/2 - check_box_rect.width()/2,
            option.rect.y() + option.rect.height()/2 - check_box_rect.height()/2
        )
        return QtCore.QRect(check_box_point, check_box_rect.size())
