from PyQt5 import QtGui, QtCore, QtWidgets, uic, Qt
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import sys

def main():
    if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("cleanlooks")
        # DATA
        data = ["one", "two", "three", "four", "five"]

        listView = QtWidgets.QListView()
        listView.show()


        model = QtCore.QStringListModel(data)

        listView.setModel(model)
        model.dataChanged.connect(edit_finished)
        listView.append('123')
        listView.currentIndex()
        print(model)
        sys.exit(app.exec_())

@pyqtSlot()
def edit_finished():
    print('Edit Finished')



if __name__ == '__main__':


    main()
