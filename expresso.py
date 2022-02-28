import sqlite3
import sys

from main import Ui_MainWindow
from addEditCoffeeForm import Ui_Dialog
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


DATABASE = "data/coffee.db"


class Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.ok = False

        self.buttonBox.accepted.connect(lambda: self.change(True))

        # adding action when form is rejected
        self.buttonBox.rejected.connect(lambda: self.change(False))

    def change(self, arg):
        self.ok = arg
        self.close()


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect(DA)
        self.titles = []
        self.load_table()
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.add.clicked.connect(self.dialog)
        self.modified = {}

    def load_table(self):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        result = cur.execute("SELECT * FROM coffees").fetchall()
        # Если запись не нашлась, то не будем ничего делать
        if not result:
            self.statusBar().showMessage('Ничего не нашлось')
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.tableWidget.clear()
            return
        else:
            self.statusBar().showMessage(f"База данных загрузилась")
        # Заполнили размеры таблицы
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def dialog(self):
        dialog = Dialog()
        dialog.exec_()
        if dialog.ok:
            self.add_item([dialog.lineEdit.text(), dialog.lineEdit_2.text(), dialog.lineEdit_3.text(),
                           dialog.textEdit.toPlainText(), dialog.lineEdit_4.text(), dialog.lineEdit_5.text()])

    def item_changed(self, item):
        # Если значение в ячейке было изменено,
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            cur = self.con.cursor()
            que = "UPDATE coffees SET\n"
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += "WHERE id = ?"
            print(que)
            cur.execute(que, (self.spinBox.text(),))
            self.con.commit()
            self.modified.clear()

    def add_item(self, *args):
        cur = self.con.cursor()
        values = map(lambda x: f"'{x}'", args[0])
        columns = map(lambda x: f"'{x}'", self.titles[1:])
        que = f"INSERT INTO coffees({', '.join(columns)}) Values({', '.join(values)})"
        print(que)
        cur.execute(que)
        self.con.commit()
        self.load_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
