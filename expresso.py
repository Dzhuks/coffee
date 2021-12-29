import sqlite3
import sys

from main import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("coffee.db")
        self.load.clicked.connect(self.load_table)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.add.clicked.connect(self.save_results)
        self.modified = {}
        self.titles = None

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
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())